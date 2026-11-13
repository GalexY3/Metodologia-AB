"""V43 preregistered final frozen comparison of random horizon and clock.

Eight V30 contract histories branched to duration fixed/hazard and visible/
hidden time. Only final u1000 checkpoints and six independent environment
seeds; never select the intermediate favorable peak.
"""
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent;OUT=ROOT/"results"
NAMES=[f"v43_{'FIX' if duration=='fixed' else 'HAZ'}_{'CLOCK' if clock=='visible' else 'HIDDEN'}_s{seed}"
  for seed in (3111,4111) for duration in ("fixed","hazard") for clock in ("visible","hidden")]
def read(p):return json.loads(p.read_text(encoding="utf8"))
def f(v):return f"{v:.4f}"
def plus(v):return f"{v:+.4f}"
def table(rows,heads):
 return "\n".join(["| "+" | ".join(heads)+" |",
 "| "+" | ".join(["---"]*len(heads))+" |"]+
 ["| "+" | ".join(map(str,row))+" |" for row in rows])
rows=[];curves={};uncertainty={}
for name in NAMES:
 p=ROOT/"runs"/name
 spec=read(p/"v43_spec.json")
 state=read(p/"v43_status.json")
 assert state["state"]=="completed" and state["updates"]==spec["updates"]==1000,name
 hold=read(OUT/("v43_holdout_"+name+".json"))
 ca=read(OUT/("v43_causal_"+name+".json"))
 assert len(hold["rows"])==21 and len(ca["rows"])==3,name
 assert len(hold["seeds"])==len(ca["seeds"])==6
 def H(cond="learned",topo="ring",init="monolith"):
  return next(x for x in hold["rows"] if x["condition"]==cond
    and x["topology"]==topo and x["init"]==init)
 def C(topo="ring",init="monolith"):
  return next(x for x in ca["rows"] if x["topology"]==topo and x["init"]==init)
 main=H();cf=C()
 role_random=max([H("role_random_"+m) for m in ("015","035","060")],
  key=lambda x:x["food"])
 history=[json.loads(z) for z in (p/"v43_history.jsonl").read_text(encoding="utf8").splitlines()]
 assert [x["update"] for x in history]==[1,200,400,600,800,1000]
 curve=[]
 for point in history:
  env=next(x for x in point["development"] if x["topology"]=="ring"
    and x["init"]=="monolith")
  curve.append(dict(update=point["update"],food=env["food"],
    gifts=env["gifts_per_person"],
    mean_life=env["mean_alive_rounds"],coverage=env["coverage"]))
 curves[name]=curve
 sampling=np.asarray([np.mean(e["per_agent"]["total"]) for e in cf["by_seed"]])
 rng=np.random.default_rng(43112026)
 boot=sampling[rng.integers(0,6,(10000,6))].mean(1)
 uncertainty[name]=dict(causal_per_environment=sampling.tolist(),
  descriptive95=np.quantile(boot,[.025,.975]).tolist())
 row=dict(model=name,seed=spec["seed"],duration=spec["duration"],
  clock=spec["clock"],effective_q=spec["effective_q"],
  food_u1=curve[0]["food"],food_u200=curve[1]["food"],
  food_u400=curve[2]["food"],food_u600=curve[3]["food"],
  food_u800=curve[4]["food"],food_u1000=main["food"],
  gifts_u1=curve[0]["gifts"],gifts_u200=curve[1]["gifts"],
  gifts_u400=curve[2]["gifts"],gifts_u600=curve[3]["gifts"],
  gifts_u800=curve[4]["gifts"],gifts_u1000=main["gifts_per_person"],
  mean_alive_rounds=main["mean_alive_rounds"],
  coverage=main["coverage"],
  food_no_gifts=H("donations_blocked")["food"],
  best_role_random=role_random["food"],
  learned_roles_advantage=main["food"]-role_random["food"],
  rewired_food=H(topo="rewired")["food"],
  shuffled_people_food=H("relocated_people")["food"],
  causal_total=cf["mean_total"],
  causal_initial=cf["mean_initial"],
  causal_future=cf["mean_future"],
  positive_agents=cf["positive_agents"],
  causal_rewired=C(topo="rewired")["mean_total"],
  positive_rewired=C(topo="rewired")["positive_agents"])
 rows.append(row)
