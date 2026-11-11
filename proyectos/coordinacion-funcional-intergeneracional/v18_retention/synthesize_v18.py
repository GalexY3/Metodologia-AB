"""Merge longitudinal checkpoints, topology transfer and frozen outcomes into one report."""
from pathlib import Path
import json,numpy as np
R=Path(__file__).resolve().parent
P=R/'results'
V17=R.parent/'v17_regime_coalition'
def load(p):return json.loads(p.read_text('utf8'))
def metric(f,model,mode='normal'):
 z=[x for x in f if x['model']==model and x['mode']==mode]
 if not z:return None
 w=sum(x['worlds'] for x in z)
 return (sum(x['food']*x['worlds'] for x in z)/w,
         sum(x['exact'] for x in z),w)
def hist(path):
 if not path.exists():return []
 return [json.loads(x) for x in path.read_text('utf8').splitlines() if x.strip()]
def main():
 names=('frozen_initial','frozen_sweep','frozen_onpolicy','frozen_long')
 uniq={}
 for name in names:
  path=P/(name+'.json')
  if not path.exists():raise FileNotFoundError(path)
  for z in load(path)['rows']:
   key=z['model'],z['case'],z['mode']
   if key in uniq:assert abs(uniq[key]['food']-z['food'])<1e-6,key
   uniq[key]=z
 frozen=list(uniq.values())
 topo=load(P/'v18_topology.json')['rows']
 conditions=len(frozen)
 worlds=sum(x['worlds'] for x in frozen)
 runs=[
  ('Profesor 1','teacher_v17_DISTILL_LATTICE_R8_s3111_fix'),
  ('Profesor 2','teacher_v17_DISTILL_LATTICE_R8_s4111_fix'),
  ('RL puro 1','v18_BC0_s6111'),
  ('RL puro 2','v18_BC0_s7111'),
  ('Sintético, 350 pasos, semilla 1','v18_BC3_s6111'),
  ('Sintético, 350 pasos, semilla 2','v18_BC3_s7111'),
  ('Sintético, 700 pasos','v18_OFF_SYNTH_3_s6111'),
  ('En trayectoria, 700 pasos, semilla 1','v18_ON_ALL_3_s6111'),
  ('En trayectoria, 700 pasos, semilla 2','v18_ON_ALL_3_s7111'),
  ('En trayectoria, 1600 pasos, semilla 1','v18_ON_ALL_LONG_3_s6111'),
  ('En trayectoria, 1600 pasos, semilla 2','v18_ON_ALL_LONG_3_s7111'),
 ]
 report=[
  '# V18 — Conservación del aprendizaje de coordinación y generalización social',
  '',
  '## Metodología',
  '',
  'N=120 redes independientes con pesos propios y recompensa estrictamente individual r=min(n_j/(N/k),(N/k)/n_j). El profesor es un protocolo programado que enseña a comprometer, fundar y consolidar profesiones; la regularización en RL **introduce** supervisión de esa política. El presente estudio prueba mantenimiento y modificación de una convención aprendida, NO emergencia espontánea de cooperación.',
  '',
  'Los experimentos separan 350, 700, 1.200 y 1.600 actualizaciones. Se congelaron los pesos antes de medir 12 configuraciones M/k por política sobre cuatro semillas nuevas con 24 sociedades cada una. También se intervinieron mensajes, y un banco independiente en el segundo ordenador varió grado 4/8/16 y red circular/reconectada.',
  '',
  f'Total de registros de evaluación congelada compilados: {conditions} condiciones modelo×tarea×comunicación, {worlds} ejecuciones de sociedades. Una sociedad contiene 120 individuos; no equivale a 120 observaciones independientes.',
  '',
  '## Rendimiento de los checkpoints, mensajes normales',
  '',
  '| Modelo | Alimentación | Repartos exactos | Tasa exacta |',
  '|---|---:|---:|---:|'
 ]
 for label,model in runs:
  x=metric(frozen,model)
  if x:report.append(f'| {label} | {x[0]:.4f} | {x[1]}/{x[2]} | {100*x[1]/x[2]:.2f}% |')
 report+=['','## Propiedades temporales','',
  'La pérdida de coordinación desde estados atrapados no equivale a grokking: se monitoriza simultáneamente el comportamiento en las tareas conocidas y en M72/k8 no entrenada. La política entrenada sin el término de conservación pierde rápidamente la organización; penalizar desvíos respecto al profesor en estados sintéticos únicamente retrasa la pérdida. Aplicar la penalización sobre las observaciones realmente visitadas la retrasa más.',
  '',
  '| Entrenamiento | Actualización | Comida trampa 2×60 | Repartos exactos en 48 mundos | Comida OOD M72/k8 |',
  '|---|---:|---:|---:|---:|']
 for name in ('v18_LONG_BC0_s6111','v18_LONG_BC3_s6111','v18_LONG_BC10_s6111'):
  for x in hist(V17/'runs'/name/'history.jsonl'):
   if x['update'] in (0,200,400,600,800,1000,1200):
    report.append(f'| {name} | {x["update"]} | {x["trap"]["food"]:.4f} | {x["trap"]["exact"]}/48 | {x["ood"]["food"]:.4f} |')
 for name in ('v18_ON_ALL_LONG_3_s6111','v18_ON_ALL_LONG_3_s7111'):
  for x in hist(R/'runs'/name/'history.jsonl'):
   if x['update'] in (700,875,1050,1225,1400,1575,1600):
    report.append(f'| {name} | {x["update"]} | {x["results"]["M50_k4_trap"]["food"]:.4f} | {x["results"]["M50_k4_trap"]["exact"]}/48 | {x["results"]["M72_k8_random"]["food"]:.4f} |')
 report+=['',
 '## Variación del tejido social, fuera de entrenamiento',
 '',
 'Las redes se entrenaron con un círculo de 8 vecinos. El experimento de transferencia alteró el número de enlaces y usó una topología reconectada con las mismas políticas congeladas. Las métricas agregan cuatro tareas, 96 sociedades por tarea y combinación.',
 '',
 '| Semilla | Red | Grado | Profesor: comida | Profesor: exactos | Regularizada λ3: comida | Regularizada λ3: exactos |',
 '|---|---|---:|---:|---:|---:|---:|']
 for seed,teacher,rl in (
  ('1','teacher_v17_DISTILL_LATTICE_R8_s3111_fix','v18_BC3_s6111'),
  ('2','teacher_v17_DISTILL_LATTICE_R8_s4111_fix','v18_BC3_s7111')):
  for topology in ('ring','rewired'):
   for degree in (4,8,16):
    def agg(name):
     z=[x for x in topo if x['model']==name and x['topology']==topology and x['degree']==degree]
     assert len(z)==4,(name,topology,degree,len(z))
     return float(np.mean([x['food'] for x in z])),sum(x['exact'] for x in z),sum(x['worlds'] for x in z)
    a=agg(teacher);b=agg(rl)
    report.append(f'| {seed} | {topology} | {degree} | {a[0]:.4f} | {a[1]}/{a[2]} | {b[0]:.4f} | {b[1]}/{b[2]} |')
 onpath=P/'v18_topology_onpolicy.json'
 if onpath.exists():
  zr=load(onpath)['rows']
  report+=['','## Transferencia a redes diferentes tras conservar la política en experiencias reales','',
   'Evaluaciones independientes de redes circulares y reconectadas con 4, 8 o 16 vecinos, usando un mismo banco de cuatro tareas y 96 sociedades por condición.',
   '',
   '| Política | Red | Grado | Comida media | Repartos exactos |',
   '|---|---|---:|---:|---:|']
  for model in sorted(set(z['model'] for z in zr)):
   for top in ('ring','rewired'):
    for degree in (4,8,16):
     rec=[z for z in zr if z['model']==model and z['topology']==top and z['degree']==degree]
     if not rec:continue
     total=sum(z['worlds'] for z in rec)
     avg=sum(z['food']*z['worlds'] for z in rec)/total
     exact=sum(z['exact'] for z in rec)
     report.append(f'| {model} | {top} | {degree} | {avg:.4f} | {exact}/{total} |')
  report.append('')
 report+=['','## Límites causales',
 '',
 'La prueba conserva una fuente externa explícita de política de coordinación y redes independientes. El éxito de regularización NO demuestra que cooperación o normas sociales aparezcan por aprendizaje individual sin profesor. La reducción al retirar los mensajes refleja también el mecanismo programado de consenso; no basta para afirmar deliberación o reciprocidad.',
 '',
 'El número exacto de grupos y la alimentación pueden divergir por configuración. Los resultados de desarrollo revisados para elegir λ están sujetos a selección de hiperparámetros; el bootstrap descriptivo por escenario está en RESULTADOS_V18.md y results/v18_statistics.json.',
 '',
 'No se ha observado una transición tardía que cumpla los criterios de grokking: la evidencia principal es retención parcial y adaptación de una política previamente enseñada.',
 '',
 '## Archivos de evidencia',
 '',
 'Los registros se mantienen en results/frozen_initial.json, frozen_sweep.json, frozen_onpolicy.json, frozen_long.json, v18_topology.json y sus scripts de evaluación. Los parámetros entrenados y optimizadores están en runs/ (V18) y en los runs/v18_* del directorio V17. Todos los informes se derivan de esos JSON.',
 ]
 (R/'RESULTADOS_INTEGRALES_V18.md').write_text('\n'.join(report),encoding='utf8')
 print('V18_INTEGRAL_REPORT_READY',len(report),'lines',conditions,'treatments',worlds,'worlds',flush=True)
if __name__=='__main__':main()
