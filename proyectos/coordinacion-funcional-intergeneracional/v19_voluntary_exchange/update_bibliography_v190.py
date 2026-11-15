"""Add consulted primary predecessors and preserve the previous catalogue."""
from pathlib import Path
import hashlib
import json
import shutil

B=Path(__file__).resolve().parent
backup=B/'literatura/backups/V187_V190_20261115'
backup.mkdir(parents=True,exist_ok=False)
names=['references_verified.json','references.bib','BIBLIOGRAFIA_ACUMULATIVA_20261114.md']
for name in names:shutil.copyfile(B/'literatura'/name,backup/name)
d=json.loads((B/'literatura/references_verified.json').read_text(encoding='utf-8'))
additions=[
 dict(id='Lyle2026GrokkingNonstationarity',authors='Lyle, Clare; Sokar, Ghada; György, András; Pascanu, Razvan',
      year=2026,title='What can grokking teach us about learning under non-stationarity?',
      container='Proceedings of the 4th Conference on Lifelong Learning Agents, PMLR330:635–656',doi=None,
      url='https://proceedings.mlr.press/v330/lyle26a.html',theme='GROKKING_PLASTICITY',
      contribution='Relates delayed generalization and primacy bias to feature learning; proposes effective-learning-rate re-warming.',
      our_experiments='V185–V190',novelty_constraint='Generic links between nonstationarity, feature plasticity and grokking are prior work; a private-interaction result needs a narrower discriminating prediction.',
      verification='primary PMLR metadata and downloaded primary PDF main text sections1–7, pp1–10; appendices not fully reviewed',
      checked_on='2026-11-15',full_text_reviewed=False,
      bibliographic_discrepancy='PMLR records 2026 and author order Lyle,Sokar,Gyorgy,Pascanu; PDF header says CoLLAs2025 and lists Lyle,Sokar,Pascanu,Gyorgy. Catalogue follows PMLR without silently reconciling the discrepancy.',
      source_manifest='literatura/original_code/Lyle2026/SOURCE_MANIFEST.json'),
 dict(id='CharpenayLeTreustRoumy2024',authors='Charpenay, Nicolas; Le Treust, Maël; Roumy, Aline',
      year=2024,title='Side Information Design in Zero-Error Coding for Computing',container='Entropy26(4):338',
      doi='10.3390/e26040338',url='https://www.mdpi.com/1099-4300/26/4/338',theme='COMMUNICATION_INFORMATION',
      contribution='Zero-error functional communication, side information, characteristic graphs and graph colorings.',
      our_experiments='V189,V189B,V190',novelty_constraint='Confusability/coloring constraints are classical. Our finite counting bound and designed support are not claimed as new information-theoretic theorems.',
      verification='primary publisher abstract/introduction, definitions1–6 and characteristic-graph/coloring equivalence in section3.1; not full paper',
      checked_on='2026-11-15',full_text_reviewed=False),
]
existing={r['id'] for r in d['references']}
assert all(r['id'] not in existing for r in additions)
d['references'].extend(additions);d['number_verified']=len(d['references']);d['review_date']='2026-11-15'
for r in d['references']:
    if r['id']=='SpikeEtAl2017LearnedSignaling':
        r['verification']='primary abstract, methods3.1–4.1 and discussion relevant to reinforcement, limited memory and inhibition; not complete full-text review'
        r['original_code_availability']='Published repository github.com/matspike/Cogscisignaling returned404 through website, connector and public API on2026-11-15. V187 is a documented independent methods reimplementation, with uniform fallback for an empty urn, not original-code execution.'
(B/'literatura/references_verified.json').write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8')
with (B/'literatura/references.bib').open('a',encoding='utf-8') as f:
    f.write('''
@inproceedings{Lyle2026GrokkingNonstationarity,
  author = {Lyle, Clare and Sokar, Ghada and György, András and Pascanu, Razvan},
  title = {What can grokking teach us about learning under non-stationarity?},
  booktitle = {Proceedings of the 4th Conference on Lifelong Learning Agents},
  series = {Proceedings of Machine Learning Research}, volume = {330},
  pages = {635--656}, year = {2026},
  url = {https://proceedings.mlr.press/v330/lyle26a.html},
  note = {PMLR metadata differs from PDF header year and author order; see verified catalogue}
}
@article{CharpenayLeTreustRoumy2024,
  author = {Charpenay, Nicolas and Le Treust, Maël and Roumy, Aline},
  title = {Side Information Design in Zero-Error Coding for Computing},
  journal = {Entropy}, volume = {26}, number = {4}, pages = {338}, year = {2024},
  doi = {10.3390/e26040338}, url = {https://www.mdpi.com/1099-4300/26/4/338}
}
''')
with (B/'literatura/BIBLIOGRAFIA_ACUMULATIVA_20261114.md').open('a',encoding='utf-8') as f:
    f.write('\n## Antecedentes contrastados en V187–V190\n\n')
    for r in additions:
        f.write(f"**{r['authors']} ({r['year']}).** [{r['title']}]({r['url']}). {r['container']}.\n\n{r['contribution']} Restricción: {r['novelty_constraint']} Alcance: {r['verification']}.\n\n")
    f.write('La revisión sigue siendo exploratoria. Los nuevos registros no constituyen una búsqueda sistemática ni acreditan prioridad por ausencia de resultados de búsqueda. El registro PMLR de Lyle difiere del PDF en fecha y orden de autores; se conserva la discrepancia en el catálogo.\n')
print(json.dumps(dict(records=len(d['references']),backups={name:hashlib.sha256((backup/name).read_bytes()).hexdigest() for name in names})))
