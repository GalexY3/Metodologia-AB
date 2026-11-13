"""V45 preregistered pre-cooperation initial bias test, full paired controls."""
from __future__ import annotations
import csv,json,hashlib
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent;OUT=ROOT/"results"
NAMES=[f"v45_B{b}_{social}_s{seed}" for seed in (3111,4111)
  for b in ("15","30") for social in ("SOC","NOSOC")]
def read(p):return json.loads(p.read_text("utf8"))
def f(x):return f"{x:.4f}"
def plus(x):return f"{x:+.4f}"
def table(rows,head):
 return "\n".join(["| "+" | ".join(head)+" |",
  "| "+" | ".join(["---"]*len(head))+" |"]+
  ["| "+" | ".join(map(str,row))+" |" for row in rows])
base={}
for seed in (3111,4111):
 for state in ("SOC","NOSOC"):
  name=f"v44_LONG_{state}_s{seed}"
  baseline_held=read(OUT/("v44_holdout_"+name+".json"))
  baseline_causal=read(OUT/("v44_causal_"+name+".json"))
  assert baseline_held["spec"]["q"]==.95
  base[(seed,state)]=dict(model=name,
    food=baseline_held["metrics"]["food"],
    gifts=baseline_held["metrics"]["gifts"],
    mutual=baseline_held["metrics"]["mutual"],
    causal=baseline_causal["mean_total"],
    positive_agents=baseline_causal["positive_agents"])
rows=[];trajectories={}
for name in NAMES:
 folder=ROOT/"runs"/name
 spec=read(folder/"v44_spec.json")
 status=read(folder/"v44_status.json")
 extension=read(folder/"v45_status.json")
 assert extension["trained"] and status["state"]=="completed"
 assert status["updates"]==spec["updates"]==1000
 assert spec["v45_initial_logit_bias"] in (1.5,3.0)
 hold=read(OUT/("v44_holdout_"+name+".json"))
 ca=read(OUT/("v44_causal_"+name+".json"))
 assert hold["seeds"]==ca["seeds"]==[980101,980107,980109,980121,980131,980137]
 hist=[json.loads(x) for x in (folder/"v44_history.jsonl").read_text().splitlines()]
 assert [z["update"] for z in hist]==[1,200,400,600,800,1000]
 b=base[(spec["seed"],"SOC" if spec["partner_info"]=="yes" else "NOSOC")]
 metrics=hold["metrics"]
 row=dict(model=name,
  neural_seed=spec["seed"],social=(spec["partner_info"]=="yes"),
  initial_bias=spec["v45_initial_logit_bias"],
  prior_initial_probability=spec["v45_initial_cooperation_probability"],
  initial_gifts_u1=hist[0]["development"]["gifts"],
  final_food=metrics["food"],final_gifts=metrics["gifts"],
  final_mutual=metrics["mutual"],
  policy_sensitivity=hold["sensitivity"]["mean"],
  positive_response_people=hold["sensitivity"]["positive"],
  private_causal=ca["mean_total"],
  positive_private_people=ca["positive_agents"],
  comparator_v44_neutral_food=b["food"],
  comparator_v44_neutral_gifts=b["gifts"],
  comparator_v44_neutral_mutual=b["mutual"],
  comparator_v44_neutral_causal=b["causal"],
  causal_advantage_over_neutral=ca["mean_total"]-b["causal"],
  food_advantage_over_neutral=metrics["food"]-b["food"],
  gifts_advantage_over_neutral=metrics["gifts"]-b["gifts"],
  social_pair_rate=metrics["mutual"])
 rows.append(row);trajectories[name]=hist
by={r["model"]:r for r in rows}
elig=[r for r in rows if r["initial_bias"]==3.0
   and r["private_causal"]>0 and r["positive_private_people"]>=24
   and r["final_mutual"]>.25]
criteria=dict(
 h45a_at_least_2_high_start_private_positive=len(elig)>=2,
 h45b_social_high_start_causal_improvement=all(
  by[f"v45_B30_SOC_s{seed}"]["causal_advantage_over_neutral"]>=.025
   for seed in (3111,4111)),
 h45c_conditional_response_if_success=(all(
   r["positive_response_people"]>=24
   and r["final_food"]>by[f"v45_B30_NOSOC_s{r['neural_seed']}"]["final_food"]
   for r in elig) if elig else None),
 h45d_descriptive_start_bias_implemented=all(
   abs(r["initial_gifts_u1"]-r["prior_initial_probability"])<.1
   for r in rows))
criteria["h45c_applicable"]=bool(elig)
with (OUT/"COMPARACION_V45.csv").open("w",newline="",encoding="utf8") as handle:
 w=csv.DictWriter(handle,list(rows[0]));w.writeheader();w.writerows(rows)
sha_sources=("PREREG_V45_BOOTSTRAP_RECIPROCITY.md",
 "v45_bootstrap_dyads.py","v45_summarize.py","test_v45_bootstrap.py")
