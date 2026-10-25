"""CLI command: `kernhell heal <test_file_or_directory>`.

Executes tests, intercepts selector failures, and runs the self-healing engine.
Supports single-file healing and directory-wide batch healing.
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
)
from kernhell.core.config import load_config
from kernhell.core.exceptions import (
    NoFailuresDetectedError,
    PlaywrightNotInstalledError,
    ScannerError,
    TestFileNotFoundError,
)
from kernhell.core.models import HealingReport
from kernhell.core.orchestrator import HealingOrchestrator
from kernhell.reporter.reporter import HealingReporter
from kernhell.utils.file_utils import read_file
from kernhell.utils.logger import setup_logging

console = Console(stderr=True)


def heal_command(
    target: Path = typer.Argument(
        ...,
        help="Path to a Playwright test file or directory of test files to heal.",
        exists=False,
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Preview healed selectors without mutating test files on disk.",
    ),
    output_format: str = typer.Option(
        "text",
        "--output",
        "-o",
        help="Output format: 'text' (Rich terminal) or 'json' (machine-parseable for CI).",
    ),
    output_file: Optional[Path] = typer.Option(
        None,
        "--output-file",
        help="Optional path to save JSON healing report.",
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

    if output_format != "json":
        print_banner()

    if not target.exists():
        console.print(f"[bold red]Error:[/bold red] Target path not found: {target}")
        raise typer.Exit(code=1)

    # Discover test files (single file vs batch directory mode, Python + TypeScript/JS)
    if target.is_dir():
        candidates = set()
        for p in target.rglob("*"):
            if not p.is_file():
                continue
            name_lower = p.name.lower()
            if (
                (name_lower.startswith("test_") and p.suffix in (".py", ".ts", ".js"))
                or name_lower.endswith("_test.py")
                or name_lower.endswith(".spec.ts")
                or name_lower.endswith(".test.ts")
                or name_lower.endswith(".spec.js")
                or name_lower.endswith(".test.js")
            ):
                candidates.add(p)
        test_files = sorted(candidates)
        if not test_files:
            console.print(f"[yellow]No Playwright test files (.py, .ts, .js) found in {target}[/yellow]")
            raise typer.Exit(code=0)
    else:
        test_files = [target]

    orchestrator = HealingOrchestrator(cfg)
    reports: list[HealingReport] = []

    for test_file in test_files:
        original_code = read_file(test_file) if test_file.is_file() else ""

        with console.status(f"[bold cyan]Scanning & healing [white]{test_file.name}[/white]..."):
            try:
                report = orchestrator.heal(test_file, dry_run=dry_run)
                reports.append(report)
            except NoFailuresDetectedError as exc:
                if output_format != "json":
                    console.print(f"[bold green]✔[/bold green] {test_file.name}: {exc}")
                continue
            except (PlaywrightNotInstalledError, ScannerError, TestFileNotFoundError) as exc:
                console.print(f"[bold red]Failed on {test_file.name}:[/bold red] {exc}")
                continue

        if output_format != "json" and report.results:
            for i, result in enumerate(report.results, start=1):
                print_failure_context(result.failure, index=i)
                if result.pruned_dom:
                    print_pruning_stats(result.pruned_dom)
                console.print()

            # Render surgical AST diff if file was patched
            if not dry_run and original_code and test_file.is_file():
                patched_code = read_file(test_file)
                if patched_code != original_code:
                    HealingReporter.render_diff(
                        old_code=original_code,
                        new_code=patched_code,
                        filename=test_file.name,
                    )

            HealingReporter.print_summary(report)

    # JSON export handling
    if output_format == "json" or output_file is not None:
        combined_json = [json_str for report in reports for json_str in [HealingReporter.export_json(report)]]
        payload = f"[\n{', '.join(combined_json)}\n]"
        if output_file:
            output_file.write_text(payload, encoding="utf-8")
        if output_format == "json":
            typer.echo(payload)
