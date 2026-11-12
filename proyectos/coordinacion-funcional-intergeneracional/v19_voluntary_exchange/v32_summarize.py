"""V32 scientific report: decentralized institution adoption with causal controls.

All 4 originally preregistered seeds retained, evaluation checkpoints frozen.
"""
from __future__ import annotations
import json,csv,hashlib
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
RESULTS=ROOT/'results'
NAMES=[f'v32_MODE{mode}_s{seed}' for mode in ('NEUTRAL','RARE') for seed in (3111,4111)]
def read(p):return json.loads(p.read_text('utf8'))
def table(rows,heads):
 return '\n'.join(['| '+' | '.join(heads)+' |',
  '| '+' | '.join(['---']*len(heads))+' |']+
  ['| '+' | '.join(map(str,values))+' |' for values in rows])
def f(x):return f'{x:.4f}'
def signed(x):return f'{x:+.4f}'
out=[];uncertainty={}
for name in NAMES:
 p=ROOT/'runs'/name
 spec=read(p/'v32_spec.json')
 status=read(p/'v32_status.json')
 assert status['state']=='completed' and status['updates']==spec['updates']==1000,name
 h=read(RESULTS/('v32_holdout_'+name+'.json'))
 c=read(RESULTS/('v32_causal_'+name+'.json'))
 assert len(h['rows'])==27 and len(c['rows'])==6,name
 assert len(h['seeds'])==len(c['seeds'])==6
 def H(condition='learned',topology='ring',init='monolith'):
  return next(r for r in h['rows'] if r['topology']==topology
    and r['init']==init and r['condition']==condition)
 def C(mode='normal',topology='ring',init='monolith'):
  return next(r for r in c['rows'] if r['topology']==topology
    and r['init']==init and r['mode']==mode)
 main=H()
 causal=C()
 best_role=H('role_random_035')
 comparison=H('random_mode')
 contrast=np.asarray([r['food'] for r in main['by_seed']])-np.asarray(
  [r['food'] for r in comparison['by_seed']])
 rng=np.random.default_rng(32112026)
 intervals=np.quantile(contrast[rng.integers(0,6,(10000,6))].mean(1),[.025,.975])
 uncertainty[name]=dict(contrast_food_learned_vs_random_mode=contrast.tolist(),
   descriptive_95=intervals.tolist())
 rec=dict(model=name,seed=spec['seed'],initial_logit=spec['mode_bias'],
   initial_contract_probability=1/(1+np.exp(-spec['mode_bias'])),
   food=main['food'],adoption=main['adoption'],
   proposals=main['proposals_per_agent'],
   transfers=main['transfers_per_agent'],
   matched_contracts=main['matched_contracts_per_agent'],
   coverage=main['realized_coverage'],potential=main['potential_coverage'],
   exact_balance=main['balanced'],
   mode_random_food=comparison['food'],
   always_mutual_food=H('always_mutual')['food'],
   always_unilateral_food=H('always_unilateral')['food'],
   role_fixed_food=H('role_fixed')['food'],
   role_random_food=best_role['food'],
   no_social_food=H('no_social')['food'],
   no_gifts_food=H('donations_blocked')['food'],
   rewired_food=H(topology='rewired')['food'],
   relocated_food=H('relocated_people')['food'],
   mode_causal=causal['mean_total'],
   mode_causal_initial=causal['mean_initial'],
   mode_causal_future=causal['mean_future'],
   mode_positive_people=causal['positive_agents'],
   mode_causal_no_social=C('no_social')['mean_total'],
   mode_causal_rewired=C(topology='rewired')['mean_total'])
 out.append(rec)
with (RESULTS/'COMPARACION_V32.csv').open('w',newline='',encoding='utf8') as fh:
 writer=csv.DictWriter(fh,list(out[0]));writer.writeheader();writer.writerows(out)
(RESULTS/'METRICAS_V32.json').write_text(json.dumps(
 dict(models=out,uncertainty=uncertainty,
  training_agent_rounds=4*1000*12*48*48,
  frozen_world_condition_paths=4*3*9*6*12,
  forced_mode_world_person_pairs=4*3*2*6*6*48),indent=2),encoding='utf8')
hash_files=['v32_institution_choice.py','v32_frozen_audits.py',
 'v32_summarize.py','test_v32_institution.py',
 'PREREG_V32_ENDOGENOUS_CONTRACT_ADOPTION.md']
hashes={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in hash_files}
rows=[[r['model'],f(r['initial_contract_probability']),f(r['adoption']),
 f(r['food']),f(r['always_unilateral_food']),f(r['always_mutual_food']),
 f(r['mode_random_food']),f(r['role_random_food']),
 f(r['no_gifts_food'])] for r in out]
