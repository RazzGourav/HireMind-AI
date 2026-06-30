"""Unit tests for the ExplanationBuilder."""

from hiremind.ranking.explanation_builder import ExplanationBuilder


def test_explanation_builder_output() -> None:
    builder = ExplanationBuilder()

    components = {
        "technical_score": 0.8,
        "career_score": 0.7,
        "behavior_score": 0.5,
        "knowledge_score": 0.3,
        "risk_penalty": 0.1,
        "final_score": 75.0,
    }

    explanation = builder.build_explanation("CAND_XYZ", components)

    assert "CAND_XYZ" in explanation
    # Final score 75.0 matches "solid candidate"
    assert "solid candidate" in explanation
    # Technical >= 0.7
    assert "Strong technical skill alignment" in explanation
    # Penalty exists
    assert "Minor risk penalty" in explanation
