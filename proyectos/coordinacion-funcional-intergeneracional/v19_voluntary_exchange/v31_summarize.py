"""V31 cross-scale voluntary contract evidence and fully frozen audits."""
from __future__ import annotations
import csv,json,hashlib
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent;RES=ROOT/"results"
NAMES=[f"v31_N120_MUTUAL_C{cost}_s{seed}"
       for cost in ("04","12") for seed in (3111,4111)]
def read(p):return json.loads(p.read_text(encoding="utf8"))
def table(rows,cols):
 return "\n".join(["| "+" | ".join(cols)+" |",
  "| "+" | ".join(["---"]*len(cols))+" |"]
  +["| "+" | ".join(map(str,r))+" |" for r in rows])
def f(x):return f"{x:.4f}"
def sgn(x):return f"{x:+.4f}"
rows=[];paired={}
for name in NAMES:
 p=ROOT/"runs"/name
 spec=read(p/"v25_spec.json");status=read(p/"v25_status.json")
 assert status["state"]=="completed" and status["updates"]==spec["updates"]==700
 assert spec["n"]==120 and spec["settlement"]=="mutual"
 held=read(RES/("v30_holdout_"+name+".json"))
 audit=read(RES/("v30_causal_"+name+".json"))
 assert len(held["rows"])==32 and len(audit["rows"])==8
 assert len(held["seeds"])==len(audit["seeds"])==6
 def H(condition="learned",topology="ring",init="monolith"):
  return next(x for x in held["rows"] if x["condition"]==condition
         and x["topology"]==topology and x["init"]==init)
 def A(mode="normal",topology="ring",init="monolith"):
  return next(x for x in audit["rows"] if x["mode"]==mode
         and x["topology"]==topology and x["init"]==init)
 normal=H();cf=A()
 best=max([H("role_random_"+x) for x in ("015","035","060")],
          key=lambda x:x["food"])
 ratio=(normal["food"]-.2)/(held["oracle"]["food"]-.2)
 row=dict(model=name,seed=spec["seed"],cost=spec["cost"],
   food=normal["food"],proposals=normal["proposals_per_person"],
   trades=normal["settled_units_per_person"],
   physical_coverage=normal["distinct_coverage"],
   useful_fraction=normal["physical_useful_ratio"],
   potential_coverage=normal["potential_coverage"],
   exact_balance=normal["balanced"],
   best_random_roles=best["food"],
   gain_vs_random_roles=normal["food"]-best["food"],
   no_gifts=H("donations_blocked")["food"],
   no_history=H("no_history")["food"],
   permuted_people=H("relocated_people")["food"],
   rewired=H(topology="rewired")["food"],
   causal_return=cf["mean_total"],
   causal_immediate=cf["mean_initial"],
   causal_future=cf["mean_future"],
   causal_positive_people=cf["positive_agents"],
   causal_no_history=A("no_history")["mean_total"],
   causal_rewired=A(topology="rewired")["mean_total"],
   oracle=held["oracle"]["food"],
   fraction_available_surplus=ratio)
 rows.append(row)
with (RES/"COMPARACION_V31.csv").open("w",newline="",encoding="utf8") as fw:
 w=csv.DictWriter(fw,list(rows[0]));w.writeheader();w.writerows(rows)
for cost in ("04","12"):
 n=sorted([v for v in rows if v["cost"]==float("0."+cost)],key=lambda x:x["seed"])
 if len(n)!=2:continue
 paired[cost]=dict(models=[x["model"] for x in n],
    food_mean=float(np.mean([x["food"] for x in n])),
    causal_return_mean=float(np.mean([x["causal_return"] for x in n])))
paths=("v30_consensual.py","v30_frozen_audits.py",
       "v31_summarize.py","PREREG_V31_BARTER_SCALE.md")
hashes={x:hashlib.sha256((ROOT/x).read_bytes()).hexdigest() for x in paths}
(RES/"METRICAS_V31.json").write_text(json.dumps(dict(models=rows,
   contrasts_by_cost=paired,hashes=hashes,
   training_agent_rounds=4*700*8*48*120,
   holdout_world_condition_paths=4*4*8*6*8,
   counterfactual_world_person_pairs=4*4*2*6*3*120),indent=2),encoding="utf8")
reference=read(RES/"METRICAS_V30.json")["models"]
compare=[]
for item in rows:
 if item["cost"]==.04:
  prev=next(x for x in reference if x["settlement"]=="mutual" and x["seed"]==item["seed"])
  compare.append([item["seed"],f(prev["food"]),f(item["food"]),
   sgn(item["food"]-prev["food"]),sgn(prev["causal_total"]),
   sgn(item["causal_return"])])
