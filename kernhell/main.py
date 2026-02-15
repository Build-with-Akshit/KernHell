import typer
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import sys

from kernhell.utils import print_banner, log_info, log_success, log_error, log_warning, log_step
from kernhell.config import config, SUPPORTED_PROVIDERS
from kernhell.scanner import run_test, capture_failure_screenshot
from kernhell.healer import get_ai_fix, get_active_model_name
from kernhell.patcher import apply_fix
from kernhell.database import db

# Windows Unicode Fix
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

app = typer.Typer(no_args_is_help=True)
console = Console()

# =============================================
# CONFIG MANAGEMENT
# =============================================
config_app = typer.Typer(help="Manage API Keys & Providers")
app.add_typer(config_app, name="config")

@config_app.command("add-key")
def add_key(
    key: str,
    provider: str = typer.Option("google", help=f"Provider: {', '.join(SUPPORTED_PROVIDERS)}")
):
    """Adds an API Key to a provider's rotation pool."""
    success, msg = config.add_key(key, provider)
    if success:
        log_success(msg)
    else:
        log_warning(msg)

@config_app.command("list-keys")
def list_keys():
    """Lists all API keys grouped by provider."""
    config.provider_keys = config._load_keys()
    providers_with_keys = config.get_all_providers_with_keys()

    if not providers_with_keys:
        log_warning("No API Keys found.")
        console.print("[dim]Add keys: kernhell config add-key <KEY> --provider google[/dim]")
        return

    table = Table(title="API Key Pool", show_header=True, header_style="bold cyan")
    table.add_column("Provider", style="bold")
    table.add_column("#", justify="center")
    table.add_column("Key (Masked)", style="dim")
    table.add_column("Status", justify="center")

    for provider, keys in providers_with_keys.items():
        for i, k in enumerate(keys):
            masked = k[:4] + "*" * 8 + k[-4:] if len(k) > 8 else "****"
            is_active = (provider == config.current_provider and i == config.current_key_index)
            status = "[bold green]Active[/bold green]" if is_active else "[dim]Ready[/dim]"
            table.add_row(provider.upper(), str(i + 1), masked, status)

    console.print(table)
    console.print(f"\n[dim]Total: {config.get_key_count()} keys across {len(providers_with_keys)} providers[/dim]")

@config_app.command("remove-key")
def remove_key(
    key: str,
    provider: str = typer.Option(None, help="Provider to remove from. Searches all if not specified.")
):
    """Removes an API Key from the pool."""
    success, msg = config.remove_key(key, provider)
    if success:
        log_success(msg)
    else:
        log_warning(msg)

@config_app.command("prune")
def prune_keys():
    """Tests all keys and removes invalid ones."""
    config.provider_keys = config._load_keys()
    providers_with_keys = config.get_all_providers_with_keys()

    if not providers_with_keys:
        log_warning("No keys to prune.")
        return

    dead_keys = []
    total = 0

    for provider, keys in providers_with_keys.items():
        for key in keys:
            total += 1
            is_valid = _test_key(provider, key)
            if not is_valid:
                dead_keys.append((provider, key))
                masked = key[:4] + "****" + key[-4:]
                log_warning(f"Dead key found: [{provider}] {masked}")

    if dead_keys:
        for provider, key in dead_keys:
            config.remove_key(key, provider)
        log_success(f"Pruned {len(dead_keys)} dead keys out of {total}.")
    else:
        log_success(f"All {total} keys are healthy!")

