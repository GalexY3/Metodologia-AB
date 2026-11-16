"""Preserve all V202 roots/checkpoints, negatives and technical repairs."""
from pathlib import Path
import hashlib
import json
import zipfile

B=Path(__file__).resolve().parent
PREFIX='research/V202_20261116/'


def sha(data):return hashlib.sha256(data).hexdigest()


def main():
    folder=B/'research/V202_20261116'
    assert not (folder/'PAYLOAD_MANIFEST.json').exists()
    registration=json.loads((B/'V202_REGISTRATION_RECEIPT.json').read_text(encoding='utf-8'))
    for name,expected in registration['source_sha256'].items():
        assert sha((B/name).read_bytes())==expected,name
    selected=set(registration['source_sha256'])
    extras=['V202_REGISTRATION_RECEIPT.json','REPRODUCE_V202.md',
        'v202_posthoc_initial_and_gradient.py','synthesize_v202_results.py',
        'reproduce_v202_selected_world.py','validation_node/v202_independent_audit.cjs',
        'archive_v202_evidence.py','publish_v202_evidence.py',
        'docs/TFM_CAPITULO_CUMPLIMIENTO_V202.md','handoff_codex/ESTADO_20261116_V202.md',
        'results/INFORME_V202_ADQUISICION_RELACIONAL_20261116.md',
        'results/FIG_V202_PRIOR_AND_CONTINUOUS_GAINS.png',
        'research/V202_20261116/REGISTRATION_MANIFEST.json']
    selected.update(extras)
    selected.update(p.relative_to(B).as_posix() for p in (B/'results').glob('V202_*') if p.is_file())
    for directory in ['V202_RELATIONAL_ACQUISITION','V202_TECHNICAL_CHECKPOINT_SMOKE',
                      'V202_TECHNICAL_INITIAL_CHECKPOINT_SMOKE']:
        selected.update(p.relative_to(B).as_posix() for p in (B/'results'/directory).rglob('*') if p.is_file())
    science=list((B/'results/V202_RELATIONAL_ACQUISITION').glob('*_world*.json'))
    checkpoints=list((B/'results/V202_RELATIONAL_ACQUISITION').glob('*.npz'))
    assert len(science)==192 and len(checkpoints)==768
    records={name:dict(bytes=(B/name).stat().st_size,sha256=sha((B/name).read_bytes())) for name in sorted(selected)}
    manifest=dict(study='V202',preregistration_commit=registration['commit'],files=records,
        payload_count=len(records),raw_bytes=sum(r['bytes'] for r in records.values()),
        scientific_root_arm_JSON=192,checkpoints=768,independent_roots=32,
        primary_result='FAIL',source_hashes_match_preregistration=True,
        external_confirmation=False,third_party_PDFs_or_human_microdata_included=False)
    (folder/'PAYLOAD_MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    parts=[];batch=[];size=0
    for name in sorted(records):
        n=records[name]['bytes']
        if batch and size+n>18000000:parts.append(batch);batch=[];size=0
        batch.append(name);size+=n
    if batch:parts.append(batch)
    archives=[]
    for i,names in enumerate(parts,1):
        dest=folder/f'V202_EVIDENCE_PART_{i:02}.zip'
        with zipfile.ZipFile(dest,'x',zipfile.ZIP_DEFLATED,compresslevel=7) as z:
            for name in names:
                entry=zipfile.ZipInfo(name,date_time=(2026,11,16,0,0,0));entry.compress_type=zipfile.ZIP_DEFLATED
                z.writestr(entry,(B/name).read_bytes(),compresslevel=7)
            z.write(folder/'PAYLOAD_MANIFEST.json','PAYLOAD_MANIFEST.json')
        with zipfile.ZipFile(dest) as z:
            for name in names:assert sha(z.read(name))==records[name]['sha256'],name
        archives.append(dict(path=dest.name,bytes=dest.stat().st_size,sha256=sha(dest.read_bytes()),payloads=len(names)))
    direct=set(registration['source_sha256'])|set(extras)|{
        'results/V202_RELATIONAL_ACQUISITION/ANALYSIS.json','results/V202_RELATIONAL_ACQUISITION/FREEZE.json',
        'results/V202_SCIENTIFIC_SYNTHESIS.json','results/V202_AB_LEDGER.json',
        'results/V202_ZERO_SUCCESS_BOUND.json','results/V202_SELECTED_FRESH_REPRODUCTION.json'}
    # Large detailed audits live in the ZIPs; small summaries remain readable.
    for audit in ['V202_NODE_INDEPENDENT_AUDIT','V202_POSTHOC_INITIAL_AND_GRADIENT']:
        obj=json.loads((B/f'results/{audit}.json').read_text(encoding='utf-8'))
        obj.pop('records',None)
        dest=folder/f'{audit}_SUMMARY.json';dest.write_text(json.dumps(obj,indent=2),encoding='utf-8')
    (folder/'ARCHIVE_CHECKSUMS.json').write_text(json.dumps(archives,indent=2),encoding='utf-8')
    public=[]
    for name in sorted(direct):
        p=B/name
        remote=name if name.startswith(PREFIX) else PREFIX+name
        public.append(dict(local=str(p.resolve()),remote=remote,sha256=sha(p.read_bytes()),bytes=p.stat().st_size))
    for p in [folder/'PAYLOAD_MANIFEST.json',folder/'ARCHIVE_CHECKSUMS.json',
              *folder.glob('*_SUMMARY.json'),*folder.glob('V202_EVIDENCE_PART_*.zip')]:
        public.append(dict(local=str(p.resolve()),remote=PREFIX+p.name,sha256=sha(p.read_bytes()),bytes=p.stat().st_size))
    assert len({r['remote'] for r in public})==len(public)
    (folder/'PUBLICATION_FILES.json').write_text(json.dumps(public,indent=2),encoding='utf-8')
    print(json.dumps(dict(payload_count=len(records),raw_bytes=manifest['raw_bytes'],archives=archives,
                         direct_files=len(public)),indent=2))


if __name__=='__main__':main()
