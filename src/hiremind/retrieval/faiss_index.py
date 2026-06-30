"""FAISS Index Wrapper — CPU-based fast nearest-neighbor search."""

from pathlib import Path

import faiss
import numpy as np


class FaissIndex:
    """Wraps FAISS IndexFlatIP (or IndexHNSWFlat) for CPU vector search."""

    def __init__(self, dimension: int = 384) -> None:
        self.dimension = dimension
        self._index: faiss.IndexFlatIP | None = None

    def build(self, embeddings: np.ndarray) -> None:
        """Construct the FAISS IndexFlatIP index with normalized float32 embeddings."""
        assert (
            embeddings.shape[1] == self.dimension
        ), f"Embedding dim mismatch. Expected {self.dimension} got {embeddings.shape[1]}"
        # Ensure array is contiguous and float32 for FAISS
        arr = np.ascontiguousarray(embeddings, dtype=np.float32)

        # IndexFlatIP uses Inner Product (Cosine similarity when vectors are normalized)
        index = faiss.IndexFlatIP(self.dimension)
        index.add(arr)
        self._index = index

    def search(self, query_vector: np.ndarray, k: int = 2000) -> tuple[np.ndarray, np.ndarray]:
        """Perform nearest-neighbor search. Returns similarity distances and matched indices."""
        if self._index is None:
            raise ValueError("FAISS index has not been built or loaded yet.")

        # Reshape to 2D array [1, dimension] if query is flat 1D
        if len(query_vector.shape) == 1:
            query_vector = query_vector.reshape(1, -1)

        arr = np.ascontiguousarray(query_vector, dtype=np.float32)

        # FAISS search: returns distances (similarities) and indices
        distances, indices = self._index.search(arr, k)
        return distances[0], indices[0]

    def save(self, path: str | Path) -> None:
        """Serialize index to disk."""
        if self._index is None:
            raise ValueError("Cannot save empty FAISS index.")
        out_path = Path(path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self._index, str(out_path))

    def load(self, path: str | Path) -> None:
        """Deserialize index from disk."""
        in_path = Path(path)
        if not in_path.exists():
            raise FileNotFoundError(f"FAISS index file not found at {in_path}")
        self._index = faiss.read_index(str(in_path))
