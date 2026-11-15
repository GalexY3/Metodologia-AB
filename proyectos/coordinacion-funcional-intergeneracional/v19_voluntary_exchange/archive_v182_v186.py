"""Archive the explicitly scoped research block with byte-exact payload hashes."""
from pathlib import Path
import hashlib
import json
import zipfile

BASE=Path(__file__).resolve().parent
OUT=BASE/'research/V182_V186_20261115'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    assert (BASE/'results/V186_INFORMATION_BOTTLENECK/SUMMARY.json').exists()
    assert (BASE/'results/V182_V186_EDITORIAL_REVISION.json').exists()
    OUT.mkdir(parents=True,exist_ok=False)
    files=set()
    direct=set()
    def add(relative,publish=True):
        p=BASE/relative
        assert p.is_file(),p
        files.add(p)
        if publish:direct.add(p)
    for pattern in ['v182_*.py','v183_*.py','v184_*.py','v185_*.py','v186_*.py',
                    'PREREG_V183_*.md','PREREG_V184_*.md','PREREG_V185_*.md','PREREG_V186_*.md']:
        for p in BASE.glob(pattern):add(p.relative_to(BASE))
    for relative in ['research_resource_limits.py','close_v182_v186.py','polish_v182_v186.py',
                     'archive_v182_v186.py','publish_v182_v186.py','REPRODUCE_V182_V186.md',
                     'docs/TFM_MANUSCRITO_TRABAJO_V181.md','docs/TFM_MANUSCRITO_TRABAJO_V186.md',
                     'docs/TFM_CAPITULO_REPRODUCCION_Y_GROKKING.md','docs/V182_V186_REPORT_TEMPLATE.md',
                     'handoff_codex/ESTADO_20261115_V186.md','handoff_codex/GOAL_CIENTIFICO_AB_TFM.md',
                     'INICIO_INVESTIGACION_CIENTIFICA.md','literatura/references_verified.json',
                     'literatura/references.bib','literatura/BIBLIOGRAFIA_ACUMULATIVA_20261114.md',
                     'results/INFORME_V182_V186_20261115.md','results/FIG_CT2_V175_V180.png']:
        add(relative)
    for p in (BASE/'validation_octave').glob('v182*.m'):add(p.relative_to(BASE))
    for folder in ['V182_YAMAN_ARCHIVE_AUDIT','V182_OCTAVE_VALIDATION','V183_HAZARD_TIMING',
                   'V184_PASTURE_REPLAY','V185_COLLECTIVE_GROKKING','V186_INFORMATION_BOTTLENECK',
                   'editorial_revision_1_V182_V186']:
        for p in (BASE/'results'/folder).rglob('*'):
            if p.is_file():add(p.relative_to(BASE),publish=p.name=='SUMMARY.json')
    for number in range(182,187):
        for pattern in [f'V{number}_*.json',f'V{number}_*.log',f'FIG_V{number}_*.png']:
            for p in (BASE/'results').glob(pattern):
                if p.is_file():add(p.relative_to(BASE),publish=p.suffix!='.log')
    for p in (BASE/'results').glob('AB_EVALUACION_V182_V186*.json'):add(p.relative_to(BASE))
    original=BASE/'literatura/original_code/Yaman2023'
    for p in (original/'source').rglob('*.m'):add(p.relative_to(BASE))
    for name in ['DOWNLOAD_MANIFEST.json','ZENODO_METADATA.json','SUPPLEMENT_METADATA.json']:
        add((original/name).relative_to(BASE))
    for folder in ['literatura/backups/V182_V186_20261115','handoff_codex/backups_V186']:
        for p in (BASE/folder).rglob('*'):
            if p.is_file():add(p.relative_to(BASE),publish=False)
    readme='''# Evidencia V182–V186

Archivo de investigación reproducible. Incluye el negativo V183, reproducción aproximada V184, piloto V185 y control causal V186. No acredita grokking colectivo ni institución privada aprendida. La reparación del diccionario es una intervención externa.

Las fuentes originales Yaman son CC0 según Zenodo8401555. Su ZIP completo está identificado y se obtiene con el downloader, no se duplica aquí. Los PDF de artículos y la distribución de Octave no se redistribuyen. Consultar REPRODUCE_V182_V186.md, el informe y los manifiestos.

El manifiesto SHA256 externo coincide byte por byte con el incrustado. Incluye todos los payloads salvo él mismo. Los borradores editoriales preservados no sustituyen al informe final. Los resultados científicos no cambiaron con la revisión editorial.
'''
    (OUT/'README.md').write_text(readme,encoding='utf-8')
    add((OUT/'README.md').relative_to(BASE))
    hashes={p.relative_to(BASE).as_posix():sha(p.read_bytes()) for p in sorted(files)}
    payload=json.dumps(hashes,indent=2,ensure_ascii=False).encode('utf-8')
    (OUT/'EVIDENCE_PAYLOAD_SHA256.json').write_bytes(payload)
    archive=OUT/'EVIDENCE.zip'
    with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
        for p in sorted(files):z.write(p,p.relative_to(BASE).as_posix())
        z.writestr('EVIDENCE_PAYLOAD_SHA256.json',payload)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert z.read('EVIDENCE_PAYLOAD_SHA256.json')==payload
        for path,expected in hashes.items():assert sha(z.read(path))==expected,path
    size=archive.stat().st_size
    assert size<95_000_000,(size,'Split archive before GitHub delivery')
    manifest=dict(archive='EVIDENCE.zip',bytes=size,sha256=sha(archive.read_bytes()),payload_files=len(hashes),
                  manifest_external_equals_embedded=True,all_payload_hashes_verified=True,CRC_verified=True,
                  original_large_archive_not_redistributed=True,private_human_data_included=False)
    (OUT/'ARCHIVE_MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    for p in [archive,OUT/'ARCHIVE_MANIFEST.json',OUT/'EVIDENCE_PAYLOAD_SHA256.json']:direct.add(p)
    paths=[p.relative_to(BASE).as_posix() for p in sorted(direct)]
    (OUT/'PUBLICATION_FILES.json').write_text(json.dumps(paths,indent=2),encoding='utf-8')
    print(json.dumps(dict(**manifest,direct_publication_files=len(paths))),flush=True)


if __name__=='__main__':main()
