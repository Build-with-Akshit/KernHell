
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Any
from kernhell.strategies.base import BaseAnalyzer
from kernhell.utils import log_info, log_success, log_warning

SKIP_DIRS: Set[str] = {
    "node_modules", ".git", "dist", "build", ".next", ".nuxt", "coverage", ".kernhell_cache",
}

SOURCE_EXTS: Set[str] = {".html", ".htm", ".jsx", ".tsx", ".vue", ".svelte", ".js", ".ts"}

class WebAnalyzer(BaseAnalyzer):
    def __init__(self, source_dir: Path):
        super().__init__(source_dir)
        self.map_data: Dict = {
            "project_name": self.source_dir.name,
            "source_root": str(self.source_dir),
            "stack": {},
            "pages": [],
            "components": [],
            "routes": [],
            "elements": [],
            "source_files": [],
        }

    def analyze(self) -> Dict[str, Any]:
        log_info(f"Using Web Strategy for: {self.source_dir}")
        self._detect_stack()
        self._scan_files()
        self._extract_routes()
        self._extract_elements()
        return self.map_data

    def _detect_stack(self):
        stack = {"language": "unknown", "framework": "unknown"}
        pkg = self.source_dir / "package.json"
        
        if pkg.exists():
            try:
                data = json.loads(pkg.read_text(encoding="utf-8"))
                deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                
                stack["language"] = "typescript" if "typescript" in deps else "javascript"
                
                for key, name in [("next", "nextjs"), ("react", "react"), ("vue", "vue"),
                                  ("svelte", "svelte"), ("express", "express"), ("@angular/core", "angular")]:
                    if key in deps:
                        stack["framework"] = name
                        break
            except Exception:
                pass
        
        self.map_data["stack"] = stack
        log_info(f"Detected Web Stack: {stack['language']} / {stack['framework']}")

    def _scan_files(self):
        for fp in self._walk():
            if fp.suffix.lower() in SOURCE_EXTS:
                rel = str(fp.relative_to(self.source_dir)).replace("\\", "/")
                self.map_data["source_files"].append({"path": rel, "ext": fp.suffix.lower(), "name": fp.stem})

                rl = rel.lower()
                if any(d in rl for d in ["pages/", "views/", "screens/", "app/", "routes/"]):
                    self.map_data["pages"].append({"name": fp.stem, "file": rel})
                elif any(d in rl for d in ["components/", "widgets/", "ui/"]):
                    self.map_data["components"].append({"name": fp.stem, "file": rel})

    def _extract_routes(self):
        routes = []
        fw = self.map_data["stack"].get("framework", "")

        if fw == "nextjs":
            for p in self.map_data["pages"]:
                route = "/" + p["file"]
                for prefix in ["src/app/", "app/", "src/pages/", "pages/"]:
                    if route.startswith("/" + prefix):
                        route = route[len(prefix):]
                        break
                route = "/" + re.sub(r'\.(jsx|tsx|js|ts)$', '', route)
                route = route.replace("/index", "/").replace("//", "/")
                routes.append({"path": route, "page": p["name"], "file": p["file"]})

        elif fw == "react":
            for fi in self.map_data["source_files"]:
                if fi["ext"] not in (".jsx", ".tsx", ".js", ".ts"):
                    continue
                try:
                    content = (self.source_dir / fi["path"]).read_text(encoding="utf-8", errors="ignore")
                    # Updated regex to match React Router Route components
                    # Matches <Route ... path="..." ...>
                    for m in re.finditer(r'<Route\s+[^>]*path=["\']([^"\']+)', content):
                        routes.append({"path": m.group(1), "file": fi["path"]})
                except Exception:
                    pass

        self.map_data["routes"] = routes

    def _extract_elements(self):
        elements = []
        for fi in self.map_data["source_files"]:
            try:
                content = (self.source_dir / fi["path"]).read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            # Buttons
            for m in re.finditer(r'<button[^>]*>(.*?)</button>', content, re.DOTALL | re.IGNORECASE):
                text = re.sub(r'<[^>]+>', '', m.group(1)).strip()[:80]
                el = {"type": "button", "text": text, "file": fi["path"]}
                el.update(self._attrs(m.group(0)))
                elements.append(el)

            # Inputs
            for m in re.finditer(r'<input[^>]*/?>',  content, re.IGNORECASE):
                el = {"type": "input", "file": fi["path"]}
                el.update(self._attrs(m.group(0)))
                elements.append(el)

            # Links
            for m in re.finditer(r'<a\s[^>]*>(.*?)</a>', content, re.DOTALL | re.IGNORECASE):
                text = re.sub(r'<[^>]+>', '', m.group(1)).strip()[:80]
                el = {"type": "link", "text": text, "file": fi["path"]}
                el.update(self._attrs(m.group(0)))
                elements.append(el)

        self.map_data["elements"] = elements

    def _attrs(self, tag: str) -> Dict:
        attrs = {}
        patterns = [
            ("id", r'id=["\']([^"\']+)'),
            ("class", r'class(?:Name)?=["\']([^"\']+)'),
            ("name", r'name=["\']([^"\']+)'),
            ("input_type", r'type=["\']([^"\']+)'),
            ("href", r'href=["\']([^"\']+)'),
            ("placeholder", r'placeholder=["\']([^"\']+)'),
            ("data_testid", r'data-testid=["\']([^"\']+)'),
        ]
        for attr_name, pattern in patterns:
            m = re.search(pattern, tag, re.IGNORECASE)
            if m:
                attrs[attr_name] = m.group(1)
        return attrs

    def _walk(self):
        for item in sorted(self.source_dir.rglob("*")):
            if item.is_file():
                skip = any(p in SKIP_DIRS for p in item.relative_to(self.source_dir).parts)
                if not skip:
                    yield item
