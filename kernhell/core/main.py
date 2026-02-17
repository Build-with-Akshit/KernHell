import typer
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import sys

from kernhell.utils import print_banner, log_info, log_success, log_error, log_warning, log_step
from kernhell.core.config import config, SUPPORTED_PROVIDERS
from kernhell.scanner import run_test, capture_failure_screenshot
from kernhell.healer import get_ai_fix, get_active_model_name
from kernhell.patcher import apply_fix
from kernhell.core.database import db

# Windows Unicode Fix
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

app = typer.Typer(no_args_is_help=True)
console = Console()

def _show_onboarding():
    """Displays a helpful setup guide for new users."""
    grid = Table.grid(expand=True)
    grid.add_column(justify="center")
    grid.add_row("[bold yellow]Welcome to KernHell - The AI QA Agent[/bold yellow]")
    grid.add_row("To start healing tests, you need to add at least one AI Provider API Key.")
    
    table = Table(title="Supported AI Providers", border_style="cyan")
    table.add_column("Provider", style="bold green")
    table.add_column("Why Use?", style="magenta")
    table.add_column("Command Template")
    
    table.add_row("google", "Best Vision (Gemini 2.0)", "kernhell config add-key <KEY> --provider google")
    table.add_row("nvidia", "Heavy Artillery (Llama 90B)", "kernhell config add-key <KEY> --provider nvidia")
    table.add_row("groq", "Fastest Text (Llama 70B)", "kernhell config add-key <KEY> --provider groq")
    table.add_row("openrouter", "Access to All Models", "kernhell config add-key <KEY> --provider openrouter")
    
    console.print(Panel(grid, border_style="yellow"))
    console.print(table)
    console.print("\n[dim]Get free keys from: build.nvidia.com, aistudio.google.com, console.groq.com[/dim]\n")


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
        _show_onboarding()
        return
    else:
        log_success(f"Total Keys: {total}")
        for p, keys in config.get_all_providers_with_keys().items():
            console.print(f"  [{p.upper()}]: {len(keys)} keys")

    stats = db.get_stats()
    console.print(f"Runs Logged: {stats.get('total_runs', 0)}")
    console.print(f"Tests Healed: {stats.get('total_healed', 0)}")
    log_success("System Ready.")

@app.command(name="help")
def custom_help():
    """Displays the official Command Reference."""
    print_banner()
    
    grid = Table.grid(expand=True)
    grid.add_column(justify="center")
    grid.add_row("[bold cyan]COMMAND REFERENCE[/bold cyan]")
    
    # Core Table
    core_table = Table(title="Core Actions", border_style="green")
    core_table.add_column("Command", style="bold yellow")
    core_table.add_column("Description", style="white")
    
    core_table.add_row("kernhell heal <target>", "Auto-Fix a file or folder recursively.")
    core_table.add_row("kernhell analyze <dir>", "Scan app source code and build a test map.")
    core_table.add_row("kernhell generate <dir>", "AI-generate Playwright tests from analyzed app.")
    core_table.add_row("kernhell hunt <log_dir>", "Monitor logs and auto-analyze bugs with AI.")
    core_table.add_row("kernhell watch <test_dir>", "Continuously monitor and auto-heal on file changes.")
    core_table.add_row("kernhell report", "Generate HTML Dashboard of saved time.")
    core_table.add_row("kernhell clean <dir>", "Wipe .kernhell_cache to free disk space.")
    core_table.add_row("kernhell doctor", "Run system diagnostics & connectivity check.")
    core_table.add_row("kernhell version", "Show version info.")
    
    # Config Table
    config_table = Table(title="Configuration (API Keys)", border_style="blue")
    config_table.add_column("Command", style="bold magenta")
    config_table.add_column("Description", style="white")
    
    config_table.add_row("kernhell config add-key <key>", "Add API Key (use --provider name).")
    config_table.add_row("kernhell config list-keys", "Show all active keys.")
    config_table.add_row("kernhell config remove-key", "Remove a specific key.")
    config_table.add_row("kernhell config prune", "Auto-remove dead/invalid keys.")
    
    console.print(Panel(grid, border_style="cyan"))
    console.print(core_table)
    console.print(config_table)
    console.print("\n[dim]Run 'kernhell [command] --help' for details.[/dim]\n")


