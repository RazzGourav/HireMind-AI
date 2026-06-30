import json
import os
import sys
import time
import tracemalloc
from pathlib import Path

import psutil

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from hiremind.domain.jd import JobDescription
from hiremind.domain.requirement import (
    ExperienceRequirement,
    ParsedRequirements,
    Requirement,
)
from hiremind.domain.requirement_type import RequirementType
from hiremind.infrastructure import load_config
from hiremind.interfaces.api.dependencies import (
    get_app_state,
    get_ranking_service,
    get_retrieval_service,
)


def profile_pipeline():
    print("Starting Profiling Session...")
    profiling_data = {
        "timestamp": time.time(),
        "environment": os.getenv("ENVIRONMENT", "development"),
    }

    tracemalloc.start()

    # Measure Startup Time
    start_time = time.time()
    load_config()
    state = get_app_state()
    startup_time = time.time() - start_time
    profiling_data["startup_time_ms"] = startup_time * 1000

    # Create dummy JD
    jd = JobDescription(
        raw_text="We are looking for a Senior AI Engineer to build retrieval systems with Python, FAISS, and Vector DBs.",
        cleaned_text="we are looking for a senior ai engineer to build retrieval systems with python faiss and vector dbs",
        source_path="mock",
    )
    reqs = ParsedRequirements(
        required=(Requirement(id="req1", name="Python", category=RequirementType.TECHNOLOGY),),
        preferred=tuple(),
        negative=tuple(),
        experience=ExperienceRequirement(min_years=5),
    )

    # Profile Retrieval
    retrieval_service = get_retrieval_service(state)
    start_time = time.time()
    retrieved = retrieval_service.retrieve_candidates(jd, reqs, k=1000)
    retrieval_time = time.time() - start_time
    profiling_data["retrieval_latency_ms"] = retrieval_time * 1000

    # Profile Ranking
    ranking_service = get_ranking_service()
    id_to_feat = {f.candidate_id: f for f in state.candidate_features}
    features_subset = [
        id_to_feat[r.candidate_id] for r in retrieved if r.candidate_id in id_to_feat
    ]

    start_time = time.time()
    ranked = ranking_service.rank_retrieved(
        retrieved=retrieved,
        candidate_store=state.candidates,
        features=features_subset,
        requirements=reqs,
    )
    ranking_time = time.time() - start_time
    profiling_data["ranking_latency_ms"] = ranking_time * 1000

    # Memory & CPU
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    profiling_data["memory_usage_peak_mb"] = peak / 10**6
    profiling_data["cpu_utilization_percent"] = psutil.cpu_percent(interval=1)

    # Estimated API Throughput (Requests per second)
    total_time_s = retrieval_time + ranking_time
    profiling_data["api_throughput_rps_estimate"] = 1.0 / total_time_s if total_time_s > 0 else 0

    # Save Profile
    out_path = Path("reports/performance/profiling.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(profiling_data, f, indent=4)

    print(f"Profiling complete. Saved to {out_path.absolute()}")
    print(json.dumps(profiling_data, indent=2))


if __name__ == "__main__":
    profile_pipeline()
