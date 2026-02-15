"""
The QA Architect's Eye - Source Code Analyzer.
Scans application directories, detects tech stack, and builds
a structural map for intelligent test generation and healing.
"""
from pathlib import Path
from typing import Dict
from kernhell.strategies.web.analyzer import WebAnalyzer
from kernhell.strategies.python.analyzer import PythonAnalyzer
from kernhell.utils import log_info, log_error

class AppAnalyzer:
    """Factory wrapper that delegates to the appropriate strategy analyzer."""

    def __init__(self, source_dir: Path):
        self.source_dir = source_dir.resolve()
        self.strategy = self._pick_strategy()

    def _pick_strategy(self):
        # Heuristic to choose strategy
        if (self.source_dir / "package.json").exists():
            log_info("Detected package.json - Using Web Strategy")
            return WebAnalyzer(self.source_dir)
            
        if (self.source_dir / "requirements.txt").exists() or \
           (self.source_dir / "pyproject.toml").exists() or \
           (self.source_dir / "manage.py").exists():
            log_info("Detected Python config - Using Python Strategy")
            return PythonAnalyzer(self.source_dir)

        # Fallback: Check for file extensions
        # If we find .py files, use Python. If .tsx/.jsx, use Web.
        has_py = any(self.source_dir.rglob("*.py"))
        has_js = any(self.source_dir.rglob("*.js")) or any(self.source_dir.rglob("*.tsx"))

        if has_py and not has_js:
            log_info("Detected Python files - Using Python Strategy")
            return PythonAnalyzer(self.source_dir)
        
        log_info("Defaulting to Web Strategy")
        return WebAnalyzer(self.source_dir)

    def analyze(self) -> Dict:
        """Run full analysis pipeline using the selected strategy."""
        return self.strategy.analyze()

    def save_map(self, path: Path):
        """Delegate save_map to strategy."""
        self.strategy.save_map(path)

