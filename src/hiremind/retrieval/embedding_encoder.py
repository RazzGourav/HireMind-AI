"""Dense Embedding Encoder wrapper around SentenceTransformers."""

import numpy as np
from sentence_transformers import SentenceTransformer


class DenseEmbeddingEncoder:
    """Wrapper class to handle model loading, batch text encoding and vector normalization."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        self.model_name = model_name
        self._model: SentenceTransformer | None = None

    def _ensure_model(self) -> SentenceTransformer:
        """Load the model lazily for speed in other execution flows."""
        if self._model is None:
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def encode(
        self, texts: list[str] | str, batch_size: int = 64, use_multi_process: bool = False
    ) -> np.ndarray:
        """Encode list of texts or single text string into normalized float32 embeddings."""
        model = self._ensure_model()
        is_single = isinstance(texts, str)
        input_texts = [texts] if is_single else list(texts)

        if use_multi_process and not is_single and len(input_texts) > 1000:
            pool = model.start_multi_process_pool()
            embeddings = model.encode_multi_process(
                input_texts,
                pool=pool,
                batch_size=batch_size,
            )
            model.stop_multi_process_pool(pool)
            # L2 Normalize
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            embeddings = embeddings / np.maximum(norms, 1e-12)
        else:
            # Generate embeddings
            embeddings = model.encode(
                input_texts,
                batch_size=batch_size,
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=True,  # Normalized for cosine distance / inner product
            )

        return embeddings[0] if is_single else embeddings
