"""V47 all 12 heldout partner turnover policies and matched Monte Carlo checks."""
from pathlib import Path
from v47_frozen_audits import evaluate
ROOT=Path(__file__).resolve().parent
names=sorted(p.name for p in (ROOT/"runs").glob("v47_Q*")
 if p.is_dir() and (p/"v47_status.json").exists())
assert len(names)==12,names
for index,name in enumerate(names,1):
 evaluate(name,worlds=128)
 print("V47_BATCH_PROGRESS",index,len(names),flush=True)
print("V47_ALL_AUDITED",len(names),flush=True)
