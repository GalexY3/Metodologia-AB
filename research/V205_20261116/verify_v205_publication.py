"""Actual HTTP byte verification of published V205 files and every ZIP payload."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import hashlib
import io
import json
import subprocess
import urllib.parse
import urllib.request
import zipfile

B=Path(__file__).resolve().parent


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    folder=B/'research/V205_20261116'
    git_receipt=json.loads((folder/'EVIDENCE_GIT_COMMIT.json').read_text(encoding='utf-8'))
    commit=git_receipt['commit']
    public=json.loads((folder/'PUBLICATION_FILES.json').read_text(encoding='utf-8'))
    manifest=json.loads((folder/'PAYLOAD_MANIFEST.json').read_text(encoding='utf-8'))
    def check(record):
        url=f'https://raw.githubusercontent.com/GalexY3/Metodologia-AB/{commit}/'+urllib.parse.quote(record['remote'],safe='/')
        with urllib.request.urlopen(url,timeout=45) as response:
            data=response.read();status=response.status
        assert status==200 and sha(data)==record['sha256'],record['remote']
        payloads=[]
        if record['remote'].endswith('.zip'):
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                for name in z.namelist():
                    if name=='PAYLOAD_MANIFEST.json':continue
                    assert sha(z.read(name))==manifest['files'][name]['sha256'],name
                    payloads.append(name)
        return dict(path=record['remote'],HTTP_status=status,bytes=len(data),sha256=sha(data),payloads=payloads)
    with ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(check,public))
    members=[p for r in results for p in r['payloads']]
    assert len(members)==len(set(members))==manifest['payload_count']
    assert set(members)==set(manifest['files'])
    repo=B.parents[2]
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo).decode().strip()
    gitdir=Path(subprocess.check_output(['git','rev-parse','--absolute-git-dir'],cwd=repo).decode('utf-8').strip())
    index_sha=sha((gitdir/'index').read_bytes());score_sha=sha((B/'results/AB_PROGRESO_CT2_CT3.json').read_bytes())
    assert head=='c032a32d2d8d7710a6ad5a88519b0801ea186891'
    assert index_sha=='0fc87bbef0de6ced68aa787004ef36d3c7934f757f51b5d8505665bd071184a1'
    assert score_sha=='0db038a35ee828a59c96de2a9e5e071545b26213ed692a29e79ad68f26778047'
    concise=[]
    for r in results:
        r['verified_payload_count']=len(r.pop('payloads'));concise.append(r)
    receipt=dict(status='VERIFIED_ACTUAL_HTTP_BYTES',verified_at_utc=datetime.now(timezone.utc).isoformat(),
        evidence_commit=commit,preregistration_commit='c7779edf154a924262ddd60a579d7b9eafab0ba9',
        files=concise,verified_payloads=len(members),all_payloads_unique_and_SHA256_verified=True,
        preservation=dict(local_HEAD=head,user_index_sha256=index_sha,canonical_score_sha256=score_sha),
        scientific_external_confirmation=False,CT2_historical=61,new_branch_score=None,N2=0,N3=0)
    output=folder/'PUBLICATION_RECEIPT.json';assert not output.exists()
    output.write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    print(json.dumps(dict(status=receipt['status'],commit=commit,files=len(results),payloads=len(members)),indent=2))


if __name__=='__main__':main()
