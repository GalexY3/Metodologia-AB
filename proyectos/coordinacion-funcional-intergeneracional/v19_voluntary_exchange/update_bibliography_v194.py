"""Record consulted primary predecessors; preserve the V190 catalogue."""
from pathlib import Path
import json
import shutil

B=Path(__file__).resolve().parent
backup=B/'literatura/backups/V191_V194_20261115';backup.mkdir(parents=True,exist_ok=False)
for name in ['references_verified.json','references.bib','BIBLIOGRAFIA_ACUMULATIVA_20261114.md']:
    shutil.copyfile(B/'literatura'/name,backup/name)
p=B/'literatura/references_verified.json';d=json.loads(p.read_text(encoding='utf-8'))
new=[
 dict(id='KleinEtAl2004MutualLearning',authors='Klein, Einat; Mislovaty, Rachel; Kanter, Ido; Ruttor, Andreas; Kinzel, Wolfgang',
      year=2004,title='Synchronization of neural networks by mutual learning and its application to cryptography',
      container='Advances in Neural Information Processing Systems17',doi=None,
      url='https://proceedings.neurips.cc/paper/2004/hash/5a45828dead8c065099cb653a2185df1-Abstract.html',
      theme='MUTUAL_LEARNING',contribution='Analytical and simulated synchronization of mutually learning neural networks.',
      our_experiments='V191–V194',novelty_constraint='Coordination and synchronization between separate neural networks are longstanding prior work; a delayed test curve is not enough for a new collective mechanism.',
      verification='primary metadata, abstract, introduction and section2 mutual-perceptron learning; remaining cryptographic sections not fully reviewed',
      full_text_reviewed=False,checked_on='2026-11-15'),
 dict(id='CiosekWhiteson2020EPG',authors='Ciosek, Kamil; Whiteson, Shimon',year=2020,
      title='Expected Policy Gradients for Reinforcement Learning',container='Journal of Machine Learning Research21(52):1–51',doi=None,
      url='https://www.jmlr.org/papers/v21/18-012.html',theme='CREDIT_VARIANCE',
      contribution='Integrates across actions in policy-gradient estimates and studies variance reduction.',
      our_experiments='V191–V194',novelty_constraint='Marginalization and generic variance reduction are not new. Our MSE-regression estimator identity is not claimed as EPG or a new algorithm.',
      verification='primary JMLR metadata and abstract; full journal text not reviewed',full_text_reviewed=False,
      version_note='V191/V192 notes initially cited the2018arXiv version1801.03326; catalogue uses the2020JMLR journal version.',checked_on='2026-11-15'),
 dict(id='KakadeEtAl2008Banditron',authors='Kakade, Sham M.; Shalev-Shwartz, Shai; Tewari, Ambuj',year=2008,
      title='Efficient bandit algorithms for online multiclass prediction',container='ICML2008:440–447',doi='10.1145/1390156.1390212',
      url='https://doi.org/10.1145/1390156.1390212',theme='BANDIT_CLASSIFICATION',
      contribution='Banditron learns multiclass predictions from correctness feedback and provides mistake bounds under its assumptions.',
      our_experiments='V194',novelty_constraint='Binary feedback is not in itself an impossibility argument. Bounds for its linear predictor are not transferred to our neural game; Banditron was not executed.',
      verification='primary ACM metadata and author-hosted PDF abstract/introduction; theorem proofs not fully reviewed',full_text_reviewed=False,checked_on='2026-11-15'),
]
ids={r['id'] for r in d['references']};assert not any(r['id'] in ids for r in new)
d['references'].extend(new);d['number_verified']=len(d['references'])
coma=next(r for r in d['references'] if r['id']=='FoersterCOMA2018')
coma['V191_V194_review_scope']='primary abstract and critic/counterfactual-baseline method excerpts; original algorithm not executed'
coma['our_experiments'] += ',V191–V194'
p.write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8')
with (B/'literatura/references.bib').open('a',encoding='utf-8') as f:
    f.write('''
@inproceedings{KleinEtAl2004MutualLearning,
 author={Klein, Einat and Mislovaty, Rachel and Kanter, Ido and Ruttor, Andreas and Kinzel, Wolfgang},
 title={Synchronization of neural networks by mutual learning and its application to cryptography},
 booktitle={Advances in Neural Information Processing Systems},volume={17},year={2004},
 url={https://proceedings.neurips.cc/paper/2004/hash/5a45828dead8c065099cb653a2185df1-Abstract.html}
}
@article{CiosekWhiteson2020EPG,
 author={Ciosek, Kamil and Whiteson, Shimon},title={Expected Policy Gradients for Reinforcement Learning},
 journal={Journal of Machine Learning Research},volume={21},number={52},pages={1--51},year={2020},
 url={https://www.jmlr.org/papers/v21/18-012.html}
}
@inproceedings{KakadeEtAl2008Banditron,
 author={Kakade, Sham M. and Shalev-Shwartz, Shai and Tewari, Ambuj},
 title={Efficient bandit algorithms for online multiclass prediction},booktitle={ICML},pages={440--447},
 year={2008},doi={10.1145/1390156.1390212}
}
''')
with (B/'literatura/BIBLIOGRAFIA_ACUMULATIVA_20261114.md').open('a',encoding='utf-8') as f:
    f.write('\n## Antecedentes de V191–V194\n\n')
    for r in new:f.write(f"**{r['authors']} ({r['year']}).** [{r['title']}]({r['url']}).\n\n{r['contribution']} Restricción: {r['novelty_constraint']} Alcance: {r['verification']}.\n\n")
    f.write('COMA ya constaba en el catálogo. Se consultaron de nuevo sus pasajes sobre crítico centralizado y baseline contrafactual. Esta revisión sigue siendo exploratoria y no sistemática; no se afirma prioridad por búsquedas sin coincidencias.\n')
print(json.dumps(dict(bibliographic_records=len(d['references']),new_records=len(new),previous_catalogue_backed_up=True)))
