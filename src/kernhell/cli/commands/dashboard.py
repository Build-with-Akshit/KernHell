"""CLI command: `kernhell dashboard` (or `kernhell ui`).

Launches the local KernHell Mission Control Dashboard (Next.js UI) and API service (FastAPI).
"""

from __future__ import annotations

import shutil
import socket
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from kernhell.cli.ui import print_banner
from kernhell.core.config import load_config
from kernhell.utils.logger import setup_logging

console = Console(stderr=True)


def _find_dashboard_dir() -> Optional[Path]:
    """Locate the Next.js dashboard directory across development and packaged setups."""
    # 1. Current working directory
    cwd_candidate = Path.cwd() / "dashboard"
    if (cwd_candidate / "package.json").is_file():
        return cwd_candidate

    # 2. Relative to repo root
    repo_candidate = Path(__file__).resolve().parents[4] / "dashboard"
    if (repo_candidate / "package.json").is_file():
        return repo_candidate

    # 3. Inside package root (if bundled)
    pkg_candidate = Path(__file__).resolve().parents[2] / "dashboard"
    if (pkg_candidate / "package.json").is_file():
        return pkg_candidate

    return None


def _terminate_process_tree(proc: subprocess.Popen) -> None:
    """Cleanly terminate a subprocess and all of its spawned child processes."""
    if proc.poll() is not None:
        return

    try:
        if sys.platform == "win32":
            # taskkill with /T (tree) and /F (force) prevents orphaned node.exe processes
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        else:
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
    except Exception:
        pass


def _wait_and_open_browser(
    target_url: str,
    check_port: int,
    host: str = "127.0.0.1",
    timeout_seconds: float = 25.0,
) -> None:
    """Poll until target port accepts HTTP connections and is ready, then open browser."""
    import urllib.request
    start = time.time()
    opened = False
    while time.time() - start < timeout_seconds:
        for check_host in (host, "127.0.0.1", "localhost"):
            try:
                test_url = f"http://{check_host}:{check_port}"
                req = urllib.request.Request(test_url, headers={"User-Agent": "KernHell-HealthCheck"})
                with urllib.request.urlopen(req, timeout=1.0) as resp:
                    if resp.status < 500:
                        opened = True
                        break
            except Exception:
                pass
        if opened:
            break
        time.sleep(0.5)

    if opened:
        console.print(f"[bold green]  ✓ Web UI is ready at {target_url}[/bold green]")
    try:
        webbrowser.open(target_url)
    except Exception:
        pass


def dashboard_command(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Bind host address for REST API."),
    port: int = typer.Option(8000, "--port", "-p", help="Bind port number for REST API."),
    ui_port: int = typer.Option(3000, "--ui-port", help="Bind port number for Web UI dashboard."),
    no_ui: bool = typer.Option(False, "--no-ui", help="Run only the FastAPI backend service without the Web UI."),
    no_open: bool = typer.Option(False, "--no-open", help="Do not automatically open browser."),
    config_path: Optional[Path] = typer.Option(None, "--config", "-c"),
) -> None:
    """Launch the KernHell Mission Control Dashboard and REST API service."""
    cfg = load_config(config_path)
    setup_logging(level=cfg.logging.level)

    print_banner()

    api_url = f"http://{host}:{port}"
    web_url = f"http://localhost:{ui_port}"

    try:
        import uvicorn
        from kernhell.api.server import create_app
    except ImportError:
        console.print(
            "\n[bold red]Error:[/bold red] Mission Control Dashboard requires [bold cyan]fastapi[/bold cyan] and [bold cyan]uvicorn[/bold cyan].\n"
            "Please install them via:\n"
            "  [green]pip install 'kernhell[dashboard]'[/green] or [green]pip install fastapi uvicorn[/green]\n"
        )
        raise typer.Exit(code=1)

    node_proc: Optional[subprocess.Popen] = None
    ui_active = False

    if not no_ui:
        dashboard_dir = _find_dashboard_dir()
        node_bin = shutil.which("node")
        npm_bin = shutil.which("npm.cmd" if sys.platform == "win32" else "npm")

        if not dashboard_dir:
            console.print("[yellow]Warning: Dashboard directory not found. Starting API service only.[/yellow]")
        elif not node_bin or not npm_bin:
            console.print("[yellow]Warning: Node.js / npm not detected on PATH. Starting API service only.[/yellow]")
        elif not (dashboard_dir / "node_modules").is_dir():
            console.print(
                f"[yellow]Notice: Dashboard dependencies missing in '{dashboard_dir / 'node_modules'}'.[/yellow]\n"
                f"[dim]Run: cd '{dashboard_dir}' && npm install[/dim]"
            )
        else:
            # Spawn Next.js dev server with explicit host and port binding
            npx_bin = shutil.which("npx.cmd" if sys.platform == "win32" else "npx") or npm_bin
            if npx_bin.endswith("npm.cmd") or npx_bin.endswith("npm"):
                cmd = [npx_bin, "run", "dev", "--", "-p", str(ui_port), "-H", "127.0.0.1"]
            else:
                cmd = [npx_bin, "next", "dev", "-p", str(ui_port), "-H", "127.0.0.1"]

            try:
                console.print(f"[dim]  › Starting Next.js Web UI on http://localhost:{ui_port}...[/dim]")
                node_proc = subprocess.Popen(
                    cmd,
                    cwd=str(dashboard_dir),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                ui_active = True
            except Exception as exc:
                console.print(f"[yellow]Could not start Next.js UI process: {exc}[/yellow]")

    # Build terminal status panel
    panel_content = [
        f"[bold cyan]Mission Control API:[/bold cyan] [underline]{api_url}[/underline]",
        f"[bold cyan]Swagger API Docs:[/bold cyan]    [underline]{api_url}/docs[/underline]",
    ]
    if ui_active:
        panel_content.append(f"[bold green]Web Dashboard UI:[/bold green]    [underline]{web_url}[/underline]")
    else:
        panel_content.append(f"[dim]Web Dashboard UI:    Disabled or unavailable[/dim]")

    panel_content.append("\n[dim]Press Ctrl+C to terminate both servers cleanly.[/dim]")
    console.print(Panel("\n".join(panel_content), title="Mission Control Active", border_style="cyan"))

    # Auto-open browser
    if not no_open:
        target_browser_url = web_url if ui_active else f"{api_url}/docs"
        target_check_port = ui_port if ui_active else port
        thread = threading.Thread(
            target=_wait_and_open_browser,
            args=(target_browser_url, target_check_port, host),
            daemon=True,
        )
        thread.start()

    app = create_app(cfg)
    try:
        uvicorn.run(app, host=host, port=port, log_level="warning")
    finally:
        if node_proc is not None:
            console.print("\n[dim]Stopping Web Dashboard UI process...[/dim]")
            _terminate_process_tree(node_proc)
