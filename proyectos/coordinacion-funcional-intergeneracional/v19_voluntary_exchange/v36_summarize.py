"""V36 paired four-factor results: own institutional choice + scarce neighbors."""
from __future__ import annotations
import csv,json,hashlib
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent;RES=ROOT/'results'
NAMES=[f'v36_D4_MODE{prior}_s{seed}' for prior in ('NEUTRAL','RARE')
       for seed in (3111,4111)]
def load(p):return json.loads(p.read_text('utf8'))
def f(x):return f'{x:.4f}'
def plus(x):return f'{x:+.4f}'
def table(rows,heads):
 return '\n'.join(['| '+' | '.join(heads)+' |',
   '| '+' | '.join(['---']*len(heads))+' |']+
   ['| '+' | '.join(map(str,values))+' |' for values in rows])
reference=load(RES/'v36_DEGREE6_REFERENCE_CONTROLS.json')
assert len(reference['models'])==4
rows=[]
for name in NAMES:
 spec=load(ROOT/'runs'/name/'v32_spec.json')
 status=load(ROOT/'runs'/name/'v32_status.json')
 assert spec['v36_degree']==4 and status['state']=='completed'
 assert status['updates']==spec['updates']==1000
 data=load(RES/('v32_holdout_'+name+'.json'))
 causal=load(RES/('v32_causal_'+name+'.json'))
 assert len(data['rows'])==33 and len(causal['rows'])==6
 assert len(data['seeds'])==len(causal['seeds'])==6
 def H(condition='learned',topology='ring',init='monolith'):
  return next(x for x in data['rows'] if x['condition']==condition
     and x['topology']==topology and x['init']==init)
 def C(mode='normal',topology='ring',init='monolith'):
  return next(x for x in causal['rows'] if x['mode']==mode
     and x['topology']==topology and x['init']==init)
 x=H()
 best=max([H('role_random_035'),H('role_random_0.15'),
           H('role_random_0.60')],key=lambda q:q['food'])
 cf=C()
 prior_name=name.replace('v36_D4_','v32_')
 pre=next(z for z in reference['models'] if z['model']==prior_name)
 assert pre['degree']==6
 assert abs(spec['mode_bias']-load(ROOT/'runs'/prior_name/'v32_spec.json')['mode_bias'])<1e-10
 rng=np.random.default_rng(36112026)
 pairs=np.array([a['food']-b['food'] for a,b in zip(x['by_seed'],best['by_seed'])])
 assert [a['seed'] for a in x['by_seed']]==[b['seed'] for b in best['by_seed']]
 boot=pairs[rng.integers(0,6,(10000,6))].mean(1)
 row=dict(model=name,seed=spec['seed'],mode_bias=spec['mode_bias'],
   food=x['food'],adoption=x['adoption'],
   transferred=x['transfers_per_agent'],
   matched_contracts=x['matched_contracts_per_agent'],
   physical_coverage=x['realized_coverage'],
   potential=x['potential_coverage'],balanced=x['balanced'],
   random_role_best=best['food'],
   random_role_best_label=best['condition'],
   role_advantage=x['food']-best['food'],
   role_adv_ci025=float(np.quantile(boot,.025)),
   role_adv_ci975=float(np.quantile(boot,.975)),
   degree6_food=pre['food'],
   degree6_role_advantage=pre['advantage_over_best'],
   gain_role_adv_over_degree6=(x['food']-best['food'])-pre['advantage_over_best'],
   mode_random_food=H('random_mode')['food'],
   unilateral_only_food=H('always_unilateral')['food'],
   contract_only_food=H('always_mutual')['food'],
   no_gifts_food=H('donations_blocked')['food'],
   no_social_food=H('no_social')['food'],
   rewired_food=H(topology='rewired')['food'],
   relocated_food=H('relocated_people')['food'],
   mode_causal=cf['mean_total'],
   mode_causal_initial=cf['mean_initial'],
   positive_agents=cf['positive_agents'],
   causal_rewired=C(topology='rewired')['mean_total'])
 rows.append(row)
with (RES/'COMPARACION_V36.csv').open('w',encoding='utf8',newline='') as file:
 writer=csv.DictWriter(file,list(rows[0]));writer.writeheader();writer.writerows(rows)
sha_names=('PREREG_V36_SCARCITY_ADOPTION.md','v36_degree4_adoption.py',
'v36_frozen_audits.py','v36_reference_degree6.py','v36_summarize.py')
sha={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in sha_names}
(RES/'METRICAS_V36.json').write_text(json.dumps(dict(
 models=rows,sha256=sha,training_agent_rounds=4*1000*12*48*48,
 matched_environment_seeds=6,worlds_per_environment=12,
 targeted_causal_world_agent_pairs=4*3*2*6*6*48,
 success_occupational=[r['role_advantage']>=.05 for r in rows],
 success_institutional=[r['adoption']>.9 and r['positive_agents']>=40 for r in rows]
 ),indent=2),encoding='utf8')
