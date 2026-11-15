"""Stage fresh reproductions, verify evidence, and build an immutable archive."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import zipfile
from PIL import Image
from research_resource_limits import apply_limits

B = Path(__file__).resolve().parent
R = B/'results'
ARCHIVE = B/'research/V199_20261115'
DOCS = ['results/INFORME_V199_APRENDICES_PRIVADOS_20261115.md',
        'docs/TFM_CAPITULO_APRENDICES_PRIVADOS_V199.md', 'docs/TFM_MANUSCRITO_TRABAJO_V199.md',
        'REPRODUCE_V199.md', 'POSTHOC_V199B_EXPECTILE_AUDIT.md']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def receipt():
    r = json.loads((R/'V199_PRIVATE_BASELINES_PREREG_RECEIPT.json').read_text(encoding='utf-8'))
    assert r['before_training']
    for path, value in dict(r['source_sha256'], **r['binary_parent_sha256']).items():
        assert sha(B/path) == value, path
    return r


def stage(destination):
    target = Path(destination).resolve()
    assert target.is_absolute() and not target.exists() and not target.is_relative_to(B.resolve())
    r = receipt()
    files = dict(r['source_sha256'], **r['binary_parent_sha256'])
    for path in ['results/V199_PRIVATE_BASELINES_PREREG_RECEIPT.json', 'results/V199_PRIVATE_BASELINES_SOURCE_PREREG.json',
                 'audit_v199_private_baselines.py', 'v199b_expectile_mechanism_audit.py', 'POSTHOC_V199B_EXPECTILE_AUDIT.md']:
        files[path] = sha(B/path)
    target.mkdir()
    for path, expected in files.items():
        source, copied = B/path, target/path
        copied.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, copied)
        assert sha(copied) == expected
    (target/'STAGED_REPRODUCTION.json').write_text(json.dumps(dict(files=files, prereg_commit=r['remote_commit'],
        new_training_executed=False), indent=2), encoding='utf-8')
    print(json.dumps(dict(destination=str(target), files=len(files), new_training_executed=False)), flush=True)


def verify(include_archive):
    r = receipt()
    links = []
    for path in DOCS:
        document = B/path
        assert document.is_file()
        for link in re.findall(r'!\[[^\]]*\]\(([^)]+)\)', document.read_text(encoding='utf-8')):
            if '://' not in link:
                image = (document.parent/link).resolve()
                assert image.is_relative_to(B.resolve()) and image.is_file()
                with Image.open(image) as im:
                    im.verify()
                links.append(dict(document=path, image=image.relative_to(B).as_posix(), verified=True))
    ledger = json.loads((R/'V199_AB_LEDGER.json').read_text(encoding='utf-8'))
    assert ledger['manuscript_sha256'] == sha(B/'docs/TFM_MANUSCRITO_TRABAJO_V199.md')
    assert ledger['parent_manuscript_sha256'] == sha(B/'docs/TFM_MANUSCRITO_TRABAJO_V198.md')
    audit = json.loads((R/'V199_PRIVATE_BASELINES_AUDIT.json').read_text(encoding='utf-8'))
    analysis = json.loads((R/'V199_PRIVATE_BASELINES_ANALYSIS.json').read_text(encoding='utf-8'))
    assert not audit['failures'] and analysis['primary_counts'] == {'MAINTENANCE': 3, 'FORMATION': 3}
    records = list((R/'V199_WORLD_RECORDS').glob('*.json'))
    assert len(records) == 384
    assert sum(json.loads(p.read_text(encoding='utf-8'))['is_new_training_root'] for p in records) == 192
    index = Path(subprocess.check_output(['git', 'rev-parse', '--git-path', 'index'], cwd=B, text=True, encoding='utf-8').strip())
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=B, text=True, encoding='utf-8').strip()
    assert head == 'c032a32d2d8d7710a6ad5a88519b0801ea186891'
    assert sha(index) == '0fc87bbef0de6ced68aa787004ef36d3c7934f757f51b5d8505665bd071184a1'
    assert sha(R/'AB_PROGRESO_CT2_CT3.json') == '0db038a35ee828a59c96de2a9e5e071545b26213ed692a29e79ad68f26778047'
    archive_count = 0
    if include_archive:
        manifest = json.loads((ARCHIVE/'ARCHIVE_MANIFEST.json').read_text(encoding='utf-8'))
        expected = json.loads((ARCHIVE/'EVIDENCE_PAYLOAD_SHA256.json').read_text(encoding='utf-8'))
        for path, value in expected.items():
            assert sha(B/path) == value, path
        seen = set()
        for item in manifest['shards']:
            path = ARCHIVE/item['archive']
            assert sha(path) == item['sha256']
            with zipfile.ZipFile(path) as z:
                assert z.testzip() is None
                sub = json.loads(z.read(next(name for name in z.namelist() if name.startswith('EVIDENCE_SHARD_'))))
                for name, value in sub.items():
                    assert name not in seen and value == expected[name]
                    assert hashlib.sha256(z.read(name)).hexdigest() == value
                    seen.add(name)
        assert seen == set(expected)
        archive_count = len(seen)
    result = dict(prereg_commit=r['remote_commit'], documents=len(DOCS),
        document_sha256={p: sha(B/p) for p in DOCS}, image_links=len(links), images=links,
        scientific_metric_checks=audit['metric_checks'], scientific_audit_failures=[],
        primary_counts=analysis['primary_counts'], world_records=384, new_formation_world_roots=192,
        user_HEAD_and_index_unchanged=True, canonical_score_unchanged=True,
        archive_payloads_verified=archive_count, all_checks_passed=True)
    print(json.dumps(result, indent=2), flush=True)


def archive():
    receipt_data = receipt()
    ARCHIVE.mkdir(exist_ok=False)
    files, direct = set(), set()

    def add(path, publish=True):
        p = (B/path).resolve()
        assert p.is_relative_to(B.resolve()) and p.is_file(), path
        files.add(p)
        if publish and p.stat().st_size <= 1000000:
            direct.add(p)

    for path in DOCS+['v199_private_baselines.py', 'analyze_v199_private_baselines.py',
        'register_v199_private_baselines.py', 'audit_v199_private_baselines.py', 'v199b_expectile_mechanism_audit.py',
        'close_v199_private_baselines.py', 'deliver_v199.py', 'publish_v199.py',
        'PREREG_V199_PRIVATE_BASELINES.md', 'handoff_codex/ESTADO_20261115_V199.md',
        'literatura/V199_PRIVATE_BASELINES_PRIOR.json', 'literatura/V199B_EXPECTILE_PRIOR.json',
        'results/FIG_V199_RIVAL_AND_PRIVATE_RISK.png', 'results/FIG_V199_STABILITY_AND_REVERSAL.png',
        'results/V199_DOCUMENT_QA.json']:
        add(path)
    for path in receipt_data['source_sha256']:
        add(path)
    for path in receipt_data['binary_parent_sha256']:
        add(path, False)
    for folder in ['V199_PRIVATE_BASELINES', 'V199_WORLD_RECORDS', 'V199B_EXPECTILE_AUDIT']:
        for p in (R/folder).rglob('*'):
            if p.is_file():
                add(p.relative_to(B), p.name == 'SUMMARY.json')
    for p in R.glob('V199*'):
        if p.is_file() and '_ARCHIVE_CONSOLE' not in p.name and '_PUBLICATION_CONSOLE' not in p.name:
            add(p.relative_to(B), p.suffix not in ['.log'])
    add('results/AB_PROGRESO_CT2_CT3.json', False)
    for link in re.findall(r'!\[[^\]]*\]\(([^)]+)\)', (B/'docs/TFM_MANUSCRITO_TRABAJO_V199.md').read_text(encoding='utf-8')):
        if '://' not in link:
            add((B/'docs'/link).resolve().relative_to(B.resolve()))
    readme = ARCHIVE/'README.md'
    readme.write_text('''# Evidencia V199 y V199B

Extraer todos los ZIP juntos en una carpeta nueva. Incluye384registros por mundo,192raíces nuevas de formación, las Q/conteos/temperaturas/RNG de todos los checkpoints fijados y seis padres históricos. Los algoritmos y el código de análisis se registraron antes de entrenar; las dos hipótesis principales fallaron3/6. V199B es auditoría posterior, no un rescate de esas hipótesis.

Los controles privados simples forman y conservan cooperación sin pulsos, pero no se adaptan robustamente a señales invertidas. Bajo mayoría puede imponerse riesgo a votantes sin salida; no llamar voluntaria a esa participación. No se acredita institución emergente, originalidad2/3ni un aumento del61histórico.

Cada ZIP y cada payload tienen SHA256; se verificaron CRC y todos los archivos. Los PDF, textos extraídos e imágenes de artículos de terceros no se redistribuyen: sus URL y hashes se registran como antecedentes. El snapshot del progreso histórico se incluye solo como procedencia, no como modificación publicada de ese archivo. Los logs de esta operación quedan fuera de su propio payload. Leer REPRODUCE_V199.md.
''', encoding='utf-8')
    add(readme.relative_to(B))
    hashes = {p.relative_to(B).as_posix(): sha(p) for p in sorted(files)}
    (ARCHIVE/'EVIDENCE_PAYLOAD_SHA256.json').write_text(json.dumps(hashes, indent=2, ensure_ascii=False), encoding='utf-8')
    groups, pending, length = [], [], 0
    for p in sorted(files):
        size = p.stat().st_size
        assert size < 40000000
        if pending and length+size > 40000000:
            groups.append(pending); pending, length = [], 0
        pending.append(p); length += size
    if pending:
        groups.append(pending)
    shards = []
    for number, payloads in enumerate(groups, 1):
        path = ARCHIVE/f'EVIDENCE_{number:02d}.zip'
        sub = {p.relative_to(B).as_posix(): hashes[p.relative_to(B).as_posix()] for p in payloads}
        with zipfile.ZipFile(path, 'x', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
            for p in payloads:
                z.write(p, p.relative_to(B).as_posix())
            z.writestr(f'EVIDENCE_SHARD_{number:02d}_PAYLOAD_SHA256.json', json.dumps(sub, indent=2, ensure_ascii=False))
        with zipfile.ZipFile(path) as z:
            assert z.testzip() is None
            for name, value in sub.items():
                assert hashlib.sha256(z.read(name)).hexdigest() == value
        shards.append(dict(archive=path.name, bytes=path.stat().st_size, sha256=sha(path), payload_files=len(payloads),
                           CRC_verified=True, all_payload_hashes_verified=True))
        direct.add(path)
    manifest = dict(shards=shards, total_payload_files=len(files), total_payload_bytes=sum(p.stat().st_size for p in files),
        primary_failures_and_posthoc_scope_preserved=True, PDFs_not_redistributed=True, canonical_score_unchanged=True)
    (ARCHIVE/'ARCHIVE_MANIFEST.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    direct |= {ARCHIVE/'ARCHIVE_MANIFEST.json', ARCHIVE/'EVIDENCE_PAYLOAD_SHA256.json'}
    paths = sorted(p.relative_to(B).as_posix() for p in direct)
    paths.append((ARCHIVE/'PUBLICATION_FILES.json').relative_to(B).as_posix())
    (ARCHIVE/'PUBLICATION_FILES.json').write_text(json.dumps(paths, indent=2), encoding='utf-8')
    print(json.dumps(dict(**manifest, direct_publication_files=len(paths))), flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('command', choices=['stage', 'verify', 'archive'])
    p.add_argument('--destination'); p.add_argument('--include-archive', action='store_true'); a = p.parse_args()
    apply_limits(2)
    if a.command == 'stage':
        assert a.destination; stage(a.destination)
    elif a.command == 'verify':
        verify(a.include_archive)
    else:
        archive()