mechanism=[[r['model'],signed(r['mode_causal']),
 signed(r['mode_causal_initial']),signed(r['mode_causal_future']),
 f"{r['mode_positive_people']}/48",signed(r['mode_causal_no_social']),
 signed(r['mode_causal_rewired'])] for r in out]
transfer=[[r['model'],f(r['food']),f(r['rewired_food']),
 f(r['relocated_food']),f(r['no_social_food']),
 f(r['matched_contracts']),f(r['coverage']),f(r['potential']),
 f(r['exact_balance'])] for r in out]
report=[
 '# V32. Coaprendizaje endógeno de adopción contractual, dones y profesiones',
 '',
 'Campaña preregistrada el 12-11-2026. N48, cuatro profesiones, 48 rondas, 1000 actualizaciones, seis semillas ambientales fuera de muestra, dos inicializaciones neuronales por tratamiento. Tres políticas privadas sin pesos compartidos por persona se inician aleatoriamente: ocupación, regalo dirigido y selección cada ronda entre intercambiar unilateralmente o por contrato recíproco. Cada una se entrena por retorno propio descontado. La institución contractual es una opción predefinida y su adopción es endógena; no se ha demostrado que las reglas institucionales fuesen inventadas espontáneamente.',
 '',
 '## Preferencia contractual aprendida y controles congelados',
 '',
 table(rows,['Política','Prob. inicial contrato','Adopción final',
 'Alimento aprendido','Modo unilateral forzado','Modo contractual forzado',
 'Modo aleatorio forzado','Rol aleatorio','Sin regalos']),
 '',
 'Se diferencia el efecto de la institución (dos formas diferentes de liquidar bienes) del efecto de la política neuronal que decide cuándo adoptarla. Las comparaciones de modo forzado utilizan exactamente las políticas finales congeladas de los otros dos subsistemas. Una política que elige contratar siempre puede converger hacia uso de una posibilidad del entorno sin aportar nuevo conocimiento sobre invención autónoma de instituciones.',
 '',
 '## Intervención causal sobre la elección del contrato',
 '',
 table(mechanism,['Política','Efecto total de elegir contrato',
 'Efecto inmediato','Efecto futuro','Personas positivas',
 'Sin historial social','Red reconectada']),
 '',
 'Cada intervención cambia únicamente si un individuo elige contrato frente a donación unilateral al inicio de un episodio, con 47 turnos posteriores de acciones aprendidas bajo políticas congeladas. Se emparentan estados y secuencias pseudoaleatorias, se fuerza cada persona por separado y se informa la proporción que obtiene retorno positivo. La elección contractual no es un regalo obligatorio: una propuesta no correspondida no se ejecuta.',
 '',
 '## Robustez y organización ocupacional',
 '',
 table(transfer,['Política','Circular','Red reconectada','Personas permutadas',
 'Sin historia social','Contratos/pers.','Cobertura efectiva',
 'Disponibilidad potencial','Roles 12/12/12/12']),
 '',
 'La cuestión ocupacional no se resuelve por una elevada adopción del contrato. Se exige una diferencia positiva frente a inmovilidad y movilidad aleatoria a igual régimen de donación. La tasa de roles exactamente balanceados no es una condición necesaria para economías complementarias locales, pero sirve para detectar si la distribución adquirida depende de convenciones de posición.',
 '',
 '## Inferencia y límites',
 '',
 'La evaluación agrupa seis semillas ambientales, doce mundos por semilla y políticas congeladas. Los intervalos descriptivos de alimento entre elección aprendida y modo aleatorio se calculan agrupando por semilla, no contando los individuos ni los mundos como entrenamientos independientes. Solo hay cuatro inicializaciones neuronales, dos por sesgo inicial. La regla de contrato sigue siendo un mecanismo material exógeno; incluso si la adopción es individualmente rentable, no acredita origen endógeno de normas.',
 '',
 'El objetivo general sigue abierto hasta contrastar escalas N120, topologías alternativas, reemplazos de personas y una división del trabajo que supere ampliamente controles ocupacionales, de forma no reducible a una institución preprogramada.',
 '',
 '## Reproducción',
 '',
 'Especificaciones, historiales, pesos y estados del optimizador en runs/v32_*.py y runs/v32_MODE*/; datos originales results/v32_holdout_*.json y results/v32_causal_*.json. Auditor v32_frozen_audits.py, entrenamiento v32_institution_choice.py, pruebas test_v32_institution.py.',
 '',
 'SHA256 de código y preregistro:',
 *[f'{k}: {v}' for k,v in hashes.items()]]
(RESULTS/'RESULTADOS_INTEGRALES_V32.md').write_text('\n'.join(report),encoding='utf8')
print('V32_REPORT',len(out))
for r in out:
 print(r['model'],'food',round(r['food'],4),'adoption',round(r['adoption'],4),
 'causal',round(r['mode_causal'],4),'positive',r['mode_positive_people'],
 'role_advantage',round(r['food']-r['role_random_food'],4))
