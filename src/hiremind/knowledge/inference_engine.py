"""Semantic Inference Engine — Infers implicit capabilities from explicit skills."""

from collections.abc import Iterable

from hiremind.knowledge.domain_graph import DomainGraph
from hiremind.knowledge.normalization import SkillNormalizer
from hiremind.knowledge.technology_graph import TechnologyGraph


class InferenceEngine:
    """Engine to perform semantic reasoning and infer implicit skills and domains."""

    def __init__(
        self,
        normalizer: SkillNormalizer,
        tech_graph: TechnologyGraph,
        domain_graph: DomainGraph,
    ) -> None:
        self.normalizer = normalizer
        self.tech_graph = tech_graph
        self.domain_graph = domain_graph

    def infer_capabilities(self, raw_skills: Iterable[str]) -> set[str]:
        """Infer canonical skills, categories, concepts, and domains from explicit skills.

        Example:
            {"Milvus", "FAISS", "Embeddings"} ->
            {"Retrieval", "Vector Search", "ANN Search", "RAG", "Similarity Search", ...}
        """
        inferred = set()
        canonical_skills = set()

        # 1. Normalize explicit skills
        for raw in raw_skills:
            normalized = self.normalizer.normalize(raw)
            if normalized:
                canonical_skills.add(normalized)
                inferred.add(normalized)

        # 2. Transitive graph inference
        for skill in canonical_skills:
            # Add ancestors (e.g. IS_A relationships)
            ancestors = self.tech_graph.ancestors(skill)
            inferred.update(ancestors)

            # Add uses / depends_on targets
            uses_targets = self.tech_graph.uses(skill)
            inferred.update(uses_targets)

            depends_on_targets = self.tech_graph.depends_on(skill)
            inferred.update(depends_on_targets)

            # Add alternatives as potential related skills
            # (e.g. if they know FAISS, they are implicitly familiar with Vector Search concept)
            alts = self.tech_graph.alternatives(skill)
            for alt in alts:
                # Add ancestors of alternative technologies to get category overlap
                alt_ancestors = self.tech_graph.ancestors(alt)
                inferred.update(alt_ancestors)

            # 3. Domain inference
            # Get domains this skill belongs to
            domains = self.domain_graph.domains_for_skill(skill)
            for dom in domains:
                # If they have a domain-specific skill, infer the domain label
                inferred.add(dom)
                # Infer subdomains or other skills associated with the domain
                # Let's not add ALL skills of that domain to avoid bloating,
                # but add domain/subdomain nodes themselves.

        return inferred
