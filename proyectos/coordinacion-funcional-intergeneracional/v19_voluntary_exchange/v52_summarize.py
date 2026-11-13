"""V52 final preregistered joint-learning reports and counterfactual controls."""
from __future__ import annotations
import csv,json,hashlib
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent;OUT=ROOT/"results"
sources=("SCRATCH","PRIOR")
seeds=(3111,4111)
roles=(7111,8111)
names=[f"v52_{s}_D{d}_R{r}" for s in sources for d in seeds for r in roles]
rows=[]; histories={}; raw_causal={}
for name in names:
 p=ROOT/"runs"/name
 settings=json.loads((p/"v52_spec.json").read_text("utf8"))
 status=json.loads((p/"v52_status.json").read_text("utf8"))
 audit=json.loads((OUT/f"v52_holdout_{name}.json").read_text("utf8"))
 assert status["state"]=="completed" and status["updates"]==settings["updates"]==1500
 assert len(audit["rows"])==60 and len(audit["causal_by_seed"])==12
 assert set(audit["seeds"])=={998101,998107,998109,998121,998131,998137}
 history=[json.loads(line) for line in (p/"v52_history.jsonl").read_text("utf8").splitlines()]
 assert [x["update"] for x in history]==[1,300,600,900,1200,1500]
 histories[name]=history
 raw_causal[name]=audit["causal_by_seed"]
 for init in ("monolith","random"):
  samples=[x for x in audit["rows"] if x["init"]==init]
  causal=[x for x in audit["causal_by_seed"] if x["init"]==init]
  assert len(samples)==30 and len(causal)==6
  def avg(metr,cond="learned"):
   values=[r[metr] for r in samples if r["condition"]==cond]
   assert len(values)==6
   return float(np.mean(values))
  eff=np.asarray([x["own_effect"] for x in causal])
  reference=[x["food"] for x in audit["frozen_reference_v51_by_seed"]
    if x["init"]==init]
  if settings["source"]=="prior":assert len(reference)==6
  row=dict(model=name,source=settings["source"],
   donor_seed=settings["gift_seed"],role_seed=settings["role_seed"],init=init,
   food=avg("food"),terminal_roles=avg("terminal_occupations"),
   gift_slot_rate=avg("gift_slot_rate"),material_full=avg("full"),
   causal_private=float(eff.mean()),
   causal_positive_agents=int((eff.mean(0)>0).sum()),
   no_role_change_food=avg("food","fixed"),
   best_random_role_food=max(avg("food",c) for c in
    ("random_0.15","random_0.35","random_0.60")),
   frozen_v51_food=float(np.mean(reference)) if reference else None,
   frozen_v51_gap=(avg("food")-float(np.mean(reference))) if reference else None)
  rows.append(row)
lookup={(r["source"],r["donor_seed"],r["role_seed"],r["init"]):r for r in rows}
prim=[r for r in rows if r["init"]=="monolith"]
scratch=[r for r in prim if r["source"]=="scratch"]
prior=[r for r in prim if r["source"]=="prior"]
def pass_coop(x):
 return x["food"]>=.55 and x["terminal_roles"]>=.5 and x["gift_slot_rate"]>=.5
qualifiers=[r for r in prim if pass_coop(r)]
criteria=dict(
 h52a_any_scratch_joint_emergence=any(pass_coop(r) for r in scratch),
 h52b_prior_stability_at_least_3of4=sum(pass_coop(r) for r in prior)>=3,
 h52c_prior_vs_v51_frozen_within_0_05=sum(
  r["frozen_v51_gap"]>=-.05 for r in prior)>=3,
 h52d_causal_positive_if_any_cooperation=(
  any(r["causal_private"]>0 and r["causal_positive_agents"]>=24 for r in qualifiers)
  if qualifiers else None))
with (OUT/"COMPARACION_V52.csv").open("w",newline="",encoding="utf8") as fh:
 writer=csv.DictWriter(fh,list(rows[0]));writer.writeheader();writer.writerows(rows)
src=("PREREG_V52_JOINT_ENDOGENOUS.md",
 "v52_joint_roles_gifts.py","v52_frozen_audits.py",
 "test_v52_joint_roles_gifts.py","test_v52_frozen_audits.py","v52_summarize.py")
hashes={file:hashlib.sha256((ROOT/file).read_bytes()).hexdigest() for file in src}
(OUT/"METRICAS_V52.json").write_text(json.dumps(dict(
 model_rows=rows,criteria=criteria,trajectories=histories,
 environmental_causes=raw_causal,sha256=hashes,
 training_agent_rounds_max=8*1500*12*48*48,
 warning="Not open society; fixed K4 teams, 4 selectable jobs, preexisting gift actors only in PRIOR"),
 indent=2),encoding="utf8")
