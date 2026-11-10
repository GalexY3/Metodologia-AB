"""Package selected, previously gitignored V6/V7 run artifacts for moving PCs.

No source code, credentials, browser state, or arbitrary directories are
collected. Code is already versioned in the Git repository.
"""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from hashlib import sha256
import json

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
OUTPUT=HERE/"TRANSFER_BUNDLE_RUNS_20261110.zip"
V6=BASE/"v6_million"/"runs"/"principal"
V6_FILES=("config.json","control.json","history.jsonl","latest.pt",
          "replay.json","status.json","worker.log")
V7_BASE=BASE/"v7_pilots"/"runs"
V7_PILOTS=("pilot_legacy","pilot_gated","pilot_gru_c1",
           "pilot_gru_c2","pilot_es_c1")
V7_FILES=("config.json","control.json","history.jsonl","latest.pt",
          "replay.json","status.json","diagnostics.json")
entries=[]
for name in V6_FILES:
    p=V6/name
    if not p.exists():
        raise FileNotFoundError(p)
    entries.append((p,Path("v6_million/runs/principal")/name))
for experiment in V7_PILOTS:
    for name in V7_FILES:
        p=V7_BASE/experiment/name
        if not p.exists():
            raise FileNotFoundError(p)
        entries.append((p,Path("v7_pilots/runs")/experiment/name))
manifest=dict(purpose="Portable checkpoint and run-data transfer from DESKTOP-I4SULKD",
              preservation="Existing V6 and V7 code is in Git; this archive contains selected gitignored run artifacts",
              restore_under="proyectos/coordinacion-funcional-intergeneracional",
              files=[dict(path=str(dest).replace("\\","/"),size=src.stat().st_size,
                          sha256=sha256(src.read_bytes()).hexdigest())
                     for src,dest in entries])
with ZipFile(OUTPUT,"w",compression=ZIP_DEFLATED,compresslevel=6) as z:
    z.writestr("MANIFEST_SHA256.json",json.dumps(manifest,ensure_ascii=False,indent=2))
    for src,dest in entries:
        z.write(src,str(dest).replace("\\","/"))
with ZipFile(OUTPUT,"r") as z:
    assert z.testzip() is None, "ZIP corruption"
    for f in manifest["files"]:
        assert sha256(z.read(f["path"])).hexdigest()==f["sha256"],f["path"]
print(json.dumps(dict(path=str(OUTPUT),files=len(entries),size=OUTPUT.stat().st_size,
                      sha256=sha256(OUTPUT.read_bytes()).hexdigest()),indent=2))
