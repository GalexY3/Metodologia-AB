"""Stage a clean experiment without editing frozen code or existing results."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys

B=Path(__file__).resolve().parent
SCRIPTS={187:'v187_classical_signaling.py',188:'v188_private_conventions.py',190:'v190_lossy_memorization.py'}


def main():
    p=argparse.ArgumentParser();p.add_argument('--experiment',type=int,choices=sorted(SCRIPTS),required=True)
    p.add_argument('--destination',type=Path,required=True);p.add_argument('--run',action='store_true');a=p.parse_args()
    dest=a.destination.resolve()
    assert not dest.exists(),'Choose a new directory; existing evidence is never overwritten.'
    assert not dest.is_relative_to(B.resolve()),'Use a separate reproduction directory outside the evidence tree.'
    receipt_path=f'results/V{a.experiment}_PREREG_RECEIPT.json'
    receipt=json.loads((B/receipt_path).read_text(encoding='utf-8'))
    files=set(receipt['source_sha256'])|{receipt_path,f'results/V{a.experiment}_TECHNICAL_AUDIT.json'}
    dest.mkdir(parents=True)
    for path in sorted(files):
        source=B/path;target=dest/path
        assert source.resolve().is_relative_to(B.resolve()) and source.is_file(),path
        if path in receipt['source_sha256']:
            assert hashlib.sha256(source.read_bytes()).hexdigest()==receipt['source_sha256'][path],path
        target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
    (dest/'REPRODUCTION_NOT_NEW_PREREGISTRATION.txt').write_text(
        'This is a reproduction of the archived protocol, not a newly timestamped prospective registration. '
        'Archived summaries copied as frozen context are not newly generated outcomes. '
        'Use a separate destination for each experiment. GPU/numerical differences may alter individual histories.\n',encoding='utf-8')
    print(json.dumps(dict(experiment=a.experiment,destination=str(dest),files_staged=len(files),
                          archived_code_unchanged=True,run_requested=a.run)),flush=True)
    if a.run:
        subprocess.run([sys.executable,'-u',str(dest/SCRIPTS[a.experiment]),'run'],cwd=dest,check=True)


if __name__=='__main__':main()
