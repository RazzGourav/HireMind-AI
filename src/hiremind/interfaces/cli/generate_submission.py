import json
from pathlib import Path

from hiremind.domain.requirement import ParsedRequirements
from hiremind.infrastructure import load_config, logger
from hiremind.interfaces.api.dependencies import (
    get_app_state,
    get_ranking_service,
    get_retrieval_service,
)


def main() -> None:
    load_config()
    logger.info("Initializing Backend State...")
    state = get_app_state()

    logger.info("Loading Job Description and Requirements...")
    artifacts_dir = Path("artifacts")

    from hiremind.infrastructure.jd.loader import JDLoader

    loader = JDLoader()
    jd = loader.load(Path("Dataset/job_description.docx"))

    with open(artifacts_dir / "jd_requirements.json", "r", encoding="utf-8") as f:
        req_data = json.load(f)

        from hiremind.domain.requirement import (
            ExperienceRequirement,
            NegativeRequirement,
            Requirement,
        )
        from hiremind.domain.requirement_type import RequirementType

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

    logger.info("Retrieving candidates...")
    retrieval_service = get_retrieval_service(state)
    retrieved = retrieval_service.retrieve_candidates(jd, requirements, k=1000)

    logger.info("Ranking {} candidates...", len(retrieved))
    ranking_service = get_ranking_service()

    # Extract features for retrieved candidates
    id_to_feat = {f.candidate_id: f for f in state.candidate_features}
    features_subset = [
        id_to_feat[r.candidate_id] for r in retrieved if r.candidate_id in id_to_feat
    ]

    ranked_records = ranking_service.rank_retrieved(
        retrieved=retrieved,
        candidate_store=state.candidates,
        features=features_subset,
        requirements=requirements,
    )

    logger.info("Generating top 100 submission...")
    top_100 = ranked_records[:100]

    output_path = Path("outputs/submission/submission.csv")
    from hiremind.submission.csv_generator import generate_submission_csv

    generate_submission_csv(top_100, output_path, max_rows=100)

    logger.info("Generating Leaderboard Simulation...")
    from hiremind.submission.leaderboard import LeaderboardSimulator

    sim = LeaderboardSimulator(top_100)
    sim_path = Path("reports/leaderboard_simulation.md")
    sim.simulate(sim_path)

    logger.info("Submission saved to: {}", output_path.absolute())


if __name__ == "__main__":
    main()
