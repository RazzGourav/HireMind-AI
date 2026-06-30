import os
import pickle
import sys

sys.path.append(os.path.abspath("src"))
from hiremind.infrastructure.cache.feature_cache import FeatureCache

cache = FeatureCache("feature_cache")

print("Loading from parquet...")
candidates = cache.load_parquet()

print(f"Loaded {len(candidates)} candidates from parquet. Slicing to 1000...")
sliced = candidates[:1000]

print("Saving to pickle...")
cache.save_pickle(sliced)
print("Saved candidate.pkl successfully!")

print("Loading artifacts/candidate_summary.pkl...")
with open("artifacts/candidate_summary.pkl", "rb") as f:
    summary = pickle.load(f)

print(f"Loaded {len(summary)} summaries. Truncating...")
if isinstance(summary, dict):
    keys = list(summary.keys())[:1000]
    mini_summary = {k: summary[k] for k in keys}
elif isinstance(summary, list):
    mini_summary = summary[:1000]
else:
    mini_summary = summary

with open("artifacts/candidate_summary.pkl", "wb") as f:
    pickle.dump(mini_summary, f)
print("Done candidate_summary.pkl.")
