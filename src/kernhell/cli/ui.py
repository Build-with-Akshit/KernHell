"""Rich console UI helpers for KernHell CLI output.

Provides reusable display components for the terminal:
  - Branded banner with version
  - Failure context panels
  - Healing result tables
  - Progress spinners
  - Diff display for patched selectors
"""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.syntax import Syntax
from rich import box

from kernhell import __version__
from kernhell.core.models import FailureContext, HealingReport, HealingResult, PrunedDOM

console = Console(stderr=True)


# ---------------------------------------------------------------------------
# Banner
# ---------------------------------------------------------------------------

_BANNER = r"""
 ██╗  ██╗███████╗██████╗ ███╗   ██╗██╗  ██╗███████╗██╗     ██╗
 ██║ ██╔╝██╔════╝██╔══██╗████╗  ██║██║  ██║██╔════╝██║     ██║
 █████╔╝ █████╗  ██████╔╝██╔██╗ ██║███████║█████╗  ██║     ██║
 ██╔═██╗ ██╔══╝  ██╔══██╗██║╚██╗██║██╔══██║██╔══╝  ██║     ██║
 ██║  ██╗███████╗██║  ██║██║ ╚████║██║  ██║███████╗███████╗███████╗
 ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝
"""


def print_banner() -> None:
    """Display the KernHell ASCII banner with version."""
    banner_text = Text(_BANNER.strip("\n"), style="bold red")
    console.print(banner_text, highlight=False)
    console.print(
        f"  [bold cyan]v{__version__}[/bold cyan] "
        f"[dim]•[/dim] [italic bright_black]An AI-powered autonomous self-healing testing engine[/italic bright_black]"
    )
    console.print()


# ---------------------------------------------------------------------------
# Clean Status & Success Panels
# ---------------------------------------------------------------------------


def print_clean_pass_panel(filename: str, duration_ms: Optional[int] = None) -> None:
    """Display a prominent, high-visibility panel when all tests pass cleanly."""
    timing = f" in [bold cyan]{duration_ms:,}ms[/bold cyan]" if duration_ms is not None else ""
    content = (
        f"[bold green]✔ All Tests Passed Cleanly![/bold green]\n\n"
        f"No broken locators or selector failures detected in [bold cyan]{filename}[/bold cyan].\n"
        f"[dim]Playwright test suite executed cleanly{timing} — nothing to heal![/dim]"
    )
    panel = Panel(
        content,
        title=f"[bold green]✨ {filename} Healthy[/bold green]",
        border_style="green",
        box=box.ROUNDED,
        padding=(1, 2),
    )
    console.print()
    console.print(panel)
    console.print()


def print_skipped_guardrail(result: HealingResult) -> None:
    """Display Anti-Hallucination Guardrail warning panel."""
    reason = result.skip_reason or "Potential application defect detected."
    panel = Panel(
        f"[bold yellow]🛡 Anti-Hallucination Guardrail Active[/bold yellow]\n\n"
        f"KernHell did [bold red]not[/bold red] mutate the selector in this test because the element is absent on the page.\n"
        f"This indicates a genuine application bug rather than a selector drift.\n\n"
        f"[bold]Root Cause / Reason:[/bold]\n"
        f"[dim]›[/dim] [white]{reason}[/white]",
        border_style="yellow",
        box=box.ROUNDED,
        padding=(1, 2),
    )
    console.print(panel)


def print_heal_success_badge(report: HealingReport) -> None:
    """Display prominent final outcome badge panel after healing."""
    if report.healed_count > 0:
        verified_msg = (
            "and [bold green]100% verified[/bold green] via Playwright re-run"
            if report.verification_passed
            else "[yellow](manual verification recommended)[/yellow]"
        )
        panel = Panel(
            f"[bold green]✨ Self-Healing Succeeded![/bold green]\n\n"
            f"[bold cyan]{report.healed_count}[/bold cyan] broken selector(s) repaired {verified_msg} in [bold cyan]{report.duration_ms:,}ms[/bold cyan].\n"
            f"[dim]Test suite in [white]{report.test_file.name}[/white] is now verified healthy.[/dim]",
            title=f"[bold green]✔ {report.test_file.name} Restored[/bold green]",
            border_style="green",
            box=box.ROUNDED,
            padding=(1, 2),
        )
        console.print(panel)
        console.print()
    elif report.skipped_count > 0:
        panel = Panel(
            f"[bold yellow]⚠ Healing Protected by Guardrails[/bold yellow]\n\n"
            f"All [bold yellow]{report.skipped_count}[/bold yellow] detected failure(s) were flagged as genuine application bugs.\n"
            f"[dim]No source code was mutated to protect test suite integrity.[/dim]",
            title=f"[bold yellow]🛡 Guardrail Protected: {report.test_file.name}[/bold yellow]",
            border_style="yellow",
            box=box.ROUNDED,
            padding=(1, 2),
        )
        console.print(panel)
        console.print()


