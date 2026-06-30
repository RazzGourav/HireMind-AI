from _bootstrap import ensure_project_environment

ensure_project_environment()

import json
import time
from pathlib import Path

from hiremind.infrastructure import load_config, logger
from hiremind.infrastructure.cache import FeatureCache
from hiremind.retrieval import (
    CandidateEncoder,
    DenseEmbeddingEncoder,
    EmbeddingCache,
    FaissIndex,
)


def main() -> None:
    """Load candidates, encode them into dense vectors, build and save the FAISS index."""
    logger.info("Initializing Retrieval Index Builder...")
    start_time = time.perf_counter()

    config = load_config()
    dataset_config = config.get("dataset", {})
    cache_dir = str(dataset_config.get("cache_dir", "feature_cache"))

    # 1. Load candidates from cache
    logger.info("Loading candidates...")
    cache = FeatureCache(cache_dir)
    if not cache.pickle_path.exists():
        logger.error("Candidate cache not found at {}. Run preprocess.py first.", cache_dir)
        return

    candidates = cache.load_pickle()
    candidates = candidates[:10000]  # Subset for verification benchmarks
    logger.info("Loaded {} candidates for indexing.", len(candidates))

    # 2. Initialize encoders
    logger.info("Loading embedding model...")
    encoder = DenseEmbeddingEncoder()
    candidate_encoder = CandidateEncoder(encoder)

    # 3. Generate candidate embeddings
    logger.info("Encoding candidate textual representations (this may take a few moments)...")
    enc_start = time.perf_counter()
    embeddings = candidate_encoder.encode_candidates(candidates)
    enc_elapsed = time.perf_counter() - enc_start
    logger.info("Encoded candidates in {:.2f}s.", enc_elapsed)

    # 4. Cache candidate embeddings
    logger.info("Saving embeddings cache...")
    emb_cache = EmbeddingCache()
    cids = [c.candidate_id for c in candidates]
    emb_cache.save_candidates(cids, embeddings)

    # 5. Build FAISS index
    logger.info("Building FAISS index...")
    faiss_idx = FaissIndex(dimension=embeddings.shape[1])
    faiss_idx.build(embeddings)
    faiss_idx.save("artifacts/faiss/index.bin")

    # 6. Save basic retrieval metrics
    logger.info("Writing index metrics...")
    metrics_path = Path("artifacts/retrieval/retrieval_metrics.json")
    metrics_path.parent.mkdir(parents=True, exist_ok=True)

    metrics = {
        "candidate_count": len(candidates),
        "embedding_dimension": embeddings.shape[1],
        "encoding_time_sec": round(enc_elapsed, 2),
        "total_build_time_sec": round(time.perf_counter() - start_time, 2),
    }
    with metrics_path.open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    logger.info("Retrieval index built successfully!")
    logger.info("  - artifacts/embeddings/candidate_embeddings.parquet")
    logger.info("  - artifacts/faiss/index.bin")
    logger.info("  - artifacts/retrieval/retrieval_metrics.json")


if __name__ == "__main__":
    main()
