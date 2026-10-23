"""FastAPI Mission Control Bridge for KernHell.

Provides REST API endpoints for:
  - Cache telemetry & inspection
  - Healing history & diff inspection
  - Live selector healing & scan triggering
  - Interactive test simulation playground
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Optional

import structlog
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from kernhell import __version__
from kernhell.analyzer.analyzer import FailureAnalyzer
from kernhell.analyzer.healer import SelectorHealer
from kernhell.cache.cache_manager import CacheManager
from kernhell.core.config import KernHellConfig, load_config
from kernhell.core.models import (
    Diagnosis,
    FailureContext,
    FailureType,
    HealingReport,
    PrunedDOM,
    SelectorFix,
    SelectorStrategy,
    SelectorType,
)
from kernhell.core.orchestrator import HealingOrchestrator
from kernhell.patcher.patcher import SurgicalPatcher
from kernhell.pruner.dom_pruner import prune_dom

logger = structlog.get_logger()

# ---------------------------------------------------------------------------
# API Data Models
# ---------------------------------------------------------------------------


class ScanRequest(BaseModel):
    test_file: str


class HealRequest(BaseModel):
    test_file: str
    dry_run: bool = False


class SimulateRequest(BaseModel):
    broken_selector: str
    dom_html: str
    surrounding_code: str = ""
    page_url: str = "https://example.com/checkout"


class SimulateResponse(BaseModel):
    broken_selector: str
    original_dom_bytes: int
    pruned_dom_bytes: int
    compression_percent: float
    pruned_dom: str
    diagnosis: Diagnosis
    healed_selector: Optional[SelectorFix] = None
    applied_diff: Optional[str] = None
    from_cache: bool = False


# ---------------------------------------------------------------------------
# History Manager
# ---------------------------------------------------------------------------


class RunHistoryManager:
    """Stores and retrieves historical healing runs in JSON storage."""

    def __init__(self, storage_dir: Path) -> None:
        self.history_file = storage_dir / "healing_history.json"
        self._ensure_file()

    def _ensure_file(self) -> None:
        if not self.history_file.is_file():
            self.history_file.write_text("[]", encoding="utf-8")

    def record_run(self, report: HealingReport, diff: str = "") -> None:
        try:
            runs = self.get_runs()
            record = {
                "test_file": str(report.test_file),
                "total_failures": report.total_failures,
                "healed_count": report.healed_count,
                "skipped_count": report.skipped_count,
                "cache_hits": report.cache_hits,
                "llm_calls": report.llm_calls,
                "verification_passed": report.verification_passed,
                "duration_ms": report.duration_ms,
                "diff": diff,
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
                    }
                    for r in report.results
                ],
            }
            runs.insert(0, record)
            # Cap at 50 recent runs
            self.history_file.write_text(json.dumps(runs[:50], indent=2), encoding="utf-8")
        except Exception as exc:
            logger.warning("history.record_failed", error=str(exc))

    def get_runs(self) -> list[dict[str, Any]]:
        try:
            if self.history_file.is_file():
                return json.loads(self.history_file.read_text(encoding="utf-8"))
        except Exception:
            pass
        return []


# ---------------------------------------------------------------------------
# App Factory
# ---------------------------------------------------------------------------


def create_app(config: Optional[KernHellConfig] = None) -> FastAPI:
    cfg = config or load_config()
    cache_path = Path(os.path.expanduser(cfg.cache.cache_dir)).resolve()
    cache_path.mkdir(parents=True, exist_ok=True)

    cache_mgr = CacheManager(cfg)
    history_mgr = RunHistoryManager(cache_path)
    orchestrator = HealingOrchestrator(cfg)
    analyzer = FailureAnalyzer(cfg)
    healer = SelectorHealer(cfg)
    patcher = SurgicalPatcher()

    app = FastAPI(
        title="KernHell Mission Control API",
        description="REST bridge for KernHell Autonomous Self-Healing Testing Engine",
        version=__version__,
    )

    # Enable CORS for Next.js development and production
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/health")
    def health():
        return {
            "status": "healthy",
            "app": "KernHell Mission Control",
            "version": __version__,
        }

    @app.get("/api/stats")
    def get_stats():
        cache_stats = cache_mgr.get_stats()
        runs = history_mgr.get_runs()

        total_heals = sum(r.get("healed_count", 0) for r in runs)
        total_skipped = sum(r.get("skipped_count", 0) for r in runs)

        # Developer value calculation: avg 25 mins per broken selector debug
        minutes_saved = total_heals * 25
        hours_saved = round(minutes_saved / 60.0, 1)
        dollars_saved = round(hours_saved * 85.0, 2)  # $85/hr QA/dev rate

        return {
            "total_runs": len(runs),
            "total_healed": total_heals,
            "real_bugs_caught": total_skipped,
            "cache_entries": cache_stats.total_entries,
            "cache_hits": cache_stats.hits,
            "cache_misses": cache_stats.misses,
            "cache_efficiency_pct": cache_stats.hit_ratio,
            "hours_saved": hours_saved,
            "dollars_saved": dollars_saved,
        }

    @app.get("/api/history")
    def get_history():
        return history_mgr.get_runs()

    @app.get("/api/cache")
    def list_cache():
        entries = cache_mgr.list_entries()
        return [e.model_dump(mode="json") for e in entries]

    @app.post("/api/cache/clear")
    def clear_cache():
        count = cache_mgr.clear()
        return {"cleared_count": count, "message": "Cache successfully cleared"}

    @app.post("/api/scan")
    def trigger_scan(req: ScanRequest):
        target = Path(req.test_file).resolve()
        if not target.is_file():
            raise HTTPException(status_code=404, detail=f"File not found: {req.test_file}")

        try:
            results = orchestrator.scan(target)
            return {
                "test_file": str(target),
                "failures_detected": len(results),
                "failures": [
                    {
                        "broken_selector": f.broken_selector,
                        "line_number": f.line_number,
                        "error_type": f.error_type.value,
                        "selector_type": f.selector_type.value,
                        "pruned_bytes": p.pruned_size if p else None,
                        "compression_pct": p.reduction_pct if p else None,
                    }
                    for f, p in results
                ],
            }
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @app.post("/api/heal")
    def trigger_heal(req: HealRequest):
        target = Path(req.test_file).resolve()
        if not target.is_file():
            raise HTTPException(status_code=404, detail=f"File not found: {req.test_file}")

        try:
            report = orchestrator.heal(target, dry_run=req.dry_run)
            history_mgr.record_run(report)
            return report.model_dump(mode="json")
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @app.post("/api/simulate", response_model=SimulateResponse)
    def simulate_playground(req: SimulateRequest):
        """Interactive Simulation: Prunes DOM, classifies, and heals in real time."""
        pruned = prune_dom(req.dom_html)

        dummy_ctx = FailureContext(
            test_file=Path("playground_simulation.py"),
            line_number=10,
            broken_selector=req.broken_selector,
            selector_type=SelectorType.CSS,
            error_message=f"Timeout waiting for locator('{req.broken_selector}')",
            live_dom=req.dom_html,
            page_url=req.page_url,
            surrounding_code=req.surrounding_code or f'page.click("{req.broken_selector}")',
        )

        # 1. Check cache first
        cached_fix, score = cache_mgr.lookup(
            req.broken_selector,
            context=dummy_ctx.surrounding_code,
            page_url=req.page_url,
        )

        if cached_fix:
            diff_text = None
            if req.surrounding_code:
                try:
                    patched = patcher.apply_patch(
                        req.surrounding_code,
                        req.broken_selector,
                        cached_fix.new_selector,
                    )
                    import difflib

                    diff_lines = list(
                        difflib.unified_diff(
                            req.surrounding_code.splitlines(),
                            patched.splitlines(),
                            fromfile="broken_code.py",
                            tofile="healed_code.py",
                            lineterm="",
                        )
                    )
                    diff_text = "\n".join(diff_lines)
                except Exception:
                    pass

            return SimulateResponse(
                broken_selector=req.broken_selector,
                original_dom_bytes=pruned.original_size,
                pruned_dom_bytes=pruned.pruned_size,
                compression_percent=pruned.reduction_pct,
                pruned_dom=pruned.html,
                diagnosis=Diagnosis(
                    failure_type=FailureType.RENAME,
                    explanation=f"Found verified fix in Semantic Memory with {int(score * 100)}% cosine similarity.",
                    confidence=score,
                ),
                healed_selector=cached_fix,
                applied_diff=diff_text,
                from_cache=True,
            )

        # 2. AI Failure Diagnosis
        diagnosis = analyzer.diagnose(dummy_ctx, pruned)

        fix: Optional[SelectorFix] = None
        diff_text = None

        if diagnosis.failure_type != FailureType.MISSING:
            try:
                fix = healer.suggest_fix(dummy_ctx, diagnosis, pruned)
                # Store in cache for future hits
                cache_mgr.store(
                    broken_selector=req.broken_selector,
                    fix=fix,
                    context=dummy_ctx.surrounding_code,
                    page_url=req.page_url,
                )
                if req.surrounding_code:
                    try:
                        patched = patcher.apply_patch(
                            req.surrounding_code,
                            req.broken_selector,
                            fix.new_selector,
                        )
                        import difflib

                        diff_lines = list(
                            difflib.unified_diff(
                                req.surrounding_code.splitlines(),
                                patched.splitlines(),
                                fromfile="broken_code.py",
                                tofile="healed_code.py",
                                lineterm="",
                            )
                        )
                        diff_text = "\n".join(diff_lines)
                    except Exception:
                        pass
            except Exception as exc:
                logger.warning("simulate.healer_failed", error=str(exc))

        return SimulateResponse(
            broken_selector=req.broken_selector,
            original_dom_bytes=pruned.original_size,
            pruned_dom_bytes=pruned.pruned_size,
            compression_percent=pruned.reduction_pct,
            pruned_dom=pruned.html,
            diagnosis=diagnosis,
            healed_selector=fix,
            applied_diff=diff_text,
            from_cache=False,
        )

    return app
