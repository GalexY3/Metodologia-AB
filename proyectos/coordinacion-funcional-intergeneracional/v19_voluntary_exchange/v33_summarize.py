"""V33 longer role specialization: 700→2100-update freezer audit.

Contrast simultaneous donor+role continuation and role-only updates against
the exact same V30 source; random-role controls evaluated on unseen worlds.
"""
from __future__ import annotations
import csv,json,hashlib
from pathlib import Path
import numpy as np,torch
ROOT=Path(__file__).resolve().parent;RES=ROOT/'results'
NAMES=[f'v33_{kind}_s{seed}' for kind in ('JOINT','ROLE_ONLY')
       for seed in (3111,4111)]
def read(p):return json.loads(p.read_text('utf8'))
def fmt(x):return f'{x:.4f}'
def sgn(x):return f'{x:+.4f}'
def table(rows,heads):
 return '\n'.join(['| '+' | '.join(heads)+' |',
  '| '+' | '.join(['---']*len(heads))+' |']+
  ['| '+' | '.join(map(str,r))+' |' for r in rows])
results=[];details={}
for name in NAMES:
 folder=ROOT/'runs'/name
 spec=read(folder/'v25_spec.json');stat=read(folder/'v25_status.json')
 assert spec['updates']==stat['updates']==2100
 assert spec['continuation_mode'] in ('joint','role_only')
 seed=spec['seed']
 base=f'v30_MUTUAL_C04_s{seed}'
 assert spec['continuation_from']==base
 audit=read(RES/('v30_holdout_'+name+'.json'))
 prior=read(RES/('v30_holdout_'+base+'.json'))
 assert len(audit['rows'])==len(prior['rows'])==32
 def get(collection,label='learned',topology='ring',init='monolith'):
  return next(x for x in collection['rows']
    if x['condition']==label and x['topology']==topology and x['init']==init)
 current=get(audit);before=get(prior)
 ctrl=max((get(audit,condition) for condition in ('role_random_015','role_random_035','role_random_060')),
    key=lambda x:x['food'])
 ctrl_before=max((get(prior,condition) for condition in ('role_random_015','role_random_035','role_random_060')),
    key=lambda x:x['food'])
 current_diff=current['food']-ctrl['food']
 before_diff=before['food']-ctrl_before['food']
 seeds_current=np.asarray([v['food'] for v in current['by_seed']])
 seeds_before=np.asarray([v['food'] for v in before['by_seed']])
 assert [v['seed'] for v in current['by_seed']]==[v['seed'] for v in before['by_seed']]
 paired=seeds_current-seeds_before
 boot=paired[np.random.default_rng(33112026).integers(0,len(paired),size=(10000,len(paired)))].mean(1)
 source=torch.load(ROOT/'runs'/base/'joint_latest.pt',weights_only=False,map_location='cpu')
 continuation=torch.load(folder/'joint_latest.pt',weights_only=False,map_location='cpu')
 assert source['update']==700 and continuation['update']==2100
 donor_unchanged=all(torch.equal(source['gift'][k],continuation['gift'][k])
    for k in source['gift'])
 assert donor_unchanged==(spec['continuation_mode']=='role_only')
 role_changed=any(not torch.equal(source['role'][k],continuation['role'][k])
    for k in source['role'])
 assert role_changed
 r=dict(model=name,seed=seed,continuation=spec['continuation_mode'],
   total_updates=2100,donor_unchanged=donor_unchanged,
   food_u700=before['food'],food_u2100=current['food'],
   food_change=current['food']-before['food'],
   trades_u700=before['settled_units_per_person'],
   trades_u2100=current['settled_units_per_person'],
   role_random_u700=ctrl_before['food'],
   role_random_u2100=ctrl['food'],
   learned_role_advantage_u700=before_diff,
   learned_role_advantage_u2100=current_diff,
   gain_in_role_advantage=current_diff-before_diff,
   rewired_food=get(audit,topology='rewired')['food'],
   relocated_food=get(audit,'relocated_people')['food'],
   exact_balance=get(audit)['balanced'],
   potential=get(audit)['potential_coverage'],
   food_change_95_descriptive=np.quantile(boot,[.025,.975]).tolist())
 results.append(r)
 log=[json.loads(line) for line in (folder/'v25_history.jsonl').read_text().splitlines()]
 details[name]=[dict(update=z['update'],food=next(v for v in z['development']
         if v['topology']=='ring' and v['init']=='monolith'
         and v['condition']=='normal')['food']) for z in log]
