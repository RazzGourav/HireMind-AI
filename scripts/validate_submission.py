import argparse
import sys
from pathlib import Path

# Ensure src is in PYTHONPATH
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from hiremind.submission.validator import SubmissionValidator


def main():
    parser = argparse.ArgumentParser(description="Validate Hackathon CSV submission")
    parser.add_argument(
        "--csv",
        type=str,
        default="outputs/submission/submission.csv",
        help="Path to submission.csv",
    )
    parser.add_argument(
        "--report", type=str, default="reports/validation_report.txt", help="Path for report output"
    )
    args = parser.parse_args()

    validator = SubmissionValidator(Path(args.csv))
    is_valid = validator.validate()

    validator.generate_report(Path(args.report))

    if is_valid:
        print(f"[PASS] Validation successful. {args.csv} is ready for submission.")
        sys.exit(0)
    else:
        print(f"[FAIL] Validation failed with {len(validator.errors)} errors.")
        for err in validator.errors[:5]:
            print(f"  - {err}")
        if len(validator.errors) > 5:
            print(f"  ... and {len(validator.errors) - 5} more. See {args.report}")
        sys.exit(1)


if __name__ == "__main__":
    main()
