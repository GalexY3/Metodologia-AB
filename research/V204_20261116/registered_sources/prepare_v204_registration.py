"""Prospective freeze of a known exact LOLA rival; no training here."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib
import json
import platform
import shutil
import numpy
import scipy
import numba
import torch

B=Path(__file__).resolve().parent
FILES=['v204_opponent_gradient.py','audit_v204_opponent_gradient.py','run_v204_lola.py',
    'PREREG_V204_LOLA_NET_RETURN.md','prepare_v204_registration.py','verify_v204_registration.py',
    'v203_exact_gradient.py','v202_exact_evaluation.py','v202_relational_learning.py',
    'research_resource_limits.py','results/V204_PRE_TRAJECTORY_TECHNICAL_AUDIT.json']


def main():
    assert not (B/'results/V204_LOLA_NET_RETURN').exists()
    f=B/'research/V204_20261116';f.mkdir(exist_ok=False)
    hashes={}
    for name in FILES:
        raw=(B/name).read_bytes();hashes[name]=hashlib.sha256(raw).hexdigest()
        target=f/'registered_sources'/name;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(B/name,target)
    qa=json.loads((B/'results/V204_PRE_TRAJECTORY_TECHNICAL_AUDIT.json').read_text(encoding='utf-8'))
    assert qa['status']=='PASS'
    for name,digest in qa['sources'].items():assert hashes[name]==digest,name
    baseline=B/'results/V203_EXACT_GRADIENT_FLOWS/SUMMARY.json'
    manifest=dict(study='V204',stage='PROSPECTIVE_BEFORE_LEARNING_TRAJECTORIES',
        timestamp_utc=datetime.now(timezone.utc).isoformat(),source_sha256=hashes,
        software=dict(python=platform.python_version(),numpy=numpy.__version__,scipy=scipy.__version__,numba=numba.__version__,torch=torch.__version__),
        method='Known LOLA-Ex Eq.4.4, AAMAS2018; own and given monetary costs in all returns',
        eta_normalized=20.,inner_step_unnormalized_return_equivalent=1.,
        main_flows=10,precision_repeats=2,independent_worlds=0,
        scientific_learning_trajectories_executed=False,
        existing_baseline=dict(study='V203',commit='b33885ac65e28c98112f5e0f1a27cbcf0e22cb37',
            archive='research/V203_20261116/V203_EVIDENCE_FINAL.zip',
            local_summary_sha256=hashlib.sha256(baseline.read_bytes()).hexdigest()),
        CT2_historical=61,new_branch_score=None,N2=0,N3=0)
    (f/'REGISTRATION_MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    files=[]
    for p in sorted(f.rglob('*')):
        if p.is_file():files.append(dict(local=str(p),path=p.relative_to(B).as_posix(),
            bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    (f/'REGISTRATION_FILES.json').write_text(json.dumps(files,indent=2),encoding='utf-8')
    print(json.dumps(dict(files=len(files),bytes=sum(x['bytes'] for x in files),sources=hashes),indent=2))


if __name__=='__main__':main()
