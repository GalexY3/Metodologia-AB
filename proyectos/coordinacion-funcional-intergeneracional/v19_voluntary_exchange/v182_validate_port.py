"""Cross-language validation against original MATLAB physics executed by Octave.

Prepare, execute, and verify are separate explicit commands. Original sources
remain untouched; replay copies change only function names and RNG providers.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import subprocess
import time
import numpy as np
from scipy.io import savemat, loadmat
from research_resource_limits import apply_limits
from v182_yaman_kernel import lifetime, make_tape

BASE = Path(__file__).resolve().parent
OUT = BASE / "results/V182_OCTAVE_VALIDATION"
ORIGINAL = BASE / "literatura/original_code/Yaman2023/source"
OCTAVE = Path(r"C:\Programación\tools\octave-11.3.0\portable\octave-11.3.0-w64\mingw64\bin\octave-cli.exe")


def prepare():
    OUT.mkdir(parents=True, exist_ok=False)
    code = OUT / "instrumented_source"
    code.mkdir()
    modifications = []
    for directory, old, new in [
        ("settlement maintenance", "game_settlement", "v182_replay_settlement"),
        ("common pasture", "game_pasture", "v182_replay_pasture"),
    ]:
        original = (ORIGINAL / directory / (old + ".m")).read_bytes()
        text = original.decode("utf-8")
        text = text.replace(f"function results = {old}(settings)", f"function results = {new}(settings)", 1)
        text, nperm = re.subn(r"\brandperm\s*\(", "v182_tape_randperm(", text)
        text, nunif = re.subn(r"\brand\b", "v182_tape_rand()", text)
        modified = text.encode("utf-8")
        (code / (new + ".m")).write_bytes(modified)
        modifications.append(dict(source=directory+"/"+old+".m", source_sha256=hashlib.sha256(original).hexdigest(),
                                  replay_sha256=hashlib.sha256(modified).hexdigest(), permutation_replacements=nperm,
                                  uniform_replacements=nunif, physical_rules_modified=False))
    data = json.loads((BASE / "results/V182_YAMAN_ARCHIVE_AUDIT/archive_audit.json").read_text(encoding="utf-8"))
    fixtures = []
    for game, name in [(0, "settlement maintenance"), (1, "common pasture")]:
        for case, env in enumerate([[.5, .5], [1., 1.]]):
            row = next(r for r in data["rows"] if r["file"].startswith(name) and r["lambda_complexity"] == .2
                       and r["env"] == env and r["cell_index"][0] == 0)
            fixtures.append((game, np.array(row["norm"]), np.array(env)))
        matrix = np.array([[0., -.5, 1.25, 0], [.25, 0, 2.5, -.25],
                           [1., -1.75, 0., 6.], [-.75, .5, 0, 0.]]) if game == 0 else np.array([
                               [0., -1.25, .75], [2.25, 0, .5], [-.4, .25, 0.]])
        fixtures.append((game, matrix, np.array([.5, .5])))
    for index, (game, matrix, env) in enumerate(fixtures):
        T = 120
        p3, p4, p10, uniforms = make_tape(T, 182100 + index)
        savemat(OUT / f"fixture_{index}.mat", dict(game=game, T=T, matrix=matrix, env=env,
                                                 p3=p3, p4=p4, p10=p10, uniforms=uniforms), do_compression=True)
    (OUT / "source_instrumentation.json").write_text(json.dumps(modifications, indent=2), encoding="utf-8")
    print("PREPARED", len(fixtures), "fixtures", flush=True)


def execute():
    assert OCTAVE.is_file(), OCTAVE
    target = OUT / "octave_execution.log"
    assert not target.exists(), target
    env = os.environ.copy()
    env.update(OPENBLAS_NUM_THREADS="2", OMP_NUM_THREADS="2")
    command = f"addpath('{(BASE/'validation_octave').as_posix()}'); v182_run_original('{BASE.as_posix()}');"
    flags = subprocess.CREATE_NO_WINDOW | subprocess.BELOW_NORMAL_PRIORITY_CLASS if os.name == "nt" else 0
    started = time.monotonic()
    with target.open("xb") as log:
        result = subprocess.run([str(OCTAVE), "--no-gui", "--quiet", "--eval", command],
                                env=env, stdout=log, stderr=subprocess.STDOUT, creationflags=flags)
    print("OCTAVE_FINISHED", result.returncode, "elapsed", time.monotonic()-started, flush=True)
    assert result.returncode == 0


def verify():
    checks = []
    for f in sorted(OUT.glob("fixture_*.mat")):
        d = loadmat(f, squeeze_me=True)
        tape = tuple(np.asarray(d[k], dtype=np.int64 if k != "uniforms" else float) for k in ["p3", "p4", "p10", "uniforms"])
        game, T = int(d["game"]), int(d["T"])
        start = time.monotonic()
        got = lifetime(np.array(d["matrix"]), np.array(d["env"]), T, .1, 182999, game, *tape, True)
        original = loadmat(OUT / ("output_"+f.name), simplify_cells=True)
        results = original["results"]
        pairs = [("phi", got[0], results["phi"], 1e-10),
                 ("field", got[1], results["wasteTrend" if game == 0 else "resourceTrend"], 1e-10),
                 ("roles", got[3], results["roleTrend"], 0),
                 ("selection", got[4]+1, results["selection"], 0),
                 ("used", got[5], results["used"], 1e-14),
                 ("nRew", got[6], results["nRew"], 0),
                 ("nPun", got[7], results["nPun"], 0),
                 ("rng_counters", got[8], original["counters"], 0)]
        if game == 0:
            pairs.append(("attacks", got[2], results["advTrend"], 0))
        for label, value, expected, tol in pairs:
            error = float(np.max(np.abs(np.asarray(value)-np.asarray(expected))))
            checks.append(dict(fixture=f.name, output=label, max_abs_error=error, tolerance=tol, passed=error <= tol))
        print("PARITY", f.name, all(c["passed"] for c in checks if c["fixture"] == f.name), "sec", round(time.monotonic()-start, 2), flush=True)
    wire = loadmat(OUT / "original_wiring_and_regularizer.mat", simplify_cells=True)
    errors = [c for c in checks if not c["passed"]]
    report = dict(technical_cross_language_validation=True, externally_independent_scientific_confirmation=False,
                  checks=checks, failures=errors, original_wiring_and_regularizer={k:(v.tolist() if isinstance(v, np.ndarray) else v)
                      for k, v in wire.items() if not k.startswith("__")})
    (OUT / "parity_audit.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("AUDIT", len(checks), "checks", len(errors), "failures", flush=True)
    assert not errors, errors


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("command", choices=["prepare", "execute", "verify"])
    args = p.parse_args()
    print("LIMITS", apply_limits(2), flush=True)
    {"prepare": prepare, "execute": execute, "verify": verify}[args.command]()
