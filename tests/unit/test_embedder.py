"""Unit tests for the SemanticEmbedder and vector operations."""

from __future__ import annotations

import math

from kernhell.cache.embedder import EMBEDDING_DIM, SemanticEmbedder, cosine_similarity


def test_cosine_similarity() -> None:
    # Identical vectors
    v1 = [1.0, 0.0, 0.0]
    v2 = [1.0, 0.0, 0.0]
    assert math.isclose(cosine_similarity(v1, v2), 1.0, rel_tol=1e-5)

    # Orthogonal vectors
    v3 = [0.0, 1.0, 0.0]
    assert math.isclose(cosine_similarity(v1, v3), 0.0, abs_tol=1e-5)

    # Opposite vectors
    v4 = [-1.0, 0.0, 0.0]
    assert math.isclose(cosine_similarity(v1, v4), -1.0, rel_tol=1e-5)

    # Empty or zero vectors
    assert cosine_similarity([], []) == 0.0
    assert cosine_similarity([0.0, 0.0], [1.0, 1.0]) == 0.0


def test_embed_dimension_and_normalization() -> None:
    embedder = SemanticEmbedder()
    vec = embedder.embed("#buy-now | click purchase | https://example.com/checkout")

    # Correct dimension
    assert len(vec) == EMBEDDING_DIM

    # Normalized to unit length (L2 norm ~ 1.0)
    norm = math.sqrt(sum(x * x for x in vec))
    assert math.isclose(norm, 1.0, rel_tol=1e-4)


def test_semantic_similarity_ranking() -> None:
    embedder = SemanticEmbedder()

    vec_base = embedder.embed("#buy-now button checkout")
    vec_similar = embedder.embed("#buy-now button checkout")
    vec_different = embedder.embed(".footer-copyright-links")

    score_similar = cosine_similarity(vec_base, vec_similar)
    score_different = cosine_similarity(vec_base, vec_different)

    assert score_similar > score_different
    assert math.isclose(score_similar, 1.0, rel_tol=1e-4)
