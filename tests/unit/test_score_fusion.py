"""Unit tests for the ScoreFusionEngine."""

from hiremind.ranking.score_fusion import ScoreFusionEngine


def test_score_fusion_engine_calculation() -> None:
    engine = ScoreFusionEngine()

    # Scores: Technical: 0.8 (weight 40%), Career: 0.7 (weight 20%), Behavior: 0.6 (weight 15%),
    # Knowledge: 0.5 (weight 15%), Growth: 0.4 (weight 5%), Leadership: 0.3 (weight 5%)
    # Penalty: 0.1
    # Raw fused: 0.4*0.8 + 0.2*0.7 + 0.15*0.6 + 0.15*0.5 + 0.05*0.4 + 0.05*0.3
    # = 0.32 + 0.14 + 0.09 + 0.075 + 0.02 + 0.015 = 0.66
    # Final score: 0.66 - 0.1 = 0.56

    final, components = engine.fuse(
        technical=0.8,
        career=0.7,
        behavior=0.6,
        knowledge=0.5,
        growth=0.4,
        leadership=0.3,
        risk_penalty=0.1,
    )

    assert final == 0.56
    assert components["raw_fused_score"] == 0.66
    assert components["technical_score"] == 0.8
    assert components["risk_penalty"] == 0.1
