"""Unit tests for the FaissIndex wrapper."""

from pathlib import Path

import numpy as np

from hiremind.retrieval.faiss_index import FaissIndex


def test_faiss_index_build_and_search() -> None:
    dimension = 128
    faiss_idx = FaissIndex(dimension=dimension)

    # 10 random vectors
    embeddings = np.random.rand(10, dimension).astype(np.float32)
    # L2 normalize them so inner product behaves like cosine similarity
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    embeddings = embeddings / norms

    # Build
    faiss_idx.build(embeddings)

    # Search with the first vector as query (should match index 0 with score close to 1.0)
    query = embeddings[0]
    distances, indices = faiss_idx.search(query, k=3)

    assert indices[0] == 0
    assert abs(distances[0] - 1.0) < 1e-4


def test_faiss_index_save_and_load(tmp_path: Path) -> None:
    dimension = 64
    faiss_idx = FaissIndex(dimension=dimension)
    embeddings = np.random.rand(5, dimension).astype(np.float32)
    faiss_idx.build(embeddings)

    path = tmp_path / "index.bin"
    faiss_idx.save(path)
    assert path.exists()

    new_idx = FaissIndex(dimension=dimension)
    new_idx.load(path)

    query = embeddings[1]
    distances, indices = new_idx.search(query, k=1)
    assert indices[0] == 1