with (RES/'COMPARACION_V33.csv').open('w',encoding='utf8',newline='') as f:
 field=[k for k in results[0] if k!='food_change_95_descriptive']
 w=csv.DictWriter(f,field);w.writeheader()
 for r in results:w.writerow({k:r.get(k) for k in field})
src=['v33_continue_barter.py','v33_summarize.py',
 'PREREG_V33_OCCUPATION_LONG_TRAINING.md']
hashes={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in src}
(RES/'METRICAS_V33.json').write_text(json.dumps(
 dict(models=results,trajectories=details,source_sha256=hashes),indent=2),encoding='utf8')
report=[
 '# V33. Aprendizaje prolongado del reparto profesional en economías contractuales',
 '',
 'Experimento de continuación preregistrado 12/11/2026. Dos checkpoints V30 ya entrenados desde cero durante 700 actualizaciones fueron continuados por 1400 actualizaciones adicionales a coste fijo final0,04. Cada semilla original se bifurcó en una condición de continuar entrenando donante y actor ocupacional y otra que congeló el donante y entrenó exclusivamente la elección de profesión. Esta es una comparación de cuatro ramas de dos modelos iniciales; las ramas no son inicializaciones independientes.',
 '',
 '## Evaluación congelada en sociedades nuevas',
 '',
 table([[z['model'],z['continuation'],fmt(z['food_u700']),
  fmt(z['food_u2100']),sgn(z['food_change']),
  fmt(z['role_random_u700']),fmt(z['role_random_u2100']),
  sgn(z['learned_role_advantage_u700']),
  sgn(z['learned_role_advantage_u2100']),
  sgn(z['gain_in_role_advantage'])] for z in results],
  ['Modelo','Tratamiento','Alimento u700','Alimento u2100',
   'Cambio comida','Azar rol u700','Azar rol u2100',
   'Ventaja rol u700','Ventaja rol u2100','Mejora de ventaja']),
 '',
 'La comparación ocupacional utiliza el mayor alimento de tres tasas de movilidad aleatoria preestablecidas, con las mismas políticas de donación congeladas en el punto evaluado. Los roles profesionales iniciales son monolíticos y la recompensa propia incluye la penalización por cambiar de oficio. Las valoraciones se repiten en seis semillas ambientales reservadas y doce mundos por semilla y condición.',
 '',
 '## Mecanismo y límites',
 '',
 'En ROLE_ONLY el vector completo de parámetros neuronales donantes al actualizar2100 es bit a bit idéntico al del checkpoint del que se partió (comprobación programática realizada durante la síntesis). En JOINT ambos actores cambiaron pesos. Por tanto, el efecto de ROLE_ONLY no puede atribuirse a mejora del actor donante; el contraste es una prolongación focalizada del aprendizaje laboral.',
 '',
 'Una mejora pequeña o nula del rendimiento ocupacional pese al entrenamiento prolongado indica que la arquitectura y la función objetivo quizá permitan ya pocas ventajas adicionales en un anillo de seis vecinos, donde las especialidades complementarias son relativamente accesibles. Esta interpretación exige el contraste topológico V34, pues más tiempo no es equivalente a una red con mayores necesidades de organización.',
 '',
 '## Reproducción y criterios',
 '',
 'Script v33_continue_barter.py, preregistro PREREG_V33_OCCUPATION_LONG_TRAINING.md, cuatro checkpoints con Adam y trazas runs/v33_*, controles JSON results/v30_holdout_v33_*.json, CSV y METRICAS_V33.json. Fuente histórica V30 y oráculo físico quedan conservados. El criterio fuerte preregistrado requería +0,05 comida de la especialización frente al mejor azar. Las conclusiones no se transfieren por sí solas a N120 ni a vínculos reconectados.',
 '',
 'SHA256:',
 *[f'{k}: {v}' for k,v in hashes.items()]]
(RES/'RESULTADOS_INTEGRALES_V33.md').write_text('\n'.join(report),encoding='utf8')
print('V33_REPORT_OK',len(results))
for r in results:
 print(r['model'],'food',round(r['food_u2100'],4),
  'role_advantage',round(r['learned_role_advantage_u2100'],4),
  'gain',round(r['gain_in_role_advantage'],4))
