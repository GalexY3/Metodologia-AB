"""Curated reproducible V204 package, preserving the prospective source freeze."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

B=Path(__file__).resolve().parent
F=B/'research/V204_20261116'


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    assert not (F/'V204_EVIDENCE.zip').exists()
    reg=json.loads((B/'V204_REGISTRATION_RECEIPT.json').read_text(encoding='utf-8'))
    for name,digest in reg['source_sha256'].items():assert sha((B/name).read_bytes())==digest,name
    baseline=B/'results/V203_EXACT_GRADIENT_FLOWS/SUMMARY.json'
    manifest0=json.loads((F/'REGISTRATION_MANIFEST.json').read_text(encoding='utf-8'))
    assert sha(baseline.read_bytes())==manifest0['existing_baseline']['local_summary_sha256']
    direct=['v204_opponent_gradient.py','audit_v204_opponent_gradient.py','run_v204_lola.py',
        'prepare_v204_registration.py','verify_v204_registration.py','prepare_v204_node_audit.py',
        'analyze_v204_lola.py','v204_posthoc_gradient_decomposition.py','certify_v204_uniform_payment.py',
        'record_v204_ab.py','archive_v204_evidence.py','publish_v204_evidence.py','verify_v204_publication.py',
        'v203_exact_gradient.py','v202_exact_evaluation.py','v202_relational_learning.py','research_resource_limits.py',
        'validation_node/v202_independent_audit.cjs','validation_node/v203_independent_audit.cjs','validation_node/v204_independent_audit.cjs',
        'PREREG_V204_LOLA_NET_RETURN.md','V204_CLOSED_FORM_PAYMENT_GRADIENT.md',
        'REPRODUCE_V204.md','V204_REGISTRATION_RECEIPT.json',
        'docs/TFM_CAPITULO_CREDITO_OPONENTES_V204.md','handoff_codex/ESTADO_20261116_V204.md',
        'literatura/RIVALES_OPPONENT_SHAPING_20261116.md',
        'results/INFORME_V204_LOLA_Y_BARRERA_CREDITO_20261116.md',
        'results/V204_SCIENTIFIC_SYNTHESIS.json','results/V204_AB_LEDGER.json','results/V204_CANDIDATE_LEDGER.json',
        'results/V204_NODE_INDEPENDENT_AUDIT.json','results/V204_CLOSED_FORM_CERTIFICATE.json',
        'results/FIG_V204_LOLA_VS_EPG.png','results/FIG_V204_PAYMENT_GRADIENT_ORDERS.png','results/FIG_V204_CT2_UNCHANGED.png']
    payload=set(direct);payload.add(baseline.relative_to(B).as_posix())
    payload.update(p.relative_to(B).as_posix() for p in (B/'results').glob('*V204*') if p.is_file())
    payload.update(p.relative_to(B).as_posix() for p in (B/'results/V204_LOLA_NET_RETURN').rglob('*') if p.is_file())
    payload.update(p.relative_to(B).as_posix() for p in (F/'registered_sources').rglob('*') if p.is_file())
    payload.update(p.relative_to(B).as_posix() for p in F.glob('REGISTRATION_*.json'))
    manifest=dict(study='V204',payload_count=len(payload),files={})
    for name in sorted(payload):
        raw=(B/name).read_bytes();manifest['files'][name]=dict(bytes=len(raw),sha256=sha(raw))
    raw=json.dumps(manifest,indent=2).encode('utf-8');(F/'PAYLOAD_MANIFEST.json').write_bytes(raw)
    archive=F/'V204_EVIDENCE.zip'
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        z.writestr('PAYLOAD_MANIFEST.json',raw)
        for name in sorted(payload):z.write(B/name,name)
    with zipfile.ZipFile(archive) as z:
        assert len(z.namelist())==len(payload)+1
        for name,info in manifest['files'].items():assert sha(z.read(name))==info['sha256']
    publication=[]
    for name in direct:
        dest=F/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(B/name,dest)
        publication.append(dict(local=str(dest),remote=dest.relative_to(B).as_posix(),sha256=sha(dest.read_bytes())))
    checks=dict(archive='V204_EVIDENCE.zip',bytes=archive.stat().st_size,sha256=sha(archive.read_bytes()),payloads=len(payload))
    (F/'ARCHIVE_CHECKSUMS.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
    for name in ['PAYLOAD_MANIFEST.json','ARCHIVE_CHECKSUMS.json','V204_EVIDENCE.zip']:
        dest=F/name;publication.append(dict(local=str(dest),remote=dest.relative_to(B).as_posix(),sha256=sha(dest.read_bytes())))
    (F/'PUBLICATION_FILES.json').write_text(json.dumps(publication,indent=2),encoding='utf-8')
    print(json.dumps(dict(publication_files=len(publication),**checks),indent=2))


if __name__=='__main__':main()
