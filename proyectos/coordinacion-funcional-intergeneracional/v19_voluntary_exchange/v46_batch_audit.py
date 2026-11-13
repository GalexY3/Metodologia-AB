"""Batch audited frozen V46 models, one process to reduce startup overhead."""
from pathlib import Path
from v46_frozen_audits import audit
ROOT=Path(__file__).resolve().parent
names=sorted(p.name for p in (ROOT/"runs").glob("v46_Q*")
 if p.is_dir() and (p/"v46_status.json").is_file())
print("V46_AUDIT_MODEL_COUNT",len(names),flush=True)
assert len(names)==36, names
for i,name in enumerate(names,1):
 audit(name,worlds=128)
 print("V46_AUDIT_PROGRESS",i,"/",len(names),flush=True)
print("V46_ALL_AUDITS_COMPLETED",len(names),flush=True)
