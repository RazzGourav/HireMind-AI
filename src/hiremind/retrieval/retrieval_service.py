"""Retrieval Service — Orchestrator for candidate retrieval and structured filtering."""

from typing import Any

from hiremind.domain.jd import JobDescription
from hiremind.domain.requirement import ParsedRequirements
from hiremind.domain.retrieval_result import RetrievalResult
from hiremind.retrieval.embedding_cache import EmbeddingCache
from hiremind.retrieval.faiss_index import FaissIndex
from hiremind.retrieval.filter_engine import StructuredFilterEngine
from hiremind.retrieval.hybrid_retriever import HybridRetriever
from hiremind.retrieval.query_encoder import QueryEncoder


class RetrievalService:
    """End-to-end service coordinating candidate embeddings, indexing, and hybrid filtering retrieval."""

    def __init__(
        self,
        retriever: HybridRetriever,
        query_encoder: QueryEncoder,
        filter_engine: StructuredFilterEngine,
        embedding_cache: EmbeddingCache,
        faiss_index: FaissIndex,
        candidate_store: Any,
        candidate_ids: list[str],
    ) -> None:
        self.retriever = retriever
        self.query_encoder = query_encoder
        self.filter_engine = filter_engine
        self.cache = embedding_cache
        self.faiss_index = faiss_index
        self.candidate_store = candidate_store
        self.candidate_ids = candidate_ids

    def retrieve_candidates(
        self,
        jd: JobDescription,
        requirements: ParsedRequirements,
        max_notice_days: int = 90,
        allowed_work_modes: list[str] | None = None,
        require_relocation_willingness: bool = False,
        mandatory_skills: list[str] | None = None,
        k: int = 2000,
    ) -> list[RetrievalResult]:
        """Orchestrate the hybrid retrieval pipeline."""
        # 1. Generate query embedding
        query_vector = self.query_encoder.encode_query(jd)

        # 2. Cache query vector
        self.cache.save_query(query_vector)

        # 3. Retrieve candidates using dense + ontology
        retrieved_raw = self.retriever.retrieve(
            query_vector,
            self.candidate_store,
            requirements,
            self.candidate_ids,
            top_k_dense=5000,
        )

        # 4. Apply structured filtering on the retrieved subset
        filtered_results = []
        for res in retrieved_raw:
            cand = self.candidate_store.get(res.candidate_id)
            if not cand:
                continue

            # Verify against filter engine
            passes = self.filter_engine.filter_candidate(
                cand,
                requirements=requirements,
                max_notice_days=max_notice_days,
                allowed_work_modes=allowed_work_modes,
                require_relocation_willingness=require_relocation_willingness,
                mandatory_skills=mandatory_skills,
            )

            if passes:
                filtered_results.append(res)

            # Limit output to k candidates
            if len(filtered_results) >= k:
                break

        return filtered_results
