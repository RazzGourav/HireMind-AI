"""Embedding Cache — handles saving and loading precomputed embeddings to Parquet/Pickle."""

import pickle
from pathlib import Path

import numpy as np
import pandas as pd


class EmbeddingCache:
    """Manages file persistence for candidate and query dense embeddings."""

    def __init__(self, cache_dir: str | Path = "artifacts/embeddings") -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    @property
    def candidate_parquet_path(self) -> Path:
        return self.cache_dir / "candidate_embeddings.parquet"

    @property
    def query_pickle_path(self) -> Path:
        return self.cache_dir / "query_embedding.pkl"

    def save_candidates(self, ids: list[str], embeddings: np.ndarray) -> Path:
        """Save candidate IDs and their embeddings to a Parquet file."""
        assert len(ids) == len(embeddings), "Mismatch between IDs and embeddings length."
        # Flatten matrix into list of floats for parquet row representation
        rows = []
        for cid, emb in zip(ids, embeddings):
            row = {"candidate_id": cid}
            # Store values in a structured flat dictionary format
            for idx, val in enumerate(emb):
                row[f"v_{idx}"] = float(val)
            rows.append(row)

        df = pd.DataFrame(rows)
        df.to_parquet(self.candidate_parquet_path, index=False)
        return self.candidate_parquet_path

    def load_candidates(self) -> tuple[list[str], np.ndarray]:
        """Load candidate IDs and their embeddings from the Parquet file."""
        if not self.candidate_parquet_path.exists():
            raise FileNotFoundError(
                f"Candidate embeddings cache not found at {self.candidate_parquet_path}"
            )

        df = pd.read_parquet(self.candidate_parquet_path)
        ids = df["candidate_id"].tolist()

        # Reconstruct embedding matrix from v_ columns
        v_cols = sorted(
            [col for col in df.columns if col.startswith("v_")], key=lambda x: int(x.split("_")[1])
        )
        embeddings = df[v_cols].to_numpy(dtype=np.float32)

        return ids, embeddings

    def save_query(self, query_vector: np.ndarray) -> Path:
        """Cache query vector to pickle."""
        with self.query_pickle_path.open("wb") as f:
            pickle.dump(query_vector, f, protocol=pickle.HIGHEST_PROTOCOL)
        return self.query_pickle_path

    def load_query(self) -> np.ndarray:
        """Load query vector from pickle."""
        with self.query_pickle_path.open("rb") as f:
            return pickle.load(f)  # noqa: S301
