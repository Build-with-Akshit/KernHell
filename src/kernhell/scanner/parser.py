"""Playwright error output parser.

Parses structured error output from Playwright/pytest to extract:
  - The broken selector string
  - The line number in the test file where the failure occurred
  - The type of selector (CSS, XPath, text, role, etc.)
  - The error type (timeout, not found, strict mode, etc.)

This parser handles the standard Playwright error format from both
``pytest-playwright`` and raw Playwright Python output.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import structlog

from kernhell.core.models import ErrorType, FailureContext, SelectorType
from kernhell.utils.file_utils import extract_surrounding_lines, read_file

logger = structlog.get_logger()

# ---------------------------------------------------------------------------
# Regex patterns for Playwright error parsing
# ---------------------------------------------------------------------------

# Matches: "locator.click: Timeout 5000ms exceeded."
_TIMEOUT_PATTERN = re.compile(
    r"(locator\.\w+|page\.\w+):\s*Timeout\s+\d+ms\s+exceeded",
    re.IGNORECASE,
)

# Matches: "waiting for locator("button#buy-now")" or 'locator("#buy-now")'
_LOCATOR_PATTERN = re.compile(
    r"""locator\(\s*["'](.+?)["']\s*\)""",
    re.IGNORECASE,
)

# Matches: page.click("#buy-now") or page.fill("input.email", ...)
_PAGE_ACTION_PATTERN = re.compile(
    r"""page\.(?:click|fill|type|check|uncheck|select_option|hover|dblclick|focus)\(\s*["'](.+?)["']""",
    re.IGNORECASE,
)

# Matches: page.get_by_role("button", name="Buy Now")
_GET_BY_ROLE_PATTERN = re.compile(
    r"""page\.get_by_role\(\s*["'](\w+)["'](?:\s*,\s*name\s*=\s*["'](.+?)["'])?\s*\)""",
    re.IGNORECASE,
)

# Matches: page.get_by_text("Buy Now")
_GET_BY_TEXT_PATTERN = re.compile(
    r"""page\.get_by_text\(\s*["'](.+?)["']\s*\)""",
    re.IGNORECASE,
)

# Matches: page.get_by_test_id("checkout-btn")
_GET_BY_TESTID_PATTERN = re.compile(
    r"""page\.get_by_test_id\(\s*["'](.+?)["']\s*\)""",
    re.IGNORECASE,
)

# Matches: page.get_by_label("Email")
_GET_BY_LABEL_PATTERN = re.compile(
    r"""page\.get_by_label\(\s*["'](.+?)["']\s*\)""",
    re.IGNORECASE,
)

# Matches: page.get_by_placeholder("Enter email")
_GET_BY_PLACEHOLDER_PATTERN = re.compile(
    r"""page\.get_by_placeholder\(\s*["'](.+?)["']\s*\)""",
    re.IGNORECASE,
)

# Matches pytest traceback lines like: "tests/test_checkout.py:15: TimeoutError"
_PYTEST_LOCATION_PATTERN = re.compile(
    r"^(.+\.py):(\d+):\s*(TimeoutError|Error|AssertionError)",
    re.MULTILINE,
)

# Matches: "strict mode violation" errors
_STRICT_MODE_PATTERN = re.compile(
    r"strict\s+mode\s+violation",
    re.IGNORECASE,
)


@dataclass
class ParsedFailure:
    """Intermediate result from parsing a single Playwright error block."""

    selector: str = ""
    selector_type: SelectorType = SelectorType.UNKNOWN
    error_type: ErrorType = ErrorType.OTHER
    line_number: int = 0
    error_message: str = ""


def classify_selector(selector: str) -> SelectorType:
    """Determine the type of a Playwright selector string.

    Examples
    --------
    >>> classify_selector("#buy-now")
    SelectorType.CSS
    >>> classify_selector("//div[@class='cart']")
    SelectorType.XPATH
    >>> classify_selector("text=Buy Now")
    SelectorType.TEXT
    """
    s = selector.strip()
    if s.startswith("//") or s.startswith("(//"):
        return SelectorType.XPATH
    if s.startswith("text=") or s.startswith('"') or s.startswith("'"):
        return SelectorType.TEXT
    if s.startswith("role="):
        return SelectorType.ROLE
    if s.startswith("data-testid=") or s.startswith("[data-testid"):
        return SelectorType.TEST_ID
    # Default to CSS for #id, .class, tag, [attr] patterns
    return SelectorType.CSS


def _detect_error_type(text: str) -> ErrorType:
    """Classify the Playwright error type from the error output."""
    if _STRICT_MODE_PATTERN.search(text):
        return ErrorType.STRICT_MODE
    if _TIMEOUT_PATTERN.search(text):
        return ErrorType.TIMEOUT
    if "waiting for" in text.lower() or "not found" in text.lower():
        return ErrorType.NOT_FOUND
    if "navigation" in text.lower():
        return ErrorType.NAVIGATION
    return ErrorType.OTHER


def _extract_selector(text: str) -> tuple[str, SelectorType]:
    """Extract the broken selector and its type from error output.

    Tries multiple patterns in priority order and returns the first match.
    """
    # Try get_by_role first (most semantic)
    m = _GET_BY_ROLE_PATTERN.search(text)
    if m:
        role = m.group(1)
        name = m.group(2) or ""
        selector = f'get_by_role("{role}", name="{name}")' if name else f'get_by_role("{role}")'
        return selector, SelectorType.ROLE

    # get_by_text
    m = _GET_BY_TEXT_PATTERN.search(text)
    if m:
        return f'get_by_text("{m.group(1)}")', SelectorType.TEXT

    # get_by_test_id
    m = _GET_BY_TESTID_PATTERN.search(text)
    if m:
        return f'get_by_test_id("{m.group(1)}")', SelectorType.TEST_ID

    # get_by_label
    m = _GET_BY_LABEL_PATTERN.search(text)
    if m:
        return f'get_by_label("{m.group(1)}")', SelectorType.LABEL

    # get_by_placeholder
    m = _GET_BY_PLACEHOLDER_PATTERN.search(text)
    if m:
        return f'get_by_placeholder("{m.group(1)}")', SelectorType.PLACEHOLDER

    # locator("selector")
    m = _LOCATOR_PATTERN.search(text)
    if m:
        sel = m.group(1)
        return sel, classify_selector(sel)

    # page.click("selector") etc.
    m = _PAGE_ACTION_PATTERN.search(text)
    if m:
        sel = m.group(1)
        return sel, classify_selector(sel)

    return "", SelectorType.UNKNOWN


def _extract_line_number(error_text: str, test_file: Path) -> int:
    """Extract the failing line number from pytest traceback output."""
    filename = test_file.name
    for m in _PYTEST_LOCATION_PATTERN.finditer(error_text):
        if filename in m.group(1):
            return int(m.group(2))

    # Fallback: look for any ":<number>:" pattern near the test filename
    fallback = re.search(
        rf"{re.escape(filename)}:(\d+)",
        error_text,
    )
    if fallback:
        return int(fallback.group(1))

    return 0


def parse_playwright_errors(
    error_output: str,
    test_file: Path,
) -> list[FailureContext]:
    """Parse Playwright/pytest error output into structured FailureContexts.

    Parameters
    ----------
    error_output:
        The combined stdout+stderr from a failed ``pytest`` run.
    test_file:
        Path to the test file that was executed.

    Returns
    -------
    list[FailureContext]
        One context per detected selector failure.  May be empty if no
        Playwright selector errors are found in the output.
    """
    logger.debug("parser.start", test_file=str(test_file), output_len=len(error_output))

    failures: list[FailureContext] = []

    # Split on "FAILED" or "ERROR" markers to handle multiple failures.
    # Playwright test output typically has sections separated by "_ _ _" or "==="
    sections = re.split(r"_{3,}|={3,}", error_output)

    # Also try parsing the whole output as a single failure
    if len(sections) <= 1:
        sections = [error_output]

    seen_selectors: set[str] = set()

    for section in sections:
        selector, sel_type = _extract_selector(section)
        if not selector or selector in seen_selectors:
            continue

        seen_selectors.add(selector)
        error_type = _detect_error_type(section)
        line_number = _extract_line_number(section, test_file)

        # Read surrounding code context if we have a valid line number
        surrounding_code = ""
        if line_number > 0 and test_file.is_file():
            try:
                content = read_file(test_file)
                surrounding_code = extract_surrounding_lines(content, line_number)
            except Exception:
                logger.warning("parser.surrounding_code.failed", line=line_number)

        ctx = FailureContext(
            test_file=test_file,
            line_number=line_number,
            broken_selector=selector,
            selector_type=sel_type,
            error_message=section.strip()[:500],  # Cap at 500 chars
            error_type=error_type,
            surrounding_code=surrounding_code,
        )
        failures.append(ctx)
        logger.info(
            "parser.failure_found",
            selector=selector,
            selector_type=sel_type.value,
            line=line_number,
            error_type=error_type.value,
        )

    logger.debug("parser.done", failures_found=len(failures))
    return failures
