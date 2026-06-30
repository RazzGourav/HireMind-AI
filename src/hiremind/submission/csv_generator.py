import csv
from pathlib import Path
from typing import Any


def generate_submission_csv(
    ranked_results: list[Any], output_path: Path, max_rows: int = 100
) -> Path:
    """
    Generates the official submission CSV format.
    Ensures exactly the required columns and format constraints.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # Required columns exactly as per the specification
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])

        for i, res in enumerate(ranked_results[:max_rows]):
            rank = i + 1
            if isinstance(res, dict):
                c_id = res.get("candidate_id")
                score = res.get("final_score", res.get("score", 0.0))
                reasoning = res.get(
                    "recruiter_summary", res.get("reasoning", "No reasoning provided.")
                )
            else:
                # Accommodate both Pydantic models (from API) and standard RetrievalResult
                c_id = getattr(res, "candidate_id", None)
                score = getattr(res, "final_score", getattr(res, "score", 0.0))

                # Fetch reasoning from Explanation object or use fallback
                reasoning = "No reasoning provided."
                explanation = getattr(res, "explanation", None)
                if explanation and getattr(explanation, "recruiter_summary", None):
                    reasoning = explanation.recruiter_summary

            score_formatted = f"{score:.4f}"

            # Replace inner newlines just in case to ensure valid CSV
            reasoning = reasoning.replace("\n", " ").strip()

            writer.writerow([c_id, rank, score_formatted, reasoning])

    return output_path