# ============================================================
# PHASE 12: THE QA ARCHITECT
# ============================================================
@app.command()
def analyze(source_dir: str = typer.Argument(..., help="Path to your application source code")):
    """Analyze an app's source code to build an intelligent map."""
    print_banner()
    from kernhell.analyzer import AppAnalyzer
    from kernhell.utils import CacheManager

    source_path = Path(source_dir).resolve()
    if not source_path.exists() or not source_path.is_dir():
        log_error(f"Directory not found: {source_path}")
        raise typer.Exit(code=1)

    cache = CacheManager(source_path)

    with console.status("[bold yellow]Analyzing source code...[/bold yellow]", spinner="dots"):
        analyzer = AppAnalyzer(source_path)
        map_data = analyzer.analyze()
        map_file = cache.get_map_path()
        analyzer.save_map(map_file)

    console.print(f"\n[bold green]Map saved to cache: {map_file}[/bold green]")
    console.print(f"[dim]Pages: {len(map_data['pages'])}, Elements: {len(map_data['elements'])}, Routes: {len(map_data['routes'])}[/dim]")
    console.print(f"[dim]Cache size: {cache.get_size_mb()} MB[/dim]")
    console.print(f"\n[dim]Next step: kernhell generate {source_dir}[/dim]")


@app.command()
def generate(
    source_dir: str = typer.Argument(..., help="Path to your analyzed application"),
    output: str = typer.Option("tests", "--out", help="Output directory for generated tests"),
    base_url: str = typer.Option("http://localhost:3000", "--url", help="Base URL of the running app"),
):
    """Generate Playwright tests from an analyzed app using AI."""
    print_banner()
    if config.get_key_count() == 0:
        _show_onboarding()
        raise typer.Exit(code=0)

    from kernhell.analyzer import AppAnalyzer
    from kernhell.generator import TestGenerator
    from kernhell.utils import CacheManager

    source_path = Path(source_dir).resolve()
    cache = CacheManager(source_path)
    map_file = cache.get_map_path()

    if not map_file.exists():
        log_warning("No map found in cache. Running analysis first...")
        with console.status("[bold yellow]Analyzing...[/bold yellow]", spinner="dots"):
            analyzer = AppAnalyzer(source_path)
            analyzer.analyze()
            analyzer.save_map(map_file)

    with console.status("[bold yellow]AI is writing tests...[/bold yellow]", spinner="dots"):
        gen = TestGenerator.from_map_file(map_file, config)
        output_dir = Path(output).resolve()
        generated = gen.generate_all(output_dir, base_url)

    if generated:
        console.print(f"\n[bold green]Generated {len(generated)} test(s) in: {output_dir}[/bold green]")
        console.print(f"\n[dim]Next step: kernhell heal {output}[/dim]")
    else:
        log_warning("No tests were generated. Check your app structure.")


@app.command()
def clean(source_dir: str = typer.Argument(..., help="Path to the project to clean cache for")):
    """Wipe KernHell's .kernhell_cache directory to free disk space."""
    print_banner()
    from kernhell.utils import CacheManager

    source_path = Path(source_dir).resolve()
    cache = CacheManager.__new__(CacheManager)
    cache.project_root = source_path
    cache.cache_dir = source_path / ".kernhell_cache"

    if cache.exists():
        size = cache.get_size_mb()
        cache.cleanup()
        console.print(f"[bold green]Freed {size} MB of cache data.[/bold green]")
    else:
        log_info("No cache found. Nothing to clean.")


@app.command()
def heal(target_path: str = typer.Argument(..., help="File or Directory to heal")):
    """
    AUTO-HEAL: Recursively fixes files or directories.
    Supports 'Smart Retry' loop for 100% fix rate.
    """
    # DEBUG: Is command running?
    # console.print("DEBUG: Heal command invoked.")
    
    print_banner()

    # Graceful exit if no keys (Onboarding shown by banner)
    if config.get_key_count() == 0:
        _show_onboarding()
        raise typer.Exit(code=0)
    
    # Resolving path manually as per logic
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


# ============================================================
# PHASE 3: BUG HUNTER & WATCH MODE
# ============================================================

