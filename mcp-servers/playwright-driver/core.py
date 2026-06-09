"""Core browser management for playwright-driver MCP server."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

try:
    from playwright.sync_api import (
        Browser,
        BrowserContext,
        Frame,
        Page,
        Playwright,
        sync_playwright,
    )

    _PLAYWRIGHT_IMPORT_ERROR: ImportError | None = None
except ImportError as exc:  # pragma: no cover - exercised via dependency-absent tests
    # Defer the failure: importing this module must NOT require Playwright to be
    # installed. Pure-logic consumers (schemas, evidence_builder, server tool
    # definitions, the JSON script executor under mock browsers) can import and
    # be unit-tested with no browser dependency. The error only surfaces when a
    # caller actually tries to drive a real browser via BrowserManager.launch().
    Browser = BrowserContext = Frame = Page = Playwright = object  # type: ignore[assignment,misc]
    sync_playwright = None  # type: ignore[assignment]
    _PLAYWRIGHT_IMPORT_ERROR = exc

from schemas import PageState, SessionInfo


def playwright_available() -> bool:
    """Return True when the optional `playwright` package is importable.

    Note: this only checks the Python package import, not whether browser
    binaries are installed. A real launch can still fail if `playwright install`
    has not been run; that surfaces from BrowserManager.launch() directly.
    """
    return sync_playwright is not None


_DEFAULT_VIEWPORT = {"width": 1440, "height": 900}
_DEFAULT_TIMEOUT_MS = 30000
_SETTLE_TIMEOUT_MS = 5000


class BrowserManager:
    """Manages browser lifecycle and interactions."""

    def __init__(self) -> None:
        self._playwright: Playwright | None = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None
        self._frame: Frame | None = None
        self._session_id: str | None = None
        self._user_data_dir: str | None = None

    @property
    def is_active(self) -> bool:
        return self._context is not None

    def launch(
        self,
        url: str,
        headless: bool = False,
        user_data_dir: str | None = None,
    ) -> SessionInfo:
        if self.is_active:
            raise RuntimeError("Browser session already active. Close first.")

        if sync_playwright is None:
            raise RuntimeError(
                "Web mode requires Playwright, but the `playwright` package is not "
                "installed. Install it and the chromium binaries, then retry:\n"
                '  1. pip install -e ".[web]"\n'
                "  2. python -m playwright install chromium\n"
                f"(original import error: {_PLAYWRIGHT_IMPORT_ERROR})"
            )

        self._playwright = sync_playwright().start()

        if user_data_dir is None:
            user_data_dir = str(
                Path.home() / ".designos" / "playwright-sessions" / "default"
            )
        Path(user_data_dir).mkdir(parents=True, exist_ok=True)
        self._user_data_dir = user_data_dir

        self._context = self._playwright.chromium.launch_persistent_context(
            user_data_dir,
            headless=headless,
            viewport=_DEFAULT_VIEWPORT,
            locale="zh-CN",
            ignore_https_errors=True,
            no_viewport=not headless,
        )
        self._context.set_default_timeout(_DEFAULT_TIMEOUT_MS)

        self._page = (
            self._context.pages[0]
            if self._context.pages
            else self._context.new_page()
        )
        self._frame = None
        self._session_id = uuid.uuid4().hex[:12]

        self._page.goto(url, wait_until="domcontentloaded", timeout=60000)
        self._wait_settle()

        return SessionInfo(
            session_id=self._session_id,
            user_data_dir=user_data_dir,
            page_state=self.get_page_state(),
        )

    def close(self) -> None:
        if self._context:
            self._context.close()
        if self._playwright:
            self._playwright.stop()
        self._context = None
        self._playwright = None
        self._page = None
        self._frame = None
        self._session_id = None

    # --- Navigation & Interaction ---

    def navigate(self, url: str) -> PageState:
        self._ensure_active()
        self._page.goto(url, wait_until="domcontentloaded", timeout=60000)
        self._wait_settle()
        self._frame = None
        return self.get_page_state()

    def click(
        self,
        selector: str,
        selector_type: str = "css",
        timeout: int = _DEFAULT_TIMEOUT_MS,
    ) -> PageState:
        self._ensure_active()
        target = self._current_target()
        if selector_type == "text":
            target.get_by_text(selector, exact=False).first.click(timeout=timeout)
        elif selector_type == "role":
            target.get_by_role("button", name=selector).first.click(timeout=timeout)
        else:
            target.locator(selector).first.click(timeout=timeout)
        self._wait_settle()
        return self.get_page_state()

    def fill(self, selector: str, value: str) -> PageState:
        self._ensure_active()
        target = self._current_target()
        locator = target.locator(selector).first
        locator.fill("")
        locator.fill(value)
        return self.get_page_state()

    # --- Evidence Collection ---

    def screenshot(self, name: str, full_page: bool = True, output_dir: str | None = None) -> str:
        self._ensure_active()
        if output_dir is None:
            output_dir = str(Path.cwd() / "evidence")
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        path = str(Path(output_dir) / f"{name}.png")
        self._page.screenshot(path=path, full_page=full_page)
        return path

    def extract_dom(self, selector: str = "body") -> dict[str, Any]:
        self._ensure_active()
        target = self._current_target()
        return target.evaluate(
            """(sel) => {
                const el = document.querySelector(sel);
                if (!el) return {error: 'not found'};
                const items = el.querySelectorAll('a, button, input, select, textarea, [role], label, h1, h2, h3');
                return {
                    text: el.innerText.slice(0, 2000),
                    elements: Array.from(items).slice(0, 150).map(e => ({
                        tag: e.tagName.toLowerCase(),
                        text: (e.innerText || e.value || '').slice(0, 80),
                        role: e.getAttribute('role') || '',
                        href: e.getAttribute('href') || '',
                        type: e.getAttribute('type') || '',
                        placeholder: e.getAttribute('placeholder') || '',
                        aria_label: e.getAttribute('aria-label') || '',
                        classes: Array.from(e.classList).slice(0, 5),
                        name: e.getAttribute('name') || '',
                        id: e.getAttribute('id') || '',
                        disabled: e.disabled || false,
                        required: e.required || false,
                    }))
                };
            }""",
            selector,
        )

    def get_page_state(self, snippet: int = 800) -> PageState:
        self._ensure_active()
        target = self._current_target()
        body_text = ""
        try:
            body_text = target.locator("body").inner_text()[:snippet]
        except Exception:
            pass

        pages = self._context.pages
        frames = self._page.frames

        return PageState(
            url=self._page.url,
            title=self._page.title(),
            dom_text=body_text,
            page_index=pages.index(self._page) if self._page in pages else 0,
            page_count=len(pages),
            frame_index=frames.index(self._frame) if self._frame and self._frame in frames else 0,
            frame_count=len(frames),
        )

    # --- Multi-tab / iframe ---

    def switch_page(self, page_index: int | str = "last") -> PageState:
        self._ensure_active()
        pages = self._context.pages
        if page_index == "last":
            self._page = pages[-1]
        else:
            self._page = pages[int(page_index)]
        self._frame = None
        self._page.bring_to_front()
        self._page.wait_for_timeout(500)
        return self.get_page_state()

    def switch_frame(self, frame_selector: str | None = None, index: int | str = "main") -> PageState:
        self._ensure_active()
        if index == "main" and frame_selector is None:
            self._frame = None
            return self.get_page_state()
        if frame_selector:
            frames = self._page.frames
            match = next((f for f in frames if frame_selector in f.url), None)
            if match is None:
                raise ValueError(f"Frame not found: {frame_selector}")
            self._frame = match
        else:
            self._frame = self._page.frames[int(index)]
        return self.get_page_state()

    # --- Internal helpers ---

    def _ensure_active(self) -> None:
        if not self.is_active:
            raise RuntimeError("No active browser session.")

    def _current_target(self) -> Page | Frame:
        return self._frame if self._frame else self._page

    def _wait_settle(self) -> None:
        try:
            self._page.wait_for_load_state("domcontentloaded")
        except Exception:
            pass
        try:
            self._page.wait_for_load_state("networkidle", timeout=_SETTLE_TIMEOUT_MS)
        except Exception:
            pass
        self._page.wait_for_timeout(500)
