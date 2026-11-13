"""V38 causal composition analysis of pretrained-vs-new cohort fractions."""
from __future__ import annotations
import csv,json,hashlib
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent;RES=ROOT/'results'
NAMES=[f'v37_COHORT_C{price}_s{seed}'
 for price in ('04','12') for seed in (3111,4111)]
LEVELS=(0,6,12,18,24,30)
def load(p):return json.loads(p.read_text('utf8'))
def f(x):return f'{x:.4f}'
def sgn(x):return f'{x:+.4f}'
def pct(x):return f'{x:.1%}'
def table(items,heads):
 return '\n'.join(['| '+' | '.join(heads)+' |',
 '| '+' | '.join(['---']*len(heads))+' |']+
 ['| '+' | '.join(map(str,v))+' |' for v in items])
rows=[];details=[]
for name in NAMES:
 spec=load(ROOT/'runs'/name/'v37_spec.json')
 status=load(ROOT/'runs'/name/'v37_status.json')
 assert status['state']=='completed' and status['updates']==700
 z=load(RES/('v38_composition_'+name+'.json'))
 assert len(z['rows'])==36 and len(z['seeds'])==6
 assert set(z['trained_quota'])==set(LEVELS) and z['worlds_per_seed']==16
 assert len(z['cohort_indices'])==30
 indexed={(x['seed'],x['trained_count']):x for x in z['rows']}
 assert len(indexed)==36
 by={}
 for degree in LEVELS:
  sample=[indexed[(seed,degree)] for seed in z['seeds']]
  avg=lambda key:float(np.mean([v[key] for v in sample]))
  ci_values=np.asarray([v['synergy_food'] for v in sample])
  rng=np.random.default_rng(38112026)
  boot=ci_values[rng.integers(0,6,(10000,6))].mean(1)
  data=dict(model=name,seed_neural=spec['source_spec']['seed'],
    price=spec['source_spec']['cost'],trained_count=degree,
    fraction=degree/30,food=avg('food_41_48'),
    newcomer_food=avg('newcomer_41_48'),
    resident_food=avg('resident_41_48'),
    retained_surplus=avg('excess_surplus_retained'),
    contracts=avg('contracts_41_48'),
    synergy=avg('synergy_food'),
    synergy_ci025=float(np.quantile(boot,.025)),
    synergy_ci975=float(np.quantile(boot,.975)),
    worlds_per_environment_seed=z['worlds_per_seed'],
    environment_seeds=len(z['seeds']))
  rows.append(data);by[degree]=data
 synergy_intermediate=[by[q]['synergy'] for q in (6,12,18,24)]
 slope=np.polyfit([q/30 for q in LEVELS],
    [by[q]['resident_food'] for q in LEVELS],1)[0]
 details.append(dict(model=name,
  synergy_all_intermediate_positive=all(q>0 for q in synergy_intermediate),
  resident_slope=float(slope),
  resident_slope_nonnegative=bool(slope>=0),
  qualifies_expensive_partial_retention=bool(spec['source_spec']['cost']==.12
      and any(by[q]['retained_surplus']>=.85 for q in LEVELS if q<30)),
  peak_synergy=float(max(synergy_intermediate)),
  full_gain_food=by[30]['food']-by[0]['food'],
  trained_0_surplus=by[0]['retained_surplus'],
  trained_30_surplus=by[30]['retained_surplus']))
with (RES/'COMPARACION_V38.csv').open('w',encoding='utf8',newline='') as file:
 w=csv.DictWriter(file,list(rows[0]));w.writeheader();w.writerows(rows)
criteria=dict(
 h38a=sum(x['synergy_all_intermediate_positive'] for x in details)>=3,
 h38b=sum(x['resident_slope_nonnegative'] for x in details)>=3,
 h38c=any(x['qualifies_expensive_partial_retention'] for x in details))
source=('PREREG_V38_COHORT_COMPLEMENTARITY.md','v38_mixed_cohort.py',
 'v38_summarize.py')
sha={x:hashlib.sha256((ROOT/x).read_bytes()).hexdigest() for x in source}
(RES/'METRICAS_V38.json').write_text(json.dumps(
 dict(rows=rows,model_diagnostics=details,criteria=criteria,sha256=sha,
     world_paths=4*6*6*16,
     agent_rounds=4*6*6*16*120*48),indent=2),encoding='utf8')