def _test_key(provider: str, key: str) -> bool:
    """Quick validation test for a key."""
    try:
        if provider == "google":
            import google.generativeai as genai
            genai.configure(api_key=key)
            model = genai.GenerativeModel("gemini-2.0-flash")
            model.generate_content("Say OK")
            return True
        elif provider == "groq":
            from groq import Groq
            client = Groq(api_key=key)
            client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": "Say OK"}],
                max_tokens=5
            )
            return True
        elif provider == "openrouter":
            from openai import OpenAI
            client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=key)
            client.chat.completions.create(
                model="meta-llama/llama-3.3-70b-instruct:free",
                messages=[{"role": "user", "content": "Say OK"}],
                max_tokens=5
            )
            return True
        elif provider == "cloudflare":
            import requests
            parts = key.split(":", 1)
            if len(parts) != 2:
                return False
            account_id, api_token = parts
            url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/@cf/meta/llama-3.1-8b-instruct"
            resp = requests.post(
                url,
                headers={"Authorization": f"Bearer {api_token}"},
                json={"messages": [{"role": "user", "content": "Say OK"}], "max_tokens": 5},
                timeout=15
            )
            return resp.status_code == 200
        elif provider == "nvidia":
            from openai import OpenAI
            client = OpenAI(
                base_url="https://integrate.api.nvidia.com/v1",
                api_key=key
            )
            client.chat.completions.create(
                model="meta/llama-3.1-8b-instruct",
                messages=[{"role": "user", "content": "Say OK"}],
                max_tokens=5
            )
            return True
    except Exception:
        return False

# =============================================
# CORE COMMANDS
# =============================================

@app.command()
def version():
    """Show KernHell version."""
    print_banner()

@app.command()
def doctor():
    """Checks system health, providers, and API connectivity."""
    print_banner()
    log_info("Running System Doctor...")

    import sys as _sys
    console.print(f"Python: {_sys.version.split()[0]}")

    config.provider_keys = config._load_keys()
    total = config.get_key_count()

    if total == 0:
        log_error("No API Keys configured!")
        console.print("[dim]Run: kernhell config add-key <KEY> --provider google[/dim]")
    else:
        log_success(f"Total Keys: {total}")
        for p, keys in config.get_all_providers_with_keys().items():
            console.print(f"  [{p.upper()}]: {len(keys)} keys")

    stats = db.get_stats()
    console.print(f"Runs Logged: {stats.get('total_runs', 0)}")
    console.print(f"Tests Healed: {stats.get('total_healed', 0)}")
    log_success("System Ready.")

@app.command()
def heal(target_path: str = typer.Argument(..., help="File or Directory to heal")):
    """
    AUTO-HEAL: Recursively fixes files or directories.
    Supports 'Smart Retry' loop for 100% fix rate.
    """
    print_banner()
    target_path = Path(target_path).resolve()

    if not target_path.exists():
        log_error(f"Path not found: {target_path}")
        raise typer.Exit(code=1)

    files_to_heal = []
    if target_path.is_dir():
        log_info(f"Scanning directory: {target_path}")
        # Find test files recursively
        files_to_heal.extend(target_path.rglob("test_*.py"))
        files_to_heal.extend(target_path.rglob("*_test.py"))
        files_to_heal = sorted(list(set(files_to_heal))) # Unique & Sorted
        if not files_to_heal:
            log_warning("No test files found in directory.")
            return
    else:
        files_to_heal = [target_path]

    console.print(f"[bold cyan]Found {len(files_to_heal)} targets for healing.[/bold cyan]\n")

    failure_count = 0
    for file_path in files_to_heal:
        if not _heal_single_file(file_path):
            failure_count += 1
    
    if failure_count > 0:
        log_warning(f"Healing completed with {failure_count} failures.")
        raise typer.Exit(code=1)
    else:
        log_success("All files processed successfully!")


