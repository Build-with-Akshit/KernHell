"""Semantic Vector Cache Manager — stores and retrieves verified selector fixes.

When a selector fails, KernHell checks this cache BEFORE calling any LLM.
If a semantically equivalent selector + context was healed previously,
it applies the fix with ZERO latency and ZERO LLM cost.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Optional

import structlog

from kernhell.cache.embedder import SemanticEmbedder, cosine_similarity
from kernhell.cache.schemas import CacheEntry, CacheStats
from kernhell.core.config import KernHellConfig
from kernhell.core.models import SelectorFix, SelectorStrategy

logger = structlog.get_logger()


class CacheManager:
    """Manages semantic vector memory and similarity retrieval for healed selectors."""

    def __init__(self, config: KernHellConfig) -> None:
        self.config = config
        self.cache_cfg = config.cache
        self.embedder = SemanticEmbedder(self.cache_cfg.embedding_model)

        # Resolve cache storage directory
        cache_path = os.path.expanduser(self.cache_cfg.cache_dir)
        self.storage_dir = Path(cache_path).resolve()
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.db_file = self.storage_dir / "semantic_index.json"
        self.stats_file = self.storage_dir / "stats.json"

        # In-memory storage: id -> (entry, vector)
        self._entries: dict[str, CacheEntry] = {}
        self._vectors: dict[str, list[float]] = {}
        self._stats = CacheStats()

        self._load()

    def _make_key(self, selector: str, context: str, page_url: str) -> str:
        """Create a deterministic hash for selector + intent context."""
        raw = f"{selector.strip()}|{context.strip()}|{page_url.strip()}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def lookup(
        self,
        broken_selector: str,
        context: str = "",
        page_url: str = "",
    ) -> tuple[Optional[SelectorFix], float]:
        """Look up a selector in semantic memory.

        Returns
        -------
        tuple[Optional[SelectorFix], float]
            (SelectorFix, similarity_score). If similarity < threshold or cache empty,
            returns (None, score).
        """
        if not self.cache_cfg.enabled or not self._entries:
            self._stats.misses += 1
            self._save_stats()
            return None, 0.0

        query_text = f"{broken_selector} | {context} | {page_url}"
        query_vec = self.embedder.embed(query_text)

        best_score = -1.0
        best_entry: Optional[CacheEntry] = None

        for entry_id, vec in self._vectors.items():
            score = cosine_similarity(query_vec, vec)
            if score > best_score:
                best_score = score
                best_entry = self._entries[entry_id]

        threshold = self.cache_cfg.similarity_threshold

        if best_entry is not None and best_score >= threshold:
            best_entry.hit_count += 1
            self._stats.hits += 1
            self._save()
            logger.info(
                "cache.hit",
                broken=broken_selector,
                healed=best_entry.new_selector,
                score=round(best_score, 4),
            )
            fix = SelectorFix(
                old_selector=best_entry.broken_selector,
                new_selector=best_entry.new_selector,
                strategy=best_entry.strategy,
                confidence=round(best_entry.confidence, 2),
                reasoning=f"Retrieved from Semantic Memory (similarity {best_score:.2f} >= {threshold:.2f}).",
                verified=True,
            )
            return fix, best_score

        self._stats.misses += 1
        self._save_stats()
        logger.debug(
            "cache.miss",
            broken=broken_selector,
            best_score=round(best_score, 4),
            threshold=threshold,
        )
        return None, best_score

    def store(
        self,
        broken_selector: str,
        fix: SelectorFix,
        context: str = "",
        page_url: str = "",
        test_file: str = "",
    ) -> CacheEntry:
        """Store a verified selector fix in semantic memory."""
        if not self.cache_cfg.enabled:
            return CacheEntry(
                id="disabled",
                broken_selector=broken_selector,
                new_selector=fix.new_selector,
                confidence=fix.confidence,
            )

        entry_id = self._make_key(broken_selector, context, page_url)
        entry_text = f"{broken_selector} | {context} | {page_url}"
        vec = self.embedder.embed(entry_text)

        entry = CacheEntry(
            id=entry_id,
            broken_selector=broken_selector,
            new_selector=fix.new_selector,
            strategy=fix.strategy,
            confidence=fix.confidence,
            context_snippet=context[:200] if context else "",
            page_url=page_url,
            test_file=test_file,
            verified=fix.verified,
        )

        self._entries[entry_id] = entry
        self._vectors[entry_id] = vec
        self._stats.total_entries = len(self._entries)
        self._save()

        logger.info(
            "cache.stored",
            broken=broken_selector,
            healed=fix.new_selector,
            total_entries=len(self._entries),
        )
        return entry

    def list_entries(self) -> list[CacheEntry]:
        """Return all stored entries in cache."""
        return list(self._entries.values())

    def clear(self) -> int:
        """Purge all entries from the vector cache."""
        count = len(self._entries)
        self._entries.clear()
        self._vectors.clear()
        self._stats = CacheStats()
        self._save()
        logger.info("cache.cleared", count=count)
        return count

    def get_stats(self) -> CacheStats:
        """Get cache performance metrics."""
        self._stats.total_entries = len(self._entries)
        return self._stats

    def _save(self) -> None:
        """Persist cache entries and vectors to disk."""
        data = {
            "entries": {k: v.model_dump(mode="json") for k, v in self._entries.items()},
            "vectors": self._vectors,
        }
        try:
            self.db_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
            self._save_stats()
        except Exception as exc:
            logger.warning("cache.save_failed", error=str(exc))

    def _save_stats(self) -> None:
        try:
            self.stats_file.write_text(
                self._stats.model_dump_json(indent=2), encoding="utf-8"
            )
        except Exception as exc:
            logger.debug("cache.save_stats_failed", error=str(exc))

    def _load(self) -> None:
        """Load persisted cache entries and vectors from disk."""
        if not self.db_file.is_file():
            return

        try:
            raw = self.db_file.read_text(encoding="utf-8")
            data = json.loads(raw)
            for k, entry_dict in data.get("entries", {}).items():
                self._entries[k] = CacheEntry.model_validate(entry_dict)
            self._vectors = data.get("vectors", {})
            self._stats.total_entries = len(self._entries)

            if self.stats_file.is_file():
                stats_raw = self.stats_file.read_text(encoding="utf-8")
                self._stats = CacheStats.model_validate_json(stats_raw)

            logger.info("cache.loaded", total_entries=len(self._entries))
        except Exception as exc:
            logger.warning("cache.load_failed", error=str(exc))
