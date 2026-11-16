"""Download the immutable prospective sources and verify their actual bytes."""
from pathlib import Path
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import urllib.parse
import urllib.request

B=Path(__file__).resolve().parent


def main():
    folder=B/'research/V203_20261116'
    git=json.loads((folder/'REGISTRATION_GIT_COMMIT.json').read_text(encoding='utf-8'))
    manifest=json.loads((folder/'REGISTRATION_MANIFEST.json').read_text(encoding='utf-8'))
    files=json.loads((folder/'REGISTRATION_FILES.json').read_text(encoding='utf-8'))
    assert not (B/'results/V203_EXACT_GRADIENT_FLOWS').exists()
    assert not (B/'V203_REGISTRATION_RECEIPT.json').exists()
    def check(row):
        url=f"https://raw.githubusercontent.com/GalexY3/Metodologia-AB/{git['commit']}/"+urllib.parse.quote(row['path'],safe='/')
        with urllib.request.urlopen(url,timeout=40) as response:
            raw=response.read();status=response.status
        digest=hashlib.sha256(raw).hexdigest()
        assert status==200 and digest==row['sha256'] and len(raw)==row['bytes'],row['path']
        target=folder/'REMOTE_DOWNLOADS'/Path(row['path']).relative_to('research/V203_20261116')
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(raw)
        return dict(path=row['path'],HTTP_status=status,bytes=len(raw),sha256=digest)
    with ThreadPoolExecutor(max_workers=3) as pool:
        checked=list(pool.map(check,files))
    for name,digest in manifest['source_sha256'].items():
        assert hashlib.sha256((B/name).read_bytes()).hexdigest()==digest,name
    receipt=dict(study='V203',registration_commit=git['commit'],registration_tree=git['tree'],
        verified_at_utc=datetime.now(timezone.utc).isoformat(),
        remote_bytes_verified_before_integration=True,scientific_integrations_executed=False,
        source_sha256=manifest['source_sha256'],verified_files=checked,
        deterministic_sensitivity_cases=20,additional_precision_runs=4,
        CT2_historical=61,new_branch_score=None,N2=0,N3=0)
    (B/'V203_REGISTRATION_RECEIPT.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    print(json.dumps(dict(status='PROSPECTIVE_REMOTE_BYTES_VERIFIED',commit=git['commit'],files=len(checked))))


if __name__=='__main__':main()
