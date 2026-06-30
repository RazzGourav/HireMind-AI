from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import orjson
from pydantic import ValidationError

from hiremind.domain import Candidate
from hiremind.infrastructure.serialization import CandidateRecord
from hiremind.infrastructure.storage.jsonl_loader import JsonlRecord
from hiremind.services.candidate_factory import (
    CandidateFactory,
    format_validation_errors,
)


@dataclass(frozen=True, slots=True)
class InvalidRecord:
    line_number: int
    errors: list[str]
    candidate_id: str | None = None
    raw: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "line_number": self.line_number,
            "candidate_id": self.candidate_id,
            "errors": self.errors,
            "raw": self.raw,
        }


@dataclass(frozen=True, slots=True)
class ValidationReport:
    total_records: int
    candidates: list[Candidate]
    invalid_records: list[InvalidRecord]
    duplicate_ids: list[str]

    @property
    def valid_count(self) -> int:
        return len(self.candidates)

    @property
    def invalid_count(self) -> int:
        return len(self.invalid_records)


@dataclass(frozen=True, slots=True)
class SchemaValidationResult:
    record: CandidateRecord | None
    errors: list[str]

    @property
    def is_valid(self) -> bool:
        return self.record is not None


class SchemaValidator:
    def __init__(self, schema_path: str | Path | None = None) -> None:
        self.schema_path = Path(schema_path) if schema_path else None
        self.schema = self._load_schema(self.schema_path)

    def validate(self, payload: dict[str, Any]) -> SchemaValidationResult:
        try:
            record = CandidateRecord.model_validate(payload)
        except ValidationError as exc:
            return SchemaValidationResult(record=None, errors=format_validation_errors(exc))
        return SchemaValidationResult(record=record, errors=[])

    @staticmethod
    def _load_schema(schema_path: Path | None) -> dict[str, Any] | None:
        if schema_path is None or not schema_path.exists():
            return None
        return orjson.loads(schema_path.read_bytes())


class ValidationService:
    def __init__(self, schema_validator: SchemaValidator | None = None) -> None:
        self.schema_validator = schema_validator or SchemaValidator()

    def validate_json_records(self, records: Iterable[JsonlRecord]) -> ValidationReport:
        total_records = 0
        candidates: list[Candidate] = []
        invalid_records: list[InvalidRecord] = []
        seen_ids: set[str] = set()
        duplicate_ids: list[str] = []

        for json_record in records:
            total_records += 1

            if json_record.error:
                invalid_records.append(
                    InvalidRecord(
                        line_number=json_record.line_number,
                        errors=[json_record.error],
                    )
                )
                continue

            if json_record.payload is None:
                invalid_records.append(
                    InvalidRecord(
                        line_number=json_record.line_number,
                        errors=["Missing JSON payload"],
                    )
                )
                continue

            result = self.schema_validator.validate(json_record.payload)
            if result.record is None:
                invalid_records.append(
                    InvalidRecord(
                        line_number=json_record.line_number,
                        candidate_id=_extract_candidate_id(json_record.payload),
                        errors=result.errors,
                        raw=json_record.payload,
                    )
                )
                continue

            if result.record.candidate_id in seen_ids:
                duplicate_ids.append(result.record.candidate_id)
                invalid_records.append(
                    InvalidRecord(
                        line_number=json_record.line_number,
                        candidate_id=result.record.candidate_id,
                        errors=[f"Duplicate candidate_id: {result.record.candidate_id}"],
                        raw=json_record.payload,
                    )
                )
                continue

            seen_ids.add(result.record.candidate_id)
            candidates.append(CandidateFactory.from_record(result.record))

        return ValidationReport(
            total_records=total_records,
            candidates=candidates,
            invalid_records=invalid_records,
            duplicate_ids=sorted(set(duplicate_ids)),
        )

    @staticmethod
    def missing_values(candidates: Iterable[Candidate]) -> dict[str, int]:
        missing: Counter[str] = Counter()
        for candidate in candidates:
            if candidate.profile.current_title in (None, ""):
                missing["profile.current_title"] += 1
            if candidate.profile.country in (None, ""):
                missing["profile.country"] += 1
            if candidate.profile.notice_period_days is None:
                missing["profile.notice_period_days"] += 1
            if candidate.signals.github_activity_score is None:
                missing["signals.github_activity_score"] += 1
            if candidate.signals.recruiter_response_score is None:
                missing["signals.recruiter_response_score"] += 1
            if not candidate.skills:
                missing["skills"] += 1
            if not candidate.education:
                missing["education"] += 1
            if not candidate.career_history:
                missing["career_history"] += 1
        return dict(sorted(missing.items()))

    @staticmethod
    def skill_inconsistencies(candidates: Iterable[Candidate]) -> dict[str, list[str]]:
        inconsistencies: dict[str, list[str]] = {}
        for candidate in candidates:
            normalized_names = [skill.name.casefold() for skill in candidate.skills]
            duplicated = sorted(
                skill_name for skill_name, count in Counter(normalized_names).items() if count > 1
            )
            if duplicated:
                inconsistencies[candidate.candidate_id] = duplicated
        return inconsistencies


def _extract_candidate_id(payload: dict[str, Any]) -> str | None:
    value = payload.get("candidate_id", payload.get("id"))
    return str(value) if value is not None else None
