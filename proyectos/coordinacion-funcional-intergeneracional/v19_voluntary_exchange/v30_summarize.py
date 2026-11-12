"""Frozen V30 factorial outcome report with causal offer analysis."""
from __future__ import annotations
import csv,json,hashlib
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent;RES=ROOT/"results"
NAMES=[f"v30_{mode}_C04_s{seed}" for mode in ("MUTUAL","UNILATERAL")
       for seed in (3111,4111)]
def load(p):return json.loads(p.read_text(encoding="utf8"))
def table(rows,heads):
 return "\n".join(["| "+" | ".join(heads)+" |",
   "| "+" | ".join(["---"]*len(heads))+" |"]+
   ["| "+" | ".join(map(str,x))+" |" for x in rows])
def fmt(x):return f"{x:.4f}"
def sgn(x):return f"{x:+.4f}"
out=[];held={};cf={}
for name in NAMES:
 p=ROOT/"runs"/name
 spec=load(p/"v25_spec.json");status=load(p/"v25_status.json")
 assert status["state"]=="completed" and spec["updates"]==status["updates"]==700
 h=load(RES/("v30_holdout_"+name+".json"))
 a=load(RES/("v30_causal_"+name+".json"))
 assert len(h["rows"])==32 and len(a["rows"])==8
 assert len(h["seeds"])==6 and len(a["seeds"])==6
 def H(label="learned",topology="ring",init="monolith"):
  return next(x for x in h["rows"] if x["topology"]==topology
    and x["init"]==init and x["condition"]==label)
 def A(mode="normal",topology="ring",init="monolith"):
  return next(x for x in a["rows"] if x["topology"]==topology
    and x["init"]==init and x["mode"]==mode)
 val=H()
 best=max([H("role_random_"+p) for p in ("015","035","060")],
       key=lambda x:x["food"])
 causal=A()
 row=dict(model=name,settlement=spec["settlement"],seed=spec["seed"],
   food=val["food"],proposals=val["proposals_per_person"],
   trades=val["settled_units_per_person"],
   acceptance=val["acceptance_fraction"],
   coverage=val["distinct_coverage"],full=val["complete"],
   useful_ratio=val["physical_useful_ratio"],
   balanced=val["balanced"],potential=val["potential_coverage"],
   random_best=best["food"],random_label=best["condition"],
   gain_random=val["food"]-best["food"],
   blocked_food=H("donations_blocked")["food"],
   no_history_food=H("no_history")["food"],
   relocated_food=H("relocated_people")["food"],
   rewired_food=H(topology="rewired")["food"],
   causal_total=causal["mean_total"],
   causal_immediate=causal["mean_initial"],
   causal_future=causal["mean_future"],
   causal_positive=causal["positive_agents"],
   causal_no_history=A("no_history")["mean_total"],
   causal_rewired=A(topology="rewired")["mean_total"],
   oracle=h["oracle"]["food"])
 out.append(row);held[name]=h;cf[name]=a
with (RES/"COMPARACION_V30.csv").open("w",newline="",encoding="utf8") as f:
 w=csv.DictWriter(f,list(out[0]));w.writeheader();w.writerows(out)
paired={}
for seed in (3111,4111):
 mutual=f"v30_MUTUAL_C04_s{seed}";unilat=f"v30_UNILATERAL_C04_s{seed}"
 def srow(name):
  return next(x for x in held[name]["rows"] if x["topology"]=="ring" and
     x["init"]=="monolith" and x["condition"]=="learned")
 x=srow(mutual)["by_seed"];y=srow(unilat)["by_seed"]
 assert [r["seed"] for r in x]==[r["seed"] for r in y]
 diff=np.asarray([z["food"] for z in x])-np.asarray([z["food"] for z in y])
 rng=np.random.default_rng(30112026)
 boot=diff[rng.integers(0,6,(10000,6))].mean(1)
 paired[str(seed)]=dict(environment_seed_differences=diff.tolist(),
   mean=float(diff.mean()),descriptive_bootstrap_95=np.quantile(boot,[.025,.975]).tolist())
src=("v30_consensual.py","v30_frozen_audits.py",
     "test_v30_barter.py","PREREG_V30_CONSENSUAL_EXCHANGE.md")
hashes={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in src}
(RES/"METRICAS_V30.json").write_text(json.dumps(dict(
 models=out,paired=paired,hashes=hashes,
 training_agent_rounds=4*700*12*48*48,
 holdout_world_condition_paths=4*4*8*6*12,
 causal_world_person_pairs=4*4*2*6*6*48),indent=2),encoding="utf8")
main=[[z["model"],fmt(z["food"]),fmt(z["proposals"]),fmt(z["trades"]),
  f'{z["acceptance"]:.1%}',fmt(z["coverage"]),fmt(z["random_best"]),
  sgn(z["gain_random"]),fmt(z["blocked_food"])] for z in out]
causal_rows=[[z["model"],sgn(z["causal_total"]),sgn(z["causal_immediate"]),
   sgn(z["causal_future"]),f'{z["causal_positive"]}/48',
   sgn(z["causal_no_history"]),sgn(z["causal_rewired"])] for z in out]
transfer=[[z["model"],fmt(z["food"]),fmt(z["no_history_food"]),
   fmt(z["relocated_food"]),fmt(z["rewired_food"]),
   fmt(z["potential"]),fmt(z["oracle"])] for z in out]
