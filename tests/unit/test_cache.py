"""Unit tests for the CacheManager and persistent vector memory."""

from __future__ import annotations

from pathlib import Path

from kernhell.cache.cache_manager import CacheManager
from kernhell.core.config import KernHellConfig
from kernhell.core.models import SelectorFix, SelectorStrategy


def test_cache_miss_on_empty(tmp_path: Path) -> None:
    cfg = KernHellConfig()
    cfg.cache.cache_dir = str(tmp_path)
    mgr = CacheManager(cfg)

    fix, score = mgr.lookup("#buy-now", "click order", "https://example.com")
    assert fix is None
    stats = mgr.get_stats()
    assert stats.misses == 1
    assert stats.hits == 0


def test_cache_store_and_hit(tmp_path: Path) -> None:
    cfg = KernHellConfig()
    cfg.cache.cache_dir = str(tmp_path)
    cfg.cache.similarity_threshold = 0.90
    mgr = CacheManager(cfg)

    sample_fix = SelectorFix(
        old_selector="#buy-now",
        new_selector="#purchase-btn",
        strategy=SelectorStrategy.CSS_FALLBACK,
        confidence=0.95,
        verified=True,
    )

    # Store entry
    mgr.store(
        broken_selector="#buy-now",
        fix=sample_fix,
        context="page.click('#buy-now')",
        page_url="https://example.com/checkout",
        test_file="tests/test_checkout.py",
    )

    # Lookup identical query
    cached_fix, score = mgr.lookup(
        broken_selector="#buy-now",
        context="page.click('#buy-now')",
        page_url="https://example.com/checkout",
    )

    assert cached_fix is not None
    assert cached_fix.new_selector == "#purchase-btn"
    assert cached_fix.verified is True
    assert score >= 0.90

    stats = mgr.get_stats()
    assert stats.hits == 1
    assert stats.total_entries == 1
    assert stats.hit_ratio == 100.0


def test_cache_disk_persistence(tmp_path: Path) -> None:
    cfg = KernHellConfig()
    cfg.cache.cache_dir = str(tmp_path)
    mgr1 = CacheManager(cfg)

    fix = SelectorFix(
        old_selector="#cart-btn",
        new_selector="#shopping-cart",
        strategy=SelectorStrategy.ROLE_MATCH,
        confidence=0.92,
        verified=True,
    )
    mgr1.store(broken_selector="#cart-btn", fix=fix)

    # Instantiate new CacheManager pointing to same directory
    mgr2 = CacheManager(cfg)
    assert len(mgr2.list_entries()) == 1

    loaded_fix, score = mgr2.lookup("#cart-btn")
    assert loaded_fix is not None
    assert loaded_fix.new_selector == "#shopping-cart"


def test_cache_clear(tmp_path: Path) -> None:
    cfg = KernHellConfig()
    cfg.cache.cache_dir = str(tmp_path)
    mgr = CacheManager(cfg)

    fix = SelectorFix(
        old_selector="#old",
        new_selector="#new",
        confidence=0.9,
        verified=True,
    )
    mgr.store("#old", fix)
    assert len(mgr.list_entries()) == 1

    cleared = mgr.clear()
    assert cleared == 1
    assert len(mgr.list_entries()) == 0
    assert mgr.get_stats().total_entries == 0
