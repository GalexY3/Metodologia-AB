"""V50 preregistered summary: frozen private policies in four-role market."""
from pathlib import Path
import csv,json,hashlib,numpy as np
R=Path(__file__).resolve().parent;O=R/"results"
SEEDS=(3111,4111,5111,6111); METHODS=("NL","LOLA5","LOLA20")
RATES=(0.,.25,1.);MODES=("carry","public","none")
rows=[]
for method in METHODS:
 for seed in SEEDS:
  name=f"v47_Q95_{method}_s{seed}"
  doc=json.loads((O/f"v50_network_{name}.json").read_text("utf8"))
  assert len(doc["rows"])==9 and len(doc["seed_list"])==6
  assert doc["occupations_exogenous"] and doc["distinct_specialty_matching"]
  for d in doc["rows"]:
   assert len(d["by_seed_holdout"])==len(d["by_seed_causal"])==6
   assert abs(d["immediate"]+.04)<1e-8
   rows.append(dict(method=method,seed=seed,name=name,rate=d["rate"],mode=d["mode"],
      food=d["food"],gifts=d["gifts"],mutual=d["mutual"],coverage=d["coverage"],
      full=d["full"],causal=d["causal"],causal_future=d["causal_future"],
      positive_agents=d["positive_agents"]))
assert len(rows)==108
def q(seed,method,rate,mode):
 return next(x for x in rows if x["seed"]==seed and x["method"]==method and x["rate"]==rate
   and x["mode"]==mode)
hyp=dict(
 h50a=sum(q(s,"LOLA20",0.,"carry")["positive_agents"]>=24 and
  q(s,"LOLA20",0.,"carry")["food"]>=.55 and
  q(s,"LOLA20",0.,"carry")["full"]>=.5 for s in SEEDS)>=3,
 h50b=sum(q(s,"LOLA20",.25,"public")["positive_agents"]>=24 and
  q(s,"LOLA20",.25,"public")["food"]>=.55 for s in SEEDS)>=3,
 h50c=sum(q(s,"LOLA20",1.,"public")["positive_agents"]>=24 and
  q(s,"LOLA20",1.,"public")["food"]>=.55 for s in SEEDS)>=3,
 h50d=all(q(s,"NL",1.,"public")["food"]<.30 and
  q(s,"NL",1.,"public")["positive_agents"]<24 for s in SEEDS),
 h50e=sum(q(s,"LOLA20",1.,"public")["causal"]-
  q(s,"LOLA20",1.,"none")["causal"]>=.025 for s in SEEDS)>=3)
aggregate={}
for method in METHODS:
 for rate in RATES:
  for mode in MODES:
   subset=[q(s,method,rate,mode) for s in SEEDS]
   aggregate[f"{method}|{rate}|{mode}"]=dict(
    food=float(np.mean([x["food"] for x in subset])),
    full=float(np.mean([x["full"] for x in subset])),
    gifts=float(np.mean([x["gifts"] for x in subset])),
    mutual=float(np.mean([x["mutual"] for x in subset])),
    causal=float(np.mean([x["causal"] for x in subset])),
    positive_agents=[x["positive_agents"] for x in subset])
contrasts=[]
for seed in SEEDS:
 for method in METHODS:
  for rate in RATES:
   p=q(seed,method,rate,"public")
   for comparison in ("carry","none"):
    c=q(seed,method,rate,comparison)
    contrasts.append(dict(method=method,seed=seed,rate=rate,contrast="public_minus_"+comparison,
      food=p["food"]-c["food"],causal=p["causal"]-c["causal"],
      full=p["full"]-c["full"],mutual=p["mutual"]-c["mutual"]))
with (O/"COMPARACION_V50.csv").open("w",newline="",encoding="utf8") as f:
 w=csv.DictWriter(f,list(rows[0]));w.writeheader();w.writerows(rows)
with (O/"CONTRASTES_V50.csv").open("w",newline="",encoding="utf8") as f:
 w=csv.DictWriter(f,list(contrasts[0]));w.writeheader();w.writerows(contrasts)
sources=("PREREG_V50_MULTINEIGHBOR_FOUR_ROLES.md",
 "v50_four_role_network.py","test_v50_four_role_network.py",
 "v50_summarize.py")
sha={s:hashlib.sha256((R/s).read_bytes()).hexdigest() for s in sources}
(O/"METRICAS_V50.json").write_text(json.dumps(dict(
 rows=rows,aggregate=aggregate,hypotheses=hyp,contrasts=contrasts,sha256=sha,
 n_model_checkpoints=12,n_treatments=108,
 n_ordinary_worlds=12*9*6*64,
 n_individual_counterfactual_worlds=12*9*6*4*48,
 comparison="V25 original own payoff exactly, 4 occupations exogenous, 3 simultaneous specialty contacts guaranteed by matching"),indent=2),encoding="utf8")
