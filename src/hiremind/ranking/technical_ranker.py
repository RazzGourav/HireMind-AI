"""Technical Ranker — evaluates technical skill alignment and production experience."""

from hiremind.domain.candidate import Candidate
from hiremind.domain.candidate_features import CandidateFeatures
from hiremind.domain.requirement import ParsedRequirements


class TechnicalRanker:
    """Computes technical score based on requirement coverage and production signals."""

    def score(
        self,
        candidate: Candidate,
        features: CandidateFeatures,
        requirements: ParsedRequirements,
    ) -> float:
        """Score candidate's technical profile (0.0 to 1.0)."""
        candidate_skills = {s.name.lower() for s in candidate.skills}

        # Calculate required skill coverage
        req_score = 1.0
        if requirements.required:
            reqs = [r.name.lower() for r in requirements.required]
            matching_reqs = [r for r in reqs if r in candidate_skills]
            req_score = len(matching_reqs) / len(reqs) if reqs else 1.0

        # Calculate preferred skill coverage
        pref_score = 1.0
        if requirements.preferred:
            prefs = [p.name.lower() for p in requirements.preferred]
            matching_prefs = [p for p in prefs if p in candidate_skills]
            pref_score = len(matching_prefs) / len(prefs) if prefs else 1.0

        # Production evidence score from features
        prod_score = features.production_score if hasattr(features, "production_score") else 0.0

        # Blend: 50% required skills + 20% preferred skills + 30% production score
        raw = 0.5 * req_score + 0.2 * pref_score + 0.3 * prod_score
        return round(min(max(raw, 0.0), 1.0), 3)