@app.command()
def hunt(
    log_dir: str = typer.Argument(..., help="Directory containing log files"),
    patterns: str = typer.Option("error,exception,crash,fatal", help="Comma-separated error patterns"),
    slack: bool = typer.Option(False, "--slack", help="Enable Slack alerts"),
    whatsapp: bool = typer.Option(False, "--whatsapp", help="Enable WhatsApp alerts")
):
    """🔍 Monitor server logs and auto-analyze bugs with AI"""
    from kernhell.bug_hunter import LogMonitor, send_slack_alert, send_whatsapp_alert
    from watchdog.observers import Observer
    import time
    
    print_banner()
    
    # Validate directory exists
    log_path = Path(log_dir).resolve()
    if not log_path.exists() or not log_path.is_dir():
        log_error(f"Directory not found: {log_path}")
        raise typer.Exit(code=1)
    
    console.print("[bold green]🔍 Bug Hunter Started[/bold green]")
    console.print(f"👀 Watching: {log_path}")
    console.print(f"🎯 Patterns: {patterns}")
    
    # Setup alert callback
    def alert_callback(message):
        if slack:
            send_slack_alert(message)
        if whatsapp:
            send_whatsapp_alert(message)
    
    # Create monitor
    monitor = LogMonitor(
        patterns=patterns.split(','),
        alert_callback=alert_callback if (slack or whatsapp) else None
    )
    
    # Start watching
    observer = Observer()
    observer.schedule(monitor, str(log_path), recursive=True)
    observer.start()
    
    console.print("\n[yellow]Press Ctrl+C to stop...[/yellow]\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        console.print("\n[bold red]Stopping Bug Hunter...[/bold red]")
        observer.stop()
    
    observer.join()
    console.print("[green]✅ Bug Hunter stopped[/green]")


@app.command()
def watch(
    test_dir: str = typer.Argument(..., help="Test directory to monitor"),
    debounce: int = typer.Option(2, help="Seconds to wait before healing after change")
):
    """👀 Continuously monitor and auto-heal tests on file changes"""
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    import time
    
    print_banner()
    
    # Validate directory exists
    test_path = Path(test_dir).resolve()
    if not test_path.exists() or not test_path.is_dir():
        log_error(f"Directory not found: {test_path}")
        raise typer.Exit(code=1)
    
    console.print("[bold green]👀 Watch Mode Active[/bold green]")
    console.print(f"Monitoring: {test_path}\n")
    
    class TestWatcher(FileSystemEventHandler):
        def __init__(self):
            self.last_run = {}
        
        def on_modified(self, event):
            if event.is_directory:
                return
            
            file_path = event.src_path
            
            # Only Python test files
            if not (file_path.endswith('.py') and ('test' in file_path.lower())):
                return
            
            # Debounce (avoid multiple triggers)
            now = time.time()
            if now - self.last_run.get(file_path, 0) < debounce:
                return
            
            self.last_run[file_path] = now
            
            # Auto-heal
            console.print(f"\n[yellow]📝 Change detected: {Path(file_path).name}[/yellow]")
            console.print("[cyan]🔄 Auto-healing...[/cyan]")
            
            # Call heal function
            try:
                if _heal_single_file(Path(file_path)):
                    console.print("[green]✅ Healed successfully![/green]\n")
                else:
                    console.print("[red]❌ Healing failed[/red]\n")
            except Exception as e:
                console.print(f"[red]❌ Healing failed: {e}[/red]\n")
    
    observer = Observer()
    observer.schedule(TestWatcher(), str(test_path), recursive=True)
    observer.start()
    
    console.print("[yellow]Press Ctrl+C to stop...[/yellow]\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        console.print("\n[bold red]Stopping Watch Mode...[/bold red]")
        observer.stop()
    
    observer.join()
    console.print("[green]✅ Watch Mode stopped[/green]")


@app.command()
def report():
    """📊 Generate a premium HTML Dashboard of your healing stats."""
    from kernhell.report_generator import generate_report, open_report

    print_banner()
    console.print("[bold cyan]📊 Generating Mission Control Dashboard...[/bold cyan]\n")

    stats = db.get_stats()
    runs = db.get_recent_runs(limit=50)

    report_path = generate_report(stats, runs)
    open_report(report_path)

if __name__ == "__main__":
    app()
