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
    Self-Healing Tests v0.1
    """
    console.print(Panel(Text(banner_text, style="bold green"), title="[bold white]KernHell v0.1 - Zero-Cost Self-Healing Agent[/bold white]", border_style="green"))

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
