"""Candidate Encoder — formats and embeds candidates into dense vector space."""

import numpy as np

from hiremind.domain.candidate import Candidate
from hiremind.retrieval.embedding_encoder import DenseEmbeddingEncoder


class CandidateEncoder:
    """Orchestrates building raw textual descriptions for candidates and embedding them."""

    def __init__(self, encoder: DenseEmbeddingEncoder) -> None:
        self.encoder = encoder

    def format_candidate(self, candidate: Candidate) -> str:
        """Construct a dense, structured string representing the candidate's profile."""
        profile = candidate.profile
        parts = []

        # 1. Headline & Title
        if profile.headline:
            parts.append(f"Headline: {profile.headline}")
        if profile.current_title:
            parts.append(f"Current Role: {profile.current_title}")

        # 2. Professional Summary
        if profile.summary:
            parts.append(f"Summary: {profile.summary}")

        # 3. Skills list
        if candidate.skills:
            skills_str = ", ".join(s.name for s in candidate.skills)
            parts.append(f"Skills: {skills_str}")

        # 4. Career History
        if candidate.career_history:
            career_parts = []
            for job in candidate.career_history:
                job_desc = f"Job title: {job.title or 'Unknown'}"
                if job.company:
                    job_desc += f" at {job.company}"
                if job.industry:
                    job_desc += f" (Industry: {job.industry})"
                if job.description:
                    job_desc += f" - {job.description}"
                career_parts.append(job_desc)
            parts.append("Work History: " + "; ".join(career_parts))

        # 5. Education
        if candidate.education:
            edu_parts = []
            for edu in candidate.education:
                edu_desc = f"Degree: {edu.degree or 'Degree'} in {edu.field_of_study or 'Field'}"
                if edu.institution:
                    edu_desc += f" from {edu.institution}"
                edu_parts.append(edu_desc)
            parts.append("Education: " + "; ".join(edu_parts))

        return "\n".join(parts)

    def encode_candidates(self, candidates: list[Candidate], batch_size: int = 128) -> np.ndarray:
        """Format and batch encode a list of candidates in chunks to prevent memory OOM."""
        texts = [self.format_candidate(cand) for cand in candidates]

        chunk_size = 5000
        embeddings_list = []

        from tqdm import tqdm

        for i in tqdm(range(0, len(texts), chunk_size), desc="Encoding candidates", unit="chunk"):
            chunk_texts = texts[i : i + chunk_size]
            chunk_embs = self.encoder.encode(
                chunk_texts, batch_size=batch_size, use_multi_process=False
            )
            embeddings_list.append(chunk_embs)

        return np.vstack(embeddings_list)
