"""Parser Service — coordinates JD parsing, ontology enrichment, and weight assignment."""

from hiremind.domain.requirement import (
    ParsedRequirements,
    Requirement,
)
from hiremind.infrastructure.jd.parser import JDParser
from hiremind.services.ontology_service import OntologyService

# ──────────────────────────────────────────────────────────────────────────────
# Default weight table — maps requirement names to weights.
# Required skills default to 1.0, preferred to 0.5.
# Specific overrides can be added here for fine-grained control.
# ──────────────────────────────────────────────────────────────────────────────
_DEFAULT_WEIGHT_OVERRIDES: dict[str, float] = {
    # Core skills — highest weight.
    "Python": 1.0,
    "Retrieval": 1.0,
    "Embeddings": 1.0,
    "Ranking": 1.0,
    # Important supporting skills.
    "FAISS": 0.9,
    "Milvus": 0.9,
    "Evaluation Metrics": 0.9,
    "BGE": 0.9,
    "Sentence Transformers": 0.85,
    "BM25": 0.8,
    "Production ML": 0.8,
    # Nice-to-have skills.
    "LoRA": 0.5,
    "Fine Tuning": 0.5,
    "LLM": 0.5,
    "Learning to Rank": 0.5,
    "Open Source": 0.4,
    "Distributed Systems": 0.4,
    "HR Tech": 0.3,
    "Marketplace": 0.3,
}


class ParserService:
    """Coordinate JD parsing with ontology enrichment and weight assignment.

    This service:
        1. Invokes the rule-based ``JDParser`` to extract raw requirements.
        2. Normalises skill names via the ``OntologyService``.
        3. Enriches requirements with aliases from the ontology.
        4. Assigns weights using the weight engine.
    """

    def __init__(
        self,
        parser: JDParser,
        ontology_service: OntologyService,
        weight_overrides: dict[str, float] | None = None,
    ) -> None:
        self._parser = parser
        self._ontology = ontology_service
        self._weights = {**_DEFAULT_WEIGHT_OVERRIDES, **(weight_overrides or {})}

    def parse_and_enrich(self, cleaned_text: str) -> ParsedRequirements:
        """Parse the JD text and enrich requirements with ontology data."""
        raw = self._parser.parse(cleaned_text)

        enriched_required = tuple(self._enrich(r) for r in raw.required)
        enriched_preferred = tuple(self._enrich(r) for r in raw.preferred)

        return ParsedRequirements(
            required=enriched_required,
            preferred=enriched_preferred,
            negative=raw.negative,
            experience=raw.experience,
        )

    def _enrich(self, req: Requirement) -> Requirement:
        """Normalise name, add aliases, and apply weight."""
        canonical = self._ontology.normalize_skill(req.name)
        aliases = tuple(self._ontology.get_aliases(canonical))
        weight = self._weights.get(canonical, req.weight)

        return Requirement(
            id=req.id,
            name=canonical,
            category=req.category,
            weight=weight,
            required=req.required,
            aliases=aliases if aliases else req.aliases,
            evidence=req.evidence,
        )
