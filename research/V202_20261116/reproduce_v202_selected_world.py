"""Fresh staging reproduction of world zero, all six arms and four checkpoints."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import numpy as np

B=Path(__file__).resolve().parent


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--destination',required=True)
    args=parser.parse_args();destination=Path(args.destination).resolve()
    assert not destination.exists()
    receipt=json.loads((B/'V202_REGISTRATION_RECEIPT.json').read_text(encoding='utf-8'))
    destination.mkdir(parents=True)
    for name,expected in receipt['source_sha256'].items():
        original=B/name;target=destination/name
        assert hashlib.sha256(original.read_bytes()).hexdigest()==expected,name
        target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(original,target)
    worker="""from pathlib import Path
from research_resource_limits import apply_limits
apply_limits(2)
import v202_relational_learning as engine
assert Path(engine.__file__).resolve().parent==Path('.').resolve()
out=Path('results/V202_SELECTED_REPRODUCTION');out.mkdir(exist_ok=False)
for arm in engine.ARMS:
    engine.run_world(0,arm,destination=out)
    print(arm,flush=True)
"""
    logfile=destination/'REPRODUCTION_CONSOLE.log'
    with logfile.open('wb') as stream:
        completed=subprocess.run([sys.executable,'-X','utf8','-c',worker],cwd=destination,
            stdout=stream,stderr=subprocess.STDOUT,check=False)
    assert completed.returncode==0,str(logfile)
    from v202_relational_learning import ARMS
    arrays=0;files=0
    for arm in ARMS:
        for step in [0,10000,30000,60000]:
            name=f'{arm}_world00_{step}.npz'
            with np.load(B/'results/V202_RELATIONAL_ACQUISITION'/name) as old,\
                 np.load(destination/'results/V202_SELECTED_REPRODUCTION'/name) as new:
                assert set(old.files)==set(new.files),name
                for key in old.files:
                    assert np.array_equal(old[key],new[key]),(name,key)
                    arrays+=1
            files+=1
    result=dict(status='PASS',fresh_directory=str(destination),world=0,arms=6,
        checkpoints_per_arm=4,files_compared=files,arrays_and_state_fields_bit_identical=arrays,
        includes='Q, logits, baselines, loss assignments, histories, partial episode buffers and Philox state',
        full_32_world_reproduction=False,external_scientific_replication=False)
    output=B/'results/V202_SELECTED_FRESH_REPRODUCTION.json';assert not output.exists()
    output.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
