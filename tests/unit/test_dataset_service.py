import json
from pathlib import Path

from hiremind.services.dataset_service import DatasetService


def test_dataset_service_writes_statistics_quality_cache_and_version(tmp_path: Path) -> None:
    raw_path = tmp_path / "candidates.jsonl"
    output_dir = tmp_path / "outputs"
    cache_dir = tmp_path / "feature_cache"
    raw_path.write_text(
        '{"candidate_id": "CAND_001", '
        '"profile": {"country": "India", "total_experience_months": 60}, '
        '"skills": [{"name": "Python"}], '
        '"signals": {"github_activity_score": 0.8, "has_github": true}}\n'
        '{"candidate_id": "CAND_001"}\n'
        '{"candidate_id": "CAND_BAD", "profile": {"total_experience_months": -4}}\n',
        encoding="utf-8",
    )

    result = DatasetService(
        raw_path=raw_path,
        output_dir=output_dir,
        cache_dir=cache_dir,
    ).preprocess()

    statistics = json.loads(result.statistics_path.read_text(encoding="utf-8"))
    quality = json.loads(result.quality_path.read_text(encoding="utf-8"))
    version = json.loads(result.version_path.read_text(encoding="utf-8"))

    assert result.valid_records == 1
    assert result.invalid_records == 2
    assert result.duplicate_ids == 1
    assert statistics["total_candidates"] == 1
    assert quality["duplicate_ids"] == ["CAND_001"]
    assert version["dataset"]["records"] == 1
    assert result.cache_pickle_path.exists()
    assert result.cache_parquet_path.exists()
