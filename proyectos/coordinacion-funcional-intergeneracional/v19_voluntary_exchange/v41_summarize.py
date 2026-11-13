"""V41 summary — causal persistence of charity after bilateral institution removal.

Use only final trained checkpoint u1000, frozen holdout on six reserved environment
seeds, individual all-agent interventions. No retrospective model selection.
"""
from __future__ import annotations
import json,csv,hashlib
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent;RES=ROOT/"results"
NAMES=[f"v41_{s}_s{seed}_{hist}" for s in ("C","U")
  for seed in (3111,4111) for hist in ("SOC","NOSOC")]
def load(path):return json.loads(path.read_text(encoding="utf8"))
def f(x):return f"{x:.4f}"
def plus(x):return f"{x:+.4f}"
def table(rows,heads):
 return "\n".join(["| "+" | ".join(heads)+" |",
   "| "+" | ".join(["---"]*len(heads))+" |"]+
   ["| "+" | ".join(map(str,r))+" |" for r in rows])
rows=[];trajectories={};uncertainty={}
for name in NAMES:
 base=ROOT/"runs"/name
 spec=load(base/"v41_spec.json");status=load(base/"v41_status.json")
 assert status["state"]=="completed" and status["updates"]==spec["updates"]==1000,name
 assert spec["settlement"]=="unilateral" and spec["n"]==48 and spec["cost"]==.04
 hold=load(RES/("v30_holdout_"+name+".json"))
 ca=load(RES/("v30_causal_"+name+".json"))
 assert len(hold["rows"])==(32 if spec["social"]=="yes" else 44) and len(ca["rows"])==8
 assert len(hold["seeds"])==len(ca["seeds"])==6
 social=spec["social"]=="yes"
 mode="normal" if social else "no_history"
 condition="learned" if social else "no_history"
 def H(choice=condition,topo="ring",init="monolith"):
  return next(x for x in hold["rows"] if x["condition"]==choice and x["topology"]==topo and x["init"]==init)
 def C(topo="ring",init="monolith",md=mode):
  return next(x for x in ca["rows"] if x["topology"]==topo and x["init"]==init and x["mode"]==md)
 main=H();causal=C()
 best=max((H("role_random_"+("" if social else "nosoc_")+rate)
   for rate in ("015","035","060")),key=lambda x:x["food"])
 history=[json.loads(line) for line in (base/"v41_history.jsonl").read_text(encoding="utf8").splitlines()]
 assert [x["update"] for x in history]==[1,200,400,600,800,1000]
 curve=[]
 for point in history:
  r=next(x for x in point["development"] if x["topology"]=="ring" and x["init"]=="monolith")
  curve.append(dict(update=point["update"],food=r["food"],gifts=r["gifts_per_person"],
    coverage=r["distinct_coverage"],full=r["complete"]))
 trajectories[name]=curve
 means=np.asarray([np.asarray(x["per_person"]["total"]).mean() for x in causal["by_seed"]])
 assert means.shape==(6,)
 rng=np.random.default_rng(41112026)
 samp=means[rng.integers(0,6,(10000,6))].mean(1)
 uncertainty[name]=dict(per_environment_causal_return=means.tolist(),
   descriptive_ci95=np.quantile(samp,[.025,.975]).tolist())
 row=dict(model=name,source=spec["source_history_type"],
  original_seed=spec["seed"],source_updates=spec["source_update"],
  social_signals=social,
  food_1=curve[0]["food"],food_200=curve[1]["food"],
  food_400=curve[2]["food"],food_600=curve[3]["food"],
  food_800=curve[4]["food"],food_1000=main["food"],
  gifts_1=curve[0]["gifts"],gifts_200=curve[1]["gifts"],
  gifts_1000=main["gifts_per_person"],
  coverage=main["distinct_coverage"],
  best_random_role_food=best["food"],
  learned_role_advantage=main["food"]-best["food"],
  no_gifts_food=H("donations_blocked")["food"],
  rewired_food=H(topo="rewired")["food"],
  permuted_people_food=H("relocated_people")["food"],
  causal=causal["mean_total"],causal_immediate=causal["mean_initial"],
  causal_future=causal["mean_future"],
  positive_agents=causal["positive_agents"],
  causal_rewired=C(topo="rewired")["mean_total"],
  positive_agents_rewired=C(topo="rewired")["positive_agents"],
  causal_random_init=C(init="random")["mean_total"],
  causal_nohistory=C(md="no_history")["mean_total"],
  causal_normal=C(md="normal")["mean_total"])
 rows.append(row)
