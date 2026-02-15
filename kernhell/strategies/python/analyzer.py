
import re
from pathlib import Path
from typing import Dict, List, Set, Any
from kernhell.strategies.base import BaseAnalyzer
from kernhell.utils import log_info

SKIP_DIRS: Set[str] = {
    "__pycache__", "venv", ".venv", ".git", ".idea", ".vscode", "env", ".env", ".kernhell_cache"
}

SOURCE_EXTS: Set[str] = {".py"}

class PythonAnalyzer(BaseAnalyzer):
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
        log_info(f"Using Python Strategy for: {self.source_dir}")
        self._detect_stack()
        self._scan_files()
        self._extract_routes()
        return self.map_data

    def _detect_stack(self):
        stack = {"language": "python", "framework": "unknown"}
        
        if (self.source_dir / "manage.py").exists():
            stack["framework"] = "django"
        elif (self.source_dir / "requirements.txt").exists():
            try:
                reqs = (self.source_dir / "requirements.txt").read_text(encoding="utf-8").lower()
                for key, name in [("flask", "flask"), ("fastapi", "fastapi"), ("django", "django")]:
                    if key in reqs:
                        stack["framework"] = name
                        break
            except Exception:
                pass
        elif (self.source_dir / "pyproject.toml").exists():
             # Basic check, can be improved
            stack["framework"] = "poetry/generic"

        self.map_data["stack"] = stack
        log_info(f"Detected Python Stack: {stack['framework']}")

    def _scan_files(self):
        for fp in self._walk():
            if fp.suffix.lower() in SOURCE_EXTS:
                rel = str(fp.relative_to(self.source_dir)).replace("\\", "/")
                self.map_data["source_files"].append({"path": rel, "ext": fp.suffix.lower(), "name": fp.stem})

                rl = rel.lower()
                if any(d in rl for d in ["views/", "controllers/", "routes/"]):
                    self.map_data["pages"].append({"name": fp.stem, "file": rel})
                elif "models" in rl:
                     self.map_data["components"].append({"name": fp.stem, "file": rel})

    def _extract_routes(self):
        routes = []
        fw = self.map_data["stack"].get("framework", "")

        if fw in ("flask", "fastapi"):
            for fi in self.map_data["source_files"]:
                try:
                    content = (self.source_dir / fi["path"]).read_text(encoding="utf-8", errors="ignore")
                    for m in re.finditer(r'@\w+\.(route|get|post|put|delete)\(["\']([^"\']+)', content):
                        routes.append({"path": m.group(2), "method": m.group(1).upper(), "file": fi["path"]})
                except Exception:
                    pass

        elif fw == "django":
            for fi in self.map_data["source_files"]:
                if fi["name"] != "urls":
                    continue
                try:
                    content = (self.source_dir / fi["path"]).read_text(encoding="utf-8", errors="ignore")
                    for m in re.finditer(r'path\(["\']([^"\']+)', content):
                        routes.append({"path": "/" + m.group(1), "file": fi["path"]})
                except Exception:
                    pass

        self.map_data["routes"] = routes

    def _walk(self):
        for item in sorted(self.source_dir.rglob("*")):
            if item.is_file():
                skip = any(p in SKIP_DIRS for p in item.relative_to(self.source_dir).parts)
                if not skip:
                    yield item
