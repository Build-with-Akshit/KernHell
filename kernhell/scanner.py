import subprocess
import os
import base64
from pathlib import Path
from typing import Tuple, Optional
from kernhell.utils import log_info, log_error, log_warning, CacheManager


def run_test(file_path: str, timeout: int = 60) -> Tuple[bool, str, str]:
    """
    Runs the given Python test script and captures output.
    Returns: (passed: bool, stdout: str, stderr: str)
    """
    file_path = str(Path(file_path).resolve())

    if not os.path.exists(file_path):
        return False, "", "File not found."

    log_info(f"Running test: {file_path}")

    try:
        result = subprocess.run(
            ["python", file_path],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        passed = (result.returncode == 0)
        return passed, result.stdout, result.stderr

    except subprocess.TimeoutExpired:
        log_error(f"Test timed out after {timeout} seconds.")
        return False, "", "TimeoutError: Test took too long to execute."
    except Exception as e:
        log_error(f"Failed to run test: {e}")
        return False, "", str(e)


def capture_failure_screenshot(file_path: str, error_url: str = None) -> Optional[str]:
    """
    Captures a screenshot of the page state at failure time.
    Uses Playwright to navigate to the URL from the test and screenshot.
    Returns: base64-encoded PNG string, or None on failure.
    """
    try:
        from playwright.sync_api import sync_playwright

        # Try to extract URL from the test file
        target_url = error_url
        if not target_url:
            target_url = _extract_url_from_file(file_path)

        if not target_url:
            log_warning("Could not extract URL from test file for screenshot.")
            return None

        # Use CacheManager relative to test file
        test_file = Path(file_path).resolve()
        # Assuming project root is parent of test file for now
        # TODO: Better project root detection
        cache = CacheManager(test_file.parent)
        screenshot_path = cache.get_screenshot_path(f"fail_{test_file.stem}")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(target_url, wait_until="domcontentloaded", timeout=15000)
            page.wait_for_timeout(2000)  # Let page settle
            page.screenshot(path=str(screenshot_path), full_page=True)
            browser.close()

        # Read and encode
        with open(screenshot_path, "rb") as f:
            img_data = base64.b64encode(f.read()).decode("utf-8")

        log_info(f"Screenshot captured: {screenshot_path.name}")
        return img_data

    except Exception as e:
        log_warning(f"Screenshot capture failed: {e}")
        return None


def _extract_url_from_file(file_path: str) -> Optional[str]:
    """Extracts the first URL from page.goto() calls in the test file."""
    import re
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Match page.goto("https://...") or page.goto('https://...')
        match = re.search(r'page\.goto\(["\']([^"\']+)["\']\)', content)
        if match:
            return match.group(1)
    except Exception:
        pass
    return None


def get_screenshot_as_base64(file_path: str) -> Optional[str]:
    """Returns cached screenshot if available, else captures new one."""
    test_file = Path(file_path).resolve()
    cache = CacheManager(test_file.parent)
    screenshot_path = cache.get_screenshot_path(f"fail_{test_file.stem}")
    
    if screenshot_path.exists():
        with open(screenshot_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return capture_failure_screenshot(file_path)
