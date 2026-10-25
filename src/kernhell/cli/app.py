"""Main CLI application entrypoint for KernHell."""

import sys

if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import typer
from rich.console import Console

from kernhell import __app_name__, __version__
from kernhell.cli.commands.cache import cache_app
from kernhell.cli.commands.config import config_app
from kernhell.cli.commands.dashboard import dashboard_command
from kernhell.cli.commands.heal import heal_command
from kernhell.cli.commands.llm import llm_app, switch_llm
from kernhell.cli.commands.scan import scan_command
from kernhell.cli.commands.setup import setup_command

console = Console(stderr=True)

app = typer.Typer(
    name=__app_name__,
    help="KernHell — AI-Powered Autonomous Self-Healing Testing Engine.\n\n"
         "'The Heart of Your System Where Innovation Meets Precision'",
    add_completion=False,
    no_args_is_help=False,
)

# Register core commands
app.command(name="setup", help="Interactive setup wizard to configure your AI / LLM provider & API keys.")(setup_command)
app.command(name="init", help="Alias for 'setup' command.")(setup_command)
app.command(name="switch-llm", help="Interactively switch the active AI / LLM provider.")(switch_llm)
app.command(name="scan", help="Scan a test file to detect broken selectors and capture DOM snapshots.")(scan_command)
app.command(name="heal", help="Autonomously heal broken Playwright selectors in a test file.")(heal_command)
app.command(name="dashboard", help="Launch the KernHell Mission Control Dashboard and REST API.")(dashboard_command)
app.command(name="ui", help="Alias for 'dashboard' command.")(dashboard_command)
app.add_typer(llm_app, name="llm")
app.add_typer(cache_app, name="cache")
app.add_typer(config_app, name="config")


def version_callback(value: bool) -> None:
    if value:
        console.print(f"[bold red]KernHell[/bold red] version [cyan]{__version__}[/cyan]")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        help="Show KernHell version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """KernHell CLI entrypoint callback."""
    if ctx.invoked_subcommand is None:
        setup_marker = Path.home() / ".kernhell" / ".setup_done"
        if not setup_marker.exists():
            from kernhell.cli.commands.setup import check_first_run_setup
            from kernhell.core.config import load_config
            check_first_run_setup(console, load_config())
        console.print(ctx.get_help())
        raise typer.Exit()


if __name__ == "__main__":
    app()
