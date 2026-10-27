import re

pattern = re.compile(
    r"""waiting\s+for\s+(?:locator\(\s*(?:(["'`])(.*?)\1|([^\)\n]+))\s*\)|selector\s+(["'`])(.*?)\4)""",
    re.IGNORECASE,
)

samples = [
    "Error: Timed out 5000ms waiting for expect(locator).toBeVisible()\nCall log:\n  - waiting for locator('#status')",
    "Locator.click: Timeout 30000ms exceeded.\nCall log:\n  - waiting for locator(\"button.legacy-place-order-cta\")",
    "waiting for selector \"#my-id\"",
    "waiting for locator(submit_btn)"
]

for s in samples:
    m = pattern.search(s)
    if m:
        extracted = m.group(2) or m.group(3) or m.group(5)
        print(f"Matched: {extracted}")
    else:
        print("No match")
