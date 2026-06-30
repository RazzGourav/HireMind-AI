from collections.abc import Iterable
from pathlib import Path

from hiremind.domain import Candidate
from hiremind.infrastructure.cache import FeatureCache


class ParquetStore:
    def __init__(self, cache_dir: str | Path = "feature_cache") -> None:
        self.cache = FeatureCache(cache_dir)

    def write_candidates(self, candidates: Iterable[Candidate]) -> Path:
        return self.cache.save_parquet(list(candidates))

    def read_candidates(self) -> list[Candidate]:
        return self.cache.load_parquet()
