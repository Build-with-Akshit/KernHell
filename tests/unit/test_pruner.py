"""Unit tests for the DOMPruner engine."""

from __future__ import annotations

from kernhell.pruner.dom_pruner import prune_dom


def test_prune_dom_strips_scripts_and_styles(sample_dom_html: str) -> None:
    pruned = prune_dom(sample_dom_html)

    assert "<script" not in pruned.html
    assert "console.log" not in pruned.html
    assert "<style" not in pruned.html
    assert "hidden-tracker" not in pruned.html


def test_prune_dom_strips_svg_and_data_uris(sample_dom_html: str) -> None:
    pruned = prune_dom(sample_dom_html)

    assert "<svg" not in pruned.html
    assert "data:image/png;base64" not in pruned.html
    assert "[data-uri]" in pruned.html or "base64" not in pruned.html


def test_prune_dom_preserves_interactive_and_semantic_elements(sample_dom_html: str) -> None:
    pruned = prune_dom(sample_dom_html)

    # Core interactive elements preserved
    assert "<button" in pruned.html
    assert 'id="buy-now"' in pruned.html
    assert 'type="submit"' in pruned.html
    assert 'role="button"' in pruned.html
    assert "Place Your Order" in pruned.html

    # Form inputs preserved
    assert "<input" in pruned.html
    assert 'id="email-input"' in pruned.html
    assert 'placeholder="you@domain.com"' in pruned.html

    # Navigation and links
    assert "<nav" in pruned.html
    assert 'href="/products"' in pruned.html


def test_prune_dom_achieves_size_reduction(sample_dom_html: str) -> None:
    pruned = prune_dom(sample_dom_html)

    assert pruned.original_size > 0
    assert pruned.pruned_size < pruned.original_size
    # Must achieve significant size reduction
    assert pruned.reduction_pct >= 40.0


def test_prune_dom_empty_and_whitespace() -> None:
    pruned_empty = prune_dom("")
    assert pruned_empty.html == ""
    assert pruned_empty.original_size == 0
    assert pruned_empty.reduction_pct == 0.0

    pruned_ws = prune_dom("   \n\t  ")
    assert pruned_ws.html == ""


def test_prune_dom_flattens_empty_nested_divs() -> None:
    html = """
    <html><body>
        <div><div><div>
            <button id="flat-btn">Click Me</button>
        </div></div></div>
    </body></html>
    """
    pruned = prune_dom(html)
    assert 'id="flat-btn"' in pruned.html
    assert "Click Me" in pruned.html
    # Deeply nested empty divs should be flattened
    assert pruned.html.count("<div") == 0
