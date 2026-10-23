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

import structlog


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
    log_level = getattr(logging, level.upper(), logging.INFO)

    # Shared processors run before the final renderer.
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

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
    for noisy in ("playwright", "urllib3", "httpx", "chromadb"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
