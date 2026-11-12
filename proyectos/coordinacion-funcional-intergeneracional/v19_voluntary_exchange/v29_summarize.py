"""Source-auditable V29 factorial results and failed mechanism ablations."""
from __future__ import annotations
import csv,json,hashlib
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
RES=ROOT/"results"
MODELS=[f"v29_{m}_D6_C{price}_s{seed}" for m in ("L","P")
 for price in ("04","01") for seed in (3111,4111)]
MODELS+= [f"v29_P_D4_C04_s{seed}" for seed in (3111,4111)]
MODELS+= [f"v29_P_D6_C01_s{seed}_NOSOC" for seed in (3111,4111)]
assert len(MODELS)==12
def load(path):return json.loads(path.read_text(encoding="utf8"))
def table(rows,heads):
 return "\n".join(["| "+" | ".join(heads)+" |",
  "| "+" | ".join(["---"]*len(heads))+" |"]+
  ["| "+" | ".join(map(str,r))+" |" for r in rows])
def fmt(x):return f"{x:.4f}"
def signed(x):return f"{x:+.4f}"
rows=[];comparison=[]
for name in MODELS:
 p=ROOT/"runs"/name
 spec=load(p/"v25_spec.json")
 status=load(p/"v25_status.json")
 assert status["state"]=="completed" and status["updates"]==spec["updates"]==850
 h=load(RES/("v25_holdout_"+name+".json"))
 a=load(RES/("v25_causal_"+name+".json"))
 assert len(h["rows"])==32 and len(a["rows"])==8
 assert len(h["seeds"])==len(a["seeds"])==6
 def H(condition="learned",topology="ring",init="monolith"):
  return next(x for x in h["rows"] if x["condition"]==condition
    and x["topology"]==topology and x["init"]==init)
 def A(mode="normal",topology="ring",init="monolith"):
  return next(x for x in a["rows"] if x["mode"]==mode
    and x["topology"]==topology and x["init"]==init)
 social_off=bool(spec["no_social_training"])
 scores=H(condition="no_history" if social_off else "learned")
 causal=A(mode="no_history" if social_off else "normal")
 best=max([H(condition="role_random_"+s) for s in ("015","035","060")],
           key=lambda r:r["food"])
 row=dict(model=name,seed=spec["seed"],cost=spec["cost"],
   graph_degree=spec["degree"],memory=spec["relational_feature"],
   no_social_training=social_off,
   food=scores["food"],food_normal=H()["food"],
   food_no_history=H("no_history")["food"],
   gifts=scores["gifts_per_person"],coverage=scores["distinct_coverage"],
   full=scores["complete"],potential=scores["potential_coverage"],
   exact_balance=scores["balanced"],
   random_best=best["food"],random_label=best["condition"],
   gain_over_best_random=scores["food"]-best["food"],
   no_gifts=H("donations_blocked")["food"],
   relocated=H("people_relocated")["food"],
   rewired=H(topology="rewired")["food"],
   causal=causal["mean_total"],positive_people=causal["positive_agents"],
   causal_normal=A()["mean_total"],
   causal_no_history=A(mode="no_history")["mean_total"],
   causal_rewired=A(topology="rewired")["mean_total"])
 rows.append(row)
by={x["model"]:x for x in rows}
for price in ("04","01"):
 for seed in (3111,4111):
  legacy=by[f"v29_L_D6_C{price}_s{seed}"]
  precise=by[f"v29_P_D6_C{price}_s{seed}"]
  comparison.append(dict(factor="precise-minus-legacy",
    cost=legacy["cost"],seed=seed,
    food=precise["food"]-legacy["food"],
    causal=precise["causal"]-legacy["causal"]))
for seed in (3111,4111):
 precise=by[f"v29_P_D6_C04_s{seed}"]
 lowdegree=by[f"v29_P_D4_C04_s{seed}"]
 comparison.append(dict(factor="degree4-minus-6",cost=.04,
    seed=seed,food=lowdegree["food"]-precise["food"],
    causal=lowdegree["causal"]-precise["causal"]))
 so=by[f"v29_P_D6_C01_s{seed}_NOSOC"]
 control=by[f"v29_P_D6_C01_s{seed}"]
 comparison.append(dict(factor="train-nosocial-minus-social-at-nosocial-eval",
   cost=.01,seed=seed,food=so["food_no_history"]-control["food_no_history"],
   causal=so["causal_no_history"]-control["causal_no_history"]))
with (RES/"COMPARACION_V29.csv").open("w",newline="",encoding="utf8") as f:
 w=csv.DictWriter(f,list(rows[0]));w.writeheader();w.writerows(rows)
with (RES/"CONTRASTES_FACTORIALES_V29.csv").open("w",newline="",encoding="utf8") as f:
 w=csv.DictWriter(f,list(comparison[0]));w.writeheader();w.writerows(comparison)
hashfiles=("v29_train.py","v29_eval.py","v29_summarize.py",
  "test_v29_feedback.py","PREREG_V29_RELATIONAL_FEEDBACK.md")