report=[
 '# V36. Adopción contractual aprendida en redes de escasez local de especialistas',
 '',
 'Cuatro entrenamientos desde pesos independientes de cada uno de los 48 habitantes. Condiciones factoriales posteriores a V32 y V34: grado4, cuatro profesiones, elección privada del contrato frente a donaciones unilaterales, sesgos institucionales iniciales 0 y −2, dos semillas neuronales por sesgo. Las mismas políticas independientes y funciones de recompensa V32, 1000 actualizaciones y precio final c=0,04. El único cambio respecto a V32 es la topología de grado4. El mecanismo contractual como posibilidad económica es exógeno; su selección individual es endógena.',
 '',
 '## Generalización y comparación profesional contra los tres controles aleatorios',
 '',
 table([[z['model'],f(z['food']),f(z['adoption']),f(z['random_role_best']),
   plus(z['role_advantage']),plus(z['degree6_role_advantage']),
   plus(z['gain_role_adv_over_degree6']),
   plus(z['mode_causal']),f"{z['positive_agents']}/48"] for z in rows],
 ['Modelo','Alimento','Adopción','Mejor rol aleatorio',
  'Ventaja roles g4','Ventaja roles g6','Aumento ventaja',
  'Causal elegir contrato','Personas positivas']),
 '',
 'En ambos grados, el comparador ocupacional es el mejor de tres tasas preestablecidas de cambio aleatorio de oficio 0,15, 0,35 y 0,60. Las evaluaciones de grado6 para tasas 0,15 y 0,60 se realizaron adicionalmente con los checkpoints V32 congelados, dejando intactos los resultados V32 originales. De este modo los cambios de ventaja ocupacional no se deben a haber escogido un control más fácil en una condición que en otra.',
 '',
 '## Contrastes de institución y transferencia',
 '',
 table([[z['model'],f(z['food']),f(z['unilateral_only_food']),
   f(z['contract_only_food']),f(z['mode_random_food']),
   f(z['no_gifts_food']),f(z['rewired_food']),
   f(z['relocated_food'])] for z in rows],
  ['Modelo','Modo aprendido','Unilateral forzado','Contrato forzado',
   'Modo aleatorio','Sin regalos','Red reconectada','Personas permutadas']),
 '',
 'Las intervenciones de modo conservan las políticas donantes y ocupacionales congeladas. La auditoría causal fuerza en una persona la elección contractual frente a unilateral al comienzo del episodio, manteniendo libres sus decisiones posteriores y las del resto. La mejora puede venir de la contraprestación inmediata del contrato; no implica que surja por sí misma la regla que la garantiza. Los resultados se agrupan en seis semillas ambientales y doce mundos por semilla.',
 '',
 '## Interpretación, selección exploratoria y límites',
 '',
 '[Inferencia] Un barrio de menos vecinos aumenta la necesidad adaptativa de encontrar especialidades distintas y puede favorecer que la organización ocupacional aprendida tenga más valor que el azar, mientras las redes privadas aprenden a adoptar contratos. Las cifras de ventaja sobre el mejor control aleatorio y su cambio entre grados deben leerse conjuntamente con el efecto causal de adoptar y el número de contratos físicos por persona.',
 '',
 'Esta hipótesis se concibió **después de observar** la ventaja de reducir el grado en V34. Es selección exploratoria de un mecanismo, no confirmación ciega independiente. Solo hay cuatro semillas de entrenamiento distribuidas en dos predisposiciones. No equivale a población abierta con incorporación generacional, ni a libre invención de normas. Aunque la ventaja ocupacional supere +0,05, sigue faltando N120, cambios de grafo y robustez a la pérdida de agentes entrenados.',
 '',
 '## Reproducibilidad',
 '',
 'Preregistro, scripts, checkpoints y auditorías de todas las personas bajo resultados results/v32_{causal,holdout}_v36_*.json, benchmarks del grado6 results/v36_DEGREE6_REFERENCE_CONTROLS.json, CSV y METRICAS_V36.json. Se conservan trazas de todas las evaluaciones, especificaciones y estado de los tres optimizadores por individuo.',
 'SHA256:',*[f'{key}: {value}' for key,value in sha.items()]]
(RES/'RESULTADOS_INTEGRALES_V36.md').write_text('\n'.join(report),encoding='utf8')
print('V36_REPORT_OK',len(rows))
for z in rows:
 print(z['model'],'food',round(z['food'],4),
 'role_adv',round(z['role_advantage'],4),
 'vsdegree6',round(z['gain_role_adv_over_degree6'],4),
 'positive',z['positive_agents'])
