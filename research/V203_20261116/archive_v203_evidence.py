"""Curated V203 evidence package; excludes third-party PDFs and renders."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

B=Path(__file__).resolve().parent
F=B/'research/V203_20261116'


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    assert not (F/'V203_EVIDENCE_FINAL.zip').exists()
    reg=json.loads((B/'V203_REGISTRATION_RECEIPT.json').read_text(encoding='utf-8'))
    for name,digest in reg['source_sha256'].items():assert sha((B/name).read_bytes())==digest,name
    scripts=['v203_exact_gradient.py','audit_v203_exact_gradient.py','audit_v203_mixture.py',
        'run_v203_exact_flows.py','prepare_v203_registration.py','verify_v203_registration.py',
        'prepare_v203_node_audit.py','analyze_v203_exact_flows.py','record_v203_ab.py',
        'archive_v203_evidence.py','publish_v203_evidence.py','verify_v203_publication.py',
        'v202_relational_learning.py','v202_exact_evaluation.py','research_resource_limits.py',
        'validation_node/v202_independent_audit.cjs','validation_node/v203_independent_audit.cjs']
    docs=['PREREG_V203_EXACT_GRADIENT_FLOWS.md','V203_HISTORY_INVARIANCE_LEMMA.md',
        'REPRODUCE_V203.md','V203_REGISTRATION_RECEIPT.json',
        'docs/TFM_CAPITULO_CONTROL_GRADIENTE_V203.md','handoff_codex/ESTADO_20261116_V203.md']
    payload=set(scripts+docs)
    payload.update(str(p.relative_to(B).as_posix()) for p in (B/'results').glob('*V203*') if p.is_file())
    payload.update(str(p.relative_to(B).as_posix()) for p in (B/'results/V203_EXACT_GRADIENT_FLOWS').rglob('*') if p.is_file())
    payload.update(str(p.relative_to(B).as_posix()) for p in (F/'registered_sources').rglob('*') if p.is_file())
    payload.update(str(p.relative_to(B).as_posix()) for p in F.glob('REGISTRATION_*.json'))
    payload.update(str(p.relative_to(B).as_posix()) for p in (F/'PACKAGING_ATTEMPT1').iterdir() if p.is_file())
    lit=B/'literatura/LIO2020_REVIEW_20261116'
    payload.update(str(p.relative_to(B).as_posix()) for p in lit.iterdir() if p.is_file() and p.suffix.lower() in ['.md','.py','.json'])
    payload.add('literatura/LIO2020_REVIEW_20261116/LICENSE')
    assert not any(Path(p).suffix.lower() in ['.pdf','.png'] and p.startswith('literatura/') for p in payload)
    manifest=dict(study='V203',payload_count=len(payload),files={})
    for name in sorted(payload):
        raw=(B/name).read_bytes();manifest['files'][name]=dict(bytes=len(raw),sha256=sha(raw))
    raw=json.dumps(manifest,indent=2).encode('utf-8')
    (F/'PAYLOAD_MANIFEST.json').write_bytes(raw)
    archive=F/'V203_EVIDENCE_FINAL.zip'
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        z.writestr('PAYLOAD_MANIFEST.json',raw)
        for name in sorted(payload):z.write(B/name,name)
    with zipfile.ZipFile(archive) as z:
        assert len(z.namelist())==len(payload)+1
        for name,info in manifest['files'].items():assert sha(z.read(name))==info['sha256']
    direct=scripts+docs+[
        'results/INFORME_V203_GRADIENTES_EXACTOS_20261116.md','results/V203_SCIENTIFIC_SYNTHESIS.json',
        'results/V203_AB_LEDGER.json','results/V203_PRIOR_LEDGER.json','results/V203_NODE_INDEPENDENT_AUDIT.json',
        'results/FIG_V203_EXACT_GRADIENT_FLOWS.png','results/FIG_V203_CT2_UNCHANGED.png',
        'literatura/LIO2020_REVIEW_20261116/COST_AND_INFORMATION_AUDIT.md']
    publication=[]
    for name in direct:
        dest=F/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(B/name,dest)
        publication.append(dict(local=str(dest),remote=dest.relative_to(B).as_posix(),sha256=sha(dest.read_bytes())))
    checks=dict(archive='V203_EVIDENCE_FINAL.zip',bytes=archive.stat().st_size,sha256=sha(archive.read_bytes()),payloads=len(payload))
    (F/'ARCHIVE_CHECKSUMS.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
    for name in ['PAYLOAD_MANIFEST.json','ARCHIVE_CHECKSUMS.json','V203_EVIDENCE_FINAL.zip']:
        dest=F/name;publication.append(dict(local=str(dest),remote=dest.relative_to(B).as_posix(),sha256=sha(dest.read_bytes())))
    (F/'PUBLICATION_FILES.json').write_text(json.dumps(publication,indent=2),encoding='utf-8')
    print(json.dumps(dict(publication_files=len(publication),**checks),indent=2))


if __name__=='__main__':main()
