"""Ranking orchestration endpoints."""

import time

from fastapi import APIRouter, Depends

from hiremind.domain.requirement import ParsedRequirements, Requirement
from hiremind.domain.requirement_type import RequirementType
from hiremind.interfaces.api.dependencies import (
    get_app_state,
    get_ranking_service,
    get_retrieval_service,
)
from hiremind.interfaces.api.schemas.ranking import (
    CandidateExplanationSchema,
    ConcernSchema,
    RankedCandidateSchema,
    RankingResponse,
    StrengthSchema,
)
from hiremind.interfaces.api.schemas.request import JDParsingResponse, RankingRequest

router = APIRouter(prefix="/api/v1/ranking", tags=["Ranking Engine"])


from typing import Any


@router.post("/run", response_model=RankingResponse)
async def run_ranking_pipeline(
    jd_reqs: JDParsingResponse,
    params: RankingRequest,
    state: Any = Depends(get_app_state),
    retrieval_service: Any = Depends(get_retrieval_service),
    ranking_service: Any = Depends(get_ranking_service),
):
    """Run full hybrid retrieval and reasoning pipeline from structured requirements."""

    # 1. Reconstruct ParsedRequirements
    reqs = []
    for s in jd_reqs.required_skills:
        reqs.append(
            Requirement(id=f"R_{s}", name=s, category=RequirementType.TECHNOLOGY, weight=1.0)
        )

    prefs = []
    for s in jd_reqs.preferred_skills:
        prefs.append(
            Requirement(
                id=f"P_{s}", name=s, category=RequirementType.TECHNOLOGY, weight=0.5, required=False
            )
        )

    parsed = ParsedRequirements(required=tuple(reqs), preferred=tuple(prefs))

    # Provide a dummy string JD since we already have the structured reqs
    dummy_jd = " ".join(jd_reqs.required_skills + jd_reqs.preferred_skills)

    # 2. Retrieval
    start = time.perf_counter()
    retrieved = retrieval_service.retrieve_candidates(
        jd=dummy_jd,
        requirements=parsed,
        max_notice_days=params.max_notice_days,
        k=params.top_k * 5,  # Retrieve 5x for filtering margin
    )
    retrieval_time = (time.perf_counter() - start) * 1000.0

    # 3. Ranking & Reasoning
    start = time.perf_counter()
    ranked = ranking_service.rank_retrieved(
        retrieved=retrieved,
        candidates=state.candidates,
        features=state.candidate_features,
        requirements=parsed,
        max_notice_days=params.max_notice_days,
    )

    # Slice top K
    ranked = ranked[: params.top_k]
    ranking_time = (time.perf_counter() - start) * 1000.0

    # 4. Format Output
    explanations = {e.candidate_id: e for e in ranking_service._explanations}

    results = []
    for i, r in enumerate(ranked):
        cid = r["candidate_id"]
        exp = explanations.get(cid)

        schema_exp = None
        if exp and params.include_explanations:
            schema_exp = CandidateExplanationSchema(
                candidate_id=cid,
                final_score=exp.final_score,
                recommendation=exp.recommendation,
                recruiter_summary=exp.recruiter_summary,
                strengths=[
                    StrengthSchema(label=s.label, description=s.description) for s in exp.strengths
                ],
                concerns=[
                    ConcernSchema(
                        label=c.label, severity=c.severity.value, description=c.description
                    )
                    for c in exp.concerns
                ],
            )

        # Get raw profile for frontend rendering
        profile = None
        cand_obj = next((c for c in state.candidates if c.candidate_id == cid), None)
        if cand_obj:
            profile = {
                "name": cand_obj.profile.headline,  # Fake name in headline
                "current_title": cand_obj.profile.current_title,
                "experience_months": cand_obj.profile.total_experience_months,
            }

        results.append(
            RankedCandidateSchema(
                candidate_id=cid,
                rank=i + 1,
                final_score=r["final_score"],
                recommendation=r.get("recommendation", "N/A"),
                technical_score=r["technical_score"],
                career_score=r["career_score"],
                behavior_score=r["behavior_score"],
                knowledge_score=r["knowledge_score"],
                risk_penalty=r["risk_penalty"],
                explanation=schema_exp,
                profile_summary=profile,
            )
        )

    return RankingResponse(
        total_candidates_retrieved=len(retrieved),
        retrieval_latency_ms=round(retrieval_time, 2),
        ranking_latency_ms=round(ranking_time, 2),
        results=results,
    )
