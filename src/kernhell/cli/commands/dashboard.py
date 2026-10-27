"""CLI command: `kernhell dashboard` (or `kernhell ui`).

Launches the local KernHell Mission Control Dashboard and API service.
"""

from __future__ import annotations

import webbrowser
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from kernhell.cli.ui import print_banner
from kernhell.core.config import load_config
from kernhell.utils.logger import setup_logging

console = Console(stderr=True)


def dashboard_command(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Bind host address."),
    port: int = typer.Option(8000, "--port", "-p", help="Bind port number."),
    no_open: bool = typer.Option(False, "--no-open", help="Do not automatically open browser."),
    config_path: Optional[Path] = typer.Option(None, "--config", "-c"),
) -> None:
    """Launch the KernHell Mission Control Dashboard and REST API service."""
    cfg = load_config(config_path)
    setup_logging(level=cfg.logging.level)

    print_banner()

    url = f"http://{host}:{port}"
    web_url = "http://localhost:3000"

    panel_content = (
        f"[bold cyan]Mission Control API:[/bold cyan] [underline]{url}[/underline]\n"
        f"[bold cyan]Swagger API Docs:[/bold cyan]    [underline]{url}/docs[/underline]\n"
        f"[bold cyan]Web Dashboard UI:[/bold cyan]    [underline]{web_url}[/underline]\n\n"
        f"[dim]Press Ctrl+C to terminate the dashboard server.[/dim]"
    )
    console.print(Panel(panel_content, title="Mission Control Active", border_style="cyan"))

    if not no_open:
        try:
            webbrowser.open(f"{url}/docs")
        except Exception:
            pass

    try:
        import uvicorn
        from kernhell.api.server import create_app
    except ImportError:
        console.print(
            "\n[bold red]Error:[/bold red] Mission Control Dashboard requires [bold cyan]fastapi[/bold cyan] and [bold cyan]uvicorn[/bold cyan].\n"
            "Please install them via:\n"
            "  [green]pip install 'kernhell[dashboard]'[/green] or [green]pip install fastapi uvicorn[/green]\n"
        )
        raise typer.Exit(code=1)

    app = create_app(cfg)
    uvicorn.run(app, host=host, port=port, log_level="warning")
