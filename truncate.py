import os
import pickle
import sys

sys.path.append(os.path.abspath("src"))

print("Loading feature_cache/candidate.pkl...")
with open("feature_cache/candidate.pkl", "rb") as f:
    candidates = pickle.load(f)

print(f"Loaded {len(candidates)} candidates. Truncating to 1000...")
sliced = candidates[:1000]

# Fix missing attribute for dumping
for c in sliced:
    if hasattr(c, "signals") and c.signals is not None:
        if not hasattr(c.signals, "notice_period_days"):
            c.signals.notice_period_days = 30

with open("feature_cache/candidate.pkl", "wb") as f:
    pickle.dump(sliced, f)
print("Done candidate.pkl.")

print("Loading artifacts/candidate_summary.pkl...")
with open("artifacts/candidate_summary.pkl", "rb") as f:
    summary = pickle.load(f)

print(f"Loaded {len(summary)} summaries. Truncating...")
# If it's a dict, keep first 1000 items
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
