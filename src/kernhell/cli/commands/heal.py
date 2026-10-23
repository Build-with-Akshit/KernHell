"""CLI command: `kernhell heal <test_file>`.

Executes test, intercepts selector failures, and runs the self-healing engine.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from kernhell.cli.ui import (
    print_banner,
    print_failure_context,
    print_healing_report,
    print_pruning_stats,
)
from kernhell.core.config import load_config
from kernhell.core.exceptions import (
    NoFailuresDetectedError,
    PlaywrightNotInstalledError,
    ScannerError,
    TestFileNotFoundError,
)
from kernhell.core.orchestrator import HealingOrchestrator
from kernhell.utils.logger import setup_logging

console = Console(stderr=True)


def heal_command(
    test_file: Path = typer.Argument(
        ...,
        help="Path to the Playwright test file to heal.",
        exists=False,
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Preview healed selectors without modifying test file.",
    ),
    config_path: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to custom .kernhellrc.toml file.",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable detailed debug logs.",
    ),
    json_log: bool = typer.Option(
        False,
        "--json-log",
        help="Output structured logs in JSON format.",
    ),
) -> None:
    """Autonomously detect and heal broken Playwright selectors."""
    cfg = load_config(config_path)
    log_level = "DEBUG" if verbose else cfg.logging.level
    setup_logging(level=log_level, json_output=json_log or cfg.logging.json_output)

    print_banner()

    if not test_file.exists():
        console.print(f"[bold red]Error:[/bold red] Test file not found: {test_file}")
        raise typer.Exit(code=1)

    orchestrator = HealingOrchestrator(cfg)

    with console.status(f"[bold cyan]Running self-healing engine on [white]{test_file.name}[/white]..."):
        try:
            report = orchestrator.heal(test_file, dry_run=dry_run)
        except NoFailuresDetectedError as exc:
            console.print(f"[bold green]✔[/bold green] {exc}")
            raise typer.Exit(code=0)
        except (PlaywrightNotInstalledError, ScannerError, TestFileNotFoundError) as exc:
            console.print(f"[bold red]Healing Pipeline Failed:[/bold red] {exc}")
            raise typer.Exit(code=1)

    if not report.results:
        console.print("[bold green]✔ All tests in file passed. Zero broken selectors detected.[/bold green]")
        raise typer.Exit(code=0)

    for i, result in enumerate(report.results, start=1):
        print_failure_context(result.failure, index=i)
        if result.pruned_dom:
            print_pruning_stats(result.pruned_dom)
        console.print()

    print_healing_report(report)