def _heal_single_file(file_path: Path) -> bool:
    """
    Heals a single file with Smart Retry Loop.
    Returns True if passed (or healthy), False if failed after retries.
    """
    str_path = str(file_path)
    console.print(Panel(f"Target: [bold cyan]{str_path}[/bold cyan]", border_style="green"))

    MAX_RETRIES = 3
    feedback_context = ""
    last_stderr = ""

    for attempt in range(MAX_RETRIES + 1):
        # 1. Run Test
        with console.status(f"[bold yellow]Running Checkup (Attempt {attempt+1}/{MAX_RETRIES+1})...[/bold yellow]", spinner="dots"):
            passed, stdout, stderr = run_test(str_path)

        if passed:
            log_success(f"Code is healthy! ({file_path.name})")
            db.log_run(str_path, None, True, get_active_model_name())
            return True

        last_stderr = stderr
        log_error(f"Test Failed! (Attempt {attempt+1})")
        
        if attempt == MAX_RETRIES:
            log_error("Max retries reached. Moving to next file.")
            break

        # 2. Capture Screenshot (Only on first failure or if relevant)
        screenshot_b64 = None
        if attempt == 0 or "Timeout" in stderr or "Element" in stderr:
             with console.status("[bold blue]Capturing Context (Screenshot)...[/bold blue]", spinner="dots"):
                screenshot_b64 = capture_failure_screenshot(str_path)

        # 3. Consult AI with Feedback Loop
        try:
            with console.status(f"[bold magenta]Consulting AI ({config.current_provider})...[/bold magenta]", spinner="earth"):
                with open(file_path, "r", encoding="utf-8") as f:
                    original_code = f.read()
                
                # Feedback logic: verification failure from previous run
                current_feedback = ""
                if attempt > 0:
                    current_feedback = f"Previous fix failed validation.\nError detected:\n{stderr}\n\nFix this error specifically."
                    # If stuck, switch provider for a second opinion
                    if attempt == 2:
                        log_warning("AI stuck. Switching provider for second opinion...")
                        config.switch_provider()

                fixed_code = get_ai_fix(
                    original_code, 
                    stderr, 
                    screenshot_b64=screenshot_b64,
                    feedback_context=current_feedback
                )

                if not fixed_code:
                     log_error("AI could not generate a fix.")
                     return False

            # 4. Patch
            log_step("Applying Surgical Fix...")
            if not apply_fix(str_path, fixed_code, stderr):
                log_error("Patching failed.")
                return False

        except Exception as e:
            log_error(f"Healing process crashed: {e}")
            return False
            
    # Final log if we exit loop without success
    db.log_run(str_path, last_stderr, False, get_active_model_name())
    return False


@app.command()
def report():
    """Generates a HTML Dashboard of your savings."""
    stats = db.get_stats()
    runs = db.get_recent_runs()

    html = f"""
    <html>
    <head><title>KernHell Mission Control</title>
    <style>
        body {{ font-family: sans-serif; background: #111; color: #fff; padding: 20px; }}
        .card {{ background: #222; padding: 20px; margin: 10px; border-radius: 8px; }}
        h1 {{ color: #0f0; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 10px; border-bottom: 1px solid #333; text-align: left; }}
        th {{ color: #888; }}
        .success {{ color: #0f0; }}
        .fail {{ color: #f00; }}
    </style>
    </head>
    <body>
        <h1>KernHell Mission Control</h1>
        <div class="card">
            <h2>Stats</h2>
            <p>Total Runs: {stats['total_runs']}</p>
            <p>Fractures Healed: <span class="success">{stats['total_healed']}</span></p>
            <p>Time Saved: <span class="success">{stats['saved_hours']} Hours</span></p>
        </div>
        <div class="card">
            <h2>Recent Runs</h2>
            <table>
                <tr><th>Time</th><th>File</th><th>Status</th></tr>
                {''.join([f"<tr><td>{r['timestamp']}</td><td>{r['file']}</td><td class='{'success' if r['healed'] else 'fail'}'>{'Healed' if r['healed'] else 'Failed'}</td></tr>" for r in runs])}
            </table>
        </div>
    </body>
    </html>
    """

    report_path = Path("kernhell_report.html")
    with open(report_path, "w") as f:
        f.write(html)

    log_success(f"Report generated: [link=file:///{report_path.absolute()}]{report_path.absolute()}[/link]")
    import webbrowser
    webbrowser.open(report_path.absolute().as_uri())

if __name__ == "__main__":
    app()