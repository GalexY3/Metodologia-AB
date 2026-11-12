"""Compare persistent individual memory and zero-memory V25 controls.

Report only frozen audits. Does not reselect runs by outcomes.
"""
from __future__ import annotations
from pathlib import Path
import csv,json,hashlib,math
import numpy as np
ROOT=Path(__file__).resolve().parent
RES=ROOT/"results"
NAMES=[f"v26_M{delta}_N48_C04_s{seed}" for delta in (94,99) for seed in (3111,4111)]
def load(path):return json.loads(path.read_text(encoding="utf8"))
def fmt(x):return f"{x:.4f}"
def signed(x):return f"{x:+.4f}"
def markdown(rows,columns):
 return "\n".join(["| "+" | ".join(columns)+" |",
   "| "+" | ".join(["---"]*len(columns))+" |"]
  +["| "+" | ".join(map(str,row))+" |" for row in rows])
baseline=load(RES/"METRICAS_V25.json")
known={r["seed"]:r for r in baseline["models"] if r["cost"]==.04}
assert set(known)=={3111,4111}
rows=[];paired={};stage=[]
for name in NAMES:
 run=ROOT/"runs"/name
 spec=load(run/"v25_spec.json")
 status=load(run/"v25_status.json")
 assert spec["memory_decay"] in (.94,.99)
 assert status["state"]=="completed" and status["updates"]==spec["updates"]==1000
 hold=load(RES/("v25_holdout_"+name+".json"))
 audit=load(RES/("v25_causal_"+name+".json"))
 assert len(hold["rows"])==32 and len(audit["rows"])==8
 def q(cond="learned",init="monolith",topology="ring"):
  return next(z for z in hold["rows"] if z["condition"]==cond and z["init"]==init and z["topology"]==topology)
 def c(mode="normal",init="monolith",topology="ring"):
  return next(z for z in audit["rows"] if z["mode"]==mode and z["init"]==init and z["topology"]==topology)
 result=q()
 control=known[spec["seed"]]
 rng=np.random.default_rng(20261112)
 clust=np.asarray([x["food"] for x in result["by_seed"]])
 # Historical V25 control six-seed grouped data can be loaded and aligned.
 old_hold=load(RES/(f'v25_holdout_v25_N48_C04_s{spec["seed"]}.json'))
 old=next(z for z in old_hold["rows"] if z["topology"]=="ring" and z["init"]=="monolith" and z["condition"]=="learned")
 assert [z["seed"] for z in result["by_seed"]]==[z["seed"] for z in old["by_seed"]]
 delta=clust-np.asarray([z["food"] for z in old["by_seed"]])
 bs=delta[rng.integers(0,6,size=(10000,6))].mean(1)
 paired[name]=dict(diff_by_environment_seed=delta.tolist(),
    mean=float(delta.mean()),descriptive_bootstrap_95=np.quantile(bs,[.025,.975]).tolist())
 item=dict(model=name,memory_decay=spec["memory_decay"],
    half_life_rounds=math.log(.5)/math.log(spec["memory_decay"]),
    seed=spec["seed"],food=result["food"],
    gift_per_person=result["gifts_per_person"],
    coverage=result["distinct_coverage"],
    complete=result["complete"],
    efficiency=result["useful_delivery_ratio"],
    no_history_food=q(cond="no_history")["food"],
    best_random_food=max(q(cond=f'role_random_{s}')["food"] for s in ("015","035","060")),
    baseline_v25_food=control["food"],
    delta_food=result["food"]-control["food"],
    return_causal=c()["mean_total"],
    positive_agents=c()["positive_agents"],
    return_no_history=c(mode="no_history")["mean_total"],
    return_rewired=c(topology="rewired")["mean_total"],
    baseline_v25_return=control["causal_return"])
 rows.append(item)
 logs=[json.loads(line) for line in (run/"v25_history.jsonl").read_text().splitlines()]
 assert logs[-1]["update"]==1000
 for r in logs:
  test=next(z for z in r["development"] if z["topology"]=="ring" and z["init"]=="monolith" and z["condition"]=="normal")
  stage.append([name,r["update"],fmt(r["unitprice"]),fmt(test["food"]),fmt(test["gifts_per_person"])])
with (RES/"COMPARACION_V26.csv").open("w",encoding="utf8",newline="") as f:
 w=csv.DictWriter(f,list(rows[0]));w.writeheader();w.writerows(rows)
(RES/"METRICAS_V26.json").write_text(json.dumps(dict(rows=rows,paired=paired,
 baselines=known,training_agent_periods=4*1000*12*48*48,
 frozen_holdout_world_condition_paths=4*32*6*16,
 forced_pair_world_individuals=4*8*6*8*48),indent=2),encoding="utf8")
