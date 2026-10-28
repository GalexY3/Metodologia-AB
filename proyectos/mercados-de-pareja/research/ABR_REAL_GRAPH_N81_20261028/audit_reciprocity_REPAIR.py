#!/usr/bin/env python3
"""N81 frozen aggregate-only graph audit. Never executes bundled dataset code."""
import hashlib
import io
import json
import sys
import zipfile
from collections import Counter
from pathlib import Path
import numpy as np
import pandas as pd

ZIP = Path(sys.argv[1] if len(sys.argv) > 1 else "/mnt/data/sjjy_data.zip")
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else "/mnt/data/N81_AGGREGATES.json")
EXPECTED = "23cff03451b13f94354d875e777f60e1c63224829f42b8adf9d73d7563812e24"
sha = hashlib.sha256(ZIP.read_bytes()).hexdigest()
assert sha == EXPECTED, "Input archive hash does not match frozen prereg"
with zipfile.ZipFile(ZIP) as z:
    df = pd.read_csv(z.open("sjjy_data/relations.csv"), low_memory=False)
    train = pd.read_csv(z.open("sjjy_data/train_data.csv"))
    test = pd.read_csv(z.open("sjjy_data/test_data.csv"))
assert list(df.columns) == [":START_ID(User)", ":END_ID(User)", ":TYPE"]
all_action_counts = {str(k): int(v) for k,v in df.iloc[:,2].value_counts().items()}
df = df.loc[df.iloc[:,2].isin(["click", "msg"])].copy()
assert len(df) == all_action_counts.get("click",0) + all_action_counts.get("msg",0), "action filter mismatch"
a = pd.to_numeric(df.iloc[:, 0], errors="raise").to_numpy(dtype=np.int64)
b = pd.to_numeric(df.iloc[:, 1], errors="raise").to_numpy(dtype=np.int64)
codes = np.unique(np.concatenate((a, b)))
assert len(codes) < 2 ** 32
u = np.searchsorted(codes, a).astype(np.uint64)
v = np.searchsorted(codes, b).astype(np.uint64)
MASK = np.uint64((1 << 32) - 1)
def reciprocal(us, vs):
    ok = us != vs
    edges = np.unique((us[ok] << np.uint64(32)) | vs[ok])
    rev = ((edges & MASK) << np.uint64(32)) | (edges >> np.uint64(32))
    ix = np.searchsorted(edges, rev)
    hits = (ix < len(edges)) & (edges[np.minimum(ix, len(edges)-1)] == rev)
    return {"unique_arcs": int(len(edges)), "reciprocated_directed_arcs": int(hits.sum()),
            "mutual_unordered_pairs": int(hits.sum() // 2),
            "reciprocal_arc_fraction": float(hits.mean()),
            "event_self_loops": int((~ok).sum()),
            "duplicate_event_arcs": int(ok.sum() - len(edges))}
obs = reciprocal(u, v)
rng = np.random.default_rng(20261028)
nulls = []
for k in range(30):
    permuted = v[rng.permutation(len(v))]
    nulls.append(reciprocal(u, permuted))
null_fracs = [n["reciprocal_arc_fraction"] for n in nulls]
def label_check(tbl):
    if not {"user","target_user","label"}.issubset(tbl.columns):
        return {"compatible_columns": False}
    ua = pd.to_numeric(tbl["user"], errors="coerce").to_numpy()
    ub = pd.to_numeric(tbl["target_user"], errors="coerce").to_numpy()
    la = pd.to_numeric(tbl["label"], errors="coerce").to_numpy()
    edges = np.unique((u[u != v] << np.uint64(32)) | v[u != v])
    ca = np.searchsorted(codes, ua).astype(np.uint64)
    cb = np.searchsorted(codes, ub).astype(np.uint64)
    ka = (ca << np.uint64(32)) | cb
    kb = (cb << np.uint64(32)) | ca
    ia = np.searchsorted(edges, ka); ib = np.searchsorted(edges, kb)
    ab = (ia < len(edges)) & (edges[np.minimum(ia, len(edges)-1)] == ka)
    ba = (ib < len(edges)) & (edges[np.minimum(ib, len(edges)-1)] == kb)
    constructed = (ab & ba).astype(int)
    return {"rows": int(len(tbl)), "labels_0": int((la == 0).sum()),
            "labels_1": int((la == 1).sum()),
            "same_label_as_full_graph_reciprocity": int((la == constructed).sum()),
            "full_graph_reciprocal_fraction_in_sample": float(constructed.mean())}
result = {
    "source": "RManLuo/MotifGNN public author archive SSJY",
    "sha256_original_zip": sha,
    "zip_bytes": int(ZIP.stat().st_size),
    "observed_directed_events": int(len(df)),
    "unique_users_in_edges": int(len(codes)),
    "actions": {str(k): int(v) for k,v in df.iloc[:,2].value_counts().items()},
    "all_action_counts": all_action_counts,
    "excluded_actions": {k:v for k,v in all_action_counts.items() if k not in ["click", "msg"]},
    "observed": obs,
    "null": {"B": 30, "seed": 20261028, "method": "exact in/out event degree stub permutation",
             "reciprocal_rate_mean": float(np.mean(null_fracs)),
             "reciprocal_rate_min": float(np.min(null_fracs)),
             "reciprocal_rate_max": float(np.max(null_fracs)),
             "reciprocal_rate_sd": float(np.std(null_fracs, ddof=1)),
             "p_upper_monte_carlo": float((1 + sum(q >= obs["reciprocal_arc_fraction"] for q in null_fracs)) / 31),
             "null_rates": null_fracs,
             "null_self_loops_mean": float(np.mean([q["event_self_loops"] for q in nulls])),
             "null_duplicate_arcs_mean": float(np.mean([q["duplicate_event_arcs"] for q in nulls]))},
    "dataset_train_labels": label_check(train),
    "dataset_test_labels": label_check(test),
    "claim_limit": "Reverse click/msg only, rec excluded. The meaning of rec is unverified and is not assumed to be opportunity or rejection. No no-like, timestamps or lasting couples; no causal ESBM mechanism identified.",
    "data_licence": "Public author link, standalone license absent; aggregates only, raw data not republished.",
    "clean_clone": "NOT_TESTED"}
OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps({k:v for k,v in result.items() if k not in ["actions","null"]},indent=2))
print("null", {k:v for k,v in result["null"].items() if k!="null_rates"})