sha={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in sha_sources}
(OUT/"METRICAS_V45.json").write_text(json.dumps(dict(
  models=rows,comparison_v44={f"{k[0]}_{k[1]}":v for k,v in base.items()},trajectories=trajectories,
  criteria=criteria,sha256=sha,
  training_agent_rounds_max=8*1000*16*48*48,
  environment_holdout=[980101,980107,980109,980121,980131,980137],
  caveat="The prosocial action bias is externally initialized; only subsequent retention or conditional response is learned."),indent=2,default=lambda obj:str(obj)),encoding="utf8")
report=[
 "# V45 — ¿La generosidad inicial favorece aprender una reciprocidad estable?",
 "",
 "Ocho nuevos entrenamientos, dos semillas neuronales y dos logitos iniciales exógenos+1,5 (~82% donar) y+3,0 (~95% donar), cruzados con la observación o no del regalo previo del compañero. Se mantiene el motor diádico V44, 24 parejas complementarias, q0,95, coste0,04, actor privado por cada una de48 personas, REINFORCE sin recompensas grupales, contratos ni normas de reciprocidad programadas, 1000 actualizaciones. Los cuatro modelos V44-LONG de logit inicial0 actúan como comparador histórico pareado por semilla, observación y arquitectura. Cambia únicamente el sesgo inicial de regalar.",
 "",
 "## Evaluación congelada con seis ambientes nuevos",
 "",
 table([[r["model"],str(r["initial_bias"]),f(r["prior_initial_probability"]),
 f(r["initial_gifts_u1"]),f(r["final_gifts"]),f(r["final_food"]),
 f(r["final_mutual"]),plus(r["private_causal"]),
 f'{r["positive_private_people"]}/48',
 plus(r["policy_sensitivity"])]
  for r in rows],
 ["Modelo","Sesgo inicial","Prob. inicial","Donación u1",
  "Donación final","Alimento final","Mutual final","Efecto privado donar",
  "Agentes positivos","Respuesta al otro"]),
 "",
 "## Comparación frente a actores idénticos inicializados sin predisposición",
 "",
 table([[r["model"],plus(r["causal_advantage_over_neutral"]),
  plus(r["food_advantage_over_neutral"]),
  plus(r["gifts_advantage_over_neutral"])] for r in rows],
 ["Modelo","Δ causal respecto V44 neutral","Δ comida",
  "Δ donaciones"]),
 "",
 "Comparar cambios netos de política en actualización1000 y no confundir alta comida inicial de una población que dona mucho con cooperación estable por incentivos individuales. Las distribuciones de duración son iguales entre condiciones; el único parámetro inicial distinto es la constante del logito Bernoulli, no la función de recompensa propia.",
 "",
 "## Criterios preregistrados",
 "",
 table([[k,("no aplicable" if value is None else "cumple" if value else "no cumple")]
   for k,value in criteria.items()],
 ["Criterio","Resultado"]),
 "",
 "H45a exige que al menos dos modelos del grupo+3,0 obtengan retorno propio causal positivo para≥24/48 individuos y tasa de donación mutua>25%. H45b exige ventaja causal≥+0,025 contra las dos referencias neuronales neutrales con historia social. H45c, solo aplicable en caso de H45a, exige respuesta positiva al regalo del compañero y mayor alimento que el control correspondiente sin señal. H45d comprueba el sesgo inicial y describe su evolución.",
 "",
 "## Validez y alcance",
 "",
 "[Inferencia] Si el incentivo privado de donar sigue siendo negativo después del entrenamiento, incluso partiendo de una población inicialmente generosa, la dificultad parece implicar la construcción de una contingencia creíble de reciprocidad y no solamente la ausencia de una oportunidad inicial de contribuir. Un eventual éxito, por su parte, mostraría aprendizaje condicionado a una predisposición cooperativa externa y no altruismo que surgió enteramente sin ayuda.",
 "",
 "La evaluación utiliza 6 semillas ambientales reservadas (980101,980107,980109,980121,980131,980137), pesos finales congelados,32 mundos por semilla y8 mundos en intervenciones forzadas de cada uno de los48 agentes. Las redes no comparten parámetros y no reciben retribución por la comida del grupo. El nombre y sesgo inicial se verifican en v45_status.json de cada entrenamiento.",
 "",
 "## Código y reproducción",
 "",
 "Preregistro, wrapper v45_bootstrap_dyads.py, entrenamiento original V44, tests, especificación de los ocho tratamientos, checkpoints por actor, auditor v44_frozen_audits.py, CSV y series completas, SHA256:",
 *[f'{k}: {v}' for k,v in sha.items()]]
(OUT/"RESULTADOS_INTEGRALES_V45.md").write_text("\n".join(report),encoding="utf8")
print("V45_REPORT_OK",len(rows),criteria)
for r in rows:
 print(r["model"],"start",round(r["initial_gifts_u1"],3),
   "gifts",round(r["final_gifts"],3),
   "causal",round(r["private_causal"],4),
   "pos",r["positive_private_people"])
