"""V34 degree-four scarcity versus degree-six exchange and random roles."""
from __future__ import annotations
import csv,json,hashlib
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
RES=ROOT/'results'
NAMES=[f'v34_N48_D4_MUTUAL_s{seed}' for seed in (3111,4111)]
def read(p):return json.loads(p.read_text('utf8'))
def fmt(x):return f'{x:.4f}'
def sign(x):return f'{x:+.4f}'
def table(items,heads):
 return '\n'.join(['| '+' | '.join(heads)+' |',
   '| '+' | '.join(['---']*len(heads))+' |']+
  ['| '+' | '.join(map(str,row))+' |' for row in items])
rows=[];intervals={}
for name in NAMES:
 p=ROOT/'runs'/name
 spec=read(p/'v25_spec.json');status=read(p/'v25_status.json')
 assert status['state']=='completed' and status['updates']==700
 assert spec['v34_degree']==4 and spec['settlement']=='mutual'
 hold=read(RES/('v30_holdout_'+name+'.json'))
 causal=read(RES/('v30_causal_'+name+'.json'))
 assert len(hold['rows'])==32 and len(causal['rows'])==8
 baseline_name=f'v30_MUTUAL_C04_s{spec["seed"]}'
 baseline=read(RES/('v30_holdout_'+baseline_name+'.json'))
 bc=read(RES/('v30_causal_'+baseline_name+'.json'))
 def get(data,condition='learned',topology='ring',init='monolith'):
  return next(x for x in data['rows'] if x['condition']==condition and x['topology']==topology and x['init']==init)
 def ca(data,topology='ring',init='monolith',mode='normal'):
  return next(x for x in data['rows'] if x['topology']==topology and x['init']==init and x['mode']==mode)
 observed=get(hold)
 winner=max([get(hold,'role_random_'+rate) for rate in ('015','035','060')],key=lambda x:x['food'])
 prior=get(baseline)
 prior_best=max([get(baseline,'role_random_'+rate) for rate in ('015','035','060')],key=lambda x:x['food'])
 cf=ca(causal)
 pre_cf=ca(bc)
 same_seeds=[v['seed'] for v in observed['by_seed']]==[v['seed'] for v in winner['by_seed']]
 assert same_seeds
 diff=np.asarray([v['food'] for v in observed['by_seed']])-np.asarray([v['food'] for v in winner['by_seed']])
 sampled=diff[np.random.default_rng(20261134).integers(0,6,(10000,6))].mean(1)
 intervals[name]=dict(seedwise_advantage=diff.tolist(),
 descriptive_bootstrap_95=np.quantile(sampled,[.025,.975]).tolist())
 rows.append(dict(model=name,seed=spec['seed'],degree=4,
 food=observed['food'],trades=observed['settled_units_per_person'],
 coverage=observed['distinct_coverage'],
 potential_learned=observed['potential_coverage'],
 potential_random=winner['potential_coverage'],
 full=observed['complete'],exact_balance=observed['balanced'],
 best_random_food=winner['food'],role_advantage=observed['food']-winner['food'],
 prior_degree6_food=prior['food'],
 prior_degree6_role_advantage=prior['food']-prior_best['food'],
 improvement_in_role_advantage=(observed['food']-winner['food'])-(prior['food']-prior_best['food']),
 no_gifts=get(hold,'donations_blocked')['food'],
 relocated=get(hold,'relocated_people')['food'],
 rewired=get(hold,topology='rewired')['food'],
 causal=cf['mean_total'],positive_people=cf['positive_agents'],
 causal_rewired=ca(causal,topology='rewired')['mean_total'],
 prior_degree6_causal=pre_cf['mean_total'],
 oracle=hold['oracle']['food']))
with (RES/'COMPARACION_V34.csv').open('w',encoding='utf8',newline='') as fh:
 w=csv.DictWriter(fh,list(rows[0]));w.writeheader();w.writerows(rows)
source=['v34_contract_degree4.py','v34_frozen_audits.py','v34_summarize.py',
 'PREREG_V34_NEIGHBOR_SCARCITY.md']
sha={x:hashlib.sha256((ROOT/x).read_bytes()).hexdigest() for x in source}
(RES/'METRICAS_V34.json').write_text(json.dumps(
 dict(models=rows,uncertainty=intervals,sha256=sha,
    training_agent_rounds=2*700*12*48*48),indent=2),encoding='utf8')
