from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import orjson

from hiremind.infrastructure.storage import JsonlLoader
from hiremind.services.cache_service import CacheService
from hiremind.services.statistics_service import StatisticsService
from hiremind.services.validation_service import (
    SchemaValidator,
    ValidationReport,
    ValidationService,
)


@dataclass(frozen=True, slots=True)
class DatasetPreprocessResult:
    total_records: int
    valid_records: int
    invalid_records: int
    duplicate_ids: int
    statistics_path: Path
    quality_path: Path
    version_path: Path
    cache_pickle_path: Path
    cache_parquet_path: Path


class DatasetService:
    def __init__(
        self,
        raw_path: str | Path = "data/raw/candidates.jsonl",
        schema_path: str | Path = "configs/candidate_schema.json",
        output_dir: str | Path = "outputs",
        cache_dir: str | Path = "feature_cache",
        dataset_version: str = "1.0",
    ) -> None:
        self.raw_path = Path(raw_path)
        self.schema_path = Path(schema_path)
        self.output_dir = Path(output_dir)
        self.cache_dir = Path(cache_dir)
        self.dataset_version = dataset_version
        self.validation_service = ValidationService(SchemaValidator(self.schema_path))
        self.statistics_service = StatisticsService()
        self.cache_service = CacheService(self.cache_dir)

    def preprocess(self) -> DatasetPreprocessResult:
        report = self._validate_dataset()
        statistics = self.statistics_service.compute(report.candidates)
        quality_report = self._build_quality_report(report)
        pickle_path, parquet_path = self.cache_service.save_candidates(report.candidates)

        self.output_dir.mkdir(parents=True, exist_ok=True)
        statistics_path = self._write_json("statistics.json", statistics)
        quality_path = self._write_json("data_quality.json", quality_report)
        version_path = self._write_json("dataset_version.json", self._build_version(report))

        return DatasetPreprocessResult(
            total_records=report.total_records,
            valid_records=report.valid_count,
            invalid_records=report.invalid_count,
            duplicate_ids=len(report.duplicate_ids),
            statistics_path=statistics_path,
            quality_path=quality_path,
            version_path=version_path,
            cache_pickle_path=pickle_path,
            cache_parquet_path=parquet_path,
        )

    def _validate_dataset(self) -> ValidationReport:
        if not self.raw_path.exists():
            return ValidationReport(
                total_records=0,
                candidates=[],
                invalid_records=[],
                duplicate_ids=[],
            )

        loader = JsonlLoader(self.raw_path)
        return self.validation_service.validate_json_records(loader.stream())

    def _build_quality_report(self, report: ValidationReport) -> dict[str, object]:
        return {
            "total_records": report.total_records,
            "valid_records": report.valid_count,
            "invalid_records_count": report.invalid_count,
            "duplicate_ids": report.duplicate_ids,
            "missing_values": self.validation_service.missing_values(report.candidates),
            "skill_inconsistencies": self.validation_service.skill_inconsistencies(
                report.candidates
            ),
            "invalid_records": [record.to_dict() for record in report.invalid_records],
        }

    def _build_version(self, report: ValidationReport) -> dict[str, object]:
        return {
            "dataset": {
                "version": self.dataset_version,
                "records": report.valid_count,
                "created": datetime.now(UTC).isoformat(),
                "checksum": self._checksum(),
            }
        }

    def _write_json(self, filename: str, payload: dict[str, object]) -> Path:
        path = self.output_dir / filename
        path.write_bytes(orjson.dumps(payload, option=orjson.OPT_INDENT_2))
        return path

    def _checksum(self) -> str | None:
        if not self.raw_path.exists():
            return None

        import hashlib

        digest = hashlib.sha256()
        with self.raw_path.open("rb") as file:
            for chunk in iter(lambda: file.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
