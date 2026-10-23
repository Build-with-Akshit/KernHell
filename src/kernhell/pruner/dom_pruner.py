"""DOM Pruner — strips noise from raw HTML for LLM consumption.

The live DOM captured by Playwright is typically 200–500 KB of raw HTML.
Sending all of that to an LLM is wasteful, slow, and often exceeds context
limits.  The pruner retains only **semantically meaningful** elements and
attributes, cutting token usage by 80–90%.

**What we keep:**
  - Interactive elements: ``<button>``, ``<a>``, ``<input>``, ``<select>``,
    ``<textarea>``, ``<form>``, ``<label>``
  - Semantic landmarks: ``<header>``, ``<nav>``, ``<main>``, ``<footer>``,
    ``<section>``, ``<article>``, ``<aside>``
  - Content elements: ``<h1>``–``<h6>``, ``<p>``, ``<li>``, ``<td>``, ``<th>``
  - Important attributes: ``id``, ``class``, ``role``, ``aria-*``,
    ``data-testid``, ``data-test``, ``name``, ``type``, ``href``, ``value``,
    ``placeholder``, ``title``, ``alt``
  - Visible text content (trimmed)

**What we strip:**
  - ``<script>``, ``<style>``, ``<svg>``, ``<noscript>``, ``<link>``, ``<meta>``
  - Inline ``style`` attributes
  - ``data:`` URIs and base64 content
  - Empty/whitespace-only text nodes
  - Deeply nested non-semantic ``<div>``/``<span>`` wrappers (flattened)
"""

from __future__ import annotations

import re

import structlog
from selectolax.lexbor import LexborHTMLParser, LexborNode

from kernhell.core.models import PrunedDOM

logger = structlog.get_logger()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Tags to remove entirely (including children)
_STRIP_TAGS: frozenset[str] = frozenset({
    "script", "style", "svg", "noscript", "link", "meta",
    "iframe", "object", "embed", "template", "picture",
})

# Tags whose children we keep but the tag itself may be meaningful
_SEMANTIC_TAGS: frozenset[str] = frozenset({
    # Interactive
    "button", "a", "input", "select", "textarea", "form", "label", "option",
    # Landmarks
    "header", "nav", "main", "footer", "section", "article", "aside", "dialog",
    # Content
    "h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "ul", "ol",
    "table", "thead", "tbody", "tr", "td", "th",
    "img", "figure", "figcaption", "details", "summary",
    # Structure (kept when they have semantic attributes)
    "div", "span",
})

# Attributes worth preserving
_KEEP_ATTRS: frozenset[str] = frozenset({
    "id", "class", "role", "name", "type", "href", "value",
    "placeholder", "title", "alt", "for", "action", "method",
    "data-testid", "data-test", "data-cy",
})

# Prefix-based attribute preservation (aria-*)
_KEEP_ATTR_PREFIXES: tuple[str, ...] = ("aria-", "data-testid", "data-test", "data-cy")

# Regex for base64 / data URIs
_DATA_URI_PATTERN = re.compile(r"data:[^;]+;base64,[A-Za-z0-9+/=]+")

# Maximum text length to keep per element
_MAX_TEXT_LENGTH = 120


# ---------------------------------------------------------------------------
# Pruner Implementation
# ---------------------------------------------------------------------------


def _should_keep_attr(name: str) -> bool:
    """Determine if an HTML attribute should be preserved."""
    if name in _KEEP_ATTRS:
        return True
    return any(name.startswith(prefix) for prefix in _KEEP_ATTR_PREFIXES)


def _clean_attr_value(value: str) -> str:
    """Clean an attribute value — strip data URIs, excessive whitespace."""
    if not value:
        return value
    # Remove base64 data URIs
    value = _DATA_URI_PATTERN.sub("[data-uri]", value)
    # Collapse whitespace
    value = " ".join(value.split())
    # Truncate extremely long values (e.g. inline SVG paths)
    if len(value) > 200:
        value = value[:200] + "…"
    return value


