"""Core data models for the KernHell healing pipeline.

Every module communicates through these typed Pydantic models.
This enforces clean boundaries and makes serialization/validation automatic.
"""

from __future__ import annotations

import enum
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class SelectorType(str, enum.Enum):
    """Classification of the Playwright selector strategy that was used."""

    CSS = "css"
    XPATH = "xpath"
    TEXT = "text"
    ROLE = "role"
    TEST_ID = "test_id"
    LABEL = "label"
    PLACEHOLDER = "placeholder"
    UNKNOWN = "unknown"


class ErrorType(str, enum.Enum):
    """Category of Playwright failure."""

    TIMEOUT = "timeout"
    NOT_FOUND = "not_found"
    STRICT_MODE = "strict_mode"
    NAVIGATION = "navigation"
    OTHER = "other"


class FailureType(str, enum.Enum):
    """Diagnosis of *why* the selector failed."""

    RENAME = "rename"          # Element exists, selector changed
    MISSING = "missing"        # Element genuinely absent (real bug)
    STRUCTURAL = "structural"  # DOM structure significantly changed
    UNKNOWN = "unknown"


class SelectorStrategy(str, enum.Enum):
    """Strategy the healer used to find the replacement selector."""

    ROLE_MATCH = "role_match"
    TEXT_MATCH = "text_match"
    ARIA_MATCH = "aria_match"
    TEST_ID_MATCH = "test_id_match"
    DATA_ATTR = "data_attr"
    CSS_FALLBACK = "css_fallback"


# ---------------------------------------------------------------------------
# Pipeline Data Models
# ---------------------------------------------------------------------------


class FailureContext(BaseModel):
    """Everything captured at the moment a Playwright selector fails.

    Produced by the Scanner, consumed by the Pruner and Analyzer.
    """

    test_file: Path
    line_number: int
    broken_selector: str
    selector_type: SelectorType = SelectorType.UNKNOWN
    error_message: str
    error_type: ErrorType = ErrorType.TIMEOUT
    live_dom: str = ""
    page_url: str = ""
    screenshot_path: Optional[Path] = None
    surrounding_code: str = ""

    # Metadata
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PrunedDOM(BaseModel):
    """The DOM after noise removal by the DOMPruner.

    Carries both the pruned HTML and reduction stats for reporting.
    """

    html: str
    original_size: int
    pruned_size: int

    @property
    def reduction_pct(self) -> float:
        """Percentage of bytes removed by pruning."""
        if self.original_size == 0:
            return 0.0
        return round((1 - self.pruned_size / self.original_size) * 100, 1)


class Diagnosis(BaseModel):
    """LLM classification of the failure — produced by the Analyzer.

    RENAME → safe to heal.  MISSING → potential real bug, skip.
    """

    failure_type: FailureType
    explanation: str
    confidence: float = Field(ge=0.0, le=1.0)


class SelectorFix(BaseModel):
    """A proposed replacement selector — produced by the Healer."""

    old_selector: str
    new_selector: str
    strategy: SelectorStrategy = SelectorStrategy.CSS_FALLBACK
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str = ""

    # Populated after Verifier confirms the fix works
    verified: bool = False


class HealingResult(BaseModel):
    """Outcome of healing a single broken selector."""

    failure: FailureContext
    pruned_dom: Optional[PrunedDOM] = None
    diagnosis: Optional[Diagnosis] = None
    fix: Optional[SelectorFix] = None
    from_cache: bool = False
    skipped: bool = False
    skip_reason: str = ""


class HealingReport(BaseModel):
    """Aggregate report for a full healing run (one or more test files)."""

    test_file: Path
    results: list[HealingResult] = []
    duration_ms: int = 0

    @property
    def total_failures(self) -> int:
        return len(self.results)

    @property
    def healed_count(self) -> int:
        return sum(1 for r in self.results if r.fix and r.fix.verified)

    @property
    def skipped_count(self) -> int:
        return sum(1 for r in self.results if r.skipped)

    @property
    def cache_hits(self) -> int:
        return sum(1 for r in self.results if r.from_cache)

    @property
    def llm_calls(self) -> int:
        return sum(1 for r in self.results if not r.from_cache and r.fix is not None)

    @property
    def verification_passed(self) -> bool:
        return all(r.fix.verified for r in self.results if r.fix is not None)
