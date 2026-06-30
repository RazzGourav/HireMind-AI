"""Domain Knowledge Graph — business domains, subdomains, and associated skills."""

import networkx as nx

from hiremind.domain.ontology_models import DomainNode
from hiremind.knowledge.ontology import SkillOntology


class DomainGraph:
    """Represents the business domain taxonomy and links to skills/technologies."""

    def __init__(self, domains: list[DomainNode], ontology: SkillOntology) -> None:
        self._ontology = ontology
        self._graph = nx.DiGraph()
        self._build_graph(domains)

    @property
    def graph(self) -> nx.DiGraph:
        """Return the raw DiGraph."""
        return self._graph

    def _build_graph(self, domains: list[DomainNode]) -> None:
        """Construct the NetworkX graph for business domains."""
        for dom in domains:
            # Add main domain node
            if not self._graph.has_node(dom.name):
                self._graph.add_node(dom.name, node_type="domain", label=dom.label)

            # Link skills to domain
            for skill in dom.skills:
                canonical_skill = self._ontology.canonical_name(skill) or skill
                if not self._graph.has_node(canonical_skill):
                    self._graph.add_node(canonical_skill, node_type="skill")
                self._graph.add_edge(dom.name, canonical_skill, relation="ASSOCIATED_SKILL")

            # Link subdomains to domain
            for subdomain in dom.subdomains:
                if not self._graph.has_node(subdomain):
                    self._graph.add_node(subdomain, node_type="subdomain")
                self._graph.add_edge(dom.name, subdomain, relation="HAS_SUBDOMAIN")

    def skills_in_domain(self, domain: str, include_subdomains: bool = True) -> set[str]:
        """Get all canonical skill names associated with a business domain."""
        domain_lower = domain.lower()
        if not self._graph.has_node(domain_lower):
            return set()

        skills = set()
        # Outgoing edges from domain
        for target, edge_data in self._graph[domain_lower].items():
            node_type = self._graph.nodes[target].get("node_type")
            if edge_data.get("relation") == "ASSOCIATED_SKILL":
                skills.add(target)
            elif include_subdomains and edge_data.get("relation") == "HAS_SUBDOMAIN":
                # Recurse into subdomain (which behaves like a domain node in terms of links)
                skills.update(self.skills_in_domain(target, include_subdomains=True))

        return skills

    def domains_for_skill(self, skill: str) -> set[str]:
        """Find all domains/subdomains associated with a specific skill."""
        canonical = self._ontology.canonical_name(skill) or skill
        if not self._graph.has_node(canonical):
            return set()

        domains = set()
        # Find predecessors pointing to this skill
        for pred in self._graph.predecessors(canonical):
            edge_data = self._graph[pred][canonical]
            if edge_data.get("relation") == "ASSOCIATED_SKILL":
                domains.add(pred)

        # Also find top-level domains for any subdomains found
        parent_domains = set()
        for dom in domains:
            node_type = self._graph.nodes[dom].get("node_type")
            if node_type == "subdomain":
                # find parent domains
                for pred in self._graph.predecessors(dom):
                    if self._graph[pred][dom].get("relation") == "HAS_SUBDOMAIN":
                        parent_domains.add(pred)
        domains.update(parent_domains)
        return domains

    def domain_overlap(self, domain_a: str, domain_b: str) -> float:
        """Calculate overlap between two domains based on shared skills (Jaccard similarity)."""
        skills_a = self.skills_in_domain(domain_a)
        skills_b = self.skills_in_domain(domain_b)
        if not skills_a or not skills_b:
            return 0.0
        intersection = skills_a & skills_b
        union = skills_a | skills_b
        return len(intersection) / len(union)
