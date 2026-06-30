"""Hybrid Retriever — combines dense vector search with graph/ontology alignment."""

from typing import Any

import numpy as np

from hiremind.domain.requirement import ParsedRequirements
from hiremind.domain.retrieval_result import RetrievalResult
from hiremind.knowledge.ontology import SkillOntology
from hiremind.retrieval.faiss_index import FaissIndex


class HybridRetriever:
    """Retrieves candidates using dense vector similarity boosted by ontology alignments."""

    def __init__(self, faiss_index: FaissIndex, ontology: SkillOntology) -> None:
        self.faiss_index = faiss_index
        self.ontology = ontology

    def retrieve(
        self,
        query_vector: np.ndarray,
        candidate_store: Any,
        requirements: ParsedRequirements,
        candidate_ids: list[str],
        top_k_dense: int = 5000,
    ) -> list[RetrievalResult]:
        """Perform dense embedding search, boost scores with ontology matching and calculate features."""
        # 1. Dense vector lookup
        distances, indices = self.faiss_index.search(
            query_vector, k=min(top_k_dense, len(candidate_ids))
        )

        results = []

        # Extracted requirements for ontology matching
        req_skills = set(requirements.required_names)
        pref_skills = set(requirements.preferred_names)
        all_req_skills = req_skills | pref_skills

        for score, idx in zip(distances, indices):
            if idx < 0 or idx >= len(candidate_ids):
                continue

            cid = candidate_ids[idx]
            candidate = candidate_store.get(cid)
            if not candidate:
                continue

            # Calculate ontology matching features
            candidate_skills = {
                self.ontology.canonical_name(s.name) or s.name for s in candidate.skills
            }

            # Required and preferred coverages
            req_coverage = 0.0
            if req_skills:
                req_coverage = len(candidate_skills & req_skills) / len(req_skills)

            pref_coverage = 0.0
            if pref_skills:
                pref_coverage = len(candidate_skills & pref_skills) / len(pref_skills)

            # Ontology similarity / graph overlap: compute overlap using ancestors/synonyms
            # Expand requirements to include their direct ontology categories/parents
            expanded_reqs = set()
            for r in all_req_skills:
                expanded_reqs.add(r)
                expanded_reqs.update(self.ontology.get_parents(r))

            expanded_cand = set()
            for cs in candidate_skills:
                expanded_cand.add(cs)
                expanded_cand.update(self.ontology.get_parents(cs))

            # Graph overlap Jaccard
            graph_overlap = 0.0
            if expanded_reqs or expanded_cand:
                graph_overlap = len(expanded_reqs & expanded_cand) / len(
                    expanded_reqs | expanded_cand
                )

            # Boost factor based on graph overlap and technical required skill coverage
            # Hybrid score = 0.6 * dense_similarity + 0.4 * graph_overlap
            dense_sim = float(score)
            # Clip dense similarity to reasonable bounds (FAISS inner product of normalized vectors is [-1, 1])
            dense_sim = max(0.0, min(dense_sim, 1.0))

            hybrid_score = 0.6 * dense_sim + 0.4 * graph_overlap

            features = {
                "semantic_similarity": dense_sim,
                "ontology_similarity": graph_overlap,
                "graph_overlap": graph_overlap,
                "required_skill_coverage": req_coverage,
                "preferred_skill_coverage": pref_coverage,
                "embedding_distance": 1.0 - dense_sim,
            }

            results.append(
                RetrievalResult(
                    candidate_id=cid,
                    score=round(hybrid_score, 4),
                    features=features,
                )
            )

        # Sort by hybrid score descending
        results.sort(key=lambda x: x.score, reverse=True)
        return results