def render_unified_patch_panel(original_code: str, patched_code: str, filename: str = "") -> Panel:
    """Render a unified AST patch view with surrounding context, red cut lines and green added lines."""
    from difflib import SequenceMatcher

    orig_lines = original_code.splitlines()
    patch_lines = patched_code.splitlines()

    matcher = SequenceMatcher(None, orig_lines, patch_lines)
    opcodes = matcher.get_opcodes()

    text = Text()

    for tag, i1, i2, j1, j2 in opcodes:
        if tag == "equal":
            continue

        # Context around change (up to 4 lines before and after)
        start_orig = max(0, i1 - 4)
        end_orig = min(len(orig_lines), i2 + 4)

        # Context lines before
        for idx in range(start_orig, i1):
            text.append(f"{idx + 1:>4}    ", style="dim")
            text.append(f"{orig_lines[idx]}\n", style="dim")

        # Removed lines (Red with strike / cut)
        for idx in range(i1, i2):
            text.append(f"{idx + 1:>4} -  ", style="bold red")
            text.append(f"{orig_lines[idx]}\n", style="bold red strike")

        # Added lines (Green)
        for jdx in range(j1, j2):
            text.append(f"{i1 + (jdx - j1) + 1:>4} +  ", style="bold green")
            text.append(f"{patch_lines[jdx]}\n", style="bold green")

        # Context lines after
        for idx in range(i2, end_orig):
            text.append(f"{idx + 1:>4}    ", style="dim")
            text.append(f"{orig_lines[idx]}\n", style="dim")

    title = (
        f"[bold green]⚡ Surgical AST Patch ({filename})[/bold green]"
        if filename
        else "[bold green]⚡ Surgical AST Patch[/bold green]"
    )
    return Panel(
        text,
        title=title,
        subtitle="[dim]Comments, indentation & formatting preserved[/dim]",
        border_style="green",
        box=box.ROUNDED,
        padding=(0, 1),
    )


# ---------------------------------------------------------------------------
# Failure Display
# ---------------------------------------------------------------------------


def print_failure_context(ctx: FailureContext, index: int = 1, show_surrounding_code: bool = True) -> None:
    """Display a single failure context as a Rich panel."""
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Key", style="bold cyan", width=16)
    table.add_column("Value")

    table.add_row("Selector", Text(ctx.broken_selector, style="bold red"))
    table.add_row("Type", ctx.selector_type.value)
    table.add_row("Error", ctx.error_type.value)
    table.add_row("Line", str(ctx.line_number) if ctx.line_number else "unknown")
    table.add_row("File", str(ctx.test_file.name))

    if ctx.page_url:
        table.add_row("URL", ctx.page_url)

    panel = Panel(
        table,
        title=f"[bold red]💀 Failure #{index}[/bold red]",
        border_style="red",
        box=box.ROUNDED,
    )
    console.print(panel)

    # Show surrounding code ONLY when not displaying the unified patch panel
    if show_surrounding_code and ctx.surrounding_code:
        syntax = Syntax(
            ctx.surrounding_code,
            "python",
            theme="monokai",
            line_numbers=False,
            word_wrap=True,
        )
        console.print(
            Panel(syntax, title="[dim]Surrounding Code[/dim]", border_style="dim", box=box.ROUNDED)
        )


def print_pruning_stats(pruned: PrunedDOM) -> None:
    """Display DOM pruning statistics."""
    console.print(
        f"  [bold magenta]🔪 DOM Pruned:[/bold magenta] "
        f"[dim]{pruned.original_size:,}[/dim] → "
        f"[bold green]{pruned.pruned_size:,}[/bold green] bytes "
        f"([bold green]-{pruned.reduction_pct}%[/bold green])"
    )


# ---------------------------------------------------------------------------
# Scan Summary
# ---------------------------------------------------------------------------


def print_scan_summary(failures: list[FailureContext]) -> None:
    """Display a summary table of all detected failures."""
    if not failures:
        print_clean_pass_panel("Test Suite")
        return

    table = Table(
        title="🔍 Detected Selector Failures",
        box=box.ROUNDED,
        show_lines=True,
    )
    table.add_column("#", style="dim", width=4)
    table.add_column("Selector", style="bold red")
    table.add_column("Type", style="cyan")
    table.add_column("Line", style="yellow", justify="right")
    table.add_column("Error", style="dim")

    for i, f in enumerate(failures, 1):
        table.add_row(
            str(i),
            f.broken_selector,
            f.selector_type.value,
            str(f.line_number) if f.line_number else "?",
            f.error_type.value,
        )

    console.print(table)
    console.print(
        f"\n  [bold red]✖[/bold red] Found [bold red]{len(failures)}[/bold red] broken selector(s).\n"
    )


# ---------------------------------------------------------------------------
# Healing Report
# ---------------------------------------------------------------------------


def print_healing_report(report: HealingReport) -> None:
    """Display the final healing report."""
    table = Table(
        title="🔥 KernHell Healing Report",
        box=box.DOUBLE_EDGE,
    )
    table.add_column("Metric", style="bold")
    table.add_column("Value", justify="right")

    table.add_row("Total Failures", str(report.total_failures))
    table.add_row("Healed", f"[bold green]{report.healed_count}[/bold green]")
    table.add_row("Skipped", f"[yellow]{report.skipped_count}[/yellow]")
    table.add_row("From Cache", str(report.cache_hits))
    table.add_row("LLM Calls", str(report.llm_calls))
    table.add_row("Duration", f"{report.duration_ms}ms")
    table.add_row(
        "Status",
        "[bold green]✅ PASSED[/bold green]"
        if report.verification_passed
        else "[bold red]❌ FAILED[/bold red]",
    )

    console.print(table)
