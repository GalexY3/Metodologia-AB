"""V25 outcome report, source hashes and cluster-aware contrasts."""
from pathlib import Path
import json,csv,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parent
RES=ROOT/"results"
MODELS=[f"v25_N48_C{c}_s{s}" for c in ("12","04") for s in (3111,4111)]
def load(p):return json.loads(p.read_text(encoding="utf-8"))
def fmt(n):return f"{n:.4f}"
def sign(n):return f"{n:+.4f}"
def table(data,labels):
 return "\n".join(["| "+" | ".join(labels)+" |",
   "| "+" | ".join(["---"]*len(labels))+" |"]
    +["| "+" | ".join(map(str,r))+" |" for r in data])
rows=[];details={};uncertainty={}
for name in MODELS:
 folder=ROOT/"runs"/name
 spec=load(folder/"v25_spec.json")
 status=load(folder/"v25_status.json")
 assert status["state"]=="completed" and status["updates"]==spec["updates"]==1000
 hist=[json.loads(r) for r in (folder/"v25_history.jsonl").read_text().splitlines()]
 assert hist[-1]["update"]==1000
 hold=load(RES/("v25_holdout_"+name+".json"))
 causal=load(RES/("v25_causal_"+name+".json"))
 assert len(hold["seeds"])==6 and len(causal["seeds"])==6
 assert len(hold["rows"])==32 and len(causal["rows"])==8
 def held(init="monolith",topology="ring",condition="learned"):
  return next(x for x in hold["rows"] if
     x["init"]==init and x["topology"]==topology and x["condition"]==condition)
 def ca(init="monolith",topology="ring",mode="normal"):
  return next(x for x in causal["rows"] if x["init"]==init and
    x["topology"]==topology and x["mode"]==mode)
 z=held()
 baseline=held(condition="donations_blocked")
 best=max((held(condition=f"role_random_{s}") for s in ("015","035","060")),
     key=lambda r:r["food"])
 diff=np.array([x["food"] for x in z["by_seed"]])-np.array([
    x["food"] for x in baseline["by_seed"]])
 rng=np.random.default_rng(221112)
 bs=diff[rng.integers(0,6,size=(10000,6))].mean(axis=1)
 uncertainty[name]=dict(vs_no_gifts_seed_differences=diff.tolist(),
   mean=float(diff.mean()),bootstrap_descriptive_95=np.quantile(bs,[.025,.975]).tolist())
 record=dict(model=name,cost=spec["cost"],seed=spec["seed"],
   food=z["food"],gift_per_agent=z["gifts_per_person"],
   coverage=z["distinct_coverage"],complete=z["complete"],
   useful_ratio=z["useful_delivery_ratio"],potential=z["potential_coverage"],
   balanced=z["balanced"],oracle=hold["oracle_constructive"]["food"],
   no_gifts_food=baseline["food"],best_random_food=best["food"],
   best_random_label=best["condition"],
   no_history_food=held(condition="no_history")["food"],
   relocated_food=held(condition="people_relocated")["food"],
   causal_return=ca()["mean_total"],positive_agents=ca()["positive_agents"],
   causal_no_history=ca(mode="no_history")["mean_total"],
   causal_rewired=ca(topology="rewired")["mean_total"],
   causal_random_init=ca(init="random")["mean_total"],
   causal_balanced_init=ca(init="balanced")["mean_total"])
 rows.append(record)
 details[name]=dict(stages=[dict(update=r["update"],training_price=r["unitprice"],
       food_next=next(x for x in r["development"] if
        x["topology"]=="ring" and x["init"]=="monolith" and x["condition"]=="normal")["food"],
       gifts_next=next(x for x in r["development"] if
        x["topology"]=="ring" and x["init"]=="monolith" and x["condition"]=="normal")["gifts_per_person"])
       for r in hist],
      source_spec=spec)
