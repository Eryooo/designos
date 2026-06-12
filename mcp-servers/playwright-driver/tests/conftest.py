"""Pytest configuration for playwright-driver tests.

Implements the web-mode test partition (see docs/releases/web-mode-baseline/):

- `unit`                : pure logic, no browser. Must pass in ANY environment.
- `requires_playwright` : needs the `playwright` Python package importable.
- `browser_smoke`       : needs chromium binaries launchable (`playwright install`).

When an optional dependency is missing, the gated layers are SKIPPED with an
explicit reason — never failed. A missing dependency is an environment fact, not
a capability regression, so it must not pollute the web-mode quality signal.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "unit: pure-logic tests that need no Playwright dependency (any environment).",
    )
    config.addinivalue_line(
        "markers",
        "requires_playwright: needs the `playwright` Python package importable.",
    )
    config.addinivalue_line(
        "markers",
        "browser_smoke: needs chromium binaries launchable (real-browser smoke).",
    )


def _playwright_importable() -> bool:
    try:
        import playwright.sync_api  # noqa: F401

        return True
    except Exception:
        return False


def _chromium_launchable() -> bool:
    if not _playwright_importable():
        return False
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            browser.close()
        return True
    except Exception:
        return False


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    have_pkg = _playwright_importable()
    have_browser: bool | None = None  # computed lazily, only if needed

    skip_pkg = pytest.mark.skip(
        reason="requires_playwright: `playwright` package not importable "
        "(install with `pip install playwright`)."
    )
    skip_browser = pytest.mark.skip(
        reason="browser_smoke: chromium binaries not launchable "
        "(run `playwright install chromium`)."
    )

    for item in items:
        if "requires_playwright" in item.keywords and not have_pkg:
            item.add_marker(skip_pkg)
            continue
        if "browser_smoke" in item.keywords:
            if have_browser is None:
                have_browser = _chromium_launchable()
            if not have_browser:
                item.add_marker(skip_browser)
