"""Unit tests for the ScoreCalibrator."""

from hiremind.ranking.calibration import ScoreCalibrator


def test_score_calibration() -> None:
    calibrator = ScoreCalibrator()

    assert calibrator.calibrate_score(0.85432) == 85.43
    assert calibrator.calibrate_score(1.2) == 100.0
    assert calibrator.calibrate_score(-0.1) == 0.0


def test_deterministic_sorting_and_tie_breaking() -> None:
    calibrator = ScoreCalibrator()

    records = [
        # Same scores, different IDs
        {
            "candidate_id": "CAND_B",
            "final_score": 0.85,
            "technical_score": 0.9,
            "behavior_score": 0.8,
        },
        {
            "candidate_id": "CAND_A",
            "final_score": 0.85,
            "technical_score": 0.9,
            "behavior_score": 0.8,
        },
        # Higher score
        {
            "candidate_id": "CAND_C",
            "final_score": 0.90,
            "technical_score": 0.8,
            "behavior_score": 0.7,
        },
        # Same final score, higher technical score (tie-breaker 1)
        {
            "candidate_id": "CAND_D",
            "final_score": 0.85,
            "technical_score": 0.95,
            "behavior_score": 0.8,
        },
        # Same final + tech, higher behavior (tie-breaker 2)
        {
            "candidate_id": "CAND_E",
            "final_score": 0.85,
            "technical_score": 0.9,
            "behavior_score": 0.85,
        },
    ]

    ranked = calibrator.rank_candidates(records)

    # Expected order:
    # 1. CAND_C (final: 90.0)
    # 2. CAND_D (final: 85.0, tech: 95.0)
    # 3. CAND_E (final: 85.0, tech: 90.0, behavior: 85.0)
    # 4. CAND_A (final: 85.0, tech: 90.0, behavior: 80.0, ID ascending -> CAND_A sorts before CAND_B)
    # 5. CAND_B (final: 85.0, tech: 90.0, behavior: 80.0)

    assert ranked[0]["candidate_id"] == "CAND_C"
    assert ranked[1]["candidate_id"] == "CAND_D"
    assert ranked[2]["candidate_id"] == "CAND_E"
    assert ranked[3]["candidate_id"] == "CAND_A"
    assert ranked[4]["candidate_id"] == "CAND_B"
