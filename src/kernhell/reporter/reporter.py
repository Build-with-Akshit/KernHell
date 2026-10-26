"""Reporter module — produces beautiful terminal summaries and machine-readable JSON exports."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from kernhell.core.models import HealingReport, HealingResult

console = Console(stderr=True)


class HealingReporter:
    """Renders healing run results to terminal and files."""

    @staticmethod
    def render_diff(old_code: str, new_code: str, filename: str = "") -> None:
        """Display a unified patch view with red cut lines and green added lines."""
        if old_code == new_code:
            return

        from kernhell.cli.ui import render_unified_patch_panel

        panel = render_unified_patch_panel(old_code, new_code, filename)
        console.print(panel)
        console.print()

    @staticmethod
    def print_summary(report: HealingReport) -> None:
        """Print full healing summary table to terminal."""
        table = Table(
            title=f"KernHell Healing Report: [bold cyan]{report.test_file.name}[/bold cyan]",
            box=box.ROUNDED,
            show_lines=True,
        )
        table.add_column("#", style="dim", width=4)
        table.add_column("Original Selector", style="bold red")
        table.add_column("Healed Selector", style="bold green")
        table.add_column("Strategy", style="cyan")
        table.add_column("Confidence", justify="right", style="bold yellow")
        table.add_column("Source", style="bold magenta")
        table.add_column("Verified", justify="center")

        from rich.markup import escape

        for i, res in enumerate(report.results, start=1):
            if res.fix:
                source = "Semantic Cache" if res.from_cache else "AI Healer"
                verified = "✅ YES" if res.fix.verified else "❌ NO"
                conf_str = f"{int(res.fix.confidence * 100)}%"
                table.add_row(
                    str(i),
                    escape(res.failure.broken_selector),
                    escape(res.fix.new_selector),
                    escape(res.fix.strategy.value),
                    conf_str,
                    source,
                    verified,
                )
            else:
                table.add_row(
                    str(i),
                    escape(res.failure.broken_selector),
                    "[yellow](SKIPPED)[/yellow]",
                    "-",
                    "-",
                    "-",
                    escape(f"{res.skip_reason[:30]}...") if res.skip_reason else "-",
                )

        console.print(table)
        console.print()

    @staticmethod
    def export_json(report: HealingReport, output_path: Optional[Path] = None) -> str:
        """Export healing report to structured JSON."""
        data = {
            "test_file": str(report.test_file),
            "total_failures": report.total_failures,
            "healed_count": report.healed_count,
            "skipped_count": report.skipped_count,
            "cache_hits": report.cache_hits,
            "llm_calls": report.llm_calls,
            "verification_passed": report.verification_passed,
            "duration_ms": report.duration_ms,
            "results": [
                {
                    "broken_selector": r.failure.broken_selector,
                    "line_number": r.failure.line_number,
                    "healed_selector": r.fix.new_selector if r.fix else None,
                    "strategy": r.fix.strategy.value if r.fix else None,
                    "confidence": r.fix.confidence if r.fix else None,
                    "from_cache": r.from_cache,
                    "skipped": r.skipped,
                    "skip_reason": r.skip_reason,
                    "verified": r.fix.verified if r.fix else False,
                }
                for r in report.results
            ],
        }
        json_str = json.dumps(data, indent=2)
        if output_path:
            output_path.write_text(json_str, encoding="utf-8")
        return json_str
