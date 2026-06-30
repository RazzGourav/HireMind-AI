from hiremind.services import SchemaValidator


def test_schema_validator_accepts_valid_candidate() -> None:
    result = SchemaValidator().validate(
        {
            "candidate_id": "CAND_001",
            "profile": {"total_experience_months": 48},
            "skills": [{"name": "Python", "endorsements": 3}],
        }
    )

    assert result.is_valid
    assert result.record is not None
    assert result.record.candidate_id == "CAND_001"


def test_schema_validator_rejects_impossible_values() -> None:
    result = SchemaValidator().validate(
        {
            "candidate_id": "CAND_002",
            "profile": {"total_experience_months": -1},
            "career_history": [{"start_date": "not-a-date"}],
            "skills": [{"name": "   "}],
        }
    )

    assert not result.is_valid
    assert any("total_experience_months" in error for error in result.errors)
    assert any("start_date" in error for error in result.errors)
    assert any("skill name cannot be empty" in error for error in result.errors)
