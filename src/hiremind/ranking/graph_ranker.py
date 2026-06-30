"""Graph Ranker — evaluates candidate knowledge graph features and technology depths."""

from hiremind.domain.candidate import Candidate
from hiremind.domain.candidate_features import CandidateFeatures
from hiremind.domain.requirement import ParsedRequirements


class GraphRanker:
    """Computes knowledge graph score based on technology diversity, subtree depths, and domain breath."""

    def score(
        self,
        candidate: Candidate,
        features: CandidateFeatures,
        requirements: ParsedRequirements,
    ) -> float:
        """Score candidate's knowledge graph alignment (0.0 to 1.0)."""
        f_vec = features.feature_vector

        # 1. Technology diversity: target 5+ categories for full score
        tech_div = f_vec.get("technology_diversity", 0.0)
        div_score = min(tech_div / 5.0, 1.0)

        # 2. Tech depths (AI, backend, cloud, retrieval)
        ai_depth = f_vec.get("ai_depth", 0.0)
        ai_score = min(ai_depth / 4.0, 1.0)  # path of length 4 is deep

        backend_depth = f_vec.get("backend_depth", 0.0)
        backend_score = min(backend_depth / 4.0, 1.0)

        retrieval_depth = f_vec.get("retrieval_depth", 0.0)
        retrieval_score = min(retrieval_depth / 4.0, 1.0)

        # 3. Domain breadth: target 3+ domains
        domain_breadth = f_vec.get("domain_breadth", 0.0)
        domain_score = min(domain_breadth / 3.0, 1.0)

        # 4. Graph connectivity
        connectivity = f_vec.get("graph_connectivity", 0.0)

        # Blend: 30% Tech diversity + 40% depths + 20% domain breadth + 10% connectivity
        depths_avg = (ai_score + backend_score + retrieval_score) / 3.0
        raw = 0.3 * div_score + 0.4 * depths_avg + 0.2 * domain_score + 0.1 * connectivity
        return round(min(max(raw, 0.0), 1.0), 3)
