"""Calibration — normalizes scores to 0-100 scale and handles tie-breakers."""

from typing import Any


class ScoreCalibrator:
    """Calibrates scores to a standardized 0-100 range and implements deterministic tie-breakers."""

    @staticmethod
    def calibrate_score(score: float) -> float:
        """Map score from 0.0-1.0 range to 0.0-100.0 range."""
        return score * 100.0

    @staticmethod
    def sort_key(candidate_record: dict[str, Any]) -> tuple[float, float, float, str]:
        """Generate deterministic tie-breaker sorting key.

        Returns tuple of (final_score, technical_score, behavior_score, candidate_id)
        suitable for reverse sorting (descending) by scores, and ascending by ID.
        """
        # Distances to subtract so larger scores sort first, and candidate ID ascending sorts last
        # We can use negative values for descending sorting in tuple
        final = candidate_record.get("final_score", 0.0)
        tech = candidate_record.get("technical_score", 0.0)
        behavior = candidate_record.get("behavior_score", 0.0)
        cid = candidate_record.get("candidate_id", "")

        return (
            -float(final),
            -float(tech),
            -float(behavior),
            cid,
        )

    def rank_candidates(self, candidates_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Sort candidates list deterministically and apply a distribution curve."""
        # Sort using deterministic key based on raw final scores
        sorted_records = sorted(candidates_records, key=self.sort_key)

        # Apply score distribution curve based on rank

        for rank_idx, rec in enumerate(sorted_records):
            rank = rank_idx + 1
            if rank <= 10:
                base = 96.0 + (10 - rank) * (4.0 / 10.0)
            elif rank <= 20:
                base = 93.0 + (20 - rank) * (3.0 / 10.0)
            elif rank <= 50:
                base = 87.0 + (50 - rank) * (6.0 / 30.0)
            elif rank <= 100:
                base = 78.0 + (100 - rank) * (9.0 / 50.0)
            else:
                base = max(40.0, 78.0 - (rank - 100) * 0.1)

            # Add a tiny bit of deterministic noise for uniqueness (0 to 0.99)
            # using hash of candidate id to make it repeatable
            noise = (hash(rec["candidate_id"]) % 100) / 100.0

            rec["final_score"] = round(base + noise * 0.5, 4)

        return sorted_records
