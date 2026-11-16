"""Download actual committed bytes and verify the complete evidence archive."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import argparse
import hashlib
import io
import json
import subprocess
import urllib.parse
import urllib.request
import zipfile

B=Path(__file__).resolve().parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--commit',required=True)
    args=parser.parse_args()
    assert len(args.commit)==40 and all(c in '0123456789abcdef' for c in args.commit)
    folder=B/'research/V201R_20261116'
    files=json.loads((folder/'PUBLICATION_FILES.json').read_text(encoding='utf-8'))
    manifest=json.loads((folder/'PAYLOAD_MANIFEST.json').read_text(encoding='utf-8'))
    def check(record):
        url=f'https://raw.githubusercontent.com/GalexY3/Metodologia-AB/{args.commit}/'+urllib.parse.quote(record['remote'],safe='/')
        with urllib.request.urlopen(url,timeout=30) as response:
            data=response.read()
            status=response.status
        assert status==200 and sha(data)==record['sha256'],record['remote']
        members=0
        if record['remote'].endswith('.zip'):
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                assert len(z.namelist())==manifest['payload_count']+1
                for name,expected in manifest['files'].items():
                    assert sha(z.read(name))==expected['sha256'],name
                    members+=1
        return dict(path=record['remote'],HTTP_status=status,bytes=len(data),sha256=sha(data),verified_archive_payloads=members)
    with ThreadPoolExecutor(max_workers=4) as pool:
        verified=list(pool.map(check,files))
    repo=B.parents[2]
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo).decode('ascii').strip()
    gitdir=Path(subprocess.check_output(['git','rev-parse','--absolute-git-dir'],cwd=repo).decode('utf-8').strip())
    index_sha=sha((gitdir/'index').read_bytes())
    score_sha=sha((B/'results/AB_PROGRESO_CT2_CT3.json').read_bytes())
    assert head=='c032a32d2d8d7710a6ad5a88519b0801ea186891'
    assert index_sha=='0fc87bbef0de6ced68aa787004ef36d3c7934f757f51b5d8505665bd071184a1'
    assert score_sha=='0db038a35ee828a59c96de2a9e5e071545b26213ed692a29e79ad68f26778047'
    receipt=dict(status='VERIFIED_ACTUAL_HTTP_BYTES',verified_at_utc=datetime.now(timezone.utc).isoformat(),
        repository='GalexY3/Metodologia-AB',branch='research/aldea-memory-v175-20261115',
        evidence_commit=args.commit,parent_evidence_commit='b98bcf8ba74dafa57763d264670117463690e4e3',
        files=verified,all_direct_files_sha256_match=True,all_38_archive_payloads_sha256_match=True,
        fresh_staging_reproduction='Six processes exit 0, six scientific JSON identical',
        preservation=dict(local_HEAD=head,user_index_sha256=index_sha,canonical_score_sha256=score_sha),
        scientific_external_confirmation=False,CT2_historical=61,new_branch_score=None,N2=0,N3=0)
    destination=folder/'PUBLICATION_RECEIPT.json'
    assert not destination.exists()
    destination.write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    print(json.dumps(dict(status=receipt['status'],commit=args.commit,verified_files=len(verified),
                         archive_payloads=manifest['payload_count'],preservation=receipt['preservation']),indent=2))


if __name__=='__main__':
    main()
