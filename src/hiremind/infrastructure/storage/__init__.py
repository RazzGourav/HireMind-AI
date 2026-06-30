from typing import Any

from hiremind.infrastructure.storage.jsonl_loader import JsonlLoader, JsonlRecord

__all__ = ["CandidateRepository", "JsonlLoader", "JsonlRecord"]


def __getattr__(name: str) -> Any:
    if name == "CandidateRepository":
        from hiremind.infrastructure.storage.repository import CandidateRepository

        return CandidateRepository
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