with (RES/"COMPARACION_V25.csv").open("w",encoding="utf-8",newline="") as f:
 w=csv.DictWriter(f,list(rows[0]));w.writeheader();w.writerows(rows)
(RES/"METRICAS_V25.json").write_text(json.dumps(dict(
 models=rows,details=details,uncertainty=uncertainty,
 training_agent_periods=4*1000*12*48*48,
 heldout_world_condition_paths=4*32*6*16,
 causal_pair_world_individuals=4*8*6*8*48,
 capacity=3),indent=2),encoding="utf-8")
data_main=[[x["model"],str(x["cost"]),fmt(x["food"]),
  fmt(x["gift_per_agent"]),fmt(x["coverage"]),fmt(x["complete"]),
  fmt(x["useful_ratio"]),fmt(x["potential"]),
  fmt(x["no_gifts_food"]),fmt(x["oracle"])] for x in rows]
data_causal=[[x["model"],sign(x["causal_return"]),
   f'{x["positive_agents"]}/48',sign(x["causal_no_history"]),
   sign(x["causal_rewired"]),sign(x["causal_random_init"]),
   sign(x["causal_balanced_init"])] for x in rows]
data_controls=[[x["model"],fmt(x["food"]),fmt(x["no_history_food"]),
 fmt(x["relocated_food"]),fmt(x["best_random_food"]),
 x["best_random_label"],fmt(x["no_gifts_food"])] for x in rows]
stage=[]
for x in rows:
 for s in details[x["model"]]["stages"]:
  stage.append([x["model"],s["update"],fmt(s["training_price"]),
    fmt(s["food_next"]),fmt(s["gifts_next"])])
hashfiles=("v25_multi_capacity.py","v25_holdout.py","v25_causal_audit.py",
  "v25_summarize.py","test_v25_capacity.py","PREREG_V25_PRODUCTION_CAPACITY.md",
  "V24_TEOREMA_FACTIBILIDAD.md")