summary=[[
 x['model'],str(x['price']),str(x['trained_count'])+'/30',
 f(x['food']),f(x['newcomer_food']),f(x['resident_food']),
 pct(x['retained_surplus']),sgn(x['synergy']),
 f"{x['synergy_ci025']:+.4f} a {x['synergy_ci975']:+.4f}"
 ] for x in rows]
report=[
 '# V38. Composición de competencia: externalidades de nuevos habitantes socializados',
 '',
 'Experimento factorial preregistrado sobre los cuatro bancos de políticas nuevas aprendidas de V37. Ninguna red es entrenada durante V38: se evalúan cuotas de0,6,12,18,24 y30 sobre las mismas30 posiciones de reemplazo y90 residentes congelados. Las cuotas se eligen de forma anidada a partir de una única permutación de posiciones por semilla ambiental, antes de simular cada composición. Se conserva la economía contractual de consentimiento bilateral, que es una regla estructural exógena.',
 '',
 '## Resultados factoriales en seis semillas ambientales emparejadas',
 '',
 table(summary,['Modelo','Coste','Nuevos formados','Alimento total',
    'Alimento nuevos','Alimento residentes','Excedente retenido',
    'Sinergia material','IC descriptivo 95%']),
 '',
 'La sinergia se define como desviación de la interpolación lineal entre la sociedad con0 nuevos formados y la sociedad con30 nuevos formados. Es algebraicamente cero en ambos extremos. Sinergia positiva para cuotas intermedias significa que la ganancia de bienestar por composición excede una interpolación lineal entre ambas economías extremas. No prueba transmisión cultural ni efectos de aprendizaje entre novatos porque los pesos se mantuvieron congelados durante cada simulación.',
 '',
 '## Contraste de hipótesis preregistradas',
 '',
 table([[x['model'],'sí' if x['synergy_all_intermediate_positive'] else 'no',
    sgn(x['resident_slope']),'sí' if x['resident_slope_nonnegative'] else 'no',
    'sí' if x['qualifies_expensive_partial_retention'] else 'no'] for x in details],
    ['Modelo','Todas las sinergias q∈{6,12,18,24} >0',
     'Pendiente de residentes','Pendiente no negativa','Caso caro ≥85% antes 30/30']),
 '',
 f"El criterio H38a, sinergia positiva en los cuatro niveles intermedios en al menos3/4 modelos, {'se alcanza' if criteria['h38a'] else 'NO se alcanza'}. El criterio H38b, pendiente media de alimento de residentes no negativa en al menos3/4 modelos, {'se alcanza' if criteria['h38b'] else 'NO se alcanza'}. El criterio H38c, recuperación del85% del excedente en al menos un modelo caro con menos del100% de novatos formados, {'se alcanza' if criteria['h38c'] else 'NO se alcanza'}.",
 '',
 '## Inferencia, identificación y límites',
 '',
 '[Inferencia] La composición de competencias puede generar complementariedades no aditivas a través de la disponibilidad de contratos recíprocos y bienes de especialidades distintas. La inferencia se limita a estas políticas neuronales congeladas, estos30 puestos determinados por modelo, seis ambientes con permutaciones anidadas y una regla de intercambio implantada desde el diseño.',
 '',
 'La independencia estadística radica principalmente en las cuatro políticas neuronales entrenadas y seis semillas ambientales por política. El bootstrap descriptivo no confiere validez universal ni debe contar los16 mundos de cada semilla como entrenamientos independientes. El experimento no mide si los nuevos aprenden observando a otros ni cómo emergen instituciones sin protocolos predefinidos.',
 '',
 '## Reproducción',
 '',
 'Preregistro PREREG_V38_COHORT_COMPLEMENTARITY.md, evaluador v38_mixed_cohort.py, auditor base v37_audit.py, datos por ronda results/v38_composition_v37_*.json, CSV y métricas.',
 'SHA256:',*[f'{k}: {v}' for k,v in sha.items()]]
(RES/'RESULTADOS_INTEGRALES_V38.md').write_text('\n'.join(report),encoding='utf8')
print('V38_REPORT_OK',len(rows),criteria)
for x in details:
 print(x['model'],'max_synergy',round(x['peak_synergy'],4),
   'resident_slope',round(x['resident_slope'],4),
   'expensive_pass',x['qualifies_expensive_partial_retention'])
