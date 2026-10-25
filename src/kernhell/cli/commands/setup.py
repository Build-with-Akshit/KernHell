"""Interactive setup wizard for KernHell LLM & engine configuration."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional

import typer
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from kernhell.core.config import KernHellConfig, load_config

console = Console(stderr=True)

PROVIDER_DETAILS = {
    "1": {
        "name": "Google Gemini",
        "provider": "gemini",
        "default_model": "gemini-2.5-flash",
        "env_var": "GEMINI_API_KEY",
        "key_hint": "Free key available at: https://aistudio.google.com/app/apikey",
        "badge": "[bold green]Recommended • Free tier • Fast[/bold green]",
    },
    "2": {
        "name": "OpenAI",
        "provider": "openai",
        "default_model": "gpt-4o-mini",
        "env_var": "OPENAI_API_KEY",
        "key_hint": "Get key at: https://platform.openai.com/api-keys",
        "badge": "[bold cyan]Industry Standard • High Accuracy[/bold cyan]",
    },
    "3": {
        "name": "Anthropic Claude",
        "provider": "anthropic",
        "default_model": "claude-3-5-sonnet-20241022",
        "env_var": "ANTHROPIC_API_KEY",
        "key_hint": "Get key at: https://console.anthropic.com/",
        "badge": "[bold magenta]Advanced Reasoning • High Precision[/bold magenta]",
    },
    "4": {
        "name": "Groq Cloud",
        "provider": "groq",
        "default_model": "llama-3.3-70b-versatile",
        "env_var": "GROQ_API_KEY",
        "key_hint": "Free key available at: https://console.groq.com/keys",
        "badge": "[bold yellow]Ultra Fast (~500 T/s) • Free Tier[/bold yellow]",
    },
    "5": {
        "name": "Ollama (Local Offline)",
        "provider": "ollama",
        "default_model": "ollama/llama3.2",
        "env_var": "",
        "key_hint": "Runs 100% locally on your machine via Ollama daemon",
        "badge": "[bold blue]100% Local & Private • Zero Cost[/bold blue]",
    },
    "6": {
        "name": "Free Offline Heuristic Mode",
        "provider": "local",
        "default_model": "none",
        "env_var": "",
        "key_hint": "Zero API keys needed! Uses Semantic Vector Cache + DOM Parser",
        "badge": "[bold white]Built-in • No API Key Needed • Fast[/bold white]",
    },
}


def run_setup_wizard() -> KernHellConfig:
    """Run the interactive LLM configuration wizard and save preferences."""
    console.print()
    banner = Panel(
        "[bold red]KernHell AI Engine Setup[/bold red]\n"
        "[dim]Choose your preferred LLM provider for autonomous selector healing[/dim]",
        box=box.DOUBLE,
        expand=False,
    )
    console.print(banner)

    table = Table(box=box.ROUNDED, show_header=True)
    table.add_column("Option", style="bold cyan", width=8)
    table.add_column("Provider", style="bold white", width=22)
    table.add_column("Features", style="dim")

    for opt, info in PROVIDER_DETAILS.items():
        table.add_row(f"[{opt}]", info["name"], f"{info['badge']}\n[dim italic]{info['key_hint']}[/dim italic]")

    console.print(table)
    choice = typer.prompt(
        "Select your AI / LLM provider [1-6]",
        default="1",
        show_default=True,
    ).strip()

    if choice not in PROVIDER_DETAILS:
        choice = "1"

    selected = PROVIDER_DETAILS[choice]
    provider = selected["provider"]
    model = selected["default_model"]
    env_var = selected["env_var"]
    api_key = ""
    api_base = None

    if provider == "local":
        console.print(
            "\n[bold green]✔ Offline Heuristic Mode Selected.[/bold green] "
            "KernHell will operate with zero external API calls using Local Vector Cache & DOM Parser."
        )
    elif provider == "ollama":
        console.print(f"\n[cyan]Configuring {selected['name']}...[/cyan]")
        custom_model = typer.prompt("Ollama model name", default="llama3.2")
        model = f"ollama/{custom_model}" if not custom_model.startswith("ollama/") else custom_model
        api_base = typer.prompt("Ollama API Base URL", default="http://localhost:11434")
    else:
        console.print(f"\n[cyan]Configuring {selected['name']}...[/cyan]")
        console.print(f"[dim]{selected['key_hint']}[/dim]")

        # Check if already present in environment
        existing_key = os.environ.get(env_var, "") if env_var else ""
        if existing_key:
            console.print(f"[dim]Existing {env_var} detected ({existing_key[:4]}...{existing_key[-4:]})[/dim]")
            use_existing = typer.confirm("Use existing key?", default=True)
            if use_existing:
                api_key = existing_key

        if not api_key:
            api_key = typer.prompt(
                f"Enter your {env_var} (hidden)",
                hide_input=True,
                default="",
            ).strip()

        change_model = typer.confirm(f"Use default model '{model}'?", default=True)
        if not change_model:
            model = typer.prompt("Enter custom model identifier", default=model).strip()

    # Determine save locations
    global_dir = Path.home() / ".kernhell"
    global_dir.mkdir(parents=True, exist_ok=True)
    global_env_file = global_dir / ".env"
    global_config_file = global_dir / ".kernhellrc.toml"

    # Save API key to ~/.kernhell/.env
    if api_key and env_var:
        env_lines: list[str] = []
        if global_env_file.is_file():
            for line in global_env_file.read_text(encoding="utf-8").splitlines():
                if line.strip() and not line.strip().startswith(f"{env_var}="):
                    env_lines.append(line)
        env_lines.append(f"{env_var}={api_key}")
        global_env_file.write_text("\n".join(env_lines) + "\n", encoding="utf-8")
        os.environ[env_var] = api_key
        console.print(f"[green]✔ Key saved securely to {global_env_file}[/green]")

    # Build TOML configuration
    toml_lines = [
        "# KernHell Engine Configuration",
        "# Generated via `kernhell setup`",
        "",
        "[llm]",
        f'provider = "{provider}"',
        f'model = "{model}"',
    ]
    if api_base:
        toml_lines.append(f'api_base = "{api_base}"')
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
    toml_content = "\n".join(toml_lines)

    global_config_file.write_text(toml_content, encoding="utf-8")

    # Write marker that setup has been completed
    setup_marker = global_dir / ".setup_done"
    setup_marker.write_text(f"{provider}:{model}\n", encoding="utf-8")

    # Confirmation Panel
    summary_table = Table(box=box.SIMPLE)
    summary_table.add_column("Setting", style="bold cyan")
    summary_table.add_column("Configured Value", style="white")
    summary_table.add_row("Provider", selected["name"])
    summary_table.add_row("Model", model)
    summary_table.add_row("API Key", "Set (Masked)" if api_key else "None (Offline / Local)")
    summary_table.add_row("Global Config", str(global_config_file))

    console.print(
        Panel(
            summary_table,
            title="[bold green]✔ KernHell Configured Successfully[/bold green]",
            box=box.ROUNDED,
        )
    )
    console.print("[dim]You can re-run this setup wizard anytime with [bold cyan]kernhell setup[/bold cyan][/dim]\n")

    return load_config(global_config_file)


def check_first_run_setup(console: Console, cfg: KernHellConfig) -> KernHellConfig:
    """Prompt user on first interactive run if no LLM provider or API key is found."""
    setup_marker = Path.home() / ".kernhell" / ".setup_done"
    if setup_marker.exists():
        return cfg

    # Check if an API key is already available from env or explicit config
    if cfg.llm.get_resolved_api_key() or cfg.llm.provider in ("ollama", "local"):
        setup_marker.parent.mkdir(parents=True, exist_ok=True)
        setup_marker.write_text("existing_key\n", encoding="utf-8")
        return cfg

    # Only prompt if running interactively in terminal (do not block CI or automated scripts)
    if not sys.stdin.isatty():
        return cfg

    console.print(
        "\n[bold yellow]⚡ Welcome to KernHell![/bold yellow] "
        "No AI / LLM provider has been configured yet."
    )
    configure_now = typer.confirm(
        "Would you like to select an LLM provider now (Gemini / OpenAI / Claude / Groq / Ollama / Free Offline)?",
        default=True,
    )
    if configure_now:
        return run_setup_wizard()
    else:
        setup_marker.parent.mkdir(parents=True, exist_ok=True)
        setup_marker.write_text("offline_skip\n", encoding="utf-8")
        console.print("[dim]Using 100% free offline heuristic mode. Run 'kernhell setup' anytime to configure.[/dim]\n")
        return cfg


def setup_command() -> None:
    """Launch interactive KernHell setup wizard."""
    run_setup_wizard()