hashes={x:hashlib.sha256((ROOT/x).read_bytes()).hexdigest() for x in hashfiles}
(RES/"METRICAS_V29.json").write_text(json.dumps(dict(rows=rows,
  planned_factorial_comparisons=comparison,hashes=hashes,
  training_agent_rounds=12*850*12*48*48,
  heldout_world_condition_paths=12*32*6*12,
  matched_causal_world_individual_pairs=12*8*6*6*48),indent=2),encoding="utf8")
out=[
 "# V29. Destinatarios recordados, incentivos y sociabilidad privada con cuatro profesiones",
 "",
 "Campaña preregistrada el 12/11/2026. Doce entrenamientos desde cero: dos versiones de registro privado del destinatario anterior (solo primer slot propuesto vs todos los destinatarios de regalos efectivamente entregados), dos costos finales de 0,04 y 0,01, grado4 contra grado6 y dos controles entrenados sin señales de ayuda recibida. Se mantiene la capacidad de tres regalos unilaterales, profesión aprendida, N48/k4, REINFORCE individual, parámetros privados y entrenamiento de 850 actualizaciones por inicialización.",
 "",
 "La corrección de memoria no modifica recompensas, producción ni transmisión física: 70 tests del directorio de investigación verificaron la conservación junto con otras invariantes. El precio c=0,01 es un entorno más favorable que el coste c=0,04, no una mejora directa de la inteligencia social del actor.",
 "",
 "## Evaluación congelada fuera de muestra",
 "",
 table([[x["model"],str(x["cost"]),x["memory"],str(x["graph_degree"]),
     fmt(x["food"]),fmt(x["gifts"]),fmt(x["coverage"]),
     fmt(x["random_best"]),signed(x["gain_over_best_random"]),
     signed(x["causal"]),f'{x["positive_people"]}/48']
   for x in rows],
   ["Modelo","Precio","Memoria","Grado","Alimento",
    "Regalos/pers.","Cobertura","Mejor rol aleatorio",
    "Ganancia","Retorno causal","Individuos positivos"]),
 "",
 "Para los modelos marcados NOSOC en el nombre, el resultado principal usa evaluación sin señales sociales, ya que durante entrenamiento los actores no dispusieron de ellas. Para el resto se muestra evaluación normal; ambos modos se preservan por separado en CSV. Seis semillas ambientales y doce mundos por semilla, pesos finales congelados en actualización850, sin selección retrospectiva del mejor checkpoint.",
 "",
 "## Comparación factorial por semilla y coste",
 "",
 table([[x["factor"],str(x["cost"]),str(x["seed"]),
     signed(x["food"]),signed(x["causal"])] for x in comparison],
   ["Cambio de mecanismo","Precio","Semilla","Cambio alimento",
    "Cambio causal"]),
 "",
 "Las comparaciones de memoria y topología son pareadas por semilla neuronal, pero solo se ensayaron dos inicializaciones en cada brazo. La ausencia de beneficio causal de donar aun cuando la alimentación se mantiene por encima de 0,20 impide identificar reciprocidad privada autosostenible: pueden existir donaciones no rentables individualmente que elevan el promedio de sus vecinos.",
 "",
 "## Interpretación",
 "",
 "[Inferencia] El colapso a c=0,04 persiste aun reconociendo todas las personas a las que se enviaron bienes realmente, y con vecinos más concentrados. Una intervención de precio muy bajo mantiene algunos flujos materialmente útiles pero tampoco establece retorno causal positivo en promedio. El control sin historial social puede tener producción colectiva material positiva cuando el precio es muy reducido, lo que impide interpretar cualquier donación como evidencia de aprendizaje de reciprocidad condicionada.",
 "",
 "La diferencia entre retornos causales privados y alimento social debe mostrarse siempre: la población puede beneficiarse en promedio de una estrategia que los individuos dejan de elegir cuando la capacitación refuerza su interés personal. Esta tensión se relaciona con la estructura de juego voluntario repetido y el problema de bienes públicos.",
 "",
 "## Incertidumbre y reproducibilidad",
 "",
 "Doce redes distintas agrupadas por un factorial con solo dos semillas por brazo; los mundos de seis semillas ambientales se comparten dentro del mismo entrenamiento y no son doce réplicas de una supuesta población de redes. La prueba causal impone un regalo en uno de los tres slots frente a impedirlo, dejando todas las otras decisiones aprendidas y estocásticas. Los archivos originales se conservan en runs/v29_* y results/v25_causal_v29_*.json / results/v25_holdout_v29_*.json.",
 "",
 "**No se alcanza el criterio de cooperación privada causal robusta con donaciones unilaterales para N48/k4.** Este fracaso coexiste con el éxito institucional V30 y debe conservarse sin fusionar sus mecanismos.",
 "",
 "## SHA256",
 *[f"{k}: {v}" for k,v in hashes.items()]]
(RES/"RESULTADOS_INTEGRALES_V29.md").write_text("\n".join(out),encoding="utf8")
print("V29_REPORT_OK",len(rows))
for x in rows:
 print(x["model"],"food",round(x["food"],4),
   "causal",round(x["causal"],4),"positive",x["positive_people"])