def table(rs,h):
 return "\n".join(["| "+" | ".join(h)+" |","| "+" | ".join(["---"]*len(h))+" |"]+
 ["| "+" | ".join(map(str,r))+" |" for r in rs])
f=lambda x:f"{x:.4f}"
report=["# V52 — Coaprendizaje de donaciones privadas y diferenciación profesional",
"",
"Ocho sociedades formadas por48 actores,12 equipos K4 exógenos,4 profesiones libremente seleccionadas y3 vínculos simultáneos por persona. Cada individuo optimizó únicamente su propia comida mediante REINFORCE durante1500 actualizaciones; se aprendieron simultáneamente donaciones (5 logits privados) y elección de profesión (MLP privada). El brazo SCRATCH arranca con ambos componentes aleatorios. El brazo PRIOR inicializa solo la política de regalo con una estrategia cooperativa LOLA20 aprendida previamente en V47, y **permite que siga actualizándose**. Sin cuotas, contratos, castigos programados ni recompensa grupal. El juego material corresponde a V51.",
"",
"## Evaluación final preregistrada con seis semillas nuevas",
"",
table([[r["model"],r["init"],f(r["food"]),f(r["terminal_roles"]),
 f(r["gift_slot_rate"]),f(r["material_full"]),
 f(r["causal_private"]),f'{r["causal_positive_agents"]}/48',
 ("—" if r["frozen_v51_gap"] is None else f(r["frozen_v51_gap"]))]
 for r in rows],["Modelo","Estado inicial","Comida",
 "Equipos 4 oficios al final","Donaciones por vínculo",
 "Recibe 3 tipos","Efecto causal regalar","Personas positivas",
 "Comida respecto V51 congelado"]),
 "",
 "La condición SCRATCH aprende una estructura ocupacional complementaria, pero la tasa de donación colapsa durante el entrenamiento hasta ~14–15% por vínculo y el incentivo causal de regalar suele ser negativo. **En este modelo el balance ocupacional terminal no es evidencia suficiente de cooperación materialmente sostenible.** Las cuatro condiciones PRIOR conservan cooperación y especialización casi completas y un incentivo causal positivo en48/48 individuos; ello depende de un donante entrenado antes con inferencia exacta del aprendizaje de la contraparte.",
 "",
 "## Hipótesis registradas antes de entrenar",
 "",
 table([[key,"cumple" if val else "no cumple" if val is False else "no aplicable"]
  for key,val in criteria.items()],["Criterio","Resultado"]),
 "",
 "H52a exige que alguna de cuatro sociedades SCRATCH alcance simultáneamente alimento≥0,55,≥50% de equipos completos al final y≥0,50 donaciones por enlace. H52b exige los mismos umbrales en3/4 PRIOR. H52c compara alimento con las políticas de rol V51 congelando los regalos, con tolerancia−0,05 en al menos3/4 pares. H52d comprueba retorno causal positivo de regalar en al menos24/48 personas si hay una sociedad que cumpla los umbrales cooperativos.",
 "",
 "## Interpretación sociológica",
 "",
 "[Inferencia] La especialización de tareas aparece más fácilmente que la cooperación que permite obtener de ella beneficios materiales; la adaptación individual simultánea erosiona el intercambio cuando no existe un mecanismo de anticipación estratégica. Las primeras contribuciones pueden facilitar la aparición de una distribución laboral que luego persiste incluso cuando se reduce el intercambio. La diferencia PRIOR–SCRATCH indica dependencia de la historia de aprendizaje (trayectoria), no una prueba de que la cooperación solo pueda surgir mediante LOLA.",
 "",
 "Las cliques de cuatro, los roles de especialidad y las recompensas fueron establecidos por el diseñador. No se ha probado apertura demográfica, cambio de compañero en V52, institución pública emergente ni existencia de una población autoorganizada de120 personas.",
 "",
 "## Reproducción",
 "",
 "Preregistro V52, motor conjunto, auditor frozen y test de intervención privada,8 checkpoints de pesos/Adam, histories y evaluaciones causales por semilla, CSV/JSON final y SHA256:",
 *[f"{key}: {val}" for key,val in hashes.items()]]
(OUT/"RESULTADOS_INTEGRALES_V52.md").write_text("\n".join(report),encoding="utf8")
print("V52_REPORT_OK",len(rows),criteria)
for r in prim:print(r["model"],round(r["food"],4),round(r["gift_slot_rate"],4),
 round(r["terminal_roles"],3),round(r["causal_private"],4),r["causal_positive_agents"])
