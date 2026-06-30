from collections.abc import Iterable
from pathlib import Path

from hiremind.domain import Candidate
from hiremind.infrastructure.cache import FeatureCache


class CacheService:
    def __init__(self, cache_dir: str | Path = "feature_cache") -> None:
        self.feature_cache = FeatureCache(cache_dir)

    def save_candidates(self, candidates: Iterable[Candidate]) -> tuple[Path, Path]:
        candidate_list = list(candidates)
        pickle_path = self.feature_cache.save_pickle(candidate_list)
        parquet_path = self.feature_cache.save_parquet(candidate_list)
        return pickle_path, parquet_path

    def load_candidates(self) -> list[Candidate]:
        return self.feature_cache.load_pickle()
