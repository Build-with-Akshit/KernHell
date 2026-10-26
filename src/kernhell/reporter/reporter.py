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
        """Print full healing summary table to terminal with wide, unclipped selector display."""
        from rich.markup import escape

        table = Table(
            title=f"KernHell Healing Report: [bold cyan]{report.test_file.name}[/bold cyan]",
            box=box.ROUNDED,
            show_lines=True,
            expand=True,
        )
        table.add_column("#", style="dim", width=3, justify="center")
        table.add_column("Selector Transformation", ratio=1, overflow="fold")
        table.add_column("Engine / Match", width=22, justify="center")
        table.add_column("Verified", justify="center", width=10)

        for i, res in enumerate(report.results, start=1):
            orig_sel = escape(res.failure.broken_selector)
            if res.fix:
                healed_sel = escape(res.fix.new_selector)
                transform_text = (
                    f"[bold red]✖ {orig_sel}[/bold red]\n"
                    f"[bold green]✔ {healed_sel}[/bold green]"
                )
                source_label = "Cache" if res.from_cache else "AI Healer"
                conf_pct = f"{int(res.fix.confidence * 100)}%"
                strategy_val = (
                    res.fix.strategy.value
                    if hasattr(res.fix.strategy, "value")
                    else str(res.fix.strategy)
                )
                engine_text = (
                    f"[bold cyan]{source_label}[/bold cyan] [dim]({conf_pct})[/dim]\n"
                    f"[dim]{strategy_val}[/dim]"
                )
                verified_text = (
                    "[bold green]YES[/bold green]"
                    if res.fix.verified
                    else "[bold red]NO[/bold red]"
                )
                table.add_row(str(i), transform_text, engine_text, verified_text)
            else:
                reason = (
                    escape(f"{res.skip_reason[:45]}...")
                    if res.skip_reason
                    else "Element absent on live page"
                )
                transform_text = (
                    f"[bold red]✖ {orig_sel}[/bold red]\n"
                    f"[dim yellow]↳ {reason}[/dim yellow]"
                )
                table.add_row(
                    str(i),
                    transform_text,
                    "[yellow]Guardrail Active[/yellow]",
                    "[yellow]SKIPPED[/yellow]",
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
