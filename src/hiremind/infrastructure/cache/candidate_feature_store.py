"""Candidate Feature Store — Parquet persistence for candidate intelligence."""

import pickle
from pathlib import Path

import pandas as pd

from hiremind.domain.candidate_features import CandidateFeatures


class CandidateFeatureStore:
    """Save and load candidate feature vectors as Parquet files.

    Produces:
        - ``candidate_features.parquet`` — flat feature vectors for ranking
        - ``candidate_summary.pkl`` — full CandidateFeatures list with graphs
    """

    def __init__(self, artifacts_dir: str | Path = "artifacts") -> None:
        self._dir = Path(artifacts_dir)
        self._dir.mkdir(parents=True, exist_ok=True)

    @property
    def parquet_path(self) -> Path:
        return self._dir / "candidate_features.parquet"

    @property
    def summary_path(self) -> Path:
        return self._dir / "candidate_summary.pkl"

    def save_features(self, features: list[CandidateFeatures]) -> Path:
        """Save feature vectors as Parquet."""
        rows: list[dict[str, object]] = []
        for feat in features:
            row: dict[str, object] = {"candidate_id": feat.candidate_id}
            row.update(feat.feature_vector)
            rows.append(row)

        df = pd.DataFrame(rows)
        df.to_parquet(self.parquet_path, index=False)
        return self.parquet_path

    def load_features(self) -> pd.DataFrame:
        """Load feature vectors from Parquet."""
        return pd.read_parquet(self.parquet_path)

    def save_summaries(self, features: list[CandidateFeatures]) -> Path:
        """Pickle the full CandidateFeatures list for downstream use."""
        with self.summary_path.open("wb") as f:
            pickle.dump(features, f, protocol=pickle.HIGHEST_PROTOCOL)
        return self.summary_path

    def load_summaries(self) -> list[CandidateFeatures]:
        """Load CandidateFeatures from pickle."""
        with self.summary_path.open("rb") as f:
            return pickle.load(f)  # noqa: S301