report=[
 '# V34. Escasez de socios y formación de especialidades en redes de cuatro vecinos',
 '',
 'Ensayo preregistrado el 12/11/2026 tras V30. Dos inicializaciones neuronales N48/k4 por tratamiento topológico. Ambas redes de oferta contractual dirigida y ocupación comenzaron con pesos aleatorios privados por individuo. Misma economía institucional de contratos recíprocos voluntarios V30, coste final0,04 y 700 actualizaciones. Intervención única: anillo de grado4 en entrenamiento en vez de grado6. No hay quotas profesionales ni objetivos sociales agregados.',
 '',
 '## Evaluación congelada fuera de muestra',
 '',
 table([[x['model'],fmt(x['food']),fmt(x['prior_degree6_food']),
   fmt(x['best_random_food']),sign(x['role_advantage']),
   sign(x['prior_degree6_role_advantage']),
   sign(x['improvement_in_role_advantage']),
   fmt(x['potential_learned']),fmt(x['potential_random']),
   sign(x['causal']),f"{x['positive_people']}/48"] for x in rows],
   ['Modelo','Alimento grado4','Alimento grado6','Azar roles grado4',
    'Ventaja roles g4','Ventaja roles g6','Mejora de ventaja',
    'Potencial roles g4','Potencial azar g4','Causal oferta','Agentes positivos']),
 '',
 'La condición de éxito ocupacional preregistrada requería superar en ambas semillas al mejor control aleatorio por ≥0,05 de alimento. El control aleatorio se selecciona por mayor comida entre tres tasas prefijadas. Aunque se usa una red con menos contactos, el proceso de aprendizaje privado y la institucionalidad contractual permanecen constantes. Los dos grados tienen asignaciones de roles aleatorias suficientemente diversas para abastecer materialmente si se consigue coordinación. Seis semillas ambientales y doce mundos por semilla controlan el efecto condicional, sin multiplicar las inicializaciones neuronales independientes.',
 '',
 '## Transferencia, controles y auditoría de consentimientos',
 '',
 table([[x['model'],fmt(x['food']),fmt(x['no_gifts']),
    fmt(x['relocated']),fmt(x['rewired']),sign(x['causal']),
    sign(x['causal_rewired']),fmt(x['oracle'])] for x in rows],
   ['Modelo','Normal','Sin ofertas','Personas reasignadas',
    'Red reconectada','Causal anillo','Causal reconectada','Oráculo']),
 '',
 'La auditoría obliga a un individuo por vez a emitir o no una oferta contractual inicial, manteniendo libres otros dos slots y todos los turnos siguientes. Su retorno puede reflejar la contraprestación inmediata del acuerdo. El oráculo de grado4 logra plena cobertura material mediante socios bilaterales a ±1 y parejas alternadas a distancia2; se utiliza solo para demostrar factibilidad matemática, no como política de entrenamiento.',
 '',
 '## Interpretación y límites',
 '',
 '[Inferencia] Una mayor escasez local de contactos complementarios puede elevar la importancia funcional de aprender posiciones ocupacionales. La comparación debe separar esa mejora de la simple variación de capacidad de contratación por número de vecinos. Una organización profesional significativamente mejor que la aleatoria con red fija todavía puede quedar ligada a posiciones particulares; por ello se midió cambio de personas y red reconectada.',
 '',
 'Criterios pendientes para el objetivo general: 120 individuos con ventaja ocupacional robusta, varias inicializaciones, cambios de vecinos, adaptabilidad después de pérdidas y sustituciones, y distinción entre regla contractual exógena y estructuras emergentes endógenas.',
 '',
 '## Procedencia y hashes',
 '',
 'Preregistro PREREG_V34_NEIGHBOR_SCARCITY.md; entrenador v34_contract_degree4.py, evaluador v34_frozen_audits.py, resultados de todos los individuos y mundos en results/v30_{holdout,causal}_v34_*.json, checkpoints runs/v34_N48_D4_*, comparadores V30 congelados.',
 *[f'{k}: {v}' for k,v in sha.items()]]
(RES/'RESULTADOS_INTEGRALES_V34.md').write_text('\n'.join(report),encoding='utf8')
print('V34_REPORT_OK',len(rows))
for x in rows:
 print(x['model'],'food',round(x['food'],4),
 'role_adv',round(x['role_advantage'],4),
 'vs g6',round(x['improvement_in_role_advantage'],4),
 'causal',round(x['causal'],4),'pos',x['positive_people'])
