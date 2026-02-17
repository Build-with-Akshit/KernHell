from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.theme import Theme

# Custom Theme for Hacker-Style UI
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "code": "bold white on black"
})

# Force terminal to basic ASCII if needed, but Rich handles most.
console = Console(theme=custom_theme)

def print_banner():
    """Prints the KernHell ASCII Banner (Safe for Windows)."""
    banner_text = """
    KERNHELL - AUTO QA AGENT
    ========================
    Self-Healing Tests v2.0
    """
    console.print(Panel(Text(banner_text, style="bold green"), title="[bold white]KernHell v2.0 - Zero-Cost Self-Healing Agent[/bold white]", border_style="green"))

def log_info(msg: str):
    console.print(f"[bold blue]INFO:[/bold blue] {msg}")

def log_success(msg: str):
    console.print(f"[bold green]SUCCESS:[/bold green] {msg}")

def log_warning(msg: str):
    console.print(f"[bold yellow]WARNING:[/bold yellow] {msg}")

def log_error(msg: str):
    console.print(f"[bold red]ERROR:[/bold red] {msg}")

def log_step(step: str):
    console.print(f"\n[bold magenta]>> {step}[/bold magenta]")


# ============================================================
# PHASE 13: ISOLATED MEMORY (CacheManager)
# ============================================================
import shutil
from pathlib import Path

CACHE_DIR_NAME = ".kernhell_cache"


class CacheManager:
    """Manages KernHell's isolated workspace directory."""

    def __init__(self, project_root: Path):
        self.project_root = project_root.resolve()
        self.cache_dir = self.project_root / CACHE_DIR_NAME
        self._ensure_dirs()

    def _ensure_dirs(self):
        """Create cache directory structure."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        (self.cache_dir / "maps").mkdir(exist_ok=True)
        (self.cache_dir / "screenshots").mkdir(exist_ok=True)
        (self.cache_dir / "logs").mkdir(exist_ok=True)
        (self.cache_dir / "temp").mkdir(exist_ok=True)

        # Add .gitignore so cache never pollutes version control
        gitignore = self.cache_dir / ".gitignore"
        if not gitignore.exists():
            gitignore.write_text("*\n", encoding="utf-8")

    @property
    def maps_dir(self) -> Path:
        return self.cache_dir / "maps"

    @property
    def screenshots_dir(self) -> Path:
        return self.cache_dir / "screenshots"

    @property
    def logs_dir(self) -> Path:
        return self.cache_dir / "logs"

    @property
    def temp_dir(self) -> Path:
        return self.cache_dir / "temp"

    def get_map_path(self, name: str = "kernhell") -> Path:
        """Returns path for the analysis map JSON."""
        return self.maps_dir / f"{name}.map"

    def get_screenshot_path(self, name: str) -> Path:
        """Returns path for a screenshot file."""
        return self.screenshots_dir / f"{name}.png"

    def save_file(self, subdir: str, filename: str, content: str) -> Path:
        """Save any text file into the cache."""
        target = self.cache_dir / subdir / filename
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return target

    def cleanup(self):
        """Delete the entire cache directory."""
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir, ignore_errors=True)
            log_success(f"Cache cleaned: {self.cache_dir}")

    def get_size_mb(self) -> float:
        """Get total cache size in MB."""
        if not self.cache_dir.exists():
            return 0.0
        total = sum(f.stat().st_size for f in self.cache_dir.rglob("*") if f.is_file())
        return round(total / (1024 * 1024), 2)

    def exists(self) -> bool:
        return self.cache_dir.exists()

