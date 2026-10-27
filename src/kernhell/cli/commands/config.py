"""CLI commands for configuration inspection and setup: `kernhell config <subcommand>`."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich import box
from rich.console import Console
from rich.table import Table

from kernhell.core.config import KernHellConfig, load_config
from kernhell.utils.logger import setup_logging

console = Console(stderr=True)

config_app = typer.Typer(
    name="config",
    help="View and configure KernHell engine parameters.",
    no_args_is_help=True,
)


@config_app.command(name="show", help="Display active configuration settings and source paths.")
def show_config(
    config_path: Optional[Path] = typer.Option(None, "--config", "-c"),
) -> None:
    cfg = load_config(config_path)
    setup_logging(level=cfg.logging.level)

    table = Table(title="KernHell Active Configuration", box=box.ROUNDED)
    table.add_column("Section", style="bold cyan")
    table.add_column("Setting", style="yellow")
    table.add_column("Value")

    # LLM
    table.add_row("LLM", "Provider", cfg.llm.provider)
    table.add_row("LLM", "Model", cfg.llm.model)
    table.add_row("LLM", "API Key", "******" if cfg.llm.api_key else "[dim](not set, using local heuristic)[/dim]")
    table.add_row("LLM", "Temperature", str(cfg.llm.temperature))

    # Healing
    table.add_row("Healing", "Confidence Threshold", f"{int(cfg.healing.confidence_threshold * 100)}%")
    table.add_row("Healing", "Max Heals / File", str(cfg.healing.max_heals_per_file))
    table.add_row("Healing", "Dry Run Default", str(cfg.healing.dry_run))

    # Cache
    table.add_row("Cache", "Enabled", str(cfg.cache.enabled))
    table.add_row("Cache", "Similarity Threshold", f"{int(cfg.cache.similarity_threshold * 100)}%")
    table.add_row("Cache", "Cache Directory", cfg.cache.cache_dir)
    table.add_row("Cache", "Embedding Model", cfg.cache.embedding_model)

    # Scanner
    table.add_row("Scanner", "Browser", cfg.scanner.browser)
    table.add_row("Scanner", "Timeout (ms)", str(cfg.scanner.timeout_ms))
    table.add_row("Scanner", "Capture Screenshot", str(cfg.scanner.capture_screenshot))

    console.print(table)


@config_app.command(name="init", help="Interactive setup wizard to initialize LLM provider & API key.")
def init_config() -> None:
    from kernhell.cli.commands.setup import run_setup_wizard
    run_setup_wizard()
