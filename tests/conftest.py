"""Shared pytest fixtures for KernHell test suite."""

from __future__ import annotations

from pathlib import Path
import pytest


@pytest.fixture
def fixtures_dir() -> Path:
    """Return the absolute path to tests/fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_dom_html(fixtures_dir: Path) -> str:
    """Read sample raw HTML."""
    return (fixtures_dir / "sample_dom.html").read_text(encoding="utf-8")


@pytest.fixture
def sample_dom_renamed_html(fixtures_dir: Path) -> str:
    """Read refactored HTML."""
    return (fixtures_dir / "sample_dom_renamed.html").read_text(encoding="utf-8")


@pytest.fixture
def sample_dom_missing_html(fixtures_dir: Path) -> str:
    """Read HTML where target element is absent."""
    return (fixtures_dir / "sample_dom_missing.html").read_text(encoding="utf-8")


@pytest.fixture
def sample_test_path(fixtures_dir: Path) -> Path:
    """Return path to sample_test.py."""
    return fixtures_dir / "sample_test.py"


@pytest.fixture
def sample_pytest_timeout_error(sample_test_path: Path) -> str:
    """Realistic pytest-playwright error output simulating a selector timeout."""
    return f"""
============================= test session starts =============================
platform win32 -- Python 3.11.0, pytest-8.1.1, pluggy-1.4.0
rootdir: C:\\project
plugins: playwright-0.4.4
collected 1 item

tests\\fixtures\\sample_test.py F                                        [100%]

================================== FAILURES ===================================
_________________________ test_checkout_purchase_flow _________________________

page = <Page url='https://example.com/checkout'>

    def test_checkout_purchase_flow(page: Page) -> None:
        page.goto("https://example.com/checkout")
        page.fill("#email-input", "buyer@example.com")
        page.fill("#address-input", "123 Innovation Way")
>       page.click("#buy-now")
E       playwright._impl._errors.TimeoutError: Page.click: Timeout 5000ms exceeded.
E       Call log:
E         - waiting for locator("#buy-now")
E         - locator resolved to 0 elements

{sample_test_path}:15: TimeoutError
=========================== short test summary info ===========================
FAILED tests/fixtures/sample_test.py::test_checkout_purchase_flow - playwright._impl._errors.TimeoutError: Page.click: Timeout 5000ms exceeded.
============================== 1 failed in 5.32s ==============================
"""
