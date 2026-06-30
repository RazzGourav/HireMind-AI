from pathlib import Path

from hiremind.infrastructure.storage import JsonlLoader


def test_jsonl_loader_streams_valid_and_invalid_records(tmp_path: Path) -> None:
    dataset_path = tmp_path / "candidates.jsonl"
    dataset_path.write_text(
        '{"candidate_id": "CAND_001"}\n' "not-json\n" "[]\n" "\n" '{"candidate_id": "CAND_002"}\n',
        encoding="utf-8",
    )

    records = list(JsonlLoader(dataset_path).stream())

    assert len(records) == 4
    assert records[0].payload == {"candidate_id": "CAND_001"}
    assert records[1].error == "Invalid JSON: Expecting value"
    assert records[2].error == "JSONL record must be an object"
    assert records[3].payload == {"candidate_id": "CAND_002"}
