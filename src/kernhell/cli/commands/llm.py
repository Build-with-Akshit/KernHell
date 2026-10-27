"""CLI commands for managing and switching LLM providers: `kernhell llm <subcommand>`."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import typer
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from kernhell.cli.commands.setup import PROVIDER_ALIASES, PROVIDER_DETAILS, run_setup_wizard
from kernhell.core.config import load_config

console = Console(stderr=True)

llm_app = typer.Typer(
    name="llm",
    help="Inspect, set, and switch AI / LLM providers (Gemini, OpenAI, Claude, Groq, Ollama).",
    no_args_is_help=False,
)


@llm_app.callback(invoke_without_command=True)
def llm_main(ctx: typer.Context) -> None:
    """Show current LLM status or switch provider if no subcommand given."""
    if ctx.invoked_subcommand is None:
        show_llm_status()


@llm_app.command(name="show", help="Display currently active LLM provider and model settings.")
def show_llm_status() -> None:
    """Display active LLM configuration in a formatted table."""
    cfg = load_config()
    resolved_key = cfg.llm.get_resolved_api_key()

    table = Table(title="Active AI / LLM Engine", box=box.ROUNDED)
    table.add_column("Property", style="bold cyan", width=18)
    table.add_column("Value", style="white")

    # Map provider to friendly display name
    friendly_name = cfg.llm.provider.title()
    for info in PROVIDER_DETAILS.values():
        if info["provider"] == cfg.llm.provider.lower():
            friendly_name = info["name"]
            break

    table.add_row("Provider", friendly_name)
    table.add_row("Model", cfg.llm.model)
    table.add_row(
        "API Key Status",
        "[bold green]Configured[/bold green]" if resolved_key and cfg.llm.provider != "ollama"
        else "[dim]Not Required (Local Ollama)[/dim]" if cfg.llm.provider == "ollama"
        else "[bold yellow]Missing (Emergency DOM Heuristic active)[/bold yellow]"
    )
    if cfg.llm.api_base:
        table.add_row("API Base URL", cfg.llm.api_base)
    table.add_row("Temperature", str(cfg.llm.temperature))
    table.add_row("Max Tokens", str(cfg.llm.max_tokens))

    console.print()
    console.print(table)
    console.print(
        "[dim]To switch provider interactively, run: [bold cyan]kernhell llm switch[/bold cyan]\n"
        "Or set directly: [bold cyan]kernhell llm set <gemini|openai|claude|groq|ollama>[/bold cyan][/dim]\n"
    )


@llm_app.command(name="switch", help="Interactively switch to a different LLM provider.")
def switch_llm() -> None:
    """Launch the interactive LLM setup wizard."""
    run_setup_wizard()


@llm_app.command(name="set", help="Quickly switch LLM provider from the command line.")
def set_llm(
    provider: str = typer.Argument(
        ...,
        help="Provider name: gemini | openai | anthropic | groq | ollama",
    ),
    model: Optional[str] = typer.Option(
        None,
        "--model",
        "-m",
        help="Optional custom model name.",
    ),
    api_key: Optional[str] = typer.Option(
        None,
        "--key",
        "-k",
        "--api-key",
        help="API key for the selected provider.",
    ),
    api_base: Optional[str] = typer.Option(
        None,
        "--api-base",
        help="Custom API base URL (useful for Ollama or custom proxies).",
    ),
) -> None:
    """Directly configure an LLM provider and save to global settings."""
    prov_key = provider.lower().strip()
    opt_num = PROVIDER_ALIASES.get(prov_key)

    if not opt_num or opt_num not in PROVIDER_DETAILS:
        valid_options = ", ".join(sorted(set(PROVIDER_ALIASES.keys())))
        console.print(f"[bold red]Error:[/bold red] Unknown provider '{provider}'. Valid choices: {valid_options}")
        raise typer.Exit(code=1)

    info = PROVIDER_DETAILS[opt_num]
    final_provider = info["provider"]
    final_model = model or info["default_model"]
    env_var = info["env_var"]
    final_api_base = api_base or ("http://localhost:11434" if final_provider == "ollama" else None)

    # Resolve API Key
    final_key = api_key
    if not final_key and env_var:
        existing = os.environ.get(env_var, "")
        if existing:
            final_key = existing
        elif final_provider != "ollama":
            final_key = typer.prompt(f"Enter your {env_var} (Press Enter to skip)", hide_input=True, default="").strip()

    # Save to ~/.kernhell/.env
    global_dir = Path.home() / ".kernhell"
    global_dir.mkdir(parents=True, exist_ok=True)
    global_env_file = global_dir / ".env"
    global_config_file = global_dir / ".kernhellrc.toml"

    if final_key and env_var:
        lines: list[str] = []
        if global_env_file.is_file():
            for l in global_env_file.read_text(encoding="utf-8").splitlines():
                if l.strip() and not l.strip().startswith(f"{env_var}="):
                    lines.append(l)
        lines.append(f"{env_var}={final_key}")
        global_env_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        os.environ[env_var] = final_key

    # Save to ~/.kernhell/.kernhellrc.toml
    toml_lines = [
        "# KernHell Engine Configuration",
        f"# Updated via `kernhell llm set {provider}`",
        "",
        "[llm]",
        f'provider = "{final_provider}"',
        f'model = "{final_model}"',
    ]
    if final_api_base:
        toml_lines.append(f'api_base = "{final_api_base}"')
    toml_lines.extend([
        "temperature = 0.1",
        "max_tokens = 2048",
        "",
        "[healing]",
        "confidence_threshold = 0.85",
        "max_heals_per_file = 5",
        "dry_run = false",
        "auto_commit = false",
        "",
        "[cache]",
        "enabled = true",
        "similarity_threshold = 0.92",
        'cache_dir = "~/.kernhell/cache"',
        'embedding_model = "all-MiniLM-L6-v2"',
        "",
        "[scanner]",
        "timeout_ms = 30000",
        "capture_screenshot = true",
        'browser = "chromium"',
        "headless = true",
        "",
        "[logging]",
        'level = "INFO"',
        "json_output = false",
        "",
    ])
    global_config_file.write_text("\n".join(toml_lines), encoding="utf-8")

    # Touch setup marker
    (global_dir / ".setup_done").write_text(f"{final_provider}:{final_model}\n", encoding="utf-8")

    console.print(
        Panel(
            f"[bold green]Successfully switched LLM to {info['name']}![/bold green]\n"
            f"Model: [cyan]{final_model}[/cyan]\n"
            f"Config saved to: [dim]{global_config_file}[/dim]",
            box=box.ROUNDED,
        )
    )