def _has_semantic_value(node: LexborNode) -> bool:
    """Check if a div/span has attributes that make it semantically meaningful.

    Naked ``<div>`` and ``<span>`` wrappers with no id, class, role, or
    aria attributes are noise — we flatten them (keep children, drop the tag).
    """
    if node.tag in ("div", "span"):
        attrs = node.attributes
        if not attrs:
            return False
        return any(_should_keep_attr(name) for name in attrs)
    return True


def _prune_node(node: LexborNode) -> str:
    """Recursively prune a DOM node, returning cleaned HTML."""
    tag = node.tag

    # Skip stripped tags entirely
    if tag and tag.lower() in _STRIP_TAGS:
        return ""

    # Handle text nodes
    if tag is None or tag == "-text":
        text = (node.text(deep=False) or "").strip()
        if not text:
            return ""
        # Truncate long text
        if len(text) > _MAX_TEXT_LENGTH:
            text = text[:_MAX_TEXT_LENGTH] + "…"
        return text

    # For non-semantic div/span: flatten (emit children only)
    if tag.lower() in ("div", "span") and not _has_semantic_value(node):
        children_html = ""
        child = node.child
        while child is not None:
            children_html += _prune_node(child)
            child = child.next
        return children_html

    # Build the pruned tag with only meaningful attributes
    attrs_str = ""
    raw_attrs = node.attributes
    if raw_attrs:
        kept_attrs: list[str] = []
        for name, value in raw_attrs.items():
            if _should_keep_attr(name):
                clean_value = _clean_attr_value(value or "")
                if name == "style":
                    continue  # Always strip inline styles
                kept_attrs.append(f'{name}="{clean_value}"')
        if kept_attrs:
            attrs_str = " " + " ".join(kept_attrs)

    # Recurse into children
    children_html = ""
    child = node.child
    while child is not None:
        children_html += _prune_node(child)
        child = child.next

    # Self-closing tags
    if tag.lower() in ("input", "img", "br", "hr"):
        return f"<{tag}{attrs_str}/>"

    # Get direct text content
    text = (node.text(deep=False) or "").strip()
    if text and len(text) > _MAX_TEXT_LENGTH:
        text = text[:_MAX_TEXT_LENGTH] + "…"

    inner = text + children_html
    if not inner.strip() and tag.lower() not in _SEMANTIC_TAGS:
        return ""

    return f"<{tag}{attrs_str}>{inner}</{tag}>"


def prune_dom(raw_html: str) -> PrunedDOM:
    """Prune raw HTML to a semantic skeleton for LLM consumption.

    Parameters
    ----------
    raw_html:
        The full ``page.content()`` HTML captured by Playwright.

    Returns
    -------
    PrunedDOM
        The pruned HTML along with size reduction metrics.

    Examples
    --------
    >>> result = prune_dom("<html><body><script>...</script><button id='buy'>Buy</button></body></html>")
    >>> "script" not in result.html
    True
    >>> "buy" in result.html.lower()
    True
    """
    original_size = len(raw_html.encode("utf-8"))
    logger.debug("pruner.start", original_size=original_size)

    if not raw_html.strip():
        return PrunedDOM(html="", original_size=0, pruned_size=0)

    parser = LexborHTMLParser(raw_html)
    body = parser.body

    if body is None:
        # Fallback: try the root
        body = parser.root
        if body is None:
            logger.warning("pruner.no_body")
            return PrunedDOM(html="", original_size=original_size, pruned_size=0)

    pruned_html = _prune_node(body)

    # Clean up excessive whitespace and empty lines in the result
    pruned_html = re.sub(r"\n{3,}", "\n\n", pruned_html)
    pruned_html = pruned_html.strip()

    pruned_size = len(pruned_html.encode("utf-8"))

    result = PrunedDOM(
        html=pruned_html,
        original_size=original_size,
        pruned_size=pruned_size,
    )

    logger.info(
        "pruner.done",
        original_size=original_size,
        pruned_size=pruned_size,
        reduction_pct=result.reduction_pct,
    )
    return result
