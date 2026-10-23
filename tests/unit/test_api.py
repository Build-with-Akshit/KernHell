"""Unit tests for the KernHell FastAPI Mission Control API."""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from kernhell.api.server import create_app
from kernhell.core.config import KernHellConfig
from kernhell.core.models import (
    Diagnosis,
    FailureType,
    SelectorFix,
    SelectorStrategy,
)


@pytest.fixture
def client(tmp_path: Path):
    cfg = KernHellConfig()
    cfg.cache.cache_dir = str(tmp_path / "cache")
    app = create_app(cfg)
    return TestClient(app)


def test_health_endpoint(client: TestClient):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "KernHell" in data["app"]


def test_stats_endpoint(client: TestClient):
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_runs" in data
    assert "total_healed" in data
    assert "cache_efficiency_pct" in data
    assert "hours_saved" in data
    assert "dollars_saved" in data


def test_cache_endpoints(client: TestClient):
    # Listing cache should be empty list initially
    res = client.get("/api/cache")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

    # Clear cache
    clear_res = client.post("/api/cache/clear")
    assert clear_res.status_code == 200
    assert "cleared_count" in clear_res.json()


def test_history_endpoint(client: TestClient):
    res = client.get("/api/history")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_simulate_missing_guardrail(client: TestClient):
    """Test that simulate classifies out of stock as MISSING."""
    payload = {
        "broken_selector": ".add-to-cart-btn",
        "dom_html": (
            "<!DOCTYPE html><html><head><script>var x = 123;</script><style>.a{color:red}</style></head>"
            "<body><svg><path d='M0 0'/></svg><div class='alert'>Out of Stock - Sold out completely</div></body></html>"
        ),
        "surrounding_code": 'page.click(".add-to-cart-btn")',
    }

    # Patch analyzer to return MISSING
    with patch("kernhell.analyzer.analyzer.FailureAnalyzer.diagnose") as mock_diag:
        mock_diag.return_value = Diagnosis(
            failure_type=FailureType.MISSING,
            explanation="Element is absent due to out of stock",
            confidence=0.92,
        )

        res = client.post("/api/simulate", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["diagnosis"]["failure_type"] == "missing"
        assert data["healed_selector"] is None
        assert isinstance(data["compression_percent"], float)


def test_simulate_rename_flow(client: TestClient):
    """Test that simulate heals a renamed button."""
    dom = '<main><button type="submit" id="purchase-btn" data-testid="complete-order-btn">Place Order</button></main>'
    code = 'page.click("#buy-now")  # purchase action'

    with (
        patch("kernhell.analyzer.analyzer.FailureAnalyzer.diagnose") as mock_diag,
        patch("kernhell.analyzer.healer.SelectorHealer.suggest_fix") as mock_heal,
    ):
        mock_diag.return_value = Diagnosis(
            failure_type=FailureType.RENAME,
            explanation="Button ID changed from #buy-now to #purchase-btn",
            confidence=0.95,
        )
        mock_heal.return_value = SelectorFix(
            old_selector="#buy-now",
            new_selector="page.get_by_role('button', name='Place Order')",
            strategy=SelectorStrategy.ROLE_MATCH,
            confidence=0.95,
            reasoning="Accessible role match",
        )

        res = client.post(
            "/api/simulate",
            json={
                "broken_selector": "#buy-now",
                "dom_html": dom,
                "surrounding_code": code,
            },
        )
        assert res.status_code == 200
        data = res.json()
        assert data["diagnosis"]["failure_type"] == "rename"
        assert data["healed_selector"]["new_selector"] == "page.get_by_role('button', name='Place Order')"
        assert data["applied_diff"] is not None
        assert "-page.click(\"#buy-now\")" in data["applied_diff"]
        assert "+page.click(\"page.get_by_role('button', name='Place Order')\")" in data["applied_diff"]
