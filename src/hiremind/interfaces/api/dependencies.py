"""Dependency Injection for FastAPI application."""

from functools import lru_cache
from pathlib import Path
from typing import Any

from hiremind.infrastructure import load_config
from hiremind.infrastructure.cache import FeatureCache
from hiremind.knowledge.graph_repository import GraphRepository
from hiremind.ranking.ranking_service import RankingService
from hiremind.retrieval.embedding_cache import EmbeddingCache
from hiremind.retrieval.embedding_encoder import DenseEmbeddingEncoder
from hiremind.retrieval.faiss_index import FaissIndex
from hiremind.retrieval.filter_engine import StructuredFilterEngine
from hiremind.retrieval.hybrid_retriever import HybridRetriever
from hiremind.retrieval.query_encoder import QueryEncoder
from hiremind.retrieval.retrieval_service import RetrievalService


class AppState:
    """Singleton holding heavy loaded models and indices."""

    def __init__(self):
        self.config = load_config()
        self.artifacts_dir = Path("artifacts")
        self.candidates: list[Any] = []
        self.candidate_features: dict[str, Any] = {}
        self.ontology = None
        self.faiss_index = None
        self.embedding_cache = None
        self.candidate_ids: list[str] = []

    def load_all(self):
        """Load all offline models into memory."""
        # 1. Candidates
        cache_dir = self.config.get("dataset", {}).get("cache_dir", "feature_cache")
        feature_cache = FeatureCache(cache_dir)
        self.candidates = feature_cache.load_lazy_store()

        # 2. Features
        import pickle

        with (self.artifacts_dir / "candidate_summary.pkl").open("rb") as f:
            self.candidate_features = pickle.load(f)

        # 3. Ontology
        graph_repo = GraphRepository(str(self.artifacts_dir))
        self.ontology = graph_repo.load_ontology()

        # 4. Embeddings
        self.faiss_index = FaissIndex(dimension=384)
        self.faiss_index.load(self.artifacts_dir / "faiss" / "index.bin")

        self.embedding_cache = EmbeddingCache(str(self.artifacts_dir / "embeddings"))
        self.candidate_ids, _ = self.embedding_cache.load_candidates()


@lru_cache()
def get_app_state() -> Any:
    state = AppState()
    state.load_all()
    return state


def get_ranking_service() -> Any:
    return RankingService(artifacts_dir="artifacts")


def get_retrieval_service(state: Any = None) -> Any:
    if state is None:
        state = get_app_state()

    dense_encoder = DenseEmbeddingEncoder()
    query_encoder = QueryEncoder(dense_encoder)
    retriever = HybridRetriever(state.faiss_index, state.ontology)
    filter_engine = StructuredFilterEngine()

    return RetrievalService(
        retriever=retriever,
        query_encoder=query_encoder,
        filter_engine=filter_engine,
        embedding_cache=state.embedding_cache,
        faiss_index=state.faiss_index,
        candidate_store=state.candidates,
        candidate_ids=state.candidate_ids,
    )