def tbl(seq,headers):
 return "\n".join(["| "+" | ".join(headers)+" |",
 "| "+" | ".join(["---"]*len(headers))+" |"]+
 ["| "+" | ".join(map(str,x))+" |" for x in seq])
f=lambda n:f"{n:.4f}"
report=["# V50 — Tres relaciones simultáneas, cuatro ocupaciones y reciprocidad privada",
"",
"Se transfirieron sin reentrenar las 12 poblaciones V47 (NL, LOLA5, LOLA20 × cuatro semillas) a un mundo de48 agentes, 4 profesiones de12 personas cada una y tres vecinos simultáneos, uno por especialidad complementaria. La decisión de donar a cada uno es unilateral y privada. La función de alimento reproduce exactamente `v25_multi_capacity.step_multi`: 0,20+0,55×cobertura de los3 bienes+0,25×cobertura completa−0,04×regalos enviados. El máximo alimentario ante tres contribuciones propias y tres bienes recibidos es 0,88.",
"",
"Las profesiones y las parejas especializadas fueron asignadas por el investigador; **no se observó aprendizaje ocupacional**. El matching puede reorganizarse dentro de cada episodio en probabilidades0, 0,25 y1, con q0,95 de continuidad temporal, máximo48 rondas y gamma0,995. Cada política tiene un logit Bernoulli para el primer encuentro y los cuatro estados de reciprocidad de memoria de una ronda, separado por cada uno de sus3 enlaces.",
"",
"## Resultados completos agregados de las cuatro semillas neuronales",
"",
tbl([[method,str(rate),mode,
 f(aggregate[f"{method}|{rate}|{mode}"]["food"]),
 f(aggregate[f"{method}|{rate}|{mode}"]["full"]),
 f(aggregate[f"{method}|{rate}|{mode}"]["mutual"]),
 f(aggregate[f"{method}|{rate}|{mode}"]["causal"]),
 ",".join(map(str,aggregate[f"{method}|{rate}|{mode}"]["positive_agents"]))]
 for method in METHODS for rate in RATES for mode in MODES],
 ["Método","Rotación","Memoria","Alimento","Cobertura completa",
  "Donación mutua","Retorno causal propio","Agentes positivos por semilla"]),
"",
"## Hipótesis preregistradas",
"",
tbl([[key,"cumple" if value else "falsada"] for key,value in hyp.items()],
 ["Hipótesis","Resultado"]),
"",
"## Diseño contrafactual y controles",
"",
"Las seis semillas ambientales reservadas996101/996107/996109/996121/996131/996137 se aplicaron a cada condición con64 mundos para alimento, mutualidad y cobertura. Para el contraste individual se utilizaron4 mundos por semilla, duplicando cada mundo48 veces para forzar o impedir únicamente el primer regalo del individuo en uno de sus tres enlaces. Se mantienen las mismas vidas, grafo de contactos y uniformes de acción para todas las decisiones posteriores. El coste inmediato del sujeto tratado es exactamente−0,04. Se guardan por separado los retornos futuros privados descontados y la distribución individual de efectos.",
"",
"En el brazo carry cada vínculo conserva la última acción de su ocupante anterior; en public se observa la última donación real del compañero actual hacia un individuo de la misma profesión del receptor; en none se anula la observación de la conducta ajena. El registro reputacional público y la profesión de cada compañero se aportan desde el entorno y no son inventados por los agentes.",
"",
"El código V50 implementa los tres enlaces con una función NumPy propia y prueba paridad física frente al motor torch `v25_multi_capacity.step_multi` para decisiones y roles idénticos, ajustando el grafo original a tres vecinos para la comparación. La prueba de igualdad del pago original pasa con varias semillas y configuraciones.",
"",
"## Lectura sociológica y límites",
"",
"[Inferencia] La generalización de las políticas LOLA a tres enlaces simultáneos y necesidades profesionales complementarias muestra que una estrategia contingente privada puede sostener colaboración funcional en redes más densas cuando los bienes de los demás aportan valor directo y la conducta de cada autor es observable. No prueba organización laboral emergente porque cada individuo fue situado desde fuera en una especialidad y recibió exactamente los tres tipos de vecinos necesarios.",
"",
"El juego de roles tiene una arquitectura favorable impuesta, y las políticas de regalar fueron entrenadas antes en parejas diádicas mediante gradientes exactos del aprendizaje ajeno. Esta transferencia congelada no es aprendizaje conjunto de profesiones y donaciones ni evolución espontánea de una institución reputacional. La robustez ante otras topologías, desequilibrio laboral y entradas de nuevos individuos sigue pendiente.",
"",
"## Reproducibilidad",
"",
"Preregistro, motor V50, pruebas de paridad con V25, CSV de108 escenarios, contrastes y métricas, 12 archivos JSON completos por modelo y escenario. Hashes:",
*[f"{k}: {v}" for k,v in sha.items()]]
(O/"RESULTADOS_INTEGRALES_V50.md").write_text("\n".join(report),encoding="utf8")
print("V50_REPORT_OK",len(rows),hyp)
