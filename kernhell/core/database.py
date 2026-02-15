import json
import time
from pathlib import Path
from typing import List, Dict, Any

APP_NAME = "kernhell"
CONFIG_DIR = Path.home() / f".{APP_NAME}"
DB_FILE = CONFIG_DIR / "db.json"

class DatabaseManager:
    """
    Local JSON Database.
    Stores 'SaaS' metrics: specific runs, errors fixed, time saved.
    """
    def __init__(self):
        self._ensure_db()

    def _ensure_db(self):
        if not DB_FILE.exists():
            self._save_db({"runs": [], "stats": {"total_healed": 0, "total_runs": 0, "saved_hours": 0.0}})

    def _load_db(self) -> Dict[str, Any]:
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except:
            return {"runs": [], "stats": {"total_healed": 0, "total_runs": 0, "saved_hours": 0.0}}

    def _save_db(self, data: Dict[str, Any]):
        with open(DB_FILE, "w") as f:
            json.dump(data, f, indent=4)

    def log_run(self, file_path: str, error: str, healed: bool, model_used: str):
        """Logs a test run to the local DB."""
        db = self._load_db()
        
        record = {
            "timestamp": time.time(),
            "file": str(file_path),
            "error": error[:200] if error else None, # Truncate long errors
            "healed": healed,
            "model": model_used
        }
        
        db["runs"].append(record)
        
        # Update Stats
        db["stats"]["total_runs"] += 1
        if healed:
            db["stats"]["total_healed"] += 1
            db["stats"]["saved_hours"] += 0.5  # Assume 30 mins saved per fix
            
        self._save_db(db)

    def get_stats(self):
        db = self._load_db()
        return db.get("stats", {})

    def get_recent_runs(self, limit=10):
        db = self._load_db()
        return db.get("runs", [])[-limit:]

# Global Instance
db = DatabaseManager()
