"""V37 reproducible individual reward-only newcomer socialization report."""
from __future__ import annotations
import json,csv,hashlib
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent;RES=ROOT/'results'
NAMES=[f'v37_COHORT_C{price}_s{seed}'
  for price in ('04','12') for seed in (3111,4111)]
def load(p):return json.loads(p.read_text('utf8'))
def fmt(x):return f'{x:.4f}'
def plus(x):return f'{x:+.4f}'
def pct(x):return f'{x:.1%}'
def table(rows,heads):
 return '\n'.join(['| '+' | '.join(heads)+' |',
  '| '+' | '.join(['---']*len(heads))+' |']+
  ['| '+' | '.join(map(str,row))+' |' for row in rows])
out=[];record={}
for name in NAMES:
 folder=ROOT/'runs'/name
 spec=load(folder/'v37_spec.json')
 status=load(folder/'v37_status.json')
 assert status['state']=='completed' and spec['updates']==status['updates']==700
 assert len(spec['newcomer_indices'])==30
 audit=load(RES/('v37_holdout_'+name+'.json'))
 assert len(audit['rows'])==18 and len(audit['seeds'])==6 and audit['worlds_per_seed']==16
 assert len(set(audit['cohort_indices']))==30
 table_seed={(v['seed'],v['mode']):v for v in audit['rows']}
 assert len(table_seed)==18
 data={mode:[table_seed[(seed,mode)] for seed in audit['seeds']]
   for mode in ('none','fresh','trained')}
 for seed in audit['seeds']:
  assert abs(table_seed[(seed,'none')]['food_pre']-
             table_seed[(seed,'fresh')]['food_pre'])<1e-7
  assert abs(table_seed[(seed,'none')]['food_pre']-
             table_seed[(seed,'trained')]['food_pre'])<1e-7
 def mean(mode,k):return float(np.mean([x[k] for x in data[mode]]))
 gain_new=np.asarray([z['newcomer_41_48']-y['newcomer_41_48']
  for z,y in zip(data['trained'],data['fresh'])])
 gain_old=np.asarray([z['resident_41_48']-y['resident_41_48']
  for z,y in zip(data['trained'],data['fresh'])])
 gain_pop=np.asarray([z['food_41_48']-y['food_41_48']
  for z,y in zip(data['trained'],data['fresh'])])
 ratio=np.asarray([z['surplus_retained'] for z in data['trained']])
 def ci(v):
  rnd=np.random.default_rng(37112026)
  boot=v[rnd.integers(0,len(v),(10000,len(v)))].mean(1)
  return np.quantile(boot,[.025,.975]).tolist()
 row=dict(model=name,seed_neural=spec['source_spec']['seed'],
  price=spec['source_spec']['cost'],
  control_no_replacement=mean('none','food_41_48'),
  fresh_food=mean('fresh','food_41_48'),
  trained_food=mean('trained','food_41_48'),
  fresh_newcomer_food=mean('fresh','newcomer_41_48'),
  trained_newcomer_food=mean('trained','newcomer_41_48'),
  newcomer_gain=float(gain_new.mean()),
  newcomer_gain_ci025=ci(gain_new)[0],
  newcomer_gain_ci975=ci(gain_new)[1],
  fresh_resident_food=mean('fresh','resident_41_48'),
  trained_resident_food=mean('trained','resident_41_48'),
  resident_gain=float(gain_old.mean()),
  resident_gain_ci025=ci(gain_old)[0],
  resident_gain_ci975=ci(gain_old)[1],
  population_gain=float(gain_pop.mean()),
  fresh_retained=mean('fresh','surplus_retained'),
  trained_retained=float(ratio.mean()),
  trained_retained_ci025=ci(ratio)[0],
  trained_retained_ci975=ci(ratio)[1],
  h37_newcomer_success=bool(gain_new.mean()>=.03),
  h37_resilience_success=bool(ratio.mean()>=.85),
  h37_no_resident_harm=bool(gain_old.mean()>=0),
  initial_new_index_set=spec['newcomer_indices'],
  n_environment_seeds=len(audit['seeds']),
  worlds_per_seed=audit['worlds_per_seed'])
 out.append(row)
 record[name]=dict(per_seed=dict(newcomer_gain=gain_new.tolist(),
   resident_gain=gain_old.tolist(),population_gain=gain_pop.tolist(),
   recovered_ratio=ratio.tolist()),trace_file='v37_holdout_'+name+'.json')
with (RES/'COMPARACION_V37.csv').open('w',encoding='utf8',newline='') as f:
 keys=[k for k in out[0] if k!='initial_new_index_set']
 w=csv.DictWriter(f,keys);w.writeheader()
 for r in out:w.writerow({k:r[k] for k in keys})
sha_files=('PREREG_V37_NEWCOMER_RELEARNING.md',
   'v37_train.py','v37_audit.py','v37_summarize.py','test_v37_cohorts.py')
sha={x:hashlib.sha256((ROOT/x).read_bytes()).hexdigest() for x in sha_files}
(RES/'METRICAS_V37.json').write_text(json.dumps(dict(models=out,
 paired_trace=record,sha256=sha,
 training_agent_rounds=4*700*12*48*120,
 training_newcomer_person_rounds=4*700*12*24*30,
 prereg_threshold_newcomer_gain=.03,
 prereg_threshold_surplus_retained=.85),indent=2),encoding='utf8')
