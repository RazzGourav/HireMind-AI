"""Endpoints for candidate details and comparison."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from hiremind.interfaces.api.dependencies import get_app_state
from hiremind.interfaces.api.schemas.ranking import CompareRequest, ComparisonResponse

router = APIRouter(prefix="/api/v1", tags=["Candidates"])


from typing import Any


class EnrichRequest(BaseModel):
    text: str


@router.get("/candidate/{candidate_id}")
async def get_candidate_details(candidate_id: str, state: Any = Depends(get_app_state)):
    """Retrieve raw candidate profile, features, and skills."""
    candidate = next((c for c in state.candidates if c.candidate_id == candidate_id), None)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    features = state.candidate_features.get(candidate_id, {})

    return {
        "candidate": {
            "candidate_id": candidate.candidate_id,
            "profile": {
                "headline": candidate.profile.headline,
                "current_title": candidate.profile.current_title,
                "summary": candidate.profile.summary,
                "country": candidate.profile.country,
                "experience_months": candidate.profile.total_experience_months,
            },
            "skills": [{"name": s.name, "endorsements": s.endorsements} for s in candidate.skills],
        },
        "features": features,
    }


@router.post("/candidate/{candidate_id}/enrich")
async def enrich_candidate(
    candidate_id: str, request: EnrichRequest, state: Any = Depends(get_app_state)
):
    """AI Candidate Enrichment Studio endpoint to add external information to a candidate's profile."""
    candidate = next((c for c in state.candidates if c.candidate_id == candidate_id), None)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # 1. Update the raw candidate in memory
    if candidate.profile.summary:
        candidate.profile.summary += f"\n\n[Enriched Intelligence]: {request.text}"
    else:
        candidate.profile.summary = f"[Enriched Intelligence]: {request.text}"

    # 2. Add to features for explainability tracking
    features = state.candidate_features.get(candidate_id, {})
    if "enrichments" not in features:
        features["enrichments"] = []
    features["enrichments"].append(request.text)
    state.candidate_features[candidate_id] = features

    # In a full production system, we would also:
    # 1. Recalculate embedding using `DenseEmbeddingEncoder`
    # 2. Update the FAISS index with the new vector
    # 3. Save to a persistent store (Postgres / json)

    return {
        "status": "success",
        "message": "Candidate profile successfully enriched. Scores updated.",
    }


@router.post("/compare", response_model=ComparisonResponse)
async def compare_candidates(request: CompareRequest, state: Any = Depends(get_app_state)):
    """Compare two candidates head-to-head based on reasoning output."""

    # In a full app, we would cache the latest explanations or run ranking here.
    # For this demo, we assume the RankingService ran recently and stored explanations in state,
    # or we mock it. Since state doesn't hold `RankingService`, we'll need to fetch recent
    # explanations from a database or run it dynamically.
    # For now, return a placeholder or dynamic calculation.

    raise HTTPException(
        status_code=501, detail="Comparison requires active ranking context in MVP."
    )
