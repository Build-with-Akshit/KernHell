import re
from kernhell.core.models import SelectorType
from kernhell.scanner.parser import _clean_extracted_selector, classify_selector

_WAITING_FOR_ROLE_PATTERN = re.compile(
    r"""waiting\s+for\s+(?:locator\(\s*)?(?:page\.)?(?:get_by_role|getByRole)\(\s*["'](\w+)["'](?:\s*,\s*(?:\{\s*name:\s*|name\s*=\s*)["']([^"']+)["']\s*\}?)?\s*\)""",
    re.IGNORECASE,
)
_WAITING_FOR_TEXT_PATTERN = re.compile(
    r"""waiting\s+for\s+(?:locator\(\s*)?(?:page\.)?(?:get_by_text|getByText)\(\s*["'](.+?)["']\s*\)""",
    re.IGNORECASE,
)
_WAITING_FOR_TESTID_PATTERN = re.compile(
    r"""waiting\s+for\s+(?:locator\(\s*)?(?:page\.)?(?:get_by_test_id|getByTestId)\(\s*["'](.+?)["']\s*\)""",
    re.IGNORECASE,
)
_WAITING_FOR_LABEL_PATTERN = re.compile(
    r"""waiting\s+for\s+(?:locator\(\s*)?(?:page\.)?(?:get_by_label|getByLabel)\(\s*["'](.+?)["']\s*\)""",
    re.IGNORECASE,
)
_WAITING_FOR_PLACEHOLDER_PATTERN = re.compile(
    r"""waiting\s+for\s+(?:locator\(\s*)?(?:page\.)?(?:get_by_placeholder|getByPlaceholder)\(\s*["'](.+?)["']\s*\)""",
    re.IGNORECASE,
)
_WAITING_FOR_LOCATOR_PATTERN = re.compile(
    r"""waiting\s+for\s+(?:locator\(\s*|selector\s+)?(?:(["'`])(.*?)\1|([^\)\n]+))\s*\)?""",
    re.IGNORECASE,
)
_STRICT_MODE_LOCATOR_PATTERN = re.compile(
    r"""strict\s+mode\s+violation:\s*(?:locator\(\s*|selector\s+)?(?:(["'`])(.*?)\1|([^\)\n]+))\s*\)?""",
    re.IGNORECASE,
)

sample_output = '''
    async def wrap_api_call(...)
        page.locator("canvas").click(button="right")
E           playwright._impl._errors.TimeoutError: Locator.click: Timeout 30000ms exceeded.
E           Call log:
E             - waiting for locator("button.legacy-place-order-cta")
'''

def test_extract(text, is_ts=False):
    # Check waiting for role
    m = _WAITING_FOR_ROLE_PATTERN.search(text)
    if m:
        role = m.group(1)
        name = m.group(2) or ""
        if is_ts:
            return (f'getByRole("{role}", {{ name: "{name}" }})' if name else f'getByRole("{role}")'), SelectorType.ROLE
        else:
            return (f'get_by_role("{role}", name="{name}")' if name else f'get_by_role("{role}")'), SelectorType.ROLE

    # Check waiting for text
    m = _WAITING_FOR_TEXT_PATTERN.search(text)
    if m:
        pfx = "getByText" if is_ts else "get_by_text"
        return f'{pfx}("{m.group(1)}")', SelectorType.TEXT

    # Check waiting for testid
    m = _WAITING_FOR_TESTID_PATTERN.search(text)
    if m:
        pfx = "getByTestId" if is_ts else "get_by_test_id"
        return f'{pfx}("{m.group(1)}")', SelectorType.TEST_ID

    # Check waiting for label
    m = _WAITING_FOR_LABEL_PATTERN.search(text)
    if m:
        pfx = "getByLabel" if is_ts else "get_by_label"
        return f'{pfx}("{m.group(1)}")', SelectorType.LABEL

    # Check waiting for placeholder
    m = _WAITING_FOR_PLACEHOLDER_PATTERN.search(text)
    if m:
        pfx = "getByPlaceholder" if is_ts else "get_by_placeholder"
        return f'{pfx}("{m.group(1)}")', SelectorType.PLACEHOLDER

    # Check waiting for locator
    m = _WAITING_FOR_LOCATOR_PATTERN.search(text)
    if m:
        raw = m.group(2) if m.group(2) is not None else m.group(3)
        sel = _clean_extracted_selector(raw or "")
        return sel, classify_selector(sel)

    # Check strict mode locator
    m = _STRICT_MODE_LOCATOR_PATTERN.search(text)
    if m:
        raw = m.group(2) if m.group(2) is not None else m.group(3)
        sel = _clean_extracted_selector(raw or "")
        return sel, classify_selector(sel)

    return "", SelectorType.UNKNOWN

result, sel_type = test_extract(sample_output)
print(f"EXTRACTED: {result!r}, TYPE: {sel_type}")
assert result == "button.legacy-place-order-cta", f"Expected button.legacy-place-order-cta but got {result}"
print("PASSED!")
