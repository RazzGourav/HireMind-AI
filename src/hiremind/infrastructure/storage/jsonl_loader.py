import json
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class JsonlRecord:
    line_number: int
    payload: dict[str, Any] | None
    error: str | None = None


class JsonlLoader:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def stream(self) -> Iterator[JsonlRecord]:
        with self.path.open("r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                if not line.strip():
                    continue

                try:
                    payload = json.loads(line)
                except json.JSONDecodeError as exc:
                    yield JsonlRecord(
                        line_number=line_number,
                        payload=None,
                        error=f"Invalid JSON: {exc.msg}",
                    )
                    continue

                if not isinstance(payload, dict):
                    yield JsonlRecord(
                        line_number=line_number,
                        payload=None,
                        error="JSONL record must be an object",
                    )
                    continue

                yield JsonlRecord(line_number=line_number, payload=payload)
