import pickle
from collections.abc import Iterable
from pathlib import Path

import orjson
import pandas as pd

from hiremind.domain import Candidate
from hiremind.services.candidate_factory import CandidateFactory


class LazyCandidateStore:
    def __init__(self, parquet_path: Path):
        self.parquet_path = parquet_path
        dataframe = pd.read_parquet(parquet_path, columns=["candidate_id", "payload"])
        self._payloads = dict(zip(dataframe["candidate_id"], dataframe["payload"]))
        self._cache = {}

    def get(self, candidate_id: str) -> Candidate | None:
        if candidate_id in self._cache:
            return self._cache[candidate_id]
        if candidate_id in self._payloads:
            payload = self._payloads[candidate_id]
            cand = CandidateFactory.from_raw(orjson.loads(payload))
            self._cache[candidate_id] = cand
            return cand
        return None

    def __len__(self) -> int:
        return len(self._payloads)

    def __iter__(self):
        for candidate_id in self._payloads:
            yield self.get(candidate_id)


class FeatureCache:
    def __init__(self, cache_dir: str | Path = "feature_cache") -> None:
        self.cache_dir = Path(cache_dir)
        self.pickle_path = self.cache_dir / "candidate.pkl"
        self.parquet_path = self.cache_dir / "candidate.parquet"

    def save_candidates(self, candidates: Iterable[Candidate]) -> None:
        candidate_list = list(candidates)
        self.save_pickle(candidate_list)
        self.save_parquet(candidate_list)

    def save_pickle(self, candidates: list[Candidate]) -> Path:
        self.pickle_path.parent.mkdir(parents=True, exist_ok=True)
        with self.pickle_path.open("wb") as file:
            pickle.dump(candidates, file, protocol=pickle.HIGHEST_PROTOCOL)
        return self.pickle_path

    def load_pickle(self) -> list[Candidate]:
        with self.pickle_path.open("rb") as file:
            candidates = pickle.load(file)
        if not isinstance(candidates, list):
            raise TypeError(f"Invalid candidate cache at {self.pickle_path}")
        return candidates

    def save_parquet(self, candidates: list[Candidate]) -> Path:
        self.parquet_path.parent.mkdir(parents=True, exist_ok=True)
        rows = [
            {
                "candidate_id": candidate.candidate_id,
                "payload": orjson.dumps(CandidateFactory.to_raw(candidate)).decode("utf-8"),
            }
            for candidate in candidates
        ]
        pd.DataFrame(rows, columns=["candidate_id", "payload"]).to_parquet(
            self.parquet_path,
            index=False,
        )
        return self.parquet_path

    def load_parquet(self) -> list[Candidate]:
        dataframe = pd.read_parquet(self.parquet_path)
        return [
            CandidateFactory.from_raw(orjson.loads(payload))
            for payload in dataframe["payload"].tolist()
        ]

    def load_lazy_store(self) -> LazyCandidateStore:
        return LazyCandidateStore(self.parquet_path)
