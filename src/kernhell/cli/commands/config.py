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

    table = Table(title="⚙️ KernHell Active Configuration", box=box.ROUNDED)
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


@config_app.command(name="init", help="Interactive setup wizard to initialize .kernhellrc.toml.")
def init_config(
    target_path: Path = typer.Option(Path(".kernhellrc.toml"), "--path", "-p", help="Target config file path."),
) -> None:
    console.print("[bold red]KernHell Engine Configuration Wizard[/bold red]\n")

    provider = typer.prompt("Select LLM Provider (groq, openai, anthropic, ollama)", default="groq")
    model = typer.prompt(
        "Default Model Name",
        default="llama-3.3-70b-versatile" if provider == "groq" else "gpt-4o",
    )
    api_key = typer.prompt("LLM API Key (press Enter to skip for local/env)", default="", hide_input=True)
    confidence = typer.prompt("Confidence Threshold for auto-healing (0.0 to 1.0)", default=0.85, type=float)
    browser = typer.prompt("Playwright Browser (chromium, firefox, webkit)", default="chromium")

    toml_content = f"""# KernHell Configuration File
# Generated via `kernhell config init`

[llm]
provider = "{provider}"
model = "{model}"
{"api_key = \"" + api_key + "\"" if api_key else "# api_key = \"\""}
temperature = 0.1
max_tokens = 2048

[healing]
confidence_threshold = {confidence}
max_heals_per_file = 5
dry_run = false
auto_commit = false

[cache]
enabled = true
similarity_threshold = 0.92
cache_dir = "~/.kernhell/cache"
embedding_model = "all-MiniLM-L6-v2"

[scanner]
timeout_ms = 5000
capture_screenshot = true
browser = "{browser}"
headless = true

[logging]
level = "INFO"
json_output = false
"""

    target_path.write_text(toml_content.strip() + "\n", encoding="utf-8")
    console.print(f"\n[bold green]✔ Configuration successfully written to {target_path.resolve()}[/bold green]")
