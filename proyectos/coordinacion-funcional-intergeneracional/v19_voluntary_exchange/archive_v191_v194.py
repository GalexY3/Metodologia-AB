"""Preserve the full V191–V194 block in bounded, verified evidence shards."""
from pathlib import Path
import hashlib
import json
import re
import zipfile
from research_resource_limits import apply_limits

B=Path(__file__).resolve().parent
OUT=B/'research/V191_V194_20261115'
MAX_RAW=42_000_000


def sha(data):return hashlib.sha256(data).hexdigest()


def main():
    assert (B/'results/V191_V194_FINAL_AUDIT.json').exists()
    assert (B/'results/V191_V194_EDITORIAL_AUDIT.json').exists()
    OUT.mkdir(parents=True,exist_ok=False)
    files=set();direct=set()
    def add(relative,publish=True):
        p=B/relative;assert p.is_file() and p.resolve().is_relative_to(B.resolve()),p
        files.add(p)
        if publish:direct.add(p)
    for pattern in ['v191*.py','v192*.py','v193*.py','v194*.py','PREREG_V192_*.md','PREREG_V193_*.md','PREREG_V194_*.md']:
        for p in B.glob(pattern):add(p.relative_to(B))
    for p in ['v185_collective_grokking.py','v187_classical_signaling.py','v188_private_conventions.py','research_resource_limits.py',
              'audit_v192_numpy.py','audit_v193_v194_numpy.py','analyze_v191_v194.py','close_v191_v194.py',
              'archive_v191_v194.py','publish_v191_v194.py','verify_v191_v194_evidence.py','reproduce_v191_v194.py',
              'register_v192_local.py','register_v193_local.py','register_v194_local.py',
              'verify_v192_registration.py','verify_v193_registration.py','verify_v194_registration.py','update_bibliography_v194.py',
              'REPRODUCE_V191_V194.md','docs/V191_DUAL_NEURAL_IDENTIFICATION.md','docs/V191_V194_REPORT_TEMPLATE.md',
              'docs/TFM_CAPITULO_DOS_REDES_V191_V194.md','docs/TFM_MANUSCRITO_TRABAJO_V190.md','docs/TFM_MANUSCRITO_TRABAJO_V194.md',
              'results/INFORME_V191_V194_20261115.md','INICIO_INVESTIGACION_CIENTIFICA.md',
              'handoff_codex/GOAL_CIENTIFICO_AB_TFM.md','handoff_codex/ESTADO_20261115_V194.md',
              'handoff_codex/ESTADO_V192_EN_CURSO_20261115.md','handoff_codex/ESTADO_V192_TERMINADO_V193_PENDIENTE_20261115.md',
              'handoff_codex/ESTADO_V194_TERMINADO_PENDIENTE_ENTREGA_20261115.md',
              'literatura/references_verified.json','literatura/references.bib','literatura/BIBLIOGRAFIA_ACUMULATIVA_20261114.md']:
        add(p)
    # The canonical progress file is an unchanged provenance snapshot inside
    # the evidence, not a staged edit of the user's tracked progress file.
    add('results/AB_PROGRESO_CT2_CT3.json',publish=False)
    for folder in ['V191_DUAL_NEURAL_AUDIT','V191_DUAL_NEURAL_AUDIT_V2','V192_DUAL_NEURAL_LEARNING','V193_FROZEN_PEER','V194_ORACLE_BANDIT']:
        for p in (B/'results'/folder).rglob('*'):
            if p.is_file():add(p.relative_to(B),publish=p.name=='SUMMARY.json')
    for prefix in ['V191','V191B','V192','V193','V194','V191_V194','V193_V194','AB_EVALUACION_V191_V194','FIG_V192','FIG_V193']:
        for p in (B/'results').glob(prefix+'*'):
            if p.is_file() and '_ARCHIVE_CONSOLE' not in p.name and '_PUBLICATION_CONSOLE' not in p.name:
                add(p.relative_to(B),publish=p.suffix not in ['.log','.py'])
    for folder in ['literatura/backups/V191_V194_20261115','handoff_codex/backups_V194']:
        for p in (B/folder).rglob('*'):
            if p.is_file():add(p.relative_to(B),publish=False)
    manuscript=B/'docs/TFM_MANUSCRITO_TRABAJO_V194.md'
    for target in re.findall(r'!\[[^\]]*\]\(([^)]+)\)',manuscript.read_text(encoding='utf-8')):
        if '://' not in target:
            p=(manuscript.parent/target).resolve();assert p.is_relative_to(B.resolve());add(p.relative_to(B))
    (OUT/'README.md').write_text('''# Evidencia V191–V194

Descargar todos los EVIDENCE_XX.zip y extraerlos en una misma carpeta vacía. Incluye todos los datos, pesos, momentos, RNG, controles positivos y negativos, borradores técnicos y protocolos de este bloque. El manifiesto externo global identifica cada payload; cada ZIP incluye el suyo. CRC y todos los hashes se comprobaron.

V192 obtiene generalización tardía de dos redes privadas con feedback completo. V193 conserva la generalización local congelando al compañero y refuta necesidad de coadaptación continua después de memorizar. V194 demuestra capacidad binaria con interlocutores correctos. No acredita grokking intrínsecamente colectivo, institución material aprendida o AB2/3.

El snapshot del progreso canónico se incluye como procedencia sin editar ni publicar una modificación de ese archivo de trabajo. Los PDF de terceros y los datos humanos de fases anteriores no se duplican. Los informes previos se identifican en el manuscrito. Leer REPRODUCE_V191_V194.md y usar el verificador de solo lectura. Los logs de esta misma operación de archivo/publicación se excluyen para evitar autorreferencia.
''',encoding='utf-8')
    add((OUT/'README.md').relative_to(B))
    hashes={p.relative_to(B).as_posix():sha(p.read_bytes()) for p in sorted(files)}
    (OUT/'EVIDENCE_PAYLOAD_SHA256.json').write_text(json.dumps(hashes,indent=2,ensure_ascii=False),encoding='utf-8')
    groups=[];current=[];size=0
    for p in sorted(files):
        length=p.stat().st_size;assert length<MAX_RAW,p
        if current and size+length>MAX_RAW:groups.append(current);current=[];size=0
        current.append(p);size+=length
    if current:groups.append(current)
    shards=[]
    for number,payloads in enumerate(groups,1):
        path=OUT/f'EVIDENCE_{number:02d}.zip'
        sub={p.relative_to(B).as_posix():hashes[p.relative_to(B).as_posix()] for p in payloads}
        encoded=json.dumps(sub,indent=2,ensure_ascii=False).encode('utf-8')
        key=f'EVIDENCE_SHARD_{number:02d}_PAYLOAD_SHA256.json'
        with zipfile.ZipFile(path,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
            for p in payloads:z.write(p,p.relative_to(B).as_posix())
            z.writestr(key,encoded)
        with zipfile.ZipFile(path) as z:
            assert z.testzip() is None and z.read(key)==encoded
            for item,expected in sub.items():assert sha(z.read(item))==expected,item
        shards.append(dict(archive=path.name,bytes=path.stat().st_size,sha256=sha(path.read_bytes()),payload_files=len(payloads),
                           CRC_verified=True,all_payload_hashes_verified=True));direct.add(path)
    manifest=dict(shards=shards,total_payload_files=len(files),total_payload_bytes=sum(p.stat().st_size for p in files),
                  all_research_payloads_preserved=True,mutable_archive_publication_logs_excluded=True,
                  PDFs_not_redistributed=True,private_human_data_included=False)
    (OUT/'ARCHIVE_MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    direct|={OUT/'ARCHIVE_MANIFEST.json',OUT/'EVIDENCE_PAYLOAD_SHA256.json'}
    paths=sorted(p.relative_to(B).as_posix() for p in direct)
    paths.append((OUT/'PUBLICATION_FILES.json').relative_to(B).as_posix())
    (OUT/'PUBLICATION_FILES.json').write_text(json.dumps(paths,indent=2),encoding='utf-8')
    print(json.dumps(dict(**manifest,direct_publication_files=len(paths))),flush=True)


if __name__=='__main__':print('LIMITS',apply_limits(2),flush=True);main()
