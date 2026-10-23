"""CLI commands for managing the Semantic Vector Cache: `kernhell cache <subcommand>`."""

from __future__ import annotations

from typing import Optional
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table
from rich import box

from kernhell.cache.cache_manager import CacheManager
from kernhell.core.config import load_config
from kernhell.utils.logger import setup_logging

console = Console(stderr=True)

cache_app = typer.Typer(
    name="cache",
    help="Inspect, query, and manage KernHell's Semantic Vector Cache.",
    no_args_is_help=True,
)


@cache_app.command(name="list", help="List all verified healed selector mappings in cache.")
def list_cache(
    config_path: Optional[Path] = typer.Option(None, "--config", "-c"),
) -> None:
    cfg = load_config(config_path)
    setup_logging(level=cfg.logging.level)
    mgr = CacheManager(cfg)

    entries = mgr.list_entries()
    if not entries:
        console.print("[yellow]Semantic Cache is currently empty. Run `kernhell heal` to populate.[/yellow]")
        return

    table = Table(title="🧠 KernHell Semantic Memory Cache", box=box.ROUNDED)
    table.add_column("Original Selector", style="red")
    table.add_column("Healed Selector", style="bold green")
    table.add_column("Strategy", style="cyan")
    table.add_column("Confidence", justify="right")
    table.add_column("Hits", justify="right")

    for e in entries:
        table.add_row(
            e.broken_selector,
            e.new_selector,
            e.strategy.value,
            f"{int(e.confidence * 100)}%",
            str(e.hit_count),
        )

    console.print(table)


@cache_app.command(name="stats", help="Show cache hit/miss metrics and efficiency ratio.")
def stats_cache(
    config_path: Optional[Path] = typer.Option(None, "--config", "-c"),
) -> None:
    cfg = load_config(config_path)
    setup_logging(level=cfg.logging.level)
    mgr = CacheManager(cfg)

    stats = mgr.get_stats()
    table = Table(title="📊 Semantic Memory Metrics", box=box.ROUNDED)
    table.add_column("Metric", style="bold")
    table.add_column("Value", justify="right")

    table.add_row("Total Entries", str(stats.total_entries))
    table.add_row("Cache Hits", f"[bold green]{stats.hits}[/bold green]")
    table.add_row("Cache Misses", str(stats.misses))
    table.add_row("Hit Efficiency", f"[bold cyan]{stats.hit_ratio}%[/bold cyan]")
    table.add_row("Storage Path", str(mgr.storage_dir))

    console.print(table)


@cache_app.command(name="clear", help="Purge all entries from the semantic cache.")
def clear_cache(
    config_path: Optional[Path] = typer.Option(None, "--config", "-c"),
    force: bool = typer.Option(False, "--force", "-f", help="Bypass confirmation prompt."),
) -> None:
    cfg = load_config(config_path)
    setup_logging(level=cfg.logging.level)
    mgr = CacheManager(cfg)

    if not force:
        confirm = typer.confirm("Are you sure you want to purge the semantic vector cache?")
        if not confirm:
            console.print("[dim]Operation cancelled.[/dim]")
            return

    count = mgr.clear()
    console.print(f"[bold green]✔ Successfully cleared {count} entries from semantic cache.[/bold green]")
