import csv
from pathlib import Path
from typing import List


class SubmissionValidator:
    """Validates the official CSV submission file against the hackathon rules."""

    def __init__(self, csv_path: Path):
        self.csv_path = csv_path
        self.errors: List[str] = []
        self.expected_columns = ["candidate_id", "rank", "score", "reasoning"]

    def validate(self) -> bool:
        """Runs all validation rules against the CSV."""
        if not self.csv_path.exists():
            self.errors.append(f"Submission file {self.csv_path} does not exist.")
            return False

        with self.csv_path.open("r", encoding="utf-8") as f:
            reader = csv.reader(f)
            try:
                headers = next(reader)
            except StopIteration:
                self.errors.append("File is empty.")
                return False

            if headers != self.expected_columns:
                self.errors.append(
                    f"Invalid columns. Expected {self.expected_columns}, got {headers}"
                )

            rows = list(reader)

            if len(rows) != 100:
                self.errors.append(f"Expected exactly 100 candidates, got {len(rows)}")

            seen_ranks = set()
            seen_cids = set()

            for i, row in enumerate(rows):
                line_num = i + 2
                if len(row) != 4:
                    self.errors.append(f"Line {line_num}: Expected 4 columns, got {len(row)}")
                    continue

                cid, rank_str, score_str, reasoning = row

                # Rank validation
                try:
                    rank = int(rank_str)
                    if rank < 1 or rank > 100:
                        self.errors.append(
                            f"Line {line_num}: Rank must be between 1-100, got {rank}"
                        )
                    if rank in seen_ranks:
                        self.errors.append(f"Line {line_num}: Duplicate rank {rank}")
                    seen_ranks.add(rank)
                except ValueError:
                    self.errors.append(f"Line {line_num}: Invalid rank format '{rank_str}'")

                # Candidate ID validation
                if not cid.startswith("CAND_"):
                    self.errors.append(
                        f"Line {line_num}: Invalid candidate_id format '{cid}', expected CAND_XXX"
                    )
                if cid in seen_cids:
                    self.errors.append(f"Line {line_num}: Duplicate candidate_id {cid}")
                seen_cids.add(cid)

                # Score validation
                try:
                    score = float(score_str)
                    if score < 0 or score > 100:
                        self.errors.append(
                            f"Line {line_num}: Score out of bounds [0, 100], got {score}"
                        )
                except ValueError:
                    self.errors.append(f"Line {line_num}: Invalid score format '{score_str}'")

                # Reasoning validation
                if not reasoning or len(reasoning.strip()) < 10:
                    self.errors.append(f"Line {line_num}: Reasoning is missing or too short")

        return len(self.errors) == 0

    def generate_report(self, report_path: Path) -> None:
        """Dumps validation errors to a text report."""
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with report_path.open("w", encoding="utf-8") as f:
            if not self.errors:
                f.write("VALIDATION SUCCESS\nNo errors found. Output matches official schema.")
            else:
                f.write(f"VALIDATION FAILED\nFound {len(self.errors)} errors:\n\n")
                for err in self.errors:
                    f.write(f"- {err}\n")
