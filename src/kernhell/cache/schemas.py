"""Schemas for the Semantic Vector Cache."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

from kernhell.core.models import SelectorStrategy


class CacheEntry(BaseModel):
    """A verified selector healing record stored in semantic memory."""

    id: str  # Hash of selector + context
    broken_selector: str
    new_selector: str
    strategy: SelectorStrategy = SelectorStrategy.CSS_FALLBACK
    confidence: float = Field(ge=0.0, le=1.0)
    context_snippet: str = ""
    page_url: str = ""
    test_file: str = ""
    verified: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    hit_count: int = 0


class CacheStats(BaseModel):
    """Aggregate statistics for the semantic vector cache."""

    total_entries: int = 0
    hits: int = 0
    misses: int = 0

    @property
    def hit_ratio(self) -> float:
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return round((self.hits / total) * 100, 1)