hashes={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in hashfiles}
lines=[
 "# V25. Capacidades productivas multiplicadas y cooperación con cuatro profesiones",
 "",
 "Experimento exploratorio 12-11-2026 derivado del teorema V24. Frente al modelo V24, ahora cada persona puede elegir de modo voluntario y dirigido hasta **tres entregas por ronda**, a cualquier vecino, con coste pagado por regalo y sin obligación de distribuirlas. No se emplearon profesores, políticas iniciales preentrenadas, cuotas ocupacionales ni funciones de bienestar colectivo. Las políticas de roles y donaciones tienen parámetros neuronales privados y se entrenan simultáneamente con retornos propios.",
 "",
 "N=48, cuatro profesiones, red circular de grado 6, 1000 actualizaciones × 12 mundos × 48 rondas para cada una de cuatro condiciones factoriales. Dos semillas neuronales por cada coste unitario final: 0,12 o 0,04. Precio de entrenamiento 0,002 hasta la actualización 500; aumenta hasta el precio final entre las actualizaciones 500 y 800, permanece constante hasta 1000. Evaluaciones de desarrollo siempre usan precio final.",
 "",
 "## Resultado congelado fuera de muestra",
 "",
 table(data_main,["Política","Precio/unidad","Alimento","Regalos/persona/ronda",
 "Cobertura material","Plenitud","Entregas útiles",
 "Complementariedad potencial","Sin regalos","Oráculo físico"]),
 "",
 "Seis semillas ambientales reservadas y 16 mundos por semilla y condición, pesos congelados. El oráculo constructivo (0,64 a precio 0,12; 0,88 a precio 0,04) es una asignación explícitamente programada SOLO para demostrar la factibilidad material del entorno, no una política que las redes aprendieran ni un target de entrenamiento. La tasa de entregas útiles se calcula como bienes distintos realmente recibidos divididos entre unidades físicas enviadas.",
 "",
 "## Comparaciones con controles",
 "",
 table(data_controls,["Política","Normal","Sin historial de ayuda",
 "Personas trasladadas","Mejor movilidad aleatoria","Tasa aleatoria",
 "Donaciones bloqueadas"]),
 "",
 "Se comparan roles aprendidos con roles fijos, tres tasas de movimiento ocupacional aleatorio y traslado conjunto de las políticas privadas a otras posiciones. La eliminación del historial social en inferencia no implica un reentrenamiento; equivale a una ablación informacional congelada. El bloqueo de todas las donaciones define una línea base física de 0,20 menos costes de movimiento.",
 "",
 "## Auditoría causal individual",
 "",
 table(data_causal,["Política","Retorno 1 regalo inicial","Personas positivas",
 "Sin información social","Red reconectada","Roles aleatorios",
 "Roles equilibrados"]),
 "",
 "Se fuerza solo una de las tres oportunidades de donación del primer turno para cada individuo y se compara con prohibir esa donación. Las otras dos oportunidades y todos los actos futuros siguen siendo estocásticos bajo redes entrenadas congeladas. Seis semillas ambientales, ocho mundos por semilla y 48 individuos, con control de coste inmediato exacto. Una diferencia de retorno media no equivale a que la mayoría de personas gane.",
 "",
 "## Historial del currículo",
 "",
 table(stage,["Modelo","Actualización","Coste al entrenar","Alimento test coste final",
 "Donaciones/persona test final"]),
 "",
 "## Interpretación causal y límites matemáticos",
 "",
 "V24 demostró que el sistema anterior de una unidad por persona era estructuralmente incapaz de abastecer completamente a todos los individuos con k=4. V25 elimina esa restricción ofreciendo k−1 oportunidades materiales, pero esto no implica que las políticas puedan coordinar su uso con reciprocidad. El regalo repetido hacia un mismo vecino puede ser redundante y la donación voluntaria debe tener retorno propio suficientemente positivo. El bloqueo de donaciones, la ablación informacional y la auditoría contrafactual permiten distinguir capacidad, acción y reciprocidad.",
 "",
 "Los intervalos bootstrap se calculan sobre seis semillas ambientales emparejadas, no sobre millones de inicializaciones de aprendizaje; dos semillas de cada precio no bastan para afirmar prevalencia universal. El gasto contributivo máximo de la condición 0,12 es 0,36 por persona y en 0,04 es 0,12, por lo que son problemas de decisión distintos y se reportan por separado.",
 "",
 "## Resultado de la hipótesis",
 "",
 "El progreso frente a V24 debe evaluarse sobre mejoras DURADERAS después de la subida al coste final, no por ventajas transitorias del período de entrenamiento barato ni por el oráculo programado. La interpretación queda limitada a las condiciones y grupos realmente auditados. El objetivo general no se considera completado mientras el aprendizaje conjunto no generalice robustamente a cuatro profesiones y diferentes inicializaciones.",
 "",
 "## Código, artefactos y verificaciones",
 "",
 "Entrenador v25_multi_capacity.py, evaluación v25_holdout.py, contraste forzado v25_causal_audit.py, test_v25_capacity.py, preregistro PREREG_V25_PRODUCTION_CAPACITY.md, checkpoints y logs en runs/v25_N48_*, datos JSON de los ocho escenarios por modelo en results/v25_causal_*.json y datos de movilidad en results/v25_holdout_*.json.",
 "",
 "Hash SHA256 del código y preregistros:",
 *[f"{x}: {digest}" for x,digest in hashes.items()]]
(RES/"RESULTADOS_INTEGRALES_V25.md").write_text("\n".join(lines),encoding="utf-8")
print("V25_REPORT_OK",len(rows),"modelos")
for x in rows:
 print(x["model"],"food",round(x["food"],4),
    "gifts",round(x["gift_per_agent"],4),
    "causal",round(x["causal_return"],4),
    "pos",x["positive_agents"])