by={r["model"]:r for r in rows}
contrasts=[]
for seed in (3111,4111):
 for state in ("SOC","NOSOC"):
  a=by[f"v41_C_s{seed}_{state}"]
  b=by[f"v41_U_s{seed}_{state}"]
  contrasts.append(dict(type="contract_history_minus_unilateral_history",
    seed=seed,observations=state,food=a["food_1000"]-b["food_1000"],
    causal=a["causal"]-b["causal"],
    gifts=a["gifts_1000"]-b["gifts_1000"]))
 for kind in ("C","U"):
  a=by[f"v41_{kind}_s{seed}_SOC"]
  b=by[f"v41_{kind}_s{seed}_NOSOC"]
  contrasts.append(dict(type="social_history_minus_no_social",
    seed=seed,observations=kind,food=a["food_1000"]-b["food_1000"],
    causal=a["causal"]-b["causal"],
    gifts=a["gifts_1000"]-b["gifts_1000"]))
A=[r for r in rows if r["source"]=="contract"]
eligible=[r for r in A if r["positive_agents"]>=24 and r["causal"]>0]
criteria=dict(
 h41a_any_contract_24_of48_positive=bool(eligible),
 h41b_social_history_causal_gain_0025=any(
   by[f"v41_C_s{seed}_SOC"]["causal"]-by[f"v41_C_s{seed}_NOSOC"]["causal"]>=.025
   for seed in (3111,4111)),
 h41c_contract_history_improves_in_2_of_4=sum(x["causal"]>0 for x in contrasts
   if x["type"]=="contract_history_minus_unilateral_history")>=2,
 h41d_all_positive_models_transfer=(all(
   r["positive_agents_rewired"]>=24 and r["causal_rewired"]>0
    and r["learned_role_advantage"]>.025 for r in eligible)
    if eligible else None))
criteria["h41d_applicable"]=criteria["h41a_any_contract_24_of48_positive"]
with (RES/"COMPARACION_V41.csv").open("w",newline="",encoding="utf8") as fh:
 w=csv.DictWriter(fh,list(rows[0]));w.writeheader();w.writerows(rows)
with (RES/"CONTRASTES_V41.csv").open("w",newline="",encoding="utf8") as fh:
 w=csv.DictWriter(fh,list(contrasts[0]));w.writeheader();w.writerows(contrasts)
sha_names=("PREREG_V41_POSTCONTRACT_RECIPROCITY.md","v41_unilateral_adaptation.py",
 "v41_frozen_audits.py","v41_summarize.py")
sha={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in sha_names}
(RES/"METRICAS_V41.json").write_text(json.dumps(
 dict(models=rows,contrasts=contrasts,criteria=criteria,
      trajectories=trajectories,environment_uncertainty=uncertainty,
      training_agent_rounds=8*1000*12*48*48,hashes=sha),indent=2),encoding="utf8")
