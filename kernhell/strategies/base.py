
import json
from abc import ABC, abstractmethod
from typing import Dict, Any
from pathlib import Path
from kernhell.utils import log_success

class BaseAnalyzer(ABC):
    def __init__(self, source_dir: Path):
        self.source_dir = source_dir
        self.map_data: Dict = {}

    @abstractmethod
    def analyze(self) -> Dict[str, Any]:
        """Analyze the project and return a structural map."""
        pass

    def save_map(self, path: Path):
        """Save map as JSON."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.map_data, indent=2, ensure_ascii=False), encoding="utf-8")
        log_success(f"Map saved: {path}")
