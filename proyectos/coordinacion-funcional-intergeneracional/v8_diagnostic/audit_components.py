"""Ex post decomposition of frozen models; verifies original transfer scores."""
import json,hashlib
from pathlib import Path
import numpy as np
from learn_acceptance import trial
ROOT=Path(__file__).resolve().parent
source=json.loads((ROOT/"RESULTS_V8_TRANSFER.json").read_text(encoding="utf-8"))
results=[]
for rr in source["replicates"]:
    file=ROOT/rr["model"]
    assert hashlib.sha256(file.read_bytes()).hexdigest()==rr["sha256"]
    theta=np.load(file)["theta"]
    rows=[]
    for item in rr["rows"]:
        k=item["k"]
        met={}
        for label in ("trained","untrained","scripted"):
            weights=(theta if label=="trained" else np.zeros_like(theta)).copy()
            current=trial(source["population"],k,source["eval_worlds"],
                  source["eval_epochs"],item["seed"],weights,
                  mode="scripted" if label=="scripted" else "policy")
            expected=item["arms"][label]
            assert abs(current["final_D"]-expected["final_D"])<1e-9
            assert current["exact"]==expected["exact"]
            met[label]=current
        rows.append(dict(k=k,arms=met))
        print("COMPONENT",rr["rep"],k,
             [(name,round(v["leakage"],4),round(v["overload"],4)) for name,v in met.items()],
             flush=True)
    results.append(dict(rep=rr["rep"],model=rr["model"],rows=rows))
(ROOT/"RESULTS_V8_COMPONENTS.json").write_text(json.dumps(dict(
    kind="POSTHOC_DECOMPOSITION_VERIFIED_AGAINST_TRANSFER",
    trained_for_k=source["trained_for_k"],results=results),indent=2,
    ensure_ascii=False),encoding="utf-8")
print("COMPONENTS_VALIDATED")
