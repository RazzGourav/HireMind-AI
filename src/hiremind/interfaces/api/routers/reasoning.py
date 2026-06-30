"""Recruiter Copilot and NLP querying."""

from typing import Any

from fastapi import APIRouter, Depends

from hiremind.interfaces.api.dependencies import get_app_state
from hiremind.interfaces.api.schemas.request import CopilotRequest, CopilotResponse

router = APIRouter(prefix="/api/v1/copilot", tags=["Recruiter Copilot"])


def _search_candidates(candidates: list, query: str) -> list[dict]:
    """Simple keyword-based candidate search across profiles and skills."""
    query_lower = query.lower()
    keywords = [w.strip() for w in query_lower.replace(",", " ").split() if len(w.strip()) > 2]

    scored: list[tuple[float, Any]] = []
    for c in candidates:
        score = 0.0
        profile = c.profile
        skills = [s.name.lower() for s in c.skills]
        headline = (profile.headline or "").lower()
        title = (profile.current_title or "").lower()
        summary = (profile.summary or "").lower()

        for kw in keywords:
            if any(kw in sk for sk in skills):
                score += 3.0
            if kw in headline:
                score += 2.0
            if kw in title:
                score += 2.0
            if kw in summary:
                score += 1.0

        if score > 0:
            scored.append((score, c))

    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:5]


@router.post("/query", response_model=CopilotResponse)
async def query_copilot(request: CopilotRequest, state: Any = Depends(get_app_state)):
    """Natural language interface for recruiters to ask questions about the candidate pool."""

    query = request.query.strip()
    query_lower = query.lower()

    # Contextual responses based on query type
    if any(w in query_lower for w in ["how many", "total", "count"]):
        total = len(state.candidates)
        answer = f"There are **{total:,}** candidates in the current database."
        return CopilotResponse(answer=answer, structured_data={"total_candidates": total})

    if any(w in query_lower for w in ["relocate", "relocation", "willing to move"]):
        # Count candidates with relocation info
        relocatable = sum(1 for c in state.candidates if getattr(c.profile, "country", "") != "")
        answer = f"I found **{relocatable}** candidates with location data. You can filter by country or region in the Candidate Search page for relocation matches."
        return CopilotResponse(
            answer=answer, structured_data={"filter": "relocation", "count": relocatable}
        )

    if any(w in query_lower for w in ["compare", "versus", "vs", "head to head"]):
        answer = "To compare candidates side-by-side, navigate to the **Candidate Search** page, run a search, then click **View Profile** on any candidate to see their full breakdown with strengths, concerns, and recommendation."
        return CopilotResponse(answer=answer, structured_data={"action": "navigate_search"})

    if any(w in query_lower for w in ["experience", "senior", "years"]):
        # Find experienced candidates
        experienced = [c for c in state.candidates if c.profile.total_experience_months >= 60]
        count = len(experienced)
        top_names = [c.profile.headline or c.candidate_id for c in experienced[:5]]
        answer = (
            f"I found **{count}** candidates with 5+ years of experience. Top profiles:\n"
            + "\n".join(f"- {n}" for n in top_names)
        )
        return CopilotResponse(
            answer=answer, structured_data={"filter": "experience_5y+", "count": count}
        )

    # Default: keyword search across candidates
    matches = _search_candidates(state.candidates, query)

    if matches:
        lines = []
        for score, c in matches:
            skills_str = ", ".join(s.name for s in c.skills[:5])
            title = c.profile.current_title or "N/A"
            exp_years = c.profile.total_experience_months // 12
            lines.append(
                f"- **{c.profile.headline or c.candidate_id}** — {title} ({exp_years}y) — Skills: {skills_str}"
            )

        answer = (
            f'I found **{len(matches)}** relevant candidates matching "{query}":\n\n'
            + "\n".join(lines)
        )
        candidate_ids = [c.candidate_id for _, c in matches]
        return CopilotResponse(
            answer=answer, structured_data={"matched_ids": candidate_ids, "count": len(matches)}
        )
    else:
        answer = f'I couldn\'t find strong matches for "{query}" in the current candidate pool. Try broader keywords like a technology name (Python, Java, React) or a role (Backend, ML Engineer).'
        return CopilotResponse(answer=answer, structured_data={"matched_ids": [], "count": 0})
