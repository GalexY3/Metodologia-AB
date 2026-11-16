"""Curated V205 package; no original author source, PDF or foreign render."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

B=Path(__file__).resolve().parent
F=B/'research/V205_20261116'


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    archive=F/'V205_EVIDENCE.zip';assert not archive.exists()
    reg=json.loads((B/'V205_REGISTRATION_RECEIPT.json').read_text(encoding='utf-8'))
    for name,digest in reg['source_sha256'].items():assert sha((B/name).read_bytes())==digest,name
    replay=json.loads((F/'FRESH_REPLAY_01/REPLAY_PROVENANCE.json').read_text(encoding='utf-8'))
    assert replay['status']=='PASS_FRESH_TREE_REPLAY'
    direct=['v205_two_stage_game.py','audit_v205_game.py','v205_author_helpers.py','run_v205_nash_audit.py',
        'prepare_v205_registration.py','verify_v205_registration.py','fetch_v205_upstream.py',
        'verify_v205_symbolic.py','v205_posthoc_marginalization.py','analyze_v205_nash_audit.py',
        'reproduce_v205_fresh.py','review_v205_priority.py','record_v205_ab.py','research_resource_limits.py',
        'archive_v205_evidence.py','publish_v205_evidence.py','verify_v205_publication.py',
        'validation_node/v205_independent_audit.cjs','PREREG_V205_ADVALIGN_NASH_AUDIT.md',
        'V205_REGISTRATION_RECEIPT.json','V205_NASH_COUNTEREXAMPLE_NOTE.md','REPRODUCE_V205.md',
        'docs/TFM_CAPITULO_VENTAJAS_Y_EQUILIBRIOS_V205.md','handoff_codex/ESTADO_20261116_V205.md',
        'results/INFORME_V205_NASH_Y_VENTAJAS_CONJUNTAS_20261116.md',
        'results/V205_SCIENTIFIC_SYNTHESIS.json','results/V205_AB_LEDGER.json','results/V205_CANDIDATE_LEDGER.json',
        'results/V205_NODE_INDEPENDENT_AUDIT.json','results/V205_SYMBOLIC_CERTIFICATE.json',
        'results/V205_POSTHOC_MARGINALIZATION.json','results/V205_CENTRAL_OPERATOR_COMPARISON.csv',
        'results/FIG_V205_NASH_DEPARTURE.png','results/FIG_V205_CT2_UNCHANGED.png',
        'literatura/ADVALIGN2025_AUDIT_20261116/PRIORITY_REVIEW_SCOPE.md',
        'literatura/ADVALIGN2025_AUDIT_20261116/OFFICIAL_SOURCE_RECEIPT.json',
        'literatura/ADVALIGN2025_AUDIT_20261116/PRIORITY_DISCUSSION_RECEIPT.json',
        'literatura/ADVALIGN2025_AUDIT_20261116/PRIORITY_DISCUSSION_RECEIPT_NETWORK_RETRY.json']
    payload=set(direct)|set(reg['source_sha256'])
    payload.update(p.relative_to(B).as_posix() for p in (B/'results/V205_ADVALIGN_NASH_AUDIT').rglob('*') if p.is_file())
    payload.update(p.relative_to(B).as_posix() for p in (B/'results').glob('V205_TECHNICAL*.json'))
    payload.update(p.relative_to(B).as_posix() for p in (F/'registered_sources').rglob('*') if p.is_file())
    payload.update(p.relative_to(B).as_posix() for p in F.glob('REGISTRATION_*.json'))
    payload.add((F/'FRESH_REPLAY_01/REPLAY_PROVENANCE.json').relative_to(B).as_posix())
    payload.update(p.relative_to(B).as_posix() for p in (F/'FRESH_REPLAY_01').glob('REPLAY_LOG_*.txt'))
    manifest=dict(study='V205',payload_count=len(payload),files={},
        exclusion_policy='No third-party code, PDFs, foreign renders, source capsules or OpenReview note bodies')
    for name in sorted(payload):
        p=B/name
        assert p.name not in ['train.py','utils.py'] and 'LOCAL_ONLY' not in name and p.suffix.lower()!='.pdf',name
        assert not ('literatura/' in name and p.suffix.lower()=='.png'),name
        raw=p.read_bytes();manifest['files'][name]=dict(bytes=len(raw),sha256=sha(raw))
    raw=json.dumps(manifest,indent=2).encode('utf-8');(F/'PAYLOAD_MANIFEST.json').write_bytes(raw)
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
    checks=dict(archive='V205_EVIDENCE.zip',bytes=archive.stat().st_size,sha256=sha(archive.read_bytes()),payloads=len(payload))
    (F/'ARCHIVE_CHECKSUMS.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
    for name in ['PAYLOAD_MANIFEST.json','ARCHIVE_CHECKSUMS.json','V205_EVIDENCE.zip']:
        dest=F/name;publication.append(dict(local=str(dest),remote=dest.relative_to(B).as_posix(),sha256=sha(dest.read_bytes())))
    (F/'PUBLICATION_FILES.json').write_text(json.dumps(publication,indent=2),encoding='utf-8')
    print(json.dumps(dict(publication_files=len(publication),**checks),indent=2))


if __name__=='__main__':main()
