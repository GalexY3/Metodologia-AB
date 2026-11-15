"""Check the delivered document links and evaluations after visual review."""
from pathlib import Path
import hashlib
import json
import re

B=Path(__file__).resolve().parent
evaluation=json.loads((B/'results/AB_EVALUACION_V187_V190_20261115.json').read_text(encoding='utf-8'))
audit=json.loads((B/'results/V187_V190_FINAL_AUDIT.json').read_text(encoding='utf-8'))
checks=[]
for relative in ['results/INFORME_V187_V190_20261115.md','docs/TFM_MANUSCRITO_TRABAJO_V190.md']:
    p=B/relative;text=p.read_text(encoding='utf-8')
    assert not re.search(r'__[A-Z_]+__',text)
    links=re.findall(r'!\[[^\]]*\]\(([^)]+)\)',text)
    for link in links:
        if '://' not in link:assert (p.parent/link).resolve().is_file(),link
    checks.append(dict(path=relative,local_image_links=len(links),all_exist=True,unfilled_placeholders=False))
assert hashlib.sha256((B/'docs/TFM_MANUSCRITO_TRABAJO_V190.md').read_bytes()).hexdigest()==evaluation['manuscript_sha256']
assert hashlib.sha256((B/'results/AB_PROGRESO_CT2_CT3.json').read_bytes()).hexdigest()==audit['canonical_progress_sha256']
assert len(json.loads((B/'literatura/references_verified.json').read_text(encoding='utf-8'))['references'])==evaluation['bibliographic_records']==96
p=B/'handoff_codex/ESTADO_V190_EN_CURSO_20261115.md'
original=p.read_text(encoding='utf-8')
assert not original.startswith('> FINALIZADO')
p.write_text('> FINALIZADO. El proceso terminó; consultar ESTADO_20261115_V190.md. Se conserva debajo el estado transitorio original.\n\n'+original,encoding='utf-8')
result=dict(document_checks=checks,figures_visually_reviewed=3,figure_labels_readable=True,
            manuscript_hash_matches=True,canonical_score_file_unchanged=True,bibliographic_records=96,
            manuscript_is_working_draft_not_academically_approved=True)
out=B/'results/V187_V190_EDITORIAL_AUDIT.json';assert not out.exists()
out.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result))
