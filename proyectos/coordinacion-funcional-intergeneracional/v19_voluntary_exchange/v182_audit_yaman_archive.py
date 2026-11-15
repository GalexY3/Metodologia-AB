"""Inspect every archived Yaman social-sanctioning fit without selecting successes.

Descriptive reproduction audit, not a preregistered scientific hypothesis test.
Unmodified source and raw .mat files remain inside the verified CC0 archive.
"""
from pathlib import Path
import hashlib
import io
import json
import zipfile
import numpy as np
from scipy.io import loadmat

BASE = Path(__file__).resolve().parent
ORIGINAL = BASE / "literatura/original_code/Yaman2023"
OUT = BASE / "results/V182_YAMAN_ARCHIVE_AUDIT"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def fields(value):
    # scipy simplify_cells does not recurse into 2-D cell arrays of structs.
    if hasattr(value, "_fieldnames"):
        return {key: getattr(value, key) for key in value._fieldnames}
    return value


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / "archive_audit.json"
    if target.exists():
        previous = json.loads(target.read_text(encoding="utf-8"))
        assert not previous["rows"], "Never silently overwrite an existing populated audit"
        previous["valid"] = False
        previous["invalidation_reason"] = "Parser skipped scipy mat_struct in 2-D cell arrays; zero fits is not a scientific result"
        target.rename(OUT / "archive_audit_invalid_parser_v1.json")
        (OUT / "archive_audit_invalid_parser_v1.json").write_text(json.dumps(previous, indent=2), encoding="utf-8")
    rows, inventory, checks = [], [], []
    with zipfile.ZipFile(ORIGINAL / "evolution-of-social-sanctions.zip") as z:
        for info in z.infolist():
            if info.filename.startswith("__MACOSX/"):
                continue
            if info.filename.endswith(".mat"):
                inventory.append(dict(path=info.filename, bytes=info.file_size))
            if not (info.filename.endswith(".mat") and "Data-social-sanctions/" in info.filename):
                continue
            payload = z.read(info)
            data = loadmat(io.BytesIO(payload), simplify_cells=True)
            candidates = [(k, v) for k, v in data.items() if not k.startswith("__")]
            file_rows = 0
            for variable, value in candidates:
                for ix, entry in np.ndenumerate(np.asarray(value, dtype=object)):
                    entry = fields(entry)
                    if not isinstance(entry, dict) or "bestInd" not in entry:
                        continue
                    settings, best = fields(entry["settings"]), fields(entry["bestInd"])
                    matrix_key = "socialSanctioningMatrix" if "socialSanctioningMatrix" in best else "SI"
                    cost_key = "complexityRegularizationParameter" if "complexityRegularizationParameter" in settings else "cost"
                    matrix = np.asarray(best[matrix_key], dtype=float)
                    phi = np.atleast_2d(np.asarray(best["phi"], dtype=float))
                    tail = float(np.mean(phi[:, -101:]))
                    l0 = int(np.count_nonzero(matrix))
                    signed = int(np.sign(matrix).sum())
                    lam = float(settings[cost_key])
                    fitness = float(entry["fitness"])
                    row = dict(file=info.filename, source_sha256=sha(payload),
                               variable=variable, cell_index=list(ix), env=np.asarray(settings["env"]).tolist(),
                               seed=float(settings.get("seed", -1)), T=int(settings["T"]),
                               nRun=int(settings["nRun"]), lambda_complexity=lam,
                               tail_mean=tail, fitness=fitness, rules=l0, signed_rule_count=signed,
                               negative_rules=int(np.sum(matrix < 0)), positive_rules=int(np.sum(matrix > 0)),
                               fitness_residual_l0=fitness-(tail-lam*l0),
                               fitness_residual_signed=fitness-(tail-lam*signed),
                               norm=matrix.tolist(), settings_keys=sorted(settings),
                               archived_matrix_field=matrix_key, archived_cost_field=cost_key,
                               initial_norm=np.asarray(settings.get("genotype", settings.get("socialNorm", []))).tolist())
                    rows.append(row)
                    file_rows += 1
            checks.append(dict(file=info.filename, sha256=sha(payload), fits=file_rows))
            print("AUDITED", info.filename, "fits", file_rows, flush=True)
    summary = []
    for path in sorted(set(r["file"] for r in rows)):
        subset = [r for r in rows if r["file"] == path]
        summary.append(dict(file=path, n=len(subset),
                            max_abs_residual_l0=max(abs(r["fitness_residual_l0"]) for r in subset),
                            max_abs_residual_signed=max(abs(r["fitness_residual_signed"]) for r in subset),
                            mean_tail=float(np.mean([r["tail_mean"] for r in subset])),
                            mean_rules=float(np.mean([r["rules"] for r in subset]))))
    assert len(rows) == 1200, f"Expected 8 archives x 30 fits x 5 environments, found {len(rows)}"
    result = dict(valid=True, design="post hoc source/data reproducibility audit; no new norm training", rows=rows,
                  source_files=checks, all_mat_inventory=inventory, summary=summary)
    (OUT / "archive_audit.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(dict(total_fits=len(rows), summary=summary, all_mat_inventory=inventory), indent=2), flush=True)


if __name__ == "__main__":
    main()
