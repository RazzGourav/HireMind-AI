import os
import sys

sys.path.append(os.path.abspath("src"))
from hiremind.infrastructure.cache.feature_cache import FeatureCache

cache = FeatureCache("feature_cache")

print("Loading from parquet...")
candidates = cache.load_parquet()

print(f"Loaded {len(candidates)} candidates from parquet.")

# Fix missing attribute for dumping
for c in candidates:
    if hasattr(c, "signals") and c.signals is not None:
        if not hasattr(c.signals, "notice_period_days"):
            c.signals.notice_period_days = 30

print("Saving full candidate.pkl...")
cache.save_pickle(candidates)
print("Saved candidate.pkl successfully with full dataset!")
