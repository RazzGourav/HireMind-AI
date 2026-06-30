from pathlib import Path

from hiremind.infrastructure.storage import CandidateRepository


def test_candidate_repository_loads_jsonl_and_indexes_by_id(tmp_path: Path) -> None:
    raw_path = tmp_path / "candidates.jsonl"
    raw_path.write_text(
        '{"candidate_id": "CAND_001", "profile": {"current_title": "Engineer"}}\n'
        '{"candidate_id": "CAND_002", "signals": {"github_activity_score": 0.7}}\n',
        encoding="utf-8",
    )

    repository = CandidateRepository(raw_path=raw_path, cache_dir=tmp_path / "cache")

    assert repository.total_count() == 2
    assert repository.get("CAND_001") is not None
    assert repository.get("CAND_001").profile.current_title == "Engineer"  # type: ignore[union-attr]
    assert repository.get("missing") is None
    assert [candidate.candidate_id for candidate in repository.iter_all()] == [
        "CAND_001",
        "CAND_002",
    ]


def test_candidate_repository_excludes_duplicate_ids(tmp_path: Path) -> None:
    raw_path = tmp_path / "candidates.jsonl"
    raw_path.write_text(
        '{"candidate_id": "CAND_001"}\n'
        '{"candidate_id": "CAND_001", "profile": {"current_title": "Duplicate"}}\n',
        encoding="utf-8",
    )

    repository = CandidateRepository(raw_path=raw_path, cache_dir=tmp_path / "cache")

    assert repository.total_count() == 1
    assert repository.get("CAND_001") is not None
