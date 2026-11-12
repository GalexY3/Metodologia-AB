"""V35 frozen-neural policy shock audit summaries and trace integrity."""
from __future__ import annotations
import csv,json,hashlib
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'results'
NAMES=[f'v31_N120_MUTUAL_C{price}_s{seed}'
  for price in ('04','12') for seed in (3111,4111)]
SHOCKS=('control','rewire','roles','newcomers')
SEEDCOUNT=6; WORLDS=16; ROUNDS=48; SHOCKROUND=25
def load(p):return json.loads(p.read_text('utf8'))
def fmt(x):return f'{x:.4f}'
def pct(x):return f'{x:.1%}'
def table(items,heads):
 return '\n'.join(['| '+' | '.join(heads)+' |',
   '| '+' | '.join(['---']*len(heads))+' |']+
   ['| '+' | '.join(map(str,row))+' |' for row in items])
rows=[];raw={}
for name in NAMES:
 z=load(OUT/('v35_shocks_'+name+'.json'))
 assert z['worlds_per_seed']==WORLDS and z['shock_round']==SHOCKROUND
 assert len(z['seeds'])==SEEDCOUNT and len(z['rows'])==SEEDCOUNT*4
 assert set(z['condition_names'])==set(SHOCKS)
 index={(x['seed'],x['shock']):x for x in z['rows']}
 assert len(index)==SEEDCOUNT*4
 for seed in z['seeds']:
  base=index[(seed,'control')]
  for shock in SHOCKS:
   x=index[(seed,shock)]
   assert len(x['round_trace'])==ROUNDS
   assert abs(x['food_first24']-base['food_first24'])<1e-7
   assert x['worlds']==WORLDS
   if shock=='control':assert abs(x['surplus_restoration_vs_control']-1)<1e-6
   assert x['food_41_48']>.2
 for shock in SHOCKS:
  cases=[index[(seed,shock)] for seed in z['seeds']]
  ratio=np.asarray([x['surplus_restoration_vs_control'] for x in cases],dtype=float)
  if shock!='control':
   baseline=np.asarray([index[(seed,'control')]['food_41_48'] for seed in z['seeds']])
   late=np.asarray([x['food_41_48'] for x in cases])
   assert np.allclose(ratio,(late-.2)/(baseline-.2))
  rng=np.random.default_rng(35112026)
  bootstrap=ratio[rng.integers(0,SEEDCOUNT,(10000,SEEDCOUNT))].mean(1)
  r=dict(model=name,seed_neural=z['original_spec']['seed'],
    price=z['original_spec']['cost'],shock=shock,
    early_food=float(np.mean([x['food_first24'] for x in cases])),
    food_25_32=float(np.mean([x['food_25_32'] for x in cases])),
    food_33_40=float(np.mean([x['food_33_40'] for x in cases])),
    food_41_48=float(np.mean([x['food_41_48'] for x in cases])),
    last8_contracts=float(np.mean([x['contracts_41_48'] for x in cases])),
    last8_potential=float(np.mean([x['potential_41_48'] for x in cases])),
    recovery=float(ratio.mean()),
    recovery_bootstrap_025=float(np.quantile(bootstrap,.025)),
    recovery_bootstrap_975=float(np.quantile(bootstrap,.975)),
    recovery_above_085=bool(ratio.mean()>=.85),
    newcomers_food=float(np.mean([x['newcomers_last8'] for x in cases]))
       if shock=='newcomers' else None,
    residents_food=float(np.mean([x['residents_last8'] for x in cases]))
       if shock=='newcomers' else None,
    n_environment_seeds=SEEDCOUNT,worlds_per_seed=WORLDS)
  rows.append(r)
 raw[name]=z
with (OUT/'COMPARACION_V35.csv').open('w',newline='',encoding='utf8') as f:
 w=csv.DictWriter(f,list(rows[0]));w.writeheader();w.writerows(rows)
paths=('v35_shock_audit.py','test_v35_shocks.py','v35_summarize.py',
       'PREREG_V35_SHOCK_RESILIENCE.md','AMENDMENT_V35_SHOCK_ORDER.md')
hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}
(OUT/'METRICAS_V35.json').write_text(json.dumps(dict(
 rows=rows,hashes=hashes,model_seeds=4,environment_seeds_per_model=6,
 worlds_per_environment_seed=16,shocks=4,rounds=48,
 total_agent_rounds=4*6*4*16*120*48,
 shock_after_occupation_decisions=True,
 prereg_threshold=.85),indent=2),encoding='utf8')
rows_short=[[r['model'],str(r['price']),r['shock'],fmt(r['early_food']),
  fmt(r['food_25_32']),fmt(r['food_41_48']),pct(r['recovery']),
  'sí' if r['recovery_above_085'] else 'no'] for r in rows]
