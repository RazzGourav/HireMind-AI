from pathlib import Path

from hiremind.infrastructure.cache import FeatureCache
from hiremind.services import CandidateFactory


def test_feature_cache_round_trips_pickle_and_parquet(tmp_path: Path) -> None:
    candidate = CandidateFactory.from_raw(
        {
            "candidate_id": "CAND_001",
            "profile": {"current_title": "Data Scientist"},
            "skills": [{"name": "Python"}],
        }
    )
    cache = FeatureCache(tmp_path / "feature_cache")

    cache.save_candidates([candidate])

    assert cache.load_pickle()[0].candidate_id == "CAND_001"
    assert cache.load_parquet()[0].profile.current_title == "Data Scientist"
