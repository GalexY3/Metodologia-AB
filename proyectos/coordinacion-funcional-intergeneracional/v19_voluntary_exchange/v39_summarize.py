"""V39 preregistered causal institutional-outage assessment."""
from __future__ import annotations
import csv,json,hashlib
from pathlib import Path
import numpy as np
from v39_contract_outage import SOURCE_NAMES,ARMS
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'results'
def read(p):return json.loads(p.read_text('utf8'))
def f(v):return f"{v:.4f}"
def signed(v):return f"{v:+.4f}"
def table(rows,heads):
 return "\n".join(["| "+" | ".join(heads)+" |",
  "| "+" | ".join(["---"]*len(heads))+" |"]+
  ["| "+" | ".join(map(str,r))+" |" for r in rows])
records=[];tests=[];uncertainty={}
for name in SOURCE_NAMES:
 doc=read(OUT/('v39_contract_outage_'+name+'.json'))
 assert doc['no_policy_training'] and doc['matched_preperiod']
 assert len(doc['seeds'])==6 and len(doc['rows'])==24
 envs={s:{x['arm']:x for x in doc['rows'] if x['seed']==s} for s in doc['seeds']}
 assert all(set(envs[s])==set(ARMS) for s in doc['seeds'])
 def m(arm,period,key):
  return float(np.mean([envs[s][arm]['intervals'][period][key] for s in doc['seeds']]))
 ctl=m('control',1,'food')
 closed=m('closed8',1,'food')
 unilateral=m('unilateral8',1,'food')
 perm=m('unilateral_permanent',3,'food')
 baseline_late=m('control',3,'food')
 recovery_late=m('closed8',3,'food')
 unilateral_recovery_late=m('unilateral8',3,'food')
 ratio=np.asarray([envs[s]['closed8']['late_surplus_ratio'] for s in doc['seeds']])
 delta_unilateral=np.asarray([
   envs[s]['unilateral8']['intervals'][1]['food']-envs[s]['control']['intervals'][1]['food'] for s in doc['seeds']])
 delta_closed=np.asarray([
   envs[s]['closed8']['intervals'][1]['food']-envs[s]['control']['intervals'][1]['food'] for s in doc['seeds']])
 rng=np.random.default_rng(39112026)
 def bootstrap(v):
  draws=v[rng.integers(0,6,(10000,6))].mean(1)
  return np.quantile(draws,[.025,.975]).tolist()
 uncertainty[name]=dict(delta_unilateral_by_seed=delta_unilateral.tolist(),
    delta_closed_by_seed=delta_closed.tolist(),
    late_retained_surplus_by_seed=ratio.tolist(),
    descriptive_boot_unilateral=bootstrap(delta_unilateral),
    descriptive_boot_closed=bootstrap(delta_closed),
    descriptive_boot_retained=bootstrap(ratio))
 r=dict(model=name,n=doc['source_spec']['n'],
  cost=doc['source_spec']['cost'],worlds_per_seed=doc['worlds_per_seed'],
  pre_food=m('control',0,'food'),
  contracted_during=m('control',1,'food'),
  closed8_during=closed,
  unilateral8_during=unilateral,
  closed8_delta=closed-ctl,
  unilateral8_delta=unilateral-ctl,
  proposals_contract=m('control',1,'proposals'),
  proposals_unilateral=m('unilateral8',1,'proposals'),
  transfers_contract=m('control',1,'transfers'),
  transfers_unilateral=m('unilateral8',1,'transfers'),
  late_control=baseline_late,
  late_recovered_from_closed=recovery_late,
  late_recovered_from_unilateral8=unilateral_recovery_late,
  late_unilateral_permanent=perm,
  late_closed_surplus_ratio=float(ratio.mean()),
  h39a_unilateral_lower_by_003=bool(unilateral-ctl<=-.03),
  h39b_closed_lower_by_010=bool(closed-ctl<=-.10),
  h39c_recovery_above_90pct=bool(float(ratio.mean())>=.90))
 records.append(r)
 tests.append(r)
for r in records:
 assert r['closed8_during']>=.19, r['model']
with (OUT/'COMPARACION_V39.csv').open('w',newline='',encoding='utf8') as file:
 w=csv.DictWriter(file,list(records[0]));w.writeheader();w.writerows(records)
decisions=dict(
 h39a=sum(x['h39a_unilateral_lower_by_003'] for x in records)>=4,
 h39b=all(x['h39b_closed_lower_by_010'] for x in records),
 h39c=sum(x['h39c_recovery_above_90pct'] for x in records)>=5)
sha_names=("PREREG_V39_CONTRACT_REMOVAL.md","v39_contract_outage.py",
           "v39_summarize.py","test_v39_outage.py",
           "NOTA_CALIDAD_V39_H39B.md")
hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sha_names}
(OUT/'METRICAS_V39.json').write_text(json.dumps(dict(
  models=records,hypotheses=decisions,paired_uncertainty=uncertainty,
  six_neural_models=True,
  environment_seed_count_per_model=6,
  hypothetical_world_paths=sum(r['worlds_per_seed']*6*4 for r in records),
  no_new_neural_training=True,
  hashes=hashes),indent=2),encoding='utf8')
short=[[x['model'],str(x['cost']),f(x['contracted_during']),
  f(x['closed8_during']),f(x['unilateral8_during']),
  signed(x['closed8_delta']),signed(x['unilateral8_delta']),
  f"{x['late_closed_surplus_ratio']:.1%}"] for x in records]