group=[[r['model'],fmt(r['newcomers_food']),fmt(r['residents_food']),
  fmt(r['residents_food']-r['newcomers_food']),pct(r['recovery'])] for r in rows
  if r['shock']=='newcomers']
report=[
 '# V35. Resiliencia de sociedades contractuales con 120 personas',
 '',
 'Evaluación de las cuatro políticas finales V31 con pesos congelados y seis semillas ambientales por política, dieciséis mundos por semilla, cuatro condiciones y cuarenta y ocho rondas. En total 96 condiciones de semilla/política/choque, 1536 trayectorias de mundo y 8.847.360 transiciones agente-ronda. Son cuatro entrenamientos neuronales distintos, no 1536 redes independientes. Todos los mundos parten de ocupaciones monolíticas y sostienen contratos voluntarios exógenamente disponibles.',
 '',
 'Se interviene entre las decisiones ocupacionales y las propuestas de la ronda 25. **Enmienda técnica declarada** en AMENDMENT_V35_SHOCK_ORDER.md: el preregistro ubicaba la intervención antes de las decisiones, pero el actor de profesiones habría revertido inmediatamente la reasignación en esa misma ronda. El orden revisado, idéntico para los cuatro grupos, impone el choque después de la decisión ocupacional ordinaria y antes de intercambiar; se verificó con test de humo previo a las corridas de seis semillas. No se incorporó la prueba de humo a la muestra.',
 '',
 '## Resultados principales',
 '',
 table(rows_short,['Política','Coste','Choque','Comida previa',
   'Comida 25–32','Comida 41–48','Excedente conservado',
   'Supera ≥85%']),
 '',
 'El indicador de recuperación se calcula contra el control de cada semilla ambiental, (comida final de la condición−0,20)/(comida final del control−0,20), y luego se promedia entre las seis semillas ambientales. El criterio preregistrado exigía al menos 85% del excedente en ambas inicializaciones neuronales de cada coste. Es una medida del excedente, no de la comida total.',
 '',
 '## Desigualdad entre residentes entrenados y recién llegados',
 '',
 table(group,['Política','Alimento 30 nuevos','Alimento 90 residentes',
   'Brecha residentes−nuevos','Excedente social retenido']),
 '',
 'El choque de sustitución reemplaza el 25% de las redes neuronales privadas y asigna aleatoriamente su ocupación a los recién incorporados. Los 90 vecinos conservan pesos adquiridos. Ni los antiguos ni los nuevos actualizan sus parámetros durante estas 48 rondas. Por lo tanto, la caída expresa vulnerabilidad frente a sustitución no aprendida, no incapacidad general de integrar generaciones cuando pueden aprender.',
 '',
 '## Interpretación y causalidad de los choques',
 '',
 '[Inferencia] La reconexión del barrio social conserva buena parte del excedente, incluso al coste 0,12, pero perjudica más al beneficio a precio elevado. La reasignación de profesiones produce un deterioro inicial y desaparece después de nuevas decisiones ocupacionales. No atribuir recuperación del rol a aprendizaje de nuevos pesos: las políticas están congeladas. El shock de newcomers reduce el bienestar tanto de sustitutos como de residentes, y produce una brecha por competencia acumulada.',
 '',
 '## Validez',
 '',
 'Las seis semillas ambientales son pares condicionados a la misma inicialización neuronal. Los intervalos bootstrap descriptivos [2,5%,97,5%] de METRICAS_V35.json re-muestrean estas seis semillas, no los mundos individuales, y no caracterizan la incertidumbre sobre todas las posibles redes y poblaciones. No se midió reentrenamiento después del choque. El 85% fue definido antes del experimento: la sustitución NO pasa el criterio preregistrado.',
 '',
 'La cooperación contractual sigue diferenciándose de reciprocidad unilateral sin ejecución mutua: los acuerdos privados voluntarios son aprendidos, la regla de entrega condicional se introdujo en el entorno. Se conserva abierto el objetivo general por faltar resiliencia intergeneracional y generalización fuerte de la especialización.',
 '',
 '## Reproducción y SHA256',
 '',
 'Preregistro, enmienda, código, tests y series de los 48 turnos de las seis semillas ambientales por condición se conservan en los archivos results/v35_shocks_v31_*.json; resumen CSV e informe en results/COMPARACION_V35.csv y results/METRICAS_V35.json.',
 *[f'{key}: {value}' for key,value in hashes.items()]]
(OUT/'RESULTADOS_INTEGRALES_V35.md').write_text('\n'.join(report),encoding='utf8')
print('V35_REPORT_OK',len(rows))
for r in rows:
 print(r['model'],r['shock'],'restoration',round(r['recovery'],4),
       'late',round(r['food_41_48'],4),
       'pass',r['recovery_above_085'])
