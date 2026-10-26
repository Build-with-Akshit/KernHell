"""Structured logging configuration for KernHell.

Uses ``structlog`` with two output modes:
  - **Console** (default): Rich-coloured, human-friendly output via
    ``structlog.dev.ConsoleRenderer``.
  - **JSON** (``--json-log`` or CI): Machine-parseable JSON lines, ideal
    for log aggregation.

Call :func:`setup_logging` once at startup (done automatically by the CLI).
After that, obtain loggers anywhere with ``structlog.get_logger()``.
"""

from __future__ import annotations

import logging
import sys

from pathlib import Path
from typing import Any, Optional

import structlog
from rich.console import Console

_cli_console = Console(stderr=True)


class MinimalCLIProcessor:
    """Formats high-level engine events into clean, minimal, human-friendly status steps."""

    def __call__(self, logger: Any, name: str, event_dict: dict[str, Any]) -> dict[str, Any]:
        event = event_dict.get("event", "")
        level = event_dict.get("level", "info").lower()

        from rich.markup import escape

        line: Optional[str] = None

        if event == "cache.loaded":
            total = event_dict.get("total_entries", 0)
            line = f"  [dim]›[/dim] Loaded [cyan]{total}[/cyan] cached selector patterns from semantic store"

        elif event == "scanner.run.start":
            test_file = Path(str(event_dict.get("test_file", ""))).name or "test suite"
            line = f"  [dim]›[/dim] Running Playwright suite on [white]{test_file}[/white]..."

        elif event == "scanner.pytest.passed":
            line = f"  [dim]›[/dim] [bold green]✔[/bold green] Playwright run completed (all tests passed)"

        elif event == "parser.failure_found":
            line_num = event_dict.get("line", "?")
            sel = escape(str(event_dict.get("selector", "")))
            line = f"  [dim]›[/dim] [bold red]✖[/bold red] Selector failure caught at line [bold yellow]{line_num}[/bold yellow]: [bold red]{sel}[/bold red]"

        elif event == "pruner.done":
            orig = event_dict.get("original_size", 0)
            pruned = event_dict.get("pruned_size", 0)
            pct = event_dict.get("reduction_pct", 0)
            line = f"  [dim]›[/dim] DOM pruned: [dim]{orig:,}[/dim] → [green]{pruned:,}[/green] bytes ([green]-{pct}%[/green])"

        elif event == "cache.hit":
            score = event_dict.get("score", 0)
            try:
                score_pct = int(float(score) * 100)
            except Exception:
                score_pct = 95
            healed = escape(str(event_dict.get("healed", "")))
            line = f"  [dim]›[/dim] [bold green]⚡[/bold green] Semantic cache hit ([bold yellow]{score_pct}%[/bold yellow]): [bold green]{healed}[/bold green]"

        elif event == "cache.miss":
            line = f"  [dim]›[/dim] Semantic cache miss — escalating to AI healer..."

        elif event == "healer.query":
            line = f"  [dim]›[/dim] Querying AI engine for repair candidate..."

        elif event == "healer.generated":
            sel = escape(str(event_dict.get("selector", "")))
            line = f"  [dim]›[/dim] AI generated candidate: [bold cyan]{sel}[/bold cyan]"

        elif event == "patcher.start":
            file_name = Path(str(event_dict.get("file", ""))).name or "test"
            l = event_dict.get("line", "")
            line = f"  [dim]›[/dim] Applying surgical AST patch to [white]{file_name}[/white] (line {l})..."

        elif event == "patcher.complete":
            line = f"  [dim]›[/dim] AST patch applied successfully"

        elif event == "verifier.start":
            line = f"  [dim]›[/dim] Re-running Playwright to verify fix..."

        elif event == "verifier.passed":
            line = f"  [dim]›[/dim] [bold green]✔[/bold green] Verification passed! Repaired selector confirmed working"

        elif event == "verifier.failed":
            line = f"  [dim]›[/dim] [bold red]✖[/bold red] Verification failed on candidate selector"

        elif level in ("warning", "error", "critical"):
            msg = escape(str(event))
            color = "yellow" if level == "warning" else "red"
            line = f"  [bold {color}]⚠ {msg}[/bold {color}]"

        if line:
            _cli_console.print(line)

        # Drop event so standard raw formatter doesn't double print
        raise structlog.DropEvent


def setup_logging(*, level: str = "INFO", json_output: bool = False) -> None:
    """Configure structlog and stdlib logging for the application.

    Parameters
    ----------
    level:
        Minimum log level (``DEBUG``, ``INFO``, ``WARNING``, ``ERROR``).
    json_output:
        When *True*, emit JSON lines instead of coloured console output.
        Recommended for CI/CD environments.
    """
    import os

    # Silence noisy LiteLLM warnings in interactive CLI
    os.environ["LITELLM_LOG"] = "ERROR"
    try:
        import litellm

        litellm.suppress_debug_info = True
        litellm.set_verbose = False
    except ImportError:
        pass

    log_level = getattr(logging, level.upper(), logging.INFO)
    is_debug = log_level <= logging.DEBUG

    # Shared processors run before the final renderer.
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    # In standard interactive mode (non-debug, non-json), use MinimalCLIProcessor
    if not json_output and not is_debug:
        shared_processors.append(MinimalCLIProcessor())

    if json_output:
        renderer: structlog.types.Processor = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(
            colors=sys.stderr.isatty(),
        )

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(log_level)

    # Silence noisy third-party loggers.
    for noisy in ("playwright", "urllib3", "httpx", "chromadb", "litellm", "LiteLLM", "google"):
        logging.getLogger(noisy).setLevel(logging.ERROR)
