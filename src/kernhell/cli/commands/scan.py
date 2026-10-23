"""CLI command: `kernhell scan <test_file>`.

Detects broken selectors and captures DOM snapshots without modifying test files.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from kernhell.cli.ui import (
    print_banner,
    print_failure_context,
    print_pruning_stats,
    print_scan_summary,
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


def scan_command(
    test_file: Path = typer.Argument(
        ...,
        help="Path to the Playwright test file to scan for broken selectors.",
        exists=False,
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
    """Scan a Playwright test file, intercepting selector failures and capturing DOM."""
    cfg = load_config(config_path)
    log_level = "DEBUG" if verbose else cfg.logging.level
    setup_logging(level=log_level, json_output=json_log or cfg.logging.json_output)

    print_banner()

    if not test_file.exists():
        console.print(f"[bold red]Error:[/bold red] Test file not found: {test_file}")
        raise typer.Exit(code=1)

    orchestrator = HealingOrchestrator(cfg)

    with console.status(f"[bold cyan]Scanning [white]{test_file.name}[/white] for selector failures..."):
        try:
            results = orchestrator.scan(test_file)
        except NoFailuresDetectedError as exc:
            console.print(f"[bold green]✔[/bold green] {exc}")
            raise typer.Exit(code=0)
        except (PlaywrightNotInstalledError, ScannerError, TestFileNotFoundError) as exc:
            console.print(f"[bold red]Scan Failed:[/bold red] {exc}")
            raise typer.Exit(code=1)

    failures = [f for f, _ in results]
    print_scan_summary(failures)

    for i, (failure, pruned) in enumerate(results, start=1):
        print_failure_context(failure, index=i)
        if pruned:
            print_pruning_stats(pruned)
        console.print()
