"""Archive the complete block in bounded shards, with verified raw-byte hashes."""
from pathlib import Path
import hashlib
import json
import re
import zipfile

B=Path(__file__).resolve().parent
OUT=B/'research/V187_V190_20261115'
MAX_RAW=42_000_000


def sha(data):return hashlib.sha256(data).hexdigest()


def main():
    assert (B/'results/V187_V190_FINAL_AUDIT.json').exists()
    assert (B/'results/AB_EVALUACION_V187_V190_20261115.json').exists()
    OUT.mkdir(parents=True,exist_ok=False)
    payload=set();direct=set()
    def add(path,publish=True):
        p=B/path
        assert p.is_file() and p.resolve().is_relative_to(B.resolve()),p
        payload.add(p)
        if publish:direct.add(p)
    for pattern in ['v187_*.py','v188_*.py','v189_*.py','v189b_*.py','v190_*.py',
                    'PREREG_V187_*.md','PREREG_V188_*.md','PREREG_V190_*.md']:
        for p in B.glob(pattern):add(p.relative_to(B))
    for p in ['v185_collective_grokking.py','research_resource_limits.py','audit_v188_v190_numpy.py',
              'analyze_v187_v190.py','close_v187_v190.py','archive_v187_v190.py','publish_v187_v190.py',
              'register_v190_local.py','verify_v190_registration.py','verify_v187_v190_documents.py','reproduce_v187_v190.py','update_bibliography_v190.py',
              'REPRODUCE_V187_V190.md','docs/V187_V190_REPORT_TEMPLATE.md','docs/CRITERIO_CAUSAL_GROKKING_COLECTIVO_V188.md',
              'docs/TFM_CAPITULO_CONVENCIONES_V187_V190.md','docs/TFM_MANUSCRITO_TRABAJO_V186.md',
              'docs/TFM_MANUSCRITO_TRABAJO_V190.md','results/INFORME_V187_V190_20261115.md',
              'INICIO_INVESTIGACION_CIENTIFICA.md','handoff_codex/GOAL_CIENTIFICO_AB_TFM.md',
              'handoff_codex/ESTADO_20261115_V190.md','handoff_codex/ESTADO_V190_EN_CURSO_20261115.md',
              'literatura/references_verified.json','literatura/references.bib','literatura/BIBLIOGRAFIA_ACUMULATIVA_20261114.md',
              'literatura/original_code/Lyle2026/SOURCE_MANIFEST.json']:
        add(p)
    for folder in ['V187_CLASSICAL_SIGNALING','V188_PRIVATE_CONVENTIONS','V189_SUPPORT_AUDIT',
                   'V189B_MATCHED_CONTEXTS','V190_LOSSY_MEMORIZATION']:
        for p in (B/'results'/folder).rglob('*'):
            if p.is_file():add(p.relative_to(B),publish=p.name=='SUMMARY.json')
    for prefix in ['V187','V188','V189','V189B','V190','V188_V190','V187_V190','AB_EVALUACION_V187_V190','FIG_V187','FIG_V189B','FIG_V190']:
        for p in (B/'results').glob(prefix+'*'):
            if p.is_file() and '_ARCHIVE_CONSOLE' not in p.name and '_PUBLICATION_CONSOLE' not in p.name:
                add(p.relative_to(B),publish=p.suffix!='.log')
    for folder in ['literatura/backups/V187_V190_20261115','handoff_codex/backups_V190']:
        for p in (B/folder).rglob('*'):
            if p.is_file():add(p.relative_to(B),publish=False)
    # Include every local scientific figure needed by the integrated manuscript.
    manuscript=B/'docs/TFM_MANUSCRITO_TRABAJO_V190.md'
    for target in re.findall(r'!\[[^\]]*\]\(([^)]+)\)',manuscript.read_text(encoding='utf-8')):
        if '://' not in target:
            p=(manuscript.parent/target).resolve();assert p.is_relative_to(B.resolve())
            add(p.relative_to(B))
    (OUT/'README.md').write_text('''# Evidencia V187–V190

Descargar todos los archivos EVIDENCE_XX.zip y extraerlos en un mismo directorio vacío. Cada archivo contiene su propio manifiesto de payloads; el manifiesto global externo registra todos los archivos originales. ARCHIVE_MANIFEST.json identifica tamaños y SHA256 de los ZIP. Se verificaron CRC y todos los hashes, no solo la existencia de archivos.

Incluye calibración clásica, transferencia negativa, prototipo de soporte descartado, corrección de marginales y contraste completo V190. Contiene pesos y optimizadores, no únicamente figuras o resúmenes. No acredita grokking colectivo, una institución material aprendida ni AB2/3. Consultar informe, manuscrito y REPRODUCE_V187_V190.md para unidades, antecedentes y límites.

Los PDF de artículos no se redistribuyen. Su referencia y manifiesto se conservan. Los datos humanos y resultados de fases anteriores no se duplican: pertenecen a las entregas previas, identificadas en el manuscrito. Este archivo preserva completo el bloque nuevo y las figuras que usa el documento integrado.
''',encoding='utf-8')
    add((OUT/'README.md').relative_to(B))
    hashes={p.relative_to(B).as_posix():sha(p.read_bytes()) for p in sorted(payload)}
    (OUT/'EVIDENCE_PAYLOAD_SHA256.json').write_text(json.dumps(hashes,indent=2,ensure_ascii=False),encoding='utf-8')
    shards=[];current=[];total=0
    for p in sorted(payload):
        size=p.stat().st_size;assert size<MAX_RAW,p
        if current and total+size>MAX_RAW:shards.append(current);current=[];total=0
        current.append(p);total+=size
    if current:shards.append(current)
    manifests=[]
    for i,files in enumerate(shards,1):
        name=f'EVIDENCE_{i:02d}.zip';archive=OUT/name
        sub={p.relative_to(B).as_posix():hashes[p.relative_to(B).as_posix()] for p in files}
        manifest_bytes=json.dumps(sub,indent=2,ensure_ascii=False).encode('utf-8')
        with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
            for p in files:z.write(p,p.relative_to(B).as_posix())
            z.writestr(f'EVIDENCE_SHARD_{i:02d}_PAYLOAD_SHA256.json',manifest_bytes)
        with zipfile.ZipFile(archive) as z:
            assert z.testzip() is None
            assert z.read(f'EVIDENCE_SHARD_{i:02d}_PAYLOAD_SHA256.json')==manifest_bytes
            for path,expected in sub.items():assert sha(z.read(path))==expected,path
        manifests.append(dict(archive=name,bytes=archive.stat().st_size,sha256=sha(archive.read_bytes()),payload_files=len(files),
                              CRC_verified=True,all_payload_hashes_verified=True))
        direct.add(archive)
    manifest=dict(shards=manifests,total_payload_files=len(hashes),total_payload_bytes=sum(p.stat().st_size for p in payload),
                  all_payload_files_preserved=True,private_human_data_included=False,PDFs_not_redistributed=True,
                  archive_and_publication_progress_logs_excluded_to_avoid_self_reference=True)
    (OUT/'ARCHIVE_MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    direct|={OUT/'ARCHIVE_MANIFEST.json',OUT/'EVIDENCE_PAYLOAD_SHA256.json'}
    files=sorted(p.relative_to(B).as_posix() for p in direct)
    files.append((OUT/'PUBLICATION_FILES.json').relative_to(B).as_posix())
    (OUT/'PUBLICATION_FILES.json').write_text(json.dumps(files,indent=2),encoding='utf-8')
    print(json.dumps(dict(**manifest,direct_publication_files=len(files))),flush=True)


if __name__=='__main__':main()