by={r["model"]:r for r in rows}
compare=[]
for seed in (3111,4111):
 for duration, prefix in (("fixed","FIX"),("hazard","HAZ")):
  hidden=by[f"v43_{prefix}_HIDDEN_s{seed}"]
  visible=by[f"v43_{prefix}_CLOCK_s{seed}"]
  compare.append(dict(seed=seed,contrast=duration+"_hidden_minus_visible",
    food=hidden["food_u1000"]-visible["food_u1000"],
    causal=hidden["causal_total"]-visible["causal_total"],
    gifts=hidden["gifts_u1000"]-visible["gifts_u1000"],
    mean_life=hidden["mean_alive_rounds"]-visible["mean_alive_rounds"]))
 for clock in ("CLOCK","HIDDEN"):
  haz=by[f"v43_HAZ_{clock}_s{seed}"]
  fix=by[f"v43_FIX_{clock}_s{seed}"]
  compare.append(dict(seed=seed,contrast=clock+"_hazard_minus_fixed",
    food=haz["food_u1000"]-fix["food_u1000"],
    causal=haz["causal_total"]-fix["causal_total"],
    gifts=haz["gifts_u1000"]-fix["gifts_u1000"],
    mean_life=haz["mean_alive_rounds"]-fix["mean_alive_rounds"]))
HAZ_HIDDEN=[r for r in rows if r["duration"]=="hazard" and r["clock"]=="hidden"]
eligible=[r for r in HAZ_HIDDEN if r["causal_total"]>0 and r["positive_agents"]>=24]
criteria=dict(
 h43a=bool(eligible),
 h43b=all(by[f"v43_HAZ_HIDDEN_s{s}"]["causal_total"]-
   by[f"v43_HAZ_CLOCK_s{s}"]["causal_total"]>=.025 for s in (3111,4111)),
 h43c=any(by[f"v43_FIX_HIDDEN_s{s}"]["causal_total"]-
   by[f"v43_FIX_CLOCK_s{s}"]["causal_total"]>=.015 for s in (3111,4111)),
 h43d=(all(r["causal_rewired"]>0 and r["positive_rewired"]>=24
   and r["learned_roles_advantage"]>=.025 for r in eligible)
    if eligible else None))
criteria["h43d_applicable"]=bool(eligible)
with (OUT/"COMPARACION_V43.csv").open("w",newline="",encoding="utf8") as fh:
 fields=list(rows[0])
 w=csv.DictWriter(fh,fields);w.writeheader();w.writerows(rows)
with (OUT/"CONTRASTES_V43.csv").open("w",newline="",encoding="utf8") as fh:
 w=csv.DictWriter(fh,list(compare[0]));w.writeheader();w.writerows(compare)
sources=("PREREG_V43_RANDOM_HORIZON.md",
 "AMENDMENT_V43_SURVIVAL_RNG.md",
 "v43_random_horizon.py","v43_frozen_audits.py",
 "v43_summarize.py","test_v43_horizon.py","test_v43_audit.py")
hashes={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in sources}
(OUT/"METRICAS_V43.json").write_text(json.dumps(dict(
 models=rows,contrasts=compare,criteria=criteria,
 trajectories=curves,uncertainty=uncertainty,sha256=hashes,
 original_train_commit="5594763d83da6be7d46783e4b7e785fa8b1b390b",
 training_agent_rounds_max=8*1000*12*48*48,
 original_train_interrupted=False,
 actual_masked_episodes=True),indent=2),encoding="utf8")
