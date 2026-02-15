"""
The QA Architect's Hands - AI-Powered Test Writer.
Reads the app map and generates Playwright test scripts.
"""
import json
from pathlib import Path
from typing import List, Optional
from kernhell.utils import log_info, log_success, log_warning, log_error
from kernhell.core.config import ConfigManager
from kernhell.providers import generic_call

GENERATE_PROMPT = """You are a senior QA automation engineer specializing in Playwright.
Write a complete, runnable Python test script using `playwright.sync_api`.

RULES:
1. Use `from playwright.sync_api import sync_playwright`.
2. Use robust selectors: text=, [data-testid=], [aria-label=], css=.
3. Test the HAPPY PATH (load page, interact, verify).
4. Include `page.wait_for_load_state("networkidle")` after navigation.
5. Use `headless=False` for visual verification.
6. Output ONLY raw Python code. No markdown, no explanations.
7. Wrap logic in a `def run():` function with `if __name__ == "__main__": run()`.
8. Close browser at the end."""


class TestGenerator:
    """Generates Playwright tests from an analyzed app map."""

    def __init__(self, map_data: dict, config: ConfigManager):
        self.map_data = map_data
        self.config = config

    @classmethod
    def from_map_file(cls, map_path: Path, config: ConfigManager):
        with open(map_path, "r", encoding="utf-8") as f:
            return cls(json.load(f), config)

    def generate_all(self, output_dir: Path, base_url: str = "http://localhost:3000") -> List[Path]:
        """Generate tests for all pages found in the map."""
        output_dir.mkdir(parents=True, exist_ok=True)
        generated = []

        # Priority: explicit 'pages' > detected 'routes'
        targets = self.map_data.get("pages", [])
        using_routes = False

        if not targets:
            log_info("No explicit pages found. Falling back to detected routes.")
            targets = self.map_data.get("routes", [])
            using_routes = True

        if not targets:
            log_warning("No pages or routes found in map. Nothing to generate.")
            return generated

        # Group elements by file
        elements_by_file = {}
        for el in self.map_data.get("elements", []):
            elements_by_file.setdefault(el.get("file", ""), []).append(el)

        for item in targets:
            if using_routes:
                # Item is a route dict: {path, file}
                route = item["path"]
                file = item["file"]
                # Create a readable name from route or filename
                if route == "/":
                    name = "Home"
                else:
                    name = route.strip("/").replace("/", "_").title()
            else:
                # Item is a page dict: {name, file}
                name = item["name"]
                file = item["file"]
                
                # Find matching route if available
                route = "/"
                for r in self.map_data.get("routes", []):
                    if r.get("file") == file or r.get("page") == name:
                        route = r["path"]
                        break

            # Read source code (truncated)
            source = ""
            src_path = Path(self.map_data["source_root"]) / file
            if src_path.exists():
                try:
                    source = src_path.read_text(encoding="utf-8", errors="ignore")[:3000]
                except Exception:
                    pass

            page_elements = elements_by_file.get(file, [])
            context = self._build_context(name, route, page_elements, source, base_url)

            log_info(f"Generating test for: {name} ({route})")
            code = self._call_ai(context)

            if code:
                out_file = output_dir / f"test_{name.lower()}.py"
                out_file.write_text(code, encoding="utf-8")
                generated.append(out_file)
                log_success(f"Created: {out_file.name}")
            else:
                log_warning(f"AI failed to generate test for: {name}")

        return generated

    def _build_context(self, name: str, route: str, elements: list, source: str, base_url: str) -> str:
        el_lines = ""
        for e in elements[:15]:
            parts = [f"type={e['type']}"]
            for key in ["text", "id", "name", "placeholder", "aria_label", "data_testid"]:
                if e.get(key):
                    parts.append(f"{key}='{e[key]}'")
            el_lines += f"  - {', '.join(parts)}\n"

        return f"""PAGE: {name}
URL: {base_url}{route}
FRAMEWORK: {self.map_data['stack'].get('framework', 'unknown')}

INTERACTIVE ELEMENTS:
{el_lines if el_lines else '  (Infer from source code below)'}

SOURCE CODE:
```
{source if source else '(Not available)'}
```

Write a Playwright test that opens {base_url}{route}, verifies it loads, and interacts with the elements."""

    def _call_ai(self, user_prompt: str) -> Optional[str]:
        """Call AI to generate test code."""
        providers = self.config.get_all_providers_with_keys()
        for provider, keys in providers.items():
            if keys:
                result = generic_call(provider, keys[0], GENERATE_PROMPT, user_prompt)
                if result:
                    return result
        log_error("No AI provider could generate the test.")
        return None
