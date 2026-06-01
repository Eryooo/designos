"""Integration tests for playwright-driver: multi-tab, iframe, end-to-end.

Layer 2/3 of the web-mode test partition. Every test here drives a REAL browser,
so the whole module is gated behind two markers:

- `requires_playwright`: the `playwright` Python package must be importable.
- `browser_smoke`: chromium binaries must be launchable (`playwright install`).

When either condition is unmet, conftest.py SKIPS these (with an explicit reason)
rather than letting them fail — a missing optional dependency is an environment
fact, not a capability regression. See docs/releases/web-mode-baseline/.
"""

import http.server
import threading
import time

import pytest

pytestmark = [pytest.mark.requires_playwright, pytest.mark.browser_smoke]

from core import BrowserManager
from schemas import ActionType, EvaluationScript, ScriptStep, SelectorType
from script_executor import ScriptExecutor


_PORT = 18925


class _TestHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        pages = {
            "/": b"<html><head><title>Main</title></head><body>"
            b"<h1>Main</h1>"
            b'<a href="/page2" target="_blank">New Tab</a>'
            b'<iframe src="/frame" id="f1"></iframe>'
            b'<button id="btn">Click</button>'
            b"</body></html>",
            "/page2": b"<html><head><title>Page2</title></head>"
            b"<body><p>Tab 2 content</p></body></html>",
            "/frame": b"<html><head><title>Frame</title></head>"
            b"<body><p>frame-inner-text</p></body></html>",
            "/rules": b"<html><head><title>Rules</title></head><body>"
            b"<h1>Rules</h1><button id='new'>New</button>"
            b"</body></html>",
            "/form": b"<html><head><title>Form</title></head><body>"
            b'<input id="name" type="text"><textarea id="desc"></textarea>'
            b"</body></html>",
        }
        self.wfile.write(pages.get(self.path, b"<html><body>404</body></html>"))


@pytest.fixture(scope="module")
def local_server():
    server = http.server.HTTPServer(("127.0.0.1", _PORT), _TestHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    time.sleep(0.3)
    yield f"http://127.0.0.1:{_PORT}"
    server.shutdown()


@pytest.fixture()
def browser(local_server):
    bm = BrowserManager()
    bm.launch(local_server, headless=True, user_data_dir=f"/tmp/pw-integ-{_PORT}")
    yield bm
    bm.close()


class TestMultiTab:
    def test_new_tab_and_switch(self, browser, local_server):
        browser.click("New Tab", selector_type="text")
        time.sleep(0.5)
        state = browser.switch_page("last")
        assert "Page2" in state.title

    def test_switch_back_to_first(self, browser, local_server):
        browser.click("New Tab", selector_type="text")
        time.sleep(0.5)
        browser.switch_page("last")
        state = browser.switch_page(0)
        assert "Main" in state.title


class TestIframe:
    def test_switch_to_iframe(self, browser):
        state = browser.switch_frame(frame_selector="frame")
        assert state.frame_count >= 2

    def test_read_iframe_content(self, browser):
        browser.switch_frame(frame_selector="frame")
        dom = browser.extract_dom("body")
        assert "frame-inner-text" in dom.get("text", "")

    def test_switch_back_to_main(self, browser):
        browser.switch_frame(frame_selector="frame")
        state = browser.switch_frame(index="main")
        assert state.frame_index == 0


class TestEndToEnd:
    def test_batch_script_execution(self, browser, local_server):
        script = EvaluationScript(
            task_id="T-E2E",
            task_title="End-to-end batch",
            steps=[
                ScriptStep(step=1, action=ActionType.NAVIGATE, url=f"{local_server}/rules", wait_after_ms=300),
                ScriptStep(step=2, action=ActionType.SCREENSHOT, name="e2e-01-rules"),
                ScriptStep(step=3, action=ActionType.EXTRACT_DOM, selector="body"),
            ],
        )
        executor = ScriptExecutor(browser, output_dir="/tmp/pw-integ-evidence")
        result = executor.execute(script)
        assert result.status == "completed"
        assert result.steps_succeeded == 3
        assert all(e.confidence == "ground_truth" for e in result.evidence)

    def test_form_fill_without_submit(self, browser, local_server):
        script = EvaluationScript(
            task_id="T-FORM",
            task_title="Form fill readonly",
            steps=[
                ScriptStep(step=1, action=ActionType.NAVIGATE, url=f"{local_server}/form", wait_after_ms=300),
                ScriptStep(step=2, action=ActionType.FILL, selector="#name", value="Test"),
                ScriptStep(step=3, action=ActionType.FILL, selector="#desc", value="Description"),
                ScriptStep(step=4, action=ActionType.SCREENSHOT, name="e2e-02-filled"),
                ScriptStep(step=5, action=ActionType.EXTRACT_DOM, selector="body"),
            ],
        )
        executor = ScriptExecutor(browser, output_dir="/tmp/pw-integ-evidence")
        result = executor.execute(script)
        assert result.status == "completed"
        assert result.steps_failed == 0
