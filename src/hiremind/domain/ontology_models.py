"""Ontology domain models — value objects for the knowledge layer."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SkillNode:
    """A single skill in the ontology."""

    canonical_name: str
    aliases: tuple[str, ...] = ()
    parents: tuple[str, ...] = ()
    category: str = ""


@dataclass(frozen=True, slots=True)
class TechRelation:
    """A directed relationship between two technologies."""

    source: str
    target: str
    relation_type: str  # USES, DEPENDS_ON, EXTENDS, ALTERNATIVE_TO, RELATED_TO


@dataclass(frozen=True, slots=True)
class SynonymGroup:
    """A group of equivalent terms. First term is canonical."""

    canonical: str
    terms: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class DomainNode:
    """A business domain with associated skills."""

    name: str
    label: str = ""
    skills: tuple[str, ...] = ()
    subdomains: tuple[str, ...] = ()


@dataclass(slots=True)
class GraphFeatures:
    """Per-candidate graph-derived features for the ranking pipeline."""

    technology_diversity: float = 0.0
    ai_depth: float = 0.0
    backend_depth: float = 0.0
    cloud_depth: float = 0.0
    retrieval_depth: float = 0.0
    domain_breadth: float = 0.0
    graph_connectivity: float = 0.0
