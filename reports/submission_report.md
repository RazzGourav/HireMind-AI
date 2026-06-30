# HireMind AI - Submission Report

## Performance Metrics
- **Generated At**: 2026-06-30T13:25:13.467421
- **Dataset Version**: v1.0 (100,000 Candidates)
- **Total Candidates Ranked**: 100
- **Status**: Validated

## Architecture Overview
This submission utilizes a **Hybrid FAISS Dense Vector search** combined with a **Skill Ontology Graph**. The candidates are lazily loaded from Parquet to maintain a sub-8GB memory footprint, and re-ranked using an intelligent Reasoning Engine to ensure high semantic accuracy and explainability.

## Validation Status
The submission format has been validated against the official hackathon schema using the strict Validator wrapper.
