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
from kernhell.cli.commands.heal import heal_command
from kernhell.cli.commands.scan import scan_command

console = Console(stderr=True)

app = typer.Typer(
    name=__app_name__,
    help="KernHell — AI-Powered Autonomous Self-Healing Testing Engine.\n\n"
         "'The Heart of Your System Where Innovation Meets Precision'",
    add_completion=False,
    no_args_is_help=True,
)

# Register core commands
app.command(name="scan", help="Scan a test file to detect broken selectors and capture DOM snapshots.")(scan_command)
app.command(name="heal", help="Autonomously heal broken Playwright selectors in a test file.")(heal_command)


def version_callback(value: bool) -> None:
    if value:
        console.print(f"[bold red]KernHell[/bold red] version [cyan]{__version__}[/cyan]")
        raise typer.Exit()


@app.callback()
def main(
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
    pass


if __name__ == "__main__":
    app()
