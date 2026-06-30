"""Candidate Intelligence Service — the main pipeline orchestrator.

Pipeline: Candidate → Normalize → Career → Skills → Evidence → Graph → Features
"""

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from joblib import Parallel, delayed
from tqdm import tqdm

from hiremind.domain.candidate import Candidate
from hiremind.domain.candidate_features import CandidateFeatures
from hiremind.infrastructure.cache.candidate_feature_store import CandidateFeatureStore
from hiremind.infrastructure.candidate.consistency import score_consistency
from hiremind.infrastructure.candidate.education import analyze_education
from hiremind.infrastructure.candidate.feature_builder import build_feature_vector
from hiremind.infrastructure.candidate.skills import analyze_skills
from hiremind.infrastructure.candidate.timeline import analyze_career
from hiremind.knowledge import (
    DomainGraph,
    GraphBuilder,
    GraphFeatureExtractor,
    GraphRepository,
    InferenceEngine,
    OntologyConfigLoader,
    SkillNormalizer,
    SkillOntology,
    SynonymEngine,
    TechnologyGraph,
)
from hiremind.services.evidence_service import EvidenceService
from hiremind.services.normalization_service import NormalizationService
from hiremind.services.ontology_service import OntologyService


@dataclass(frozen=True, slots=True)
class CandidateProcessResult:
    """Summary of the candidate processing pipeline output."""

    total_processed: int
    features_path: Path
    summary_path: Path


