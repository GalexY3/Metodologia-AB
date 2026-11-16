"""Create an additive evidence package; never stage or alter the user's worktree."""
from pathlib import Path
import hashlib
import json
import zipfile

B = Path(__file__).resolve().parent


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    folder = B/'research/V201R_20261116'
    assert not folder.exists()
    ledger = json.loads((B/'results/V201R_AB_AUDIT_LEDGER.json').read_text(encoding='utf-8'))
    payload = dict(ledger['frozen_files'])
    payload.update(ledger['retained_drafts_and_attempts'])
    additional = ['results/V201R_AB_AUDIT_LEDGER.json', 'close_v201r_theory_audit.py',
        'archive_v201r_evidence.py', 'results/V201R_THEORY_PRECHECK_CONSOLE.log',
        'results/V201R_SINGLE_AGENT_BELLMAN_CONSOLE.log', 'results/V201R_CAPITAL_COALITION_CONSOLE.log',
        'results/V201R_RELATIONAL_CERTIFICATES_CONSOLE.log', 'results/V201R_CAPITAL_BOUND_AUDIT_CONSOLE.log',
        'results/V201R_SYNTHESIS_CONSOLE.log', 'results/V201R_REPRODUCTION_CONSOLE.log',
        'results/V201R_CLOSE_CONSOLE.log']
    for name in additional:
        data = (B/name).read_bytes()
        payload[name] = dict(sha256=digest(data), bytes=len(data))
    for name, expected in payload.items():
        assert digest((B/name).read_bytes()) == expected['sha256'], name
    folder.mkdir(parents=True)
    manifest = dict(archive='V201R_20261116', evidence='Post-input theory audit, not learned agents',
        files=payload, payload_count=len(payload),
        raw_bytes=sum(r['bytes'] for r in payload.values()),
        exclusions=['Third-party PDFs and extracted text','Other user conversation attachment, preserved locally',
                    'Existing human microdata','Canonical AB score and unrelated user edits'],
        local_input_source_hashes=[
          '82592df070764a5889df4227536fd24bdaf935512de5965aa02aa77197eda411',
          '384a59baf12c15723ca64ed6a6d4b1158b8b88953caf070a956dc931139e7672'])
    (folder/'PAYLOAD_MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    archive = folder/'V201R_REPRODUCIBLE_EVIDENCE.zip'
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name in sorted(payload):
            entry=zipfile.ZipInfo(name,date_time=(2026,11,16,0,0,0))
            entry.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(entry,(B/name).read_bytes(),compresslevel=9)
        z.write(folder/'PAYLOAD_MANIFEST.json','PAYLOAD_MANIFEST.json')
    with zipfile.ZipFile(archive) as z:
        for name, expected in payload.items():
            assert digest(z.read(name)) == expected['sha256'], name
    # Every current scientific file is also readable directly on GitHub.
    direct = list(ledger['frozen_files'])+['results/V201R_AB_AUDIT_LEDGER.json',
        'close_v201r_theory_audit.py','archive_v201r_evidence.py']
    records = [dict(local=str((B/name).resolve()), remote='research/V201R_20261116/'+name,
        sha256=digest((B/name).read_bytes()), bytes=(B/name).stat().st_size) for name in direct]
    for name in ['PAYLOAD_MANIFEST.json','V201R_REPRODUCIBLE_EVIDENCE.zip']:
        p=folder/name
        records.append(dict(local=str(p.resolve()),remote='research/V201R_20261116/'+name,
                            sha256=digest(p.read_bytes()),bytes=p.stat().st_size))
    # Attest previously delivered V199 without modifying any archived payload.
    for name in ['research/V199_20261115/PUBLICATION_RECEIPT.json',
                 'research/V199_20261115/LOCAL_DELIVERY_VERIFIED.json',
                 'docs/V199_CONTINUIDAD_TRAS_ARCHIVO.md']:
        p=B/name
        records.append(dict(local=str(p.resolve()),remote=name,sha256=digest(p.read_bytes()),bytes=p.stat().st_size))
    (folder/'PUBLICATION_FILES.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
    print(json.dumps(dict(payload_count=len(payload), archive_bytes=archive.stat().st_size,
        archive_sha256=digest(archive.read_bytes()), direct_Git_files=len(records)),indent=2))


if __name__ == '__main__':
    main()