report=[
 "# V41. Persistencia de cooperación unilateral tras retirar definitivamente el contrato",
 "",
 "Ocho ramas de continuación de redes previamente entrenadas a N48/k4/anillo de seis vecinos, dos semillas neuronales por fuente institucional. Los orígenes difieren: V30/c0,04/700 actualizaciones bajo contratos; V29-L/c0,04/850 actualizaciones bajo dones unilaterales y currículo distinto. Cada fuente se bifurcó en historial social visible o suprimido. Los ocho modelos continuaron durante1000 actualizaciones a coste fijo c0,04, aprendiendo solo por alimento individual y bajo entregas unilaterales, sin liquidación bilateral, sin profesor ni recompensa grupal.",
 "",
 "## Trayectoria y estado congelado al final de 1000 nuevas actualizaciones",
 "",
 table([[r["model"],r["source"],"sí" if r["social_signals"] else "no",
  f(r["food_1"]),f(r["food_200"]),f(r["food_400"]),
  f(r["food_600"]),f(r["food_800"]),f(r["food_1000"]),
  f(r["gifts_1"]),f(r["gifts_1000"])] for r in rows],
 ["Modelo","Entrenamiento previo","Historia social",
  "Comida u1","u200","u400","u600","u800","u1000",
  "Dones u1","Dones u1000"]),
 "",
 "La población que había aprendido a contratar empezó regalando mucho más que la población acostumbrada a unilateralidad; esta conducta no se considerará cooperación robusta a menos que sostenga un retorno privado causal positivo después de reentrenarse en el nuevo régimen. Las trayectorias completas están incluidas en METRICAS_V41.json.",
 "",
 "## Beneficio privado causal descontado y controles fuera de muestra",
 "",
 table([[r["model"],f(r["food_1000"]),f(r["gifts_1000"]),
   f(r["best_random_role_food"]),plus(r["learned_role_advantage"]),
   plus(r["causal"]),plus(r["causal_immediate"]),
   plus(r["causal_future"]),f'{r["positive_agents"]}/48',
   plus(r["causal_rewired"]),f'{r["positive_agents_rewired"]}/48'] for r in rows],
 ["Modelo","Alimento","Donaciones/pers.","Mejor rol aleatorio",
  "Ventaja laboral","Causal total","Inmediato",
  "Futuro","Positivos","Causal reconectado","Positivos reconectado"]),
 "",
 "La auditoría fuerza una propuesta unilateral adicional frente a impedirla para cada uno de los48 individuos, con seis semillas ambientales independientes de los entrenamientos y políticas congeladas. El coste inmediato de forzar el regalo es -0,04 para quien contribuye. Solo una mejora posterior mayor que0,04 puede producir retorno privado total positivo. Los controles de profesiones aleatorias evalúan la misma política de donar y tres tasas predefinidas; en las ramas entrenadas sin historial social se usa evaluación sin esa información.",
 "",
 "## Comparaciones pareadas por fuente, semilla y observación",
 "",
 table([[c["type"],str(c["seed"]),c["observations"],
  plus(c["food"]),plus(c["causal"]),plus(c["gifts"])] for c in contrasts],
 ["Diferencia","Semilla","Factor mantenido","Δ comida","Δ causal","Δ regalos"]),
 "",
 "No es un factorial plenamente identificado de formación institucional: el checkpoint unilateral V29 acumuló150 pasos más que V30 y siguió un currículo de costes diferente. Las comparaciones entre fuentes son exploratorias; las bifurcaciones de observación sí parten de los mismos pesos y estados originales de Adam. El cumplimiento literal de H41c solo depende del signo de diferencias de retorno minúsculas (entre aproximadamente -0,00060 y +0,00051) cuando los ocho modelos ya convergieron cerca de -0,040. **H41c es nominalmente positiva pero no refleja una mejora individualmente relevante ni cooperación estable.**",
 "",
 "## Hipótesis preregistradas",
 "",
 table([[k,("no aplicable" if v is None else "cumple" if v else "no cumple")] for k,v in criteria.items()],
 ["Hipótesis","Resultado"]),
 "",
 "H41d solo es aplicable si se alcanzó H41a; si no hay ningún modelo con retorno causal positivo para≥24 personas, informar «no aplicable», no interpretar una verdad vacía de programación como éxito experimental.",
 "",
 "## Interpretación",
 "",
 "[Inferencia] El entrenamiento continuo después de retirar las garantías contractuales permite examinar si las estrategias heredadas de una institución formal pueden adaptarse a relaciones de reciprocidad diferida sin liquidación automática. La alimentación social, por sí misma, no demuestra que contribuir sea una mejor respuesta privada; los controles causales son necesarios. La historia social puede modular la extinción de regalos sin resolver necesariamente su coste privado.",
 "",
 "La evaluación no demuestra aparición autónoma de nuevas instituciones, ni constitución cultural de normas, ni cooperación en una población abierta: todas las políticas se aprendieron previamente dentro de una ecología simulada y solo se probaron dos semillas por fuente.",
 "",
 "## Reproducción",
 "",
 "Preregistro, entrenador v41_unilateral_adaptation.py, ocho optimizadores y checkpoints finales runs/v41_*, evaluaciones congeladas results/v30_holdout_v41_*.json y results/v30_causal_v41_*.json, CSV de modelos, CSV de contrastes, métricas e histogramas de individuos en METRICAS_V41.json.",
 "SHA256:",
 *[f"{name}: {value}" for name,value in sha.items()]]
(RES/"RESULTADOS_INTEGRALES_V41.md").write_text("\n".join(report),encoding="utf8")
print("V41_REPORT_OK",len(rows),criteria)
for r in rows:
 print(r["model"],"food",round(r["food_1000"],4),
   "causal",round(r["causal"],4),"positive",r["positive_agents"],
   "gifts",round(r["gifts_1000"],4))
