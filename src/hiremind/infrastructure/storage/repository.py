from collections.abc import Iterator
from pathlib import Path

from hiremind.domain import Candidate
from hiremind.infrastructure.cache import FeatureCache
from hiremind.infrastructure.storage.jsonl_loader import JsonlLoader
from hiremind.services.validation_service import SchemaValidator, ValidationService


class CandidateRepository:
    def __init__(
        self,
        raw_path: str | Path = "data/raw/candidates.jsonl",
        cache_dir: str | Path = "feature_cache",
        schema_path: str | Path = "configs/candidate_schema.json",
    ) -> None:
        self.raw_path = Path(raw_path)
        self.cache = FeatureCache(cache_dir)
        self.schema_path = Path(schema_path)
        self._candidates = self._load_candidates()
        self._by_id = {candidate.candidate_id: candidate for candidate in self._candidates}

    @classmethod
    def from_candidates(cls, candidates: list[Candidate]) -> "CandidateRepository":
        repository = cls.__new__(cls)
        repository.raw_path = Path("data/raw/candidates.jsonl")
        repository.cache = FeatureCache()
        repository.schema_path = Path("configs/candidate_schema.json")
        repository._candidates = candidates
        repository._by_id = {candidate.candidate_id: candidate for candidate in candidates}
        return repository

    def get(self, candidate_id: str) -> Candidate | None:
        return self._by_id.get(candidate_id)

    def iter_all(self) -> Iterator[Candidate]:
        return iter(self._candidates)

    def total_count(self) -> int:
        return len(self._candidates)

    def _load_candidates(self) -> list[Candidate]:
        if self.cache.pickle_path.exists():
            return self.cache.load_pickle()

        if not self.raw_path.exists():
            return []

        validation_service = ValidationService(SchemaValidator(self.schema_path))
        report = validation_service.validate_json_records(JsonlLoader(self.raw_path).stream())
        return report.candidates
