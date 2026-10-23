"""Scanner runner — executes Playwright tests and captures failures + live DOM.

Weekend 1 strategy: **Subprocess-based** execution.
  1. Run the test file via ``pytest`` in a subprocess.
  2. If it fails, parse the error output for broken selectors.
  3. Re-launch a browser, navigate to the page URL extracted from the test,
     and capture ``page.content()`` for the live DOM snapshot.

This approach is simpler but less precise than the step-by-step interceptor
(planned for Weekend 3).  It works reliably for the common case where the
test navigates to a URL before interacting with elements.
"""

from __future__ import annotations

import asyncio
import subprocess
import re
import sys
from pathlib import Path

import structlog

from kernhell.core.config import KernHellConfig
from kernhell.core.exceptions import (
    NoFailuresDetectedError,
    PlaywrightNotInstalledError,
    ScannerError,
    TestFileNotFoundError,
)
from kernhell.core.models import FailureContext
from kernhell.scanner.parser import parse_playwright_errors

logger = structlog.get_logger()


def _extract_url_from_test(test_file: Path) -> str | None:
    """Extract the first ``page.goto(...)`` URL from a test file.

    This is a best-effort heuristic used to re-open the page for DOM capture.
    """
    try:
        content = test_file.read_text(encoding="utf-8")
    except Exception:
        return None

    # Match: page.goto("https://example.com") or page.goto('...')
    m = re.search(r"""page\.goto\(\s*["'](.+?)["']""", content)
    return m.group(1) if m else None


class ScannerRunner:
    """Executes a Playwright test file and captures failure context.

    Parameters
    ----------
    config:
        The KernHell configuration (scanner timeout, browser, headless, etc.).
    """

    def __init__(self, config: KernHellConfig) -> None:
        self._config = config
        self._scanner_cfg = config.scanner

    def run(self, test_file: Path) -> list[FailureContext]:
        """Run the test file and return structured failures.

        Parameters
        ----------
        test_file:
            Path to the Playwright test file (e.g., ``tests/test_checkout.py``).

        Returns
        -------
        list[FailureContext]
            One entry per broken selector detected.  The ``live_dom`` field
            will be populated if we can successfully re-open the page.

        Raises
        ------
        TestFileNotFoundError
            If *test_file* does not exist.
        ScannerError
            If the test runner itself fails to execute.
        NoFailuresDetectedError
            If the test passes with zero selector failures.
        """
        test_file = test_file.resolve()
        if not test_file.is_file():
            raise TestFileNotFoundError(f"Test file not found: {test_file}")

        logger.info("scanner.run.start", test_file=str(test_file))

        # Step 1: Run the test via pytest subprocess
        error_output = self._run_pytest(test_file)

        if error_output is None:
            raise NoFailuresDetectedError(
                f"All tests passed in {test_file.name} — nothing to heal!"
            )

        # Step 2: Parse the error output
        failures = parse_playwright_errors(error_output, test_file)

        if not failures:
            raise NoFailuresDetectedError(
                f"Test failed but no Playwright selector errors detected in {test_file.name}. "
                "The failure may not be selector-related."
            )

        # Step 3: Capture live DOM for each failure
        page_url = _extract_url_from_test(test_file)
        if page_url:
            live_dom = self._capture_live_dom(page_url)
            if live_dom:
                for f in failures:
                    f.live_dom = live_dom
                    f.page_url = page_url

        logger.info(
            "scanner.run.done",
            test_file=str(test_file),
            failures=len(failures),
            has_dom=bool(failures[0].live_dom) if failures else False,
        )
        return failures

    def _run_pytest(self, test_file: Path) -> str | None:
        """Execute pytest on the test file and return error output.

        Returns *None* if the test passes (exit code 0).
        """
        cmd = [
            sys.executable,
            "-m",
            "pytest",
            str(test_file),
            "-v",
            "--tb=long",
            "--no-header",
            f"--timeout={self._scanner_cfg.timeout_ms // 1000}",
        ]

        logger.debug("scanner.pytest.exec", cmd=" ".join(cmd))

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self._scanner_cfg.timeout_ms * 3 / 1000,  # 3x the action timeout
                cwd=str(test_file.parent),
            )
        except FileNotFoundError:
            raise PlaywrightNotInstalledError(
                "pytest is not installed or not on PATH. "
                "Run: pip install pytest pytest-playwright"
            )
        except subprocess.TimeoutExpired:
            raise ScannerError(
                f"Test execution timed out after {self._scanner_cfg.timeout_ms * 3}ms"
            )

        if result.returncode == 0:
            logger.info("scanner.pytest.passed", test_file=str(test_file))
            return None

        # Combine stdout and stderr for full error context
        combined = result.stdout + "\n" + result.stderr
        logger.debug(
            "scanner.pytest.failed",
            exit_code=result.returncode,
            output_len=len(combined),
        )
        return combined

    def _capture_live_dom(self, url: str) -> str:
        """Re-open the page URL and capture the live DOM HTML.

        Uses Playwright's sync API to launch a browser, navigate to the URL,
        and grab ``page.content()``.  This gives us the actual DOM state
        the developer sees, even if selectors changed.
        """
        try:
            return asyncio.get_event_loop().run_until_complete(
                self._async_capture_dom(url)
            )
        except RuntimeError:
            # No event loop running — create one
            return asyncio.run(self._async_capture_dom(url))

    async def _async_capture_dom(self, url: str) -> str:
        """Async implementation of DOM capture."""
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            raise PlaywrightNotInstalledError(
                "Playwright is not installed. Run: pip install playwright && playwright install"
            )

        logger.debug("scanner.dom_capture.start", url=url)

        try:
            async with async_playwright() as p:
                browser_type = getattr(p, self._scanner_cfg.browser, p.chromium)
                browser = await browser_type.launch(headless=self._scanner_cfg.headless)
                page = await browser.new_page()

                try:
                    await page.goto(
                        url,
                        wait_until="domcontentloaded",
                        timeout=self._scanner_cfg.timeout_ms,
                    )
                    # Wait a bit for dynamic content
                    await page.wait_for_timeout(1000)
                    dom = await page.content()

                    # Optional screenshot
                    if self._scanner_cfg.capture_screenshot:
                        screenshot = await page.screenshot(full_page=True)
                        logger.debug(
                            "scanner.screenshot.captured",
                            size=len(screenshot),
                        )

                    logger.info(
                        "scanner.dom_capture.done",
                        url=url,
                        dom_size=len(dom),
                    )
                    return dom
                finally:
                    await browser.close()

        except Exception as exc:
            logger.warning(
                "scanner.dom_capture.failed",
                url=url,
                error=str(exc),
            )
            return ""
