"""Read-only verification of document links, byte manifests and optional metrics."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','2')
from pathlib import Path
import argparse
import hashlib
import json
import re
import zipfile
from research_resource_limits import apply_limits

B=Path(__file__).resolve().parent


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main(documents_only,metrics):
    evaluation=json.loads((B/'results/AB_EVALUACION_V191_V194_20261115.json').read_text(encoding='utf-8'))
    assert digest(B/'docs/TFM_MANUSCRITO_TRABAJO_V194.md')==evaluation['manuscript_sha256']
    assert digest(B/'results/AB_PROGRESO_CT2_CT3.json')=='0db038a35ee828a59c96de2a9e5e071545b26213ed692a29e79ad68f26778047'
    documents=[]
    for relative in ['results/INFORME_V191_V194_20261115.md','docs/TFM_MANUSCRITO_TRABAJO_V194.md']:
        p=B/relative;text=p.read_text(encoding='utf-8');assert not re.search(r'__[A-Z_]+__',text)
        images=re.findall(r'!\[[^\]]*\]\(([^)]+)\)',text)
        for link in images:
            if '://' not in link:assert (p.parent/link).resolve().is_file(),link
        documents.append(dict(path=relative,image_links=len(images),all_local_images_exist=True))
    result=dict(documents=documents,manuscript_hash_valid=True,canonical_score_file_unchanged=True,read_only=True)
    if not documents_only:
        out=B/'research/V191_V194_20261115'
        hashes=json.loads((out/'EVIDENCE_PAYLOAD_SHA256.json').read_text(encoding='utf-8'))
        for path,expected in hashes.items():assert digest(B/path)==expected,path
        archives=json.loads((out/'ARCHIVE_MANIFEST.json').read_text(encoding='utf-8'))
        for entry in archives['shards']:
            p=out/entry['archive'];assert p.stat().st_size==entry['bytes'] and digest(p)==entry['sha256']
            with zipfile.ZipFile(p) as z:assert z.testzip() is None
        result.update(local_payloads_verified=len(hashes),archive_shards_verified=len(archives['shards']))
    if metrics:
        from audit_v192_numpy import audit
        computations=[audit(f,60000) for f in ['ORACLE_FULL','PRIVATE_FULL','PRIVATE_BANDIT_IS']]
        computations.extend(audit('V193_'+a,60000,B/f'results/V193_FROZEN_PEER/{a}/checkpoint_60000.pt') for a in ['FREEZE_A','FREEZE_B'])
        computations.append(audit('V194_ORACLE_BANDIT_IS',60000,B/'results/V194_ORACLE_BANDIT/checkpoint_60000.pt'))
        checks=[c for a in computations for c in a['checks']];assert not any(not c['passed'] for c in checks)
        result.update(unique_numpy_metrics_recomputed=len(checks),max_numeric_error=max(c['error'] for c in checks))
    print(json.dumps(result),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--documents-only',action='store_true');p.add_argument('--metrics',action='store_true');a=p.parse_args()
    print('LIMITS',apply_limits(2),flush=True);main(a.documents_only,a.metrics)
