"""Verify immutable attestations, remote branch and local preservation witnesses."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib
import json
import subprocess
import sys
import urllib.parse
import urllib.request

B=Path(__file__).resolve().parent


def main():
    commit=sys.argv[1]
    assert len(commit)==40 and all(c in '0123456789abcdef' for c in commit)
    f=B/'research/V204_20261116'
    rows=json.loads((f/'FINAL_ATTESTATION_FILES.json').read_text(encoding='utf-8'))
    checked=[]
    for row in rows:
        url=f'https://raw.githubusercontent.com/GalexY3/Metodologia-AB/{commit}/'+urllib.parse.quote(row['path'],safe='/')
        with urllib.request.urlopen(url,timeout=30) as r:raw=r.read();status=r.status
        digest=hashlib.sha256(raw).hexdigest()
        assert status==200 and digest==row['sha256'],row['path']
        checked.append(dict(path=row['path'],bytes=len(raw),sha256=digest))
    url='https://api.github.com/repos/GalexY3/Metodologia-AB/git/ref/heads/research/aldea-memory-v175-20261115'
    with urllib.request.urlopen(url,timeout=30) as r:head=json.load(r)['object']['sha']
    assert head==commit
    repo=B.parents[2]
    local_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo).decode().strip()
    gitdir=Path(subprocess.check_output(['git','rev-parse','--absolute-git-dir'],cwd=repo).decode('utf-8').strip())
    index=hashlib.sha256((gitdir/'index').read_bytes()).hexdigest()
    score=hashlib.sha256((B/'results/AB_PROGRESO_CT2_CT3.json').read_bytes()).hexdigest()
    assert local_head=='c032a32d2d8d7710a6ad5a88519b0801ea186891'
    assert index=='0fc87bbef0de6ced68aa787004ef36d3c7934f757f51b5d8505665bd071184a1'
    assert score=='0db038a35ee828a59c96de2a9e5e071545b26213ed692a29e79ad68f26778047'
    for study in ['V203','V204']:
        reg=json.loads((B/f'{study}_REGISTRATION_RECEIPT.json').read_text(encoding='utf-8'))
        for name,digest in reg['source_sha256'].items():assert hashlib.sha256((B/name).read_bytes()).hexdigest()==digest,name
    result=dict(status='PASS',verified_at_utc=datetime.now(timezone.utc).isoformat(),
        final_attestation_commit=commit,remote_branch_head=head,verified_attestation_files=checked,
        local_HEAD_preserved=local_head,user_index_sha256=index,canonical_score_sha256=score,
        both_registered_scientific_source_freezes_preserved=True,overall_goal='ACTIVE',
        CT2_historical=61,new_branch_score=None,N2=0,N3=0)
    out=f/'FINAL_REMOTE_VERIFICATION.json';assert not out.exists()
    out.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(dict(status='PASS',remote_head=head,attestation_files=len(checked),local_state_preserved=True)))


if __name__=='__main__':main()
