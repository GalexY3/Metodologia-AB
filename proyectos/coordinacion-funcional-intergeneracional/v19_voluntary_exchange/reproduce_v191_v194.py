"""Stage isolated reproductions, including all V193 historical reference states."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys

B=Path(__file__).resolve().parent
SCRIPTS={192:'v192_dual_neural_learning.py',193:'v193_frozen_peer.py',194:'v194_oracle_bandit_control.py'}


def main():
    p=argparse.ArgumentParser();p.add_argument('--experiment',type=int,choices=sorted(SCRIPTS),required=True)
    p.add_argument('--destination',type=Path,required=True);p.add_argument('--run',action='store_true');a=p.parse_args()
    dest=a.destination.resolve();assert not dest.exists(),'Destination must be new.'
    assert not dest.is_relative_to(B.resolve()),'Use a separate directory outside the archived evidence tree.'
    receipt_path=f'results/V{a.experiment}_PREREG_RECEIPT.json'
    receipt=json.loads((B/receipt_path).read_text(encoding='utf-8'))
    files=set(receipt['source_sha256'])|{receipt_path}
    if a.experiment==193:
        # The frozen run compares every saved active state against its original
        # joint continuation, not just the5000checkpoint pinned for replay.
        for step in range(5000,60001,5000):files.add(f'results/V192_DUAL_NEURAL_LEARNING/PRIVATE_FULL/checkpoint_{step}.pt')
    dest.mkdir(parents=True)
    digests={}
    for path in sorted(files):
        source=B/path;target=dest/path
        assert source.is_file() and source.resolve().is_relative_to(B.resolve()),path
        sha=hashlib.sha256(source.read_bytes()).hexdigest()
        if path in receipt['source_sha256']:assert sha==receipt['source_sha256'][path],path
        target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target);digests[path]=sha
    note=dict(experiment=a.experiment,staged_files_sha256=digests,
        historical_registration_copied_not_new_preregistration=True,
        context_summaries_and_reference_states_not_new_results=True,run_requested=a.run)
    (dest/'REPRODUCTION_STAGE.json').write_text(json.dumps(note,indent=2),encoding='utf-8')
    print(json.dumps(dict(experiment=a.experiment,destination=str(dest),files=len(files),source_bytes_verified=True,run_requested=a.run)),flush=True)
    if a.run:subprocess.run([sys.executable,'-u',str(dest/SCRIPTS[a.experiment]),'run'],cwd=dest,check=True)


if __name__=='__main__':main()