report=[
 "# V31. Contratos bilaterales descentralizados con 120 individuos y cuatro profesiones",
 "",
 "Campaña preregistrada el 12/11/2026 después de los resultados preliminares de V30 y antes de conocer el final de V30. Todos los actores de V31 se iniciaron con pesos aleatorios privados (no se transfirieron redes de V30), y aprendieron al mismo tiempo ofertas dirigidas y decisiones de ocupación. La regla institucional de liquidación mutuamente consentida permaneció disponible exógenamente, sin planificación de objetivos sociales ni recompensa de grupo.",
 "",
 "N120, k4, anillo grado6, horizonte48, 700 actualizaciones, lote8, dos semillas por coste unitario final0,04 y0,12. Seis semillas ambientales nuevas para evaluación congelada; ocho mundos por semilla/condición para alimento y tres mundos por semilla para intervenciones de todas las personas. Los mundos no son semillas independientes de las redes neuronales.",
 "",
 "## Resultados congelados",
 "",
 table([[r["model"],str(r["cost"]),f(r["food"]),
 f(r["trades"]),f(r["physical_coverage"]),
 f(r["best_random_roles"]),sgn(r["gain_vs_random_roles"]),
 sgn(r["causal_return"]),f'{r["causal_positive_people"]}/120',
 f(r["oracle"]),f'{r["fraction_available_surplus"]:.1%}'] for r in rows],
 ["Modelo","Coste","Alimento","Contratos efectivos/pers.",
 "Cobertura","Mejor movilidad aleatoria","Ventaja",
 "Retorno causal","Personas positivas","Oráculo físico",
 "Fracción del excedente máximo"]),
 "",
 "El oráculo supone 3 parejas contractuales útiles por persona y roles periódicos, sin movilidad ni redundancias; comida 0,88 a coste0,04 o 0,64 a coste0,12. Está programado explícitamente solo como test de posibilidad material, no como profesor ni política aprendida. La fracción del excedente máximo = (alimento−0,20)/(oráculo−0,20) cuantifica distancia al techo bajo el mismo precio.",
 "",
 "## Transferencia al aumentar de 48 a 120 personas",
 "",
 table(compare,["Semilla","N48 alimento","N120 alimento",
   "Diferencia","N48 causal","N120 causal"]),
 "",
 "Las redes de N48 y N120 están entrenadas separadamente desde cero: esta es una comparación del protocolo a dos tamaños de población, no una prueba de que los mismos pesos se transfieran. La red mantiene grado6, de modo que el barrio local por persona tiene la misma cardinalidad aunque la población total aumente.",
 "",
 "## Mecanismos y heterogeneidad",
 "",
 table([[r["model"],f(r["food"]),f(r["no_history"]),
 f(r["permuted_people"]),f(r["rewired"]),
 sgn(r["causal_immediate"]),sgn(r["causal_future"]),
 sgn(r["causal_no_history"]),sgn(r["causal_rewired"])] for r in rows],
 ["Modelo","Circular","Sin historial","Personas permutadas",
 "Red reconectada","Causal inmediato","Causal futuro",
 "Causal sin historial","Causal reconectada"]),
 "",
 "La contribución contractual no implica necesariamente altruismo o memoria de favores anteriores: los acuerdos simultáneos permiten pagar un bien mientras se recibe otro. Las pruebas fuera de muestra verifican beneficios materiales sin obligar a dar, y la auditoría fuerza solo una propuesta del primer turno frente a prohibirla, manteniendo libres las otras acciones. El retorno causal puede deberse principalmente a la contraprestación inmediata. Una oferta que no encuentra otra correspondiente no se liquida ni ocasiona gasto.",
 "",
 "## Condiciones de éxito y límites",
 "",
 "Este resultado permite explorar cooperación contractual y especialización profesional con 120 personas y cuatro oficios en dos precios, pero no acredita que la **institución contractual misma** surgiese endógenamente: sus reglas fueron diseñadas antes. Las políticas laborales aprendidas deben superar de modo sustancial controles de movilidad aleatoria y mantener estabilidad ante reconfiguración relacional para considerarse organización funcional superior. Solo dos semillas neuronales por coste y seis contextos ambientales no permiten universales ni certeza sobre todas las poblaciones.",
 "",
 "Se conserva el objetivo general abierto. La línea V32 prueba la adopción institucional libre y V33 el aprendizaje laboral prolongado. Las conclusiones positivas V30–V31 no deben usarse para borrar los fracasos de reciprocidad unilateral V24–V29.",
 "",
 "## Código y reproducción",
 "",
 "Preregistro PREREG_V31_BARTER_SCALE.md, código del mercado v30_consensual.py, auditor v30_frozen_audits.py, checkpoints de las cuatro condiciones en runs/v31_N120_*, resultados crudos results/v30_holdout_v31_*.json y results/v30_causal_v31_*.json.",
 "",
 "SHA256:",
 *[f"{k}: {v}" for k,v in hashes.items()]]
(RES/"RESULTADOS_INTEGRALES_V31.md").write_text("\n".join(report),encoding="utf8")
print("V31_REPORT_OK",len(rows))
for r in rows:
 print(r["model"],"food",round(r["food"],4),
 "causal",round(r["causal_return"],4),"positives",r["causal_positive_people"])
