"""
Pytest + Playwright Configuration for Wagtail Tests.

Features:
- 1280x720 viewport (demo-friendly)
- 10s default timeout
- Automatic screenshot on failure
"""

import pytest
import os
from playwright.sync_api import Page


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
    }


@pytest.fixture(autouse=True)
def configure_page(page: Page):
    page.set_default_timeout(10000)
    page.set_default_navigation_timeout(30000)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed:
        page = item.funcargs.get("page")
        if page:
            os.makedirs("test-results/screenshots", exist_ok=True)
            path = f"test-results/screenshots/{item.name}.png"
            try:
                page.screenshot(path=path)
            except Exception:
                pass