report=[
 "# V30. Coaprendizaje de intercambios contractuales voluntarios con cuatro profesiones",
 "",
 "Informe experimental fechado 12/11/2026. Tras el fracaso de V25 y V26, V30 cambia de forma explícita el régimen institucional. Mantiene donaciones propuestas voluntariamente, dos políticas neuronales privadas por persona, división ocupacional endógena y recompensa estrictamente propia, pero los bienes se entregan y pagan solamente en las parejas donde ambas partes se han propuesto donar mutuamente en la misma ronda. No hay intercambio obligatorio ni planeación de profesiones. El mecanismo de liquidación **se programó como regla externa** y no debe presentarse como una institución inventada por los agentes.",
 "",
 "Dos semillas neuronales por tratamiento, n=48, k=4, grado seis, 700 actualizaciones, 12 mundos por actualización, 48 rondas, coste unitario final 0,04, programa inicial de coste reducido hasta u300, transición a precio final entre u300 y 500, y 200 actualizaciones adicionales a precio final. Comparación emparejada frente a entregas unilaterales costosas aprendidas con la misma arquitectura, semillas y calendario.",
 "",
 "## Evaluación congelada fuera de muestra",
 "",
 table(main,["Política","Alimento","Propuestas/pers.","Contratos efectivos/pers.",
  "Fracción aceptada","Cobertura","Mejor rol aleatorio",
  "Ventaja sobre aleatorio","Bloqueo de contratos"]),
 "",
 "Los controles incluyen seis semillas ambientales reservadas, doce mundos por semilla y condición, rol fijo, movilidad aleatoria a varias tasas, bloqueo total de propuestas, ablación de historial social, traslado de personas y red reconectada. El número de propuestas no equivale a la cantidad de bienes: una propuesta no aceptada no se ejecuta ni genera coste. La tasa de aceptación cuenta unidades acordadas por propuesta emitida; las propuestas repetidas a un mismo vecino se liquidan como máximo una vez.",
 "",
 "## Causalidad individual de ofrecer un contrato",
 "",
 table(causal_rows,["Política","Retorno total","Efecto inmediato",
   "Efecto futuro","Agentes positivos","Sin historial",
   "Red reconectada"]),
 "",
 "Intervenir en una oferta individual al comienzo de la simulación cambia la probabilidad de celebrar un contrato solamente si el vecino también ha ofertado. En el régimen unilateral forzar la oferta ocasiona de manera inmediata −0,04 sin beneficiar simultáneamente al donante. En el régimen contractual el efecto puede ser positivo de inmediato porque un acuerdo genera dos entregas recíprocas y ambas partes reciben un bien potencialmente útil. Esto es **un juego institucionalmente diferente**; la comparación no identifica un mayor altruismo en las políticas.",
 "",
 "En k=4 la primera nueva categoría material recibida vale 0,55/3 ≈0,1833 raciones, antes de bonificación de 0,25 por completar las tres. Un contrato que aporta exactamente una categoría complementaria útil a cada parte tiene ganancia material inmediata de 0,1833−0,04≈0,1433 por persona. Una oferta no correspondida no se liquida ni tiene coste. La regla institucional hace que el intercambio beneficioso sea compatible con el interés propio inmediato y puede evitar el problema de reciprocidad diferida de V25. No hay garantía de que la política aprenda a encontrar socios compatibles o de que todos los agentes ganen.",
 "",
 "## Dependencia social, identidades y redes",
 "",
 table(transfer,["Política","Alimento circular","Sin historial",
   "Personas permutadas","Red reconectada","Potencial material",
   "Oráculo constructivo"]),
 "",
 "La política construida a mano para el oráculo requiere simultaneidad de propuestas mutuas, tres contratos de especialidades distintas por persona y roles balanceados. Su máximo físico a este coste es 0,88. La política programada se usa **únicamente** para comprobar factibilidad y no entrena a los agentes. La distancia entre el alimento conseguido y ese techo revela las oportunidades de mejora de selección de socios y estabilización ocupacional.",
 "",
 "## Inferencia estadística y limitaciones",
 "",
 "Solo hay dos semillas neuronales por tratamiento. Cada media de evaluación usa seis semillas ambientales y doce mundos por semilla; estos mundos no son replicaciones independientes de redes entrenadas. El bootstrap descriptivo de ventajas mutuo–unilateral se hace sobre las seis semillas ambientales emparejadas y no captura incertidumbre entre arquitecturas, tamaños poblacionales ni nuevas semillas de entrenamiento.",
 "",
 "No se declara OBJETIVO COMPLETADO aunque existan mejoras: sigue pendiente la prueba preregistrada de N120/k4 (V31), robustez frente a socios sustituídos, y distinguir emergencia de formas de reciprocidad de una regla contractual creada por el diseñador. Los resultados institucionales no sustituyen los negativos de V24–V26.",
 "",
 "## Reproducción",
 "",
 "Scripts v30_consensual.py y v30_frozen_audits.py, tests test_v30_barter.py, preregistro PREREG_V30_CONSENSUAL_EXCHANGE.md; configuraciones, modelos y estados en runs/v30_*; mediciones originales results/v30_holdout_v30_*.json y results/v30_causal_v30_*.json.",
 "",
 "## SHA256",
 *[f"{key}: {value}" for key,value in hashes.items()]]
(RES/"RESULTADOS_INTEGRALES_V30.md").write_text("\n".join(report),encoding="utf8")
print("V30_REPORT_OK",len(out))
for z in out:
 print(z["model"],"food",round(z["food"],4),
   "trades",round(z["trades"],3),
   "causal",round(z["causal_total"],4),
   "immediate",round(z["causal_immediate"],4),
   "positive",z["causal_positive"])
