"""CLI command to build and cache the Knowledge Intelligence Layer artifacts."""

import time

from hiremind.infrastructure import logger
from hiremind.knowledge import (
    DomainGraph,
    GraphBuilder,
    GraphRepository,
    GraphVisualizer,
    OntologyConfigLoader,
    SkillOntology,
    SkillSimilarityEngine,
    SynonymEngine,
    TechnologyGraph,
)


def main() -> None:
    """Build ontology, technology graph, domain graph, similarity matrix and visual representation."""
    logger.info("Initializing Knowledge Intelligence Layer Build...")
    start_time = time.perf_counter()

    artifacts_dir = "artifacts"
    loader = OntologyConfigLoader()

    # 1. Load configurations
    logger.info("Loading configurations...")
    skills = loader.load_skills()
    protected = loader.load_protected_terms()
    synonyms = loader.load_synonyms()
    relations = loader.load_relationships()
    domains = loader.load_domains()

    # 2. Build ontology & engines
    logger.info("Building Skill Ontology & Synonym Engine...")
    synonym_engine = SynonymEngine(synonyms)
    ontology = SkillOntology(skills, protected, synonym_engine)

    logger.info("Building Technology Knowledge Graph...")
    tech_builder = GraphBuilder(ontology, relations)
    tech_g = tech_builder.build()
    tech_graph = TechnologyGraph(tech_g)

    logger.info("Building Domain Knowledge Graph...")
    domain_graph = DomainGraph(domains, ontology)

    # 3. Cache structures
    logger.info("Caching graphs to artifacts...")
    repo = GraphRepository(artifacts_dir)
    repo.save_ontology(ontology)
    repo.save_tech_graph(tech_g)
    repo.save_domain_graph(domain_graph.graph)

    # 4. Compute and save similarity matrix
    logger.info("Computing Skill Similarity Matrix (this may take a few seconds)...")
    sim_start = time.perf_counter()
    similarity_engine = SkillSimilarityEngine(tech_graph, ontology)
    similarity_engine.compute_matrix()
    similarity_engine.save_matrix("artifacts/skill_similarity_matrix.parquet")
    sim_elapsed = time.perf_counter() - sim_start
    logger.info("Similarity matrix computed and saved in {:.2f}s.", sim_elapsed)

    # 5. Generate visual representation
    logger.info("Generating graph visualization...")
    vis_start = time.perf_counter()
    visualizer = GraphVisualizer(tech_g)
    visualizer.visualize("docs/images/knowledge_graph.png")
    vis_elapsed = time.perf_counter() - vis_start
    logger.info("Graph visualization generated and saved in {:.2f}s.", vis_elapsed)

    elapsed = time.perf_counter() - start_time
    logger.info("Knowledge Intelligence Layer built successfully in {:.2f}s.", elapsed)
    logger.info("Generated artifacts:")
    logger.info("  - artifacts/ontology.pkl")
    logger.info("  - artifacts/knowledge_graph.pkl")
    logger.info("  - artifacts/domain_graph.pkl")
    logger.info("  - artifacts/skill_similarity_matrix.parquet")
    logger.info("  - docs/images/knowledge_graph.png")


if __name__ == "__main__":
    main()
