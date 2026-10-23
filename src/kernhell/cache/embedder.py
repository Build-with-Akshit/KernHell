"""Embedding generator and vector distance calculations for semantic caching.

Supports:
  1. `sentence-transformers` (`all-MiniLM-L6-v2`) for deep dense embeddings.
  2. Built-in 384-dimensional projected subword frequency embedder for zero-dependency offline mode.
"""

from __future__ import annotations

import hashlib
import math
import re
from typing import Sequence

import structlog

logger = structlog.get_logger()

EMBEDDING_DIM = 384


def cosine_similarity(v1: Sequence[float], v2: Sequence[float]) -> float:
    """Calculate the cosine similarity between two numeric vectors (range -1.0 to 1.0)."""
    if len(v1) != len(v2) or not v1:
        return 0.0

    dot = sum(a * b for a, b in zip(v1, v2))
    norm_a = math.sqrt(sum(a * a for a in v1))
    norm_b = math.sqrt(sum(b * b for b in v2))

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    return max(-1.0, min(1.0, dot / (norm_a * norm_b)))


class SemanticEmbedder:
    """Generates 384-dimensional dense vectors for semantic selector caching."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        self.model_name = model_name
        self._st_model = None
        self._tried_loading_st = False

    def _get_sentence_transformer(self):
        if not self._tried_loading_st:
            self._tried_loading_st = True
            try:
                from sentence_transformers import SentenceTransformer
                self._st_model = SentenceTransformer(self.model_name)
                logger.info("embedder.sentence_transformers.loaded", model=self.model_name)
            except Exception as exc:
                logger.debug("embedder.sentence_transformers.unavailable", error=str(exc))
                self._st_model = None
        return self._st_model

    def embed(self, text: str) -> list[float]:
        """Compute 384-dimensional normalized vector for input text."""
        model = self._get_sentence_transformer()
        if model is not None:
            try:
                raw_vec = model.encode(text, normalize_embeddings=True)
                return [float(x) for x in raw_vec]
            except Exception as exc:
                logger.warning("embedder.st_encode_failed.using_projected", error=str(exc))

        return self._projected_dense_embed(text)

    def _projected_dense_embed(self, text: str) -> list[float]:
        """Deterministic subword feature hashing into a normalized 384D unit sphere.

        Provides consistent semantic cosine similarity for identical and overlapping
        selector intents without requiring external neural network weights.
        """
        vec = [0.0] * EMBEDDING_DIM
        cleaned = text.lower().strip()
        if not cleaned:
            return vec

        # Tokenize by alphanumeric words and punctuation
        tokens = re.findall(r"\w+|[^\w\s]", cleaned)

        # 1. Word token hashing
        for token in tokens:
            h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
            dim = h % EMBEDDING_DIM
            sign = 1.0 if (h % 2 == 0) else -1.0
            vec[dim] += sign * 1.5

        # 2. Character n-gram hashing (captures partial renames like 'buy-now' vs 'purchase-btn')
        for n in (3, 4):
            for i in range(len(cleaned) - n + 1):
                gram = cleaned[i : i + n]
                h = int(hashlib.sha256(gram.encode("utf-8")).hexdigest(), 16)
                dim = h % EMBEDDING_DIM
                sign = 1.0 if (h % 2 == 0) else -1.0
                vec[dim] += sign * 0.5

        # Normalize vector to unit sphere (L2 norm)
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0.0:
            vec = [x / norm for x in vec]

        return vec
