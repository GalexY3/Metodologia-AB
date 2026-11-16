"""Freeze the candidate counterexample and helper protocol before primary calculation."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib
import json
import shutil
import platform
import numpy
import torch

B=Path(__file__).resolve().parent
FILES=['v205_two_stage_game.py','audit_v205_game.py','v205_author_helpers.py','run_v205_nash_audit.py',
    'PREREG_V205_ADVALIGN_NASH_AUDIT.md','fetch_v205_upstream.py',
    'prepare_v205_registration.py','verify_v205_registration.py','research_resource_limits.py',
    'results/V205_TECHNICAL_GAME_AUDIT_EXPANDED.json',
    'literatura/ADVALIGN2025_AUDIT_20261116/SOURCE_RECEIPT.json',
    'literatura/ADVALIGN2025_AUDIT_20261116/AUTHOR_CODE_RECEIPT.json']


def main():
    assert not (B/'results/V205_ADVALIGN_NASH_AUDIT').exists()
    folder=B/'research/V205_20261116';folder.mkdir(exist_ok=False)
    hashes={}
    for name in FILES:
        raw=(B/name).read_bytes();hashes[name]=hashlib.sha256(raw).hexdigest()
        p=folder/'registered_sources'/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(B/name,p)
    qa=json.loads((B/'results/V205_TECHNICAL_GAME_AUDIT_EXPANDED.json').read_text(encoding='utf-8'))
    assert qa['status']=='PASS'
    for name,digest in qa['sources'].items():assert hashes[name]==digest,name
    manifest=dict(study='V205',stage='PROSPECTIVE_BEFORE_PRIMARY_FIELD_AND_AUTHOR_HELPERS',
        timestamp_utc=datetime.now(timezone.utc).isoformat(),source_sha256=hashes,
        versions=dict(python=platform.python_version(),numpy=numpy.__version__,torch=torch.__version__),
        primary_audit_executed=False,constructed_analytical_counterexample_not_blind_search=True,
        literal_profiles=320,author_helper_profiles=144,independent_worlds=0,
        third_party_sources_not_embedded=True,historical_CT2=61,new_branch_score=None,N2=0,N3=0)
    (folder/'REGISTRATION_MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    rows=[]
    for p in sorted(folder.rglob('*')):
        if p.is_file():rows.append(dict(local=str(p),path=p.relative_to(B).as_posix(),bytes=p.stat().st_size,
            sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    (folder/'REGISTRATION_FILES.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
    print(json.dumps(dict(files=len(rows),bytes=sum(x['bytes'] for x in rows),source_sha256=hashes),indent=2))


if __name__=='__main__':main()