later=[[x['model'],f(x['late_control']),f(x['late_recovered_from_closed']),
 f(x['late_recovered_from_unilateral8']),
 f(x['late_unilateral_permanent']),
 f(x['transfers_contract']),f(x['transfers_unilateral'])]
 for x in records]
report=[
 '# V39 — Dependencia de políticas cooperativas respecto a las reglas de liquidación contractual',
 '',
 'Campaña preregistrada 12/11/2026 sin reentrenamiento. Seis checkpoints neuronales: dos V30 de48 personas con precio0,04 y cuatro V31 de120 personas, dos a precio0,04 y dos a0,12. Todas las políticas de propuestas dirigidas y cambio de profesión se congelan. Seis semillas ambientales por checkpoint y12 u8 mundos por semilla, emparejados. En rondas1–24 las intervenciones son idénticas al control; en rondas25–32 se cambia temporalmente la regla contractual o se bloquean entregas; en rondas33–48 se restaura, salvo el comparador de unilateralidad permanente.',
 '',
 '## Efecto de retirar la garantía contractual en rondas25–32',
 '',
 table(short,['Modelo','Precio','Contratos normales','Cierre del mercado',
 'Donaciones unilaterales','Δ cierre','Δ unilateral','Excedente restaurado']),
 '',
 'Importante: la intervención UNILATERAL8 ejecuta **todas las propuestas** de las redes originalmente entrenadas bajo contratos. No obliga a los agentes a volver a aprender un juego de donaciones unilaterales, ni demuestra que mantendrían ese volumen de contribuciones a largo plazo ante incentivos personales negativos. El efecto de reemplazar una regla de liquidación es diferente del efecto de capacitar un actor en esa regla.',
 '',
 '## Recuperación y transferencia de políticas congeladas',
 '',
 table(later,['Modelo','Comida final control',
  'Restaurada tras cierre','Restaurada tras unilateral8',
  'Unilateral permanente','Entregas normales/pers.',
  'Entregas unilaterales/pers.']),
 '',
 'Las cifras de propuestas distinguen intención de intercambio y transferencia efectivamente liquidada. En el brazo unilateral pueden ejecutarse más unidades que bajo consentimiento bilateral, elevando también el coste privado por unidad enviada; si mejora el alimento poblacional ello no implica que la estrategia sea estable o que cada donante se beneficie de su contribución marginal. La prueba de contrato y no contrato deja constantes redes, roles, costos y recompensas individuales pero altera el procedimiento de entrega.',
 '',
 '## Falsadores preregistrados',
 '',
 table([[k,('NO EVALUABLE: umbral inalcanzable para coste 0,12'
     if k=='h39b' else 'CUMPLIDO' if v else 'FALSADO')]
     for k,v in decisions.items()],
   ['Hipótesis','Resultado']),
 '',
 'H39a predecía que quitar el consentimiento recíproco reduciría≥0,03 la alimentación durante la intervención unilateral en≥4/6 modelos y quedó falsada. H39b exigía reducir≥0,10 en6/6 modelos; sin embargo, fue **mal calibrada**: los modelos de coste0,12 solo disponían de aproximadamente0,053 de excedente sobre0,20. La caída≥0,10 es materialmente imposible al cerrar el mercado en esos dos modelos. La validez inferencial de H39b queda INVALIDADA sin alterar retrospectivamente su umbral; se mantiene el resultado numérico literal y el test mecánico de0 entregas. Véase NOTA_CALIDAD_V39_H39B.md. H39c predecía conservar≥90% al restaurar la liquidación, y se observó en6/6.',
 '',
 '## Validez, incertidumbre y límites',
 '',
 'Este diseño separa dependencia de política y dependencia de regla institucional, pero no reemplaza un experimento de aprendizaje endógeno sin contratos. Las seis semillas ambientales condicionadas a cada checkpoint son pares de prueba, no seis inicializaciones de entrenamiento distintas. Los intervalos bootstrap descriptivos se calculan por semilla ambiental, no por mundo ni individuo. La regla de contrato sigue programada por el diseñador.',
 '',
 'RQ1 queda abordada para **políticas congeladas entrenadas bajo contrato**. RQ2, surgimiento de reciprocidad no contractual individualmente estable, continúa abierta. Tampoco se identifica invención de normas ni equilibrio perfecto en subjuegos. No declarar OBJETIVO COMPLETADO.',
 '',
 '## Datos y procedencia',
 '',
 'Preregistro PREREG_V39_CONTRACT_REMOVAL.md. Evaluador v39_contract_outage.py, tests test_v39_outage.py, por semilla y ronda results/v39_contract_outage_v30_*.json y results/v39_contract_outage_v31_*.json, CSV COMPARACION_V39.csv. Código y preregistro SHA256:',
 *[f'{name}: {value}' for name,value in hashes.items()]]
(OUT/'RESULTADOS_INTEGRALES_V39.md').write_text('\n'.join(report),encoding='utf8')
print('V39_REPORT_OK',len(records),'H39',decisions)
for r in records:
 print(r['model'],'contract',round(r['contracted_during'],4),
  'unilateral',round(r['unilateral8_during'],4),
  'closed',round(r['closed8_during'],4),
  'recover',round(r['late_closed_surplus_ratio'],3))
