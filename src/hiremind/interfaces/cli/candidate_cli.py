"""CLI entrypoint for the Candidate Intelligence Engine pipeline."""

import time

from hiremind.infrastructure import load_config, logger
from hiremind.infrastructure.cache import FeatureCache
from hiremind.infrastructure.jd.ontology import OntologyLoader
from hiremind.services.candidate_intelligence_service import (
    CandidateIntelligenceService,
)
from hiremind.services.ontology_service import OntologyService


def main() -> None:
    """Run the full candidate intelligence pipeline from config."""
    config = load_config()
    dataset_config = config.get("dataset", {})
    jd_config = config.get("jd", {})

    cache_dir = str(dataset_config.get("cache_dir", "feature_cache"))
    ontology_path = str(jd_config.get("ontology_path", "configs/ontology.yaml"))
    artifacts_dir = str(jd_config.get("artifacts_dir", "artifacts"))

    # Load candidates from M2 cache.
    logger.info("Loading candidates...")
    cache = FeatureCache(cache_dir)
    if not cache.pickle_path.exists():
        logger.error("Candidate cache not found at {}. Run preprocess.py first.", cache_dir)
        return

    candidates = cache.load_pickle()
    logger.info("{} candidates loaded from cache.", len(candidates))

    # Load ontology.
    logger.info("Loading ontology...")
    ontology_loader = OntologyLoader(ontology_path).load()
    ontology_service = OntologyService(ontology_loader)

    # Run intelligence pipeline.
    logger.info("Processing {} candidates...", len(candidates))
    start = time.perf_counter()

    service = CandidateIntelligenceService(
        ontology_service=ontology_service,
        artifacts_dir=artifacts_dir,
    )
    result = service.process(candidates)

    elapsed = time.perf_counter() - start
    logger.info("Career analysis complete.")
    logger.info("Skill analysis complete.")
    logger.info("Evidence scoring complete.")
    logger.info("Saving feature store...")
    logger.info("Features: {}", result.features_path)
    logger.info("Summaries: {}", result.summary_path)
    logger.info(
        "Done. {} candidates processed in {:.1f}s.",
        result.total_processed,
        elapsed,
    )
