"""One-shot fresh-tree V205 replay; preserve all original outputs and source QA."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys

B=Path(__file__).resolve().parent


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True)
    args=parser.parse_args();dest=Path(args.output).resolve()
    assert not dest.exists() and dest!=B
    reg=json.loads((B/'V205_REGISTRATION_RECEIPT.json').read_text(encoding='utf-8'))
    names=list(reg['source_sha256'])+['V205_REGISTRATION_RECEIPT.json',
        'verify_v205_symbolic.py','v205_posthoc_marginalization.py','analyze_v205_nash_audit.py',
        'validation_node/v205_independent_audit.cjs']
    for name,expected in reg['source_sha256'].items():assert sha(B/name)==expected,name
    dest.mkdir(parents=True)
    for name in names:
        p=dest/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(B/name,p)
    tech=dest/'technical_check';tech.mkdir()
    for name in ['v205_two_stage_game.py','audit_v205_game.py']:shutil.copyfile(dest/name,tech/name)
    (tech/'results').mkdir()
    upstream='literatura/ADVALIGN2025_AUDIT_20261116'
    cached=[]
    for filename,expected in [('train.py','995b645c05103957855abfe1420e80cb0ac5e3f24ed9ee399081578019348c61'),
                              ('utils.py','7f0e0e019e4b47aa9c7077676bb1ae950fb69d1c4a3cf06c291f5664e0657f66')]:
        source=B/upstream/filename
        if source.exists():
            assert sha(source)==expected
            shutil.copyfile(source,dest/upstream/filename);cached.append(filename)
    env=os.environ.copy()
    for name in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:env[name]='2'
    completed=[]
    commands=[[sys.executable,'-X','utf8',str(dest/'fetch_v205_upstream.py')],
        [sys.executable,'-X','utf8',str(tech/'audit_v205_game.py')],
        [sys.executable,'-X','utf8',str(dest/'run_v205_nash_audit.py')],
        ['node',str(dest/'validation_node/v205_independent_audit.cjs')],
        [sys.executable,'-X','utf8',str(dest/'verify_v205_symbolic.py')],
        [sys.executable,'-X','utf8',str(dest/'v205_posthoc_marginalization.py')],
        [sys.executable,'-X','utf8',str(dest/'analyze_v205_nash_audit.py')]]
    for index,command in enumerate(commands):
        result=subprocess.run(command,cwd=dest,env=env,capture_output=True)
        (dest/f'REPLAY_LOG_{index}.txt').write_bytes(result.stdout+b'\nSTDERR\n'+result.stderr)
        assert result.returncode==0,(index,result.stderr.decode('utf-8',errors='replace'))
        completed.append(dict(program=Path(command[-1]).name,exit_code=result.returncode))
        print('COMPLETED',index,completed[-1]['program'],flush=True)
    paired=['LITERAL_FIELDS.json','AUTHOR_HELPERS.json','FIXTURE.json','SUMMARY.json']
    identical={}
    for filename in paired:
        name='results/V205_ADVALIGN_NASH_AUDIT/'+filename
        identical[filename]=sha(dest/name)==sha(B/name)
        assert identical[filename],filename
    result=dict(status='PASS_FRESH_TREE_REPLAY',registered_sources_verified=True,
        exact_original_primary_output_SHA256_matches=identical,
        completed=completed,verified_local_upstream_cache_used=cached,
        original_outputs_untouched=True,independent_author_or_scientific_replication=False)
    (dest/'REPLAY_PROVENANCE.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