report=[
 "# V43 — Horizonte incierto y reloj oculto en donaciones privadas sin contrato",
 "",
 "Diseño factorial preregistrado 13/11/2026 con cuatro condiciones por dos inicializaciones neuronales originales. Todos los agentes N48/k4/anillo grado6 proceden de sus propios checkpoints V30 contractuales y optimizadores Adam; 1000 nuevas actualizaciones sin ejecución de contrato, con recompensas alimentarias individuales únicamente. Dos factores: horizonte fijo de48 rondas frente a supervivencia por mundo q0,98 (máximo48), y observación del avance de tiempo frente a reloj oculto. No se introduce profesor, norma de castigo ni cooperación como objetivo.",
 "",
 "## Trayectorias completas y prueba final fuera de muestra",
 "",
 table([[r["model"],r["duration"],r["clock"],
  f(r["food_u1"]),f(r["food_u200"]),f(r["food_u400"]),
  f(r["food_u600"]),f(r["food_u800"]),f(r["food_u1000"]),
  f(r["gifts_u1000"]),f(r["mean_alive_rounds"])]
   for r in rows],
 ["Modelo","Duración","Reloj","Comida u1","u200","u400","u600","u800",
  "u1000","Donaciones finales","Rondas vivas"]),
 "",
 "Las métricas de alimento y donaciones en la condición HAZARD se calculan **por agente-ronda vivo**. Los mundos muertos dejan de aportar recompensas o gradientes. El valor de desarrollo se evalúa a coste0,04 con políticas congeladas y seis semillas ambientales nuevas. La longitud media observada depende de q y del truncamiento48; no compararla con48 como si fuera idéntica experiencia.",
 "",
 "## Retorno propio descontado de una donación inicial y controles laborales",
 "",
 table([[r["model"],f(r["food_u1000"]),plus(r["causal_total"]),
  plus(r["causal_initial"]),plus(r["causal_future"]),
  f'{r["positive_agents"]}/48',
  plus(r["causal_rewired"]),f'{r["positive_rewired"]}/48',
  plus(r["learned_roles_advantage"])] for r in rows],
 ["Modelo","Comida","Causal privado","Inmediato","Futuro",
  "Agentes positivos","Causal red reconectada",
  "Positivos reconectados","Ventaja roles vs azar"]),
 "",
 "La auditoría fuerza solo el primer regalo de un individuo frente a prohibirlo, manteniendo las demás políticas libres, seis semillas ambientales y seis mundos por semilla, intervención sobre las48 personas de cada mundo. **No se computa un contrato escondido**. Se empareja la terminación aleatoria de cada mundo por medio de un generador dedicado y semilla ambiental, con un mismo calendario de muerte dentro de cada par contrafactual; consultar AMENDMENT_V43_SURVIVAL_RNG.md. El efecto inicial equivale a−c, y el resultado futuro evalúa si las reacciones sociales compensan ese coste.",
 "",
 "## Comparación factorial",
 "",
 table([[r["contrast"],str(r["seed"]),plus(r["food"]),
   plus(r["causal"]),plus(r["gifts"]),plus(r["mean_life"])]
    for r in compare],
 ["Diferencia","Semilla neuronal","Δ alimento",
  "Δ retorno causal","Δ regalos","Δ rondas vivas"]),
 "",
 "Las comparaciones reloj visible/oculto dentro de cada tipo de horizonte son las más controladas. El contraste HAZARD vs FIX también cambia la cantidad media efectiva de experiencia por episodio y la distribución de recompensas futuras. La introducción de q afecta a toda la sociedad simultáneamente, no a la supervivencia individual, y un límite de48 rondas permanece programado.",
 "",
 "## Hipótesis preregistradas",
 "",
 table([[k,("no aplicable" if v is None else "cumple" if v else "no cumple")]
  for k,v in criteria.items()],["Hipótesis","Resultado"]),
 "",
 "H43a exige al menos un modelo HAZARD_HIDDEN con retorno privado causal>0 y al menos24/48 personas positivas. H43b exige ventaja del reloj oculto en HAZARD≥0,025 en ambas semillas. H43c exige ventaja del reloj oculto en FIX≥0,015 en alguna semilla. H43d solo se aplica si H43a se logró: requiere transferencia a red reconectada y ventaja sobre las tres tasas de movilidad profesional aleatoria.",
 "",
 "## Resultados válidos y límites",
 "",
 "[Inferencia] Las diferencias entre duración y acceso a un reloj pueden modificar la exploración, el valor descontado de encuentros futuros y los incentivos aprendidos, pero conservar alimento positivo no es prueba de cooperación autoestable si la contribución forzada tiene efecto privado negativo. Se separan resultados de entrenamiento, resultados congelados fuera de muestra y retorno contrafactual individual.",
 "",
 "Se conserva la desigualdad de relaciones potenciales entre cuatro profesiones, el vector de confianza privado heredado de versiones anteriores y un mecanismo material unilateral preprogramado; no existe evidencia de invención institucional autónoma. Solo dos semillas neuronales por brazo y seis ambientales para cada checkpoint. Esta campaña no sustituye una prueba de reproducción intergeneracional bajo juego unilateral.",
 "",
 "## Código, enmienda y reproducción",
 "",
 "Preregistro V43, código de entrenamiento y test de paridad FIX_CLOCK, enmienda de generador separado para supervivencia en la evaluación, código auditor v43_frozen_audits.py, test_v43_audit.py y checkpoints con pesos/Adam por cada modelo. Auditorías originales results/v43_holdout_*.json y results/v43_causal_*.json; CSV, curvas históricas y métricas resumidas.",
 "SHA256:",
 *[f'{k}: {v}' for k,v in hashes.items()]]
(OUT/"RESULTADOS_INTEGRALES_V43.md").write_text("\n".join(report),encoding="utf8")
print("V43_REPORT_OK",len(rows),criteria)
for r in rows:
 print(r["model"],"food",round(r["food_u1000"],4),
  "gifts",round(r["gifts_u1000"],4),
  "causal",round(r["causal_total"],4),
  "positive",r["positive_agents"])
