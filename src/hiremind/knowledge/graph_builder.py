"""Graph Builder — constructs the NetworkX technology knowledge graph."""

import networkx as nx

from hiremind.domain.ontology_models import TechRelation
from hiremind.knowledge.ontology import SkillOntology


class GraphBuilder:
    """Builds a directed technology knowledge graph from ontology and tech relationships."""

    def __init__(
        self,
        ontology: SkillOntology,
        relations: list[TechRelation],
    ) -> None:
        self.ontology = ontology
        self.relations = relations

    def build(self) -> nx.DiGraph:
        """Build and return the NetworkX DiGraph."""
        g = nx.DiGraph()

        # 1. Add all skills/categories/concepts as nodes, and add IS_A parent relationships
        for skill_name in self.ontology.all_canonical_names():
            skill_node = self.ontology.get_skill(skill_name)
            if not skill_node:
                continue

            # Ensure current skill node exists
            if not g.has_node(skill_name):
                g.add_node(skill_name, node_type="skill", category=skill_node.category)

            # Add parent categories and IS_A relationships
            for parent in skill_node.parents:
                if not g.has_node(parent):
                    g.add_node(parent, node_type="category")

                # skill -> parent (is_a)
                g.add_edge(skill_name, parent, relation="IS_A")
                g.add_edge(parent, skill_name, relation="CHILD_OF")

        # 2. Add technology relationships
        for rel in self.relations:
            # Resolve to canonical names if possible
            src_canonical = self.ontology.canonical_name(rel.source) or rel.source
            tgt_canonical = self.ontology.canonical_name(rel.target) or rel.target

            # Ensure nodes exist
            if not g.has_node(src_canonical):
                g.add_node(src_canonical, node_type="skill")
            if not g.has_node(tgt_canonical):
                g.add_node(tgt_canonical, node_type="skill")

            # Add relation edge
            g.add_edge(src_canonical, tgt_canonical, relation=rel.relation_type)

            # Add some logical reverse relations if helpful
            if rel.relation_type == "PARENT_OF":
                g.add_edge(tgt_canonical, src_canonical, relation="CHILD_OF")
            elif rel.relation_type == "CHILD_OF":
                g.add_edge(tgt_canonical, src_canonical, relation="PARENT_OF")

        return g