success_a=all(r['h37_newcomer_success'] for r in out)
success_b=sum(r['h37_resilience_success'] for r in out)>=3 and any(
 r['h37_resilience_success'] and r['price']==.12 for r in out)
success_c=all(r['h37_no_resident_harm'] for r in out)
result=[
 '# V37. Aprendizaje de recién llegados mediante retorno material individual en sociedades establecidas',
 '',
 'Campaña preregistrada el 12/11/2026 tras el resultado de V35. Se conservan como incumbentes los cuatro modelos V31 con 120 personas y cuatro profesiones, a precios0,04 y0,12. En cada modelo se seleccionan por semilla30 posiciones fijas para nuevos habitantes inicializados sin transferir pesos de los antiguos. Los 90 residentes mantienen su política congelada; las nuevas personas aprenden por su alimento propio mediante REINFORCE durante700 actualizaciones de 12 mundos por corrida. En cada repetición hay 24 rondas con los residentes anteriores y 24 con las nuevas personas, desde la ronda25 hasta48.',
 '',
 'El régimen contractual de mutuo consentimiento sigue disponible institucionalmente de modo externo; este experimento prueba aprendizaje individual de adaptación a una institución existente, no evolución natural de normas ni entrenamiento supervisado por residentes.',
 '',
 '## Evaluación congelada y emparejada en seis ambientes nuevos',
 '',
 table([[r['model'],str(r['price']),
   fmt(r['control_no_replacement']),fmt(r['fresh_food']),
   fmt(r['trained_food']),fmt(r['fresh_newcomer_food']),
   fmt(r['trained_newcomer_food']),plus(r['newcomer_gain']),
   plus(r['resident_gain']),pct(r['trained_retained'])] for r in out],
 ['Modelo','Precio','Control original','Nuevos sin entrenar',
   'Nuevos entrenados','Nuevos crudos','Nuevos formados',
   'Mejora nuevos','Cambio residentes','Excedente recuperado']),
 '',
 'El control original no incorpora nuevos agentes; los brazos de reemplazo utilizan exactamente los mismos30 puestos y guardan la misma inicialización de sus redes nuevas. Para el contrafactual sin aprender se usan sus pesos iniciales guardados antes de cualquier actualización; para el brazo entrenado, los pesos después de700 actualizaciones. Se restablecen las semillas antes de cada brazo y las 24 rondas anteriores al choque se verifican iguales. No se aplica imitación ni recompensa grupal.',
 '',
 '## Contraste de hipótesis preregistradas',
 '',
 table([['H37a aumento de comida de nuevos ≥0,030 en todas las cuatro',
    'sí' if success_a else 'no'],
 ['H37b excedente social recuperado ≥85% en 3/4, con caso caro',
    'sí' if success_b else 'no'],
 ['H37c residentes no perjudicados por nuevos aprendidos en 4/4',
    'sí' if success_c else 'no']],
 ['Criterio','Cumplimiento']),
 '',
 '## Mecanismos y límites',
 '',
 '[Inferencia] Si los nuevos mejoran más que los residentes por efecto del entrenamiento sobre su propio alimento, existe una vía de recuperación intergeneracional mediante adquisición individual de competencias dentro de una estructura social preexistente. Sin embargo, los mismos participantes de la cohorte pasan por cientos de episodios experimentales, por lo que la intervención representa aprendizaje acumulado por experiencia replicada, no adaptación completa dentro de un único episodio de 24 rondas. La identidad de los30 puestos es fija por modelo, una dimensión de dependencia contextual todavía sin resolver.',
 '',
 'Los seis ambientes nuevos contienen16 mundos cada uno; estos mundos no son inicializaciones independientes de los modelos de entrenamiento. Los intervalos descriptivos bootstrap de ganancia de cohorte y recuperación se re-muestrean sobre seis semillas ambientales apareadas, no sobre los individuos. La variación de costes permite observar la sensibilidad de aprendizaje bajo beneficios económicos distintos.',
 '',
 '## Reproducción',
 '',
 'Preregistro PREREG_V37_NEWCOMER_RELEARNING.md, script de entrenamiento v37_train.py, auditor v37_audit.py, tests test_v37_cohorts.py, checkpoints de dos actores privados por cada cohorte en runs/v37_COHORT_*, snapshots iniciales guardados, historial y datos crudos por ronda y mundo en results/v37_holdout_v37_*.json. CSV y JSON agrupados en COMPARACION_V37.csv y METRICAS_V37.json.',
 '',
 'SHA256:',*[f'{k}: {v}' for k,v in sha.items()]]
(RES/'RESULTADOS_INTEGRALES_V37.md').write_text('\n'.join(result),encoding='utf8')
print('V37_REPORT_OK',len(out),'H37a',success_a,'H37b',success_b,'H37c',success_c)
for r in out:
 print(r['model'],'new_gain',round(r['newcomer_gain'],4),
   'resident_gain',round(r['resident_gain'],4),
   'surplus',round(r['trained_retained'],4))
