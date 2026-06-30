import json
from pathlib import Path

from hiremind.domain.requirement import (
    ExperienceRequirement,
    NegativeRequirement,
    ParsedRequirements,
    Requirement,
)
from hiremind.domain.requirement_type import RequirementType
from hiremind.infrastructure import load_config
from hiremind.infrastructure.jd.loader import JDLoader
from hiremind.interfaces.api.dependencies import get_app_state, get_retrieval_service


def main() -> None:
    load_config()
    state = get_app_state()

    loader = JDLoader()
    jd = loader.load(Path("Dataset/job_description.docx"))

    artifacts_dir = Path("artifacts")
    with open(artifacts_dir / "jd_requirements.json", "r", encoding="utf-8") as f:
        req_data = json.load(f)

        required = [
            Requirement(**{**r, "category": RequirementType(r["category"])})
            for r in req_data.get("required", [])
        ]
        preferred = [
            Requirement(**{**r, "category": RequirementType(r["category"])})
            for r in req_data.get("preferred", [])
        ]
        negative = [NegativeRequirement(**n) for n in req_data.get("negative", [])]
        experience = ExperienceRequirement(**req_data.get("experience", {}))

        requirements = ParsedRequirements(
            required=tuple(required),
            preferred=tuple(preferred),
            negative=tuple(negative),
            experience=experience,
        )

    retrieval_service = get_retrieval_service(state)

    # Debug: Check first 10 candidates
    for c in state.candidates[:10]:
        print(
            f"{c.candidate_id}: Exp={c.profile.experience_years}, Notice={getattr(c.signals, 'notice_period_days', 'N/A')}"
        )

    print(f"Total candidates: {len(state.candidates)}")
    print(f"Total FAISS size: {state.faiss_index.index.ntotal if state.faiss_index.index else 0}")
    print(f"Candidate IDs: {len(state.candidate_ids)}")

    # Run retrieval
    query_vector = retrieval_service.query_encoder.encode_query(jd)
    raw = retrieval_service.retriever.retrieve(
        query_vector, state.candidates, requirements, state.candidate_ids, 5000
    )
    print(f"Hybrid returned: {len(raw)} candidates")

    filtered = retrieval_service.retrieve_candidates(jd, requirements, k=1000)
    print(f"Final filtered returned: {len(filtered)} candidates")


if __name__ == "__main__":
    main()
