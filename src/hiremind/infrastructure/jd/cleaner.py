"""JD Text Cleaning Pipeline.

Normalises raw JD text for downstream parsing while preserving
meaningful technical entities (Python, FAISS, LoRA, BGE, etc.).
"""

import re
import unicodedata

# Default protected terms that must not be lowercased.
# The ontology YAML may extend this list at runtime.
_DEFAULT_PROTECTED_TERMS: frozenset[str] = frozenset(
    {
        "Python",
        "FAISS",
        "LoRA",
        "QLoRA",
        "BGE",
        "PEFT",
        "RAG",
        "LLM",
        "NLP",
        "NDCG",
        "MAP",
        "MRR",
        "AUC",
        "BM25",
        "TF-IDF",
        "ColBERT",
        "XGBoost",
        "LightGBM",
        "PyTorch",
        "TensorFlow",
        "LangChain",
        "MLflow",
        "CI/CD",
        "ETL",
        "AWS",
        "GCP",
        "SQL",
    }
)

# Common bullet-point characters to normalise.
_BULLET_PATTERN = re.compile(r"[•●○◦▪▸►‣⁃–—]\s*")

# Multiple whitespace (but not newlines).
_MULTI_SPACE = re.compile(r"[^\S\n]+")

# Multiple consecutive newlines.
_MULTI_NEWLINE = re.compile(r"\n{3,}")


class JDCleaner:
    """Deterministic text cleaning pipeline for Job Descriptions.

    Normalises whitespace, unicode, and bullet points while preserving
    meaningful technical entities. Cleaning is done in-place and returns
    a new string without mutating the original.
    """

    def __init__(self, protected_terms: frozenset[str] | None = None) -> None:
        self._protected = protected_terms or _DEFAULT_PROTECTED_TERMS
        # Build a lookup: lowercase → original casing.
        self._case_map: dict[str, str] = {t.lower(): t for t in self._protected}

    def clean(self, text: str) -> str:
        """Run the full cleaning pipeline.

        Steps:
            1. Unicode normalisation (NFKC)
            2. Bullet point normalisation
            3. Whitespace normalisation
            4. Newline normalisation
            5. Strip leading/trailing whitespace
            6. Lowercase with protected-term restoration
        """
        text = self._normalise_unicode(text)
        text = self._normalise_bullets(text)
        text = self._normalise_whitespace(text)
        text = self._normalise_newlines(text)
        text = text.strip()
        text = self._lowercase_with_protection(text)
        return text

    @staticmethod
    def _normalise_unicode(text: str) -> str:
        """NFKC normalisation decomposes then recomposes characters."""
        return unicodedata.normalize("NFKC", text)

    @staticmethod
    def _normalise_bullets(text: str) -> str:
        """Replace bullet characters with a standard dash."""
        return _BULLET_PATTERN.sub("- ", text)

    @staticmethod
    def _normalise_whitespace(text: str) -> str:
        """Collapse multiple spaces/tabs into a single space."""
        return _MULTI_SPACE.sub(" ", text)

    @staticmethod
    def _normalise_newlines(text: str) -> str:
        """Collapse 3+ consecutive newlines into 2."""
        return _MULTI_NEWLINE.sub("\n\n", text)

    def _lowercase_with_protection(self, text: str) -> str:
        """Lowercase the text but restore casing for protected terms.

        Strategy: lowercase everything, then find occurrences of protected
        terms (by their lowercase form) and replace them back.
        """
        lowered = text.lower()

        # Sort by length descending so longer terms are restored first
        # (e.g. "TF-IDF" before "TF").
        for lower_form in sorted(self._case_map, key=len, reverse=True):
            original = self._case_map[lower_form]
            if lower_form in lowered:
                lowered = lowered.replace(lower_form, original)

        return lowered
