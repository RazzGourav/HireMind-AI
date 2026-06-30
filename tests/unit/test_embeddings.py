"""Unit tests for DenseEmbeddingEncoder, CandidateEncoder, QueryEncoder and EmbeddingCache."""

from pathlib import Path

import numpy as np
import pytest

from hiremind.domain.candidate import Candidate, RedrobSignals
from hiremind.domain.profile import Profile
from hiremind.retrieval.candidate_encoder import CandidateEncoder
from hiremind.retrieval.embedding_cache import EmbeddingCache
from hiremind.retrieval.embedding_encoder import DenseEmbeddingEncoder
from hiremind.retrieval.query_encoder import QueryEncoder


@pytest.fixture(scope="module")
def encoder() -> DenseEmbeddingEncoder:
    return DenseEmbeddingEncoder(model_name="all-MiniLM-L6-v2")


def test_embedding_encoder_output(encoder: DenseEmbeddingEncoder) -> None:
    text = "Machine learning engineer with Python expertise"
    emb = encoder.encode(text)

    assert isinstance(emb, np.ndarray)
    assert emb.shape == (384,)
    # Verify embeddings are normalized (L2 norm is approximately 1.0)
    norm = np.linalg.norm(emb)
    assert abs(norm - 1.0) < 1e-3


def test_candidate_encoder_formatting(encoder: DenseEmbeddingEncoder) -> None:
    cand_encoder = CandidateEncoder(encoder)
    cand = Candidate(
        candidate_id="CAND_001",
        profile=Profile(
            headline="AI Engineer", current_title="AI Engineer", summary="Expert in ML"
        ),
        career_history=[],
        education=[],
        skills=[],
        signals=RedrobSignals(),
    )
    formatted = cand_encoder.format_candidate(cand)

    assert "AI Engineer" in formatted
    assert "Expert in ML" in formatted


def test_query_encoder_formatting(encoder: DenseEmbeddingEncoder) -> None:
    class MockJD:
        raw_text = "Job"
        cleaned_text = "Job"
        source_path = "job_desc.docx"
        title = "AI Team Lead"
        summary = "Looking for Python ML developer"
        responsibilities = ["Build production systems"]
        requirements = None

    q_encoder = QueryEncoder(encoder)
    jd = MockJD()

    formatted = q_encoder.format_jd(jd)  # type: ignore
    assert "AI Team Lead" in formatted
    assert "Python ML developer" in formatted
    assert "Build production systems" in formatted


def test_embedding_cache_roundtrip(tmp_path: Path) -> None:
    cache = EmbeddingCache(cache_dir=tmp_path)
    ids = ["CAND_1", "CAND_2"]
    embs = np.random.rand(2, 384).astype(np.float32)

    # Save candidates
    cache.save_candidates(ids, embs)
    assert cache.candidate_parquet_path.exists()

    # Load candidates
    loaded_ids, loaded_embs = cache.load_candidates()
    assert loaded_ids == ids
    assert loaded_embs.shape == (2, 384)
    # Check that they match within floating point precision
    assert np.allclose(loaded_embs[0], embs[0], atol=1e-5)