class CandidateIntelligenceService:
    """Orchestrate the full candidate intelligence pipeline.

    For each candidate:
        1. Normalize title + skills
        2. Analyze career timeline
        3. Analyze skills with ontology
        4. Score evidence (production, leadership, growth)
        5. Score consistency
        6. Score education
        7. Compute graph-based semantic features & infer capabilities
        8. Build feature vector

    Outputs a list of ``CandidateFeatures`` and persists to the feature store.
    """

    def __init__(
        self,
        ontology_service: OntologyService,
        artifacts_dir: str | Path = "artifacts",
    ) -> None:
        self._ontology_service = ontology_service
        self._normalization = NormalizationService(ontology_service)
        self._evidence = EvidenceService()
        self._store = CandidateFeatureStore(artifacts_dir)
        self._repo = GraphRepository(artifacts_dir)

        # Initialize knowledge layer (caching enabled)
        self._init_knowledge_layer()

    def _init_knowledge_layer(self) -> None:
        """Load graphs/ontology from pickle cache or build them if missing."""
        try:
            # Try to load cached graphs
            raw_ontology = self._repo.load_ontology()
            raw_tech = self._repo.load_tech_graph()
            raw_domain = self._repo.load_domain_graph()

            self._ontology = raw_ontology
            self._tech_graph = TechnologyGraph(raw_tech)
            self._domain_graph = DomainGraph([], self._ontology)
            self._domain_graph._graph = raw_domain
        except Exception:
            # Cache miss/staleness -> rebuild from YAML files
            loader = OntologyConfigLoader()
            skills = loader.load_skills()
            protected = loader.load_protected_terms()
            synonyms = loader.load_synonyms()
            relations = loader.load_relationships()
            domains = loader.load_domains()

            # Instantiate components
            synonym_engine = SynonymEngine(synonyms)
            self._ontology = SkillOntology(skills, protected, synonym_engine)

            builder = GraphBuilder(self._ontology, relations)
            tech_g = builder.build()
            self._tech_graph = TechnologyGraph(tech_g)

            self._domain_graph = DomainGraph(domains, self._ontology)

            # Save to cache
            self._repo.save_ontology(self._ontology)
            self._repo.save_tech_graph(tech_g)
            self._repo.save_domain_graph(self._domain_graph.graph)

        self._normalizer = SkillNormalizer(self._ontology)
        self._inference = InferenceEngine(self._normalizer, self._tech_graph, self._domain_graph)
        self._extractor = GraphFeatureExtractor(
            self._tech_graph, self._domain_graph, self._ontology
        )

    def process(
        self,
        candidates: Iterable[Candidate],
        *,
        show_progress: bool = True,
    ) -> CandidateProcessResult:
        """Run the full pipeline on all candidates.

        Args:
            candidates: Iterable of Candidate domain objects.
            show_progress: Whether to show a tqdm progress bar.

        Returns:
            A CandidateProcessResult with artifact paths.
        """
        candidate_list = list(candidates)
        features: list[CandidateFeatures] = []

        iterator: Iterable[Candidate] = candidate_list
        if show_progress:
            iterator = tqdm(candidate_list, desc="Processing candidates", unit="cand")

        # Run the CPU-bound candidate analysis using joblib in parallel
        # n_jobs=-1 will utilize all available cores
        # Using loky (the default joblib backend) or threading backend is safe.
        # loky is highly suitable since this is mostly CPU-bound string matching and traversal.
        # We wrap the candidate processing in a list builder.
        features = Parallel(n_jobs=-1, prefer="processes")(
            delayed(self._process_one)(candidate) for candidate in iterator
        )

        # Persist.
        features_path = self._store.save_features(features)
        summary_path = self._store.save_summaries(features)

        return CandidateProcessResult(
            total_processed=len(features),
            features_path=features_path,
            summary_path=summary_path,
        )

    def _process_one(self, candidate: Candidate) -> CandidateFeatures:
        """Process a single candidate through all analysis modules."""
        # 1. Normalize skills.
        normalized_skills = self._normalization.normalize_candidate_skills(candidate)

        # 2. Career analysis.
        career_summary = analyze_career(candidate.career_history)

        # Career score: blend of stability + experience depth.
        experience_depth = min(career_summary.total_experience_months / 120.0, 1.0)
        career_score = 0.5 * career_summary.career_stability + 0.5 * experience_depth

        # 3. Skill analysis.
        skill_summary = analyze_skills(candidate, self._ontology_service)

        # Technical score: based on AI/ML skill count + confidence.
        ai_ratio = skill_summary.ai_ml_skill_count / max(skill_summary.total_skills, 1)
        avg_confidence = sum(s.confidence for s in skill_summary.skills) / max(
            len(skill_summary.skills), 1
        )
        technical_score = 0.5 * min(ai_ratio * 2.0, 1.0) + 0.5 * avg_confidence

        # 4. Evidence scoring.
        evidence = self._evidence.score(candidate)

        # 5. Consistency.
        consistency = score_consistency(candidate)

        # 6. Education.
        education = analyze_education(candidate.education)

        # 8. Graph-based feature extraction and semantic inference.
        inferred = self._inference.infer_capabilities(normalized_skills)
        combined_skills = list(dict.fromkeys(normalized_skills + sorted(inferred)))

        graph_features = self._extractor.extract(normalized_skills)

        # 7. Build feature vector.
        feature_vector = build_feature_vector(
            candidate_id=candidate.candidate_id,
            technical_score=round(technical_score, 3),
            career_score=round(career_score, 3),
            leadership_score=evidence["leadership_score"],
            production_score=evidence["production_score"],
            growth_score=evidence["growth_score"],
            consistency_score=consistency,
            education_score=education,
            career_summary=career_summary,
            skill_summary=skill_summary,
            graph_features=graph_features,
        )

        return CandidateFeatures(
            candidate_id=candidate.candidate_id,
            technical_score=round(technical_score, 3),
            career_score=round(career_score, 3),
            leadership_score=evidence["leadership_score"],
            production_score=evidence["production_score"],
            growth_score=evidence["growth_score"],
            consistency_score=consistency,
            education_score=education,
            career_summary=career_summary,
            skill_summary=skill_summary,
            normalized_skills=combined_skills,
            feature_vector=feature_vector,
        )