src=("v26_memory_train.py","v26_memory_holdout.py","v26_memory_causal.py",
     "v26_summarize.py","test_v26_memory.py",
     "PREREG_V26_LONG_MEMORY.md","v25_multi_capacity.py")
hashes={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in src}
report=[
 "# V26. Duración de memoria relacional y reciprocidad en economía de cuatro profesiones",
 "",
 "Exploración preregistrada 12/11/2026 sobre el fracaso de V25. Se conservó íntegramente el motor de recompensa y el actor neuronal de producción de hasta tres bienes por trabajador. El único parámetro cambiado es el decaimiento de la memoria privada de favores entre vecinos: δ=0,94 y δ=0,99, frente al control histórico V25 δ=0. En cada configuración se reentrenaron desde pesos aleatorios dos semillas neuronales 3111 y 4111, 1000 actualizaciones, 48 personas, 4 profesiones, grado de red 6. Coste final unitario 0,04 tras currículo barato 0,002.",
 "",
 "La memoria almacena por vecino un rastro de ayuda recibida y aplica max(ayuda actual, δ×ayuda previa). Su efecto es informacional y no crea productos nuevos ni recompensa a donantes de manera externa. La semivida formal es log(0,5)/log(δ) rondas.",
 "",
 "## Evaluación congelada frente al control histórico",
 "",
 markdown([[r["model"],str(r["memory_decay"]),
   f'{r["half_life_rounds"]:.1f}',fmt(r["baseline_v25_food"]),
   fmt(r["food"]),signed(r["delta_food"]),fmt(r["gift_per_person"]),
   fmt(r["coverage"]),fmt(r["no_history_food"])] for r in rows],
   ["Modelo","δ","Semivida","V25 δ0 alimento","V26 alimento",
    "Cambio","Regalos/ronda","Cobertura","Sin historial"]),
 "",
 "## Efecto causal individual de forzar la donación inicial",
 "",
 markdown([[r["model"],signed(r["baseline_v25_return"]),
   signed(r["return_causal"]),f'{r["positive_agents"]}/48',
   signed(r["return_no_history"]),signed(r["return_rewired"])] for r in rows],
   ["Modelo","Retorno causal V25","Retorno causal V26",
    "Personas positivas","Sin historial","Red reconectada"]),
 "",
 "Las estimaciones causales corresponden a un regalo inicial impuesto en uno de tres slots, dejando libres las otras decisiones, en mundos emparejados. Seis semillas ambientales por condición y ocho mundos por semilla. El coste inmediato exacto equivale a -0,04 y todos los agentes se auditan. La eliminación del historial social durante inferencia es ablación informacional, no ausencia de memoria en entrenamiento.",
 "",
 "## Evolución durante el currículo",
 "",
 markdown(stage,["Modelo","Actualización","Precio de entrenamiento",
   "Alimento a precio final","Regalos a precio final"]),
 "",
 "## Incertidumbre y limites",
 "",
 "Los contrastes de alimentación de V26 frente a V25 se emparejan por seis semillas ambientales idénticas. Los intervalos bootstrap descriptivos se estiman sobre los seis clústeres, no entre entrenamientos. Existen solo dos inicializaciones neuronales por duración de memoria, y dos por control δ=0; no se debe declarar una regularidad poblacional universal.",
 "",
 "La existencia de roles potencialmente complementarios no permite inferir intercambio real, y una tasa de donaciones no certifica beneficio individual futuro. La auditoría causal y el bloqueo de señales informativas son los falsadores decisivos. Ningún hallazgo de N48/k4 justificaría por sí solo declarar el objetivo completo sin replicación en N120 y múltiples topologías.",
 "",
 "## Reproducibilidad",
 "",
 "Código exacto V25 preservado sin modificaciones. Los wrappers V26 inyectan exclusivamente el parámetro C.memory_decay en entornos de entrenamiento y evaluación. Archivos runs/v26_M*/v25_spec.json registran memory_decay; pesos y estados Adam en joint_latest.pt, logs en v25_history.jsonl, escenarios de prueba JSON results/v25_holdout_v26_*.json, audit JSON results/v25_causal_v26_*.json. Pruebas de persistencia test_v26_memory.py.",
 "",
 "Hash SHA256 del código y preregistros:",
 *[f"{name}: {digest}" for name,digest in hashes.items()]]
(RES/"RESULTADOS_INTEGRALES_V26.md").write_text("\n".join(report),encoding="utf8")
print("V26_REPORT_OK",len(rows))
for r in rows:
 print(r["model"],"food",round(r["food"],4),
  "causal",round(r["return_causal"],4),"positives",r["positive_agents"])
