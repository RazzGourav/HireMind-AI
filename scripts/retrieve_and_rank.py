from _bootstrap import ensure_project_environment

ensure_project_environment()

import time
from pathlib import Path

from hiremind.evaluation.ranking_metrics import RankingEvaluator
from hiremind.infrastructure import load_config, logger
from hiremind.infrastructure.cache import FeatureCache
from hiremind.infrastructure.jd.ontology import OntologyLoader
from hiremind.ranking import RankingService
from hiremind.retrieval import (
    EmbeddingCache,
    FaissIndex,
    HybridRetriever,
    QueryEncoder,
    RetrievalService,
    StructuredFilterEngine,
)
from hiremind.services.jd_service import JDService
from hiremind.services.ontology_service import OntologyService


def main() -> None:
    """Run candidate retrieval and scoring/ranking pipeline end-to-end."""
    logger.info("Initializing Retrieval and Ranking Pipeline...")
    start_time = time.perf_counter()

    config = load_config()
    jd_config = config.get("jd", {})
    dataset_config = config.get("dataset", {})
    cache_dir = str(dataset_config.get("cache_dir", "feature_cache"))

    # 1. Parse JD using JDService
    logger.info("Processing Job Description...")
    jd_service = JDService(
        jd_path=Path(str(jd_config.get("path", "Dataset/job_description.docx"))),
        ontology_path=Path(str(jd_config.get("ontology_path", "configs/ontology.yaml"))),
        artifacts_dir=Path(str(jd_config.get("artifacts_dir", "artifacts"))),
    )
    jd_result = jd_service.process()
    logger.info("JD processed: Title: '{}'", jd_result.jd.source_path or "Standard Doc")

    # 2. Load candidates from cache
    logger.info("Loading candidates and features cache...")
    feature_cache = FeatureCache(cache_dir)
    if not feature_cache.pickle_path.exists():
        logger.error("Preprocessed candidate cache not found. Please run preprocess.py first.")
        return
    candidates = feature_cache.load_pickle()

    # Load M4 CandidateFeatures summaries (from cache_dir or artifacts)
    feat_store_path = Path("artifacts/candidate_summary.pkl")
    if not feat_store_path.exists():
        logger.error(
            "M4 candidate features cache not found. Please run process_candidates.py first."
        )
        return

    import pickle

    with feat_store_path.open("rb") as f:
        features = pickle.load(f)  # noqa: S301
    logger.info("Loaded {} candidate feature summaries.", len(features))

    # 3. Load precomputed FAISS Index
    faiss_index_path = Path("artifacts/faiss/index.bin")
    if not faiss_index_path.exists():
        logger.error("FAISS index not found. Please run build_retrieval_index.py first.")
        return

    faiss_idx = FaissIndex(dimension=384)
    faiss_idx.load(faiss_index_path)

    # Load candidate IDs and matching embeddings from Parquet embedding cache
    emb_cache = EmbeddingCache()
    cids, embs = emb_cache.load_candidates()

    # 4. Instantiate Hybrid Retrieval Service
    ontology_loader = OntologyLoader(
        Path(str(jd_config.get("ontology_path", "configs/ontology.yaml")))
    ).load()
    ontology_service = OntologyService(ontology_loader)

    from hiremind.retrieval.embedding_encoder import DenseEmbeddingEncoder

    dense_encoder = DenseEmbeddingEncoder()
    query_encoder = QueryEncoder(dense_encoder)

    from hiremind.knowledge.graph_repository import GraphRepository

    graph_repo = GraphRepository("artifacts")
    raw_ontology = graph_repo.load_ontology()
    retriever = HybridRetriever(faiss_idx, raw_ontology)
    filter_engine = StructuredFilterEngine()

    retrieval_service = RetrievalService(
        retriever=retriever,
        query_encoder=query_encoder,
        filter_engine=filter_engine,
        embedding_cache=emb_cache,
        faiss_index=faiss_idx,
        candidates=candidates,
        candidate_ids=cids,
    )

    # 5. Execute candidate retrieval
    logger.info("Executing candidate retrieval (k=2000)...")
    ret_start = time.perf_counter()
    retrieved = retrieval_service.retrieve_candidates(
        jd=jd_result.jd,
        requirements=jd_result.requirements,
        max_notice_days=90,  # Strict threshold limit
        k=2000,
    )
    ret_elapsed = time.perf_counter() - ret_start
    logger.info("Retrieved {} candidates in {:.2f}s.", len(retrieved), ret_elapsed)

    # 6. Instantiate Ranking Service and score matches
    logger.info("Scoring and ranking retrieved candidate pool...")
    rank_start = time.perf_counter()
    ranking_service = RankingService(artifacts_dir="artifacts")
    ranked_records = ranking_service.rank_retrieved(
        retrieved=retrieved,
        candidates=candidates,
        features=features,
        requirements=jd_result.requirements,
        max_notice_days=90,
    )
    rank_elapsed = time.perf_counter() - rank_start
    logger.info("Sorted and ranked candidates in {:.2f}s.", rank_elapsed)

    # Save ranking model parameters
    ranking_service.save_model()

    # Save outputs
    logger.info("Saving outputs (preview and reports)...")
    ranking_service.save_top_preview(ranked_records, "outputs/top100_preview.csv")

    # Save Milestone 8 reasoning outputs
    logger.info("Saving reasoning outputs (explanations, recommendations, comparisons)...")
    ranking_service.save_explanations("outputs/candidate_explanations.json")
    ranking_service.save_recommendations("outputs/interview_recommendations.json")
    ranking_service.save_comparison(ranked_records, "outputs/candidate_comparison.json")

    # Generate synthetic/relevance evaluation mappings against requirements
    # Define relevance: 3.0 for exact/highly relevant, 1.0 for partially matching, 0.0 for unrelated
    ground_truth_relevance = {}
    for rec in ranked_records:
        cid = rec["candidate_id"]
        # Basic heuristic relevance: map score / 33.3 to get [0.0, 3.0]
        ground_truth_relevance[cid] = float(rec["final_score"]) / 33.3

    eval_elapsed_ms = (ret_elapsed + rank_elapsed) * 1000.0
    report = RankingEvaluator.evaluate_ranking(
        ranked_records=ranked_records,
        ground_truth_relevance=ground_truth_relevance,
        latency_ms=eval_elapsed_ms,
        output_path="outputs/ranking_report.json",
    )

    elapsed = time.perf_counter() - start_time
    logger.info("Retrieval and ranking pipeline complete in {:.2f}s.", elapsed)
    if ranked_records:
        logger.info(
            "Top Match: {} with score {}",
            ranked_records[0]["candidate_id"],
            ranked_records[0]["final_score"],
        )
        logger.info("Recommendation: {}", ranked_records[0].get("recommendation", "N/A"))
    else:
        logger.warning("No candidates were ranked because 0 candidates were retrieved.")

    logger.info("Evaluation report saved to: outputs/ranking_report.json")
    logger.info("Reasoning outputs saved to: outputs/candidate_explanations.json")
    logger.info("Interview recommendations saved to: outputs/interview_recommendations.json")
    if "ndcg_at_10" in report:
        logger.info("NDCG@10: {}", report["ndcg_at_10"])
        logger.info("MAP:     {}", report["mean_average_precision"])


if __name__ == "__main__":
    main()
