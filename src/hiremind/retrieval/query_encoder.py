"""Query Encoder — formats and embeds job descriptions into query vectors."""

import numpy as np

from hiremind.domain.jd import JobDescription
from hiremind.retrieval.embedding_encoder import DenseEmbeddingEncoder


class QueryEncoder:
    """Orchestrates formatting the parsed Job Description and embedding it into the query vector."""

    def __init__(self, encoder: DenseEmbeddingEncoder) -> None:
        self.encoder = encoder

    def format_jd(self, jd: JobDescription) -> str:
        """Construct a dense, structured string representing the job description query."""
        parts = []

        title = getattr(jd, "title", None)
        summary = getattr(jd, "summary", None)
        responsibilities = getattr(jd, "responsibilities", None)
        requirements = getattr(jd, "requirements", None)

        if title:
            parts.append(f"Job Title: {title}")
        if summary:
            parts.append(f"Summary: {summary}")

        if responsibilities:
            resp_str = " ".join(responsibilities)
            parts.append(f"Responsibilities: {resp_str}")

        if requirements and requirements.required:
            req_skills = ", ".join(r.name for r in requirements.required)
            parts.append(f"Required Skills: {req_skills}")

        if requirements and requirements.preferred:
            pref_skills = ", ".join(r.name for r in requirements.preferred)
            parts.append(f"Preferred Skills: {pref_skills}")

        if not parts:
            return jd.cleaned_text

        return "\n".join(parts)

    def encode_query(self, jd: JobDescription) -> np.ndarray:
        """Format and encode a Job Description to a dense query vector."""
        text = self.format_jd(jd)
        return self.encoder.encode(text)
