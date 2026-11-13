"""V51 preregistered report: learned 4-role functional cooperation from monolith."""
from pathlib import Path
import csv,json,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parent;OUT=ROOT/"results"
DONORS=("LOLA20","NL")
DONOR_SEEDS=(3111,4111);ROLE_SEEDS=(7111,8111)
INIT=("monolith","random")
CONTROLS=("fixed","random_0.15","random_0.35","random_0.60","relocated_roles")
METRICS=("food","gifts","full","coverage","balanced_teams","switches_per_person",
 "terminal_food","terminal_full","terminal_balanced_teams")
def read(p):return json.loads(p.read_text("utf8"))
records=[];curves={};holdout_by_seed={}
for method in DONORS:
 for dseed in DONOR_SEEDS:
  for role_seed in ROLE_SEEDS:
   name=f"v51_{method}_D{dseed}_R{role_seed}"
   folder=ROOT/"runs"/name
   spec=read(folder/"v51_spec.json")
   status=read(folder/"v51_status.json")
   assert status["state"]=="completed" and status["updates"]==spec["updates"]==1500
   data=read(OUT/f"v51_holdout_{name}.json")
   assert len(data["rows"])==72
   assert set(data["seeds"])=={997101,997107,997109,997121,997131,997137}
   history=[json.loads(x) for x in (folder/"v51_history.jsonl").read_text("utf8").splitlines()]
   assert [p["update"] for p in history]==[1,300,600,900,1200,1500]
   curves[name]=history
   holdout_by_seed[name]=data["rows"]
   for init in INIT:
    subset=[z for z in data["rows"] if z["init"]==init]
    def by_condition(label):
     z=[x for x in subset if x["condition"]==label]
     assert len(z)==6
     return {metric:float(np.mean([r[metric] for r in z])) for metric in METRICS}
    learned=by_condition("learned")
    best=max((by_condition(c) for c in ("random_0.15","random_0.35","random_0.60")),
     key=lambda x:x["food"])
    others={ctrl:by_condition(ctrl) for ctrl in CONTROLS}
    row=dict(name=name,donor_method=method,donor_seed=dseed,role_seed=role_seed,
     init=init,
     learned_food=learned["food"],
     learned_terminal_food=learned["terminal_food"],
     learned_occupational_full=learned["balanced_teams"],
     learned_terminal_occupational_full=learned["terminal_balanced_teams"],
     learned_material_full=learned["full"],
     learned_terminal_material_full=learned["terminal_full"],
     gifts_per_person=learned["gifts"],
     role_switches=learned["switches_per_person"],
     fixed_food=others["fixed"]["food"],
     best_random_role_food=best["food"],
     advantage_vs_best_random=learned["food"]-best["food"],
     relocated_roles_food=others["relocated_roles"]["food"],
     relocated_terminal_occupational_full=others["relocated_roles"]["terminal_balanced_teams"],
     relocated_occupational_full=others["relocated_roles"]["balanced_teams"],
     relocation_food_delta=others["relocated_roles"]["food"]-learned["food"])
    records.append(row)
def get(method,donor,role,init="monolith"):
 return next(r for r in records if r["donor_method"]==method and
 r["donor_seed"]==donor and r["role_seed"]==role and r["init"]==init)
primary=[r for r in records if r["init"]=="monolith" and r["donor_method"]=="LOLA20"]
controls=[r for r in records if r["init"]=="monolith" and r["donor_method"]=="NL"]
hyp=dict(
 h51a=sum(r["learned_terminal_occupational_full"]>=.5
   and r["learned_food"]>=.55 for r in primary)>=3,
 h51b=sum(r["advantage_vs_best_random"]>=.05 for r in primary)>=3,
 h51c=all(not (r["learned_terminal_occupational_full"]>=.5
  and r["learned_food"]>=.55) for r in controls),
 h51d=sum(r["relocated_terminal_occupational_full"]>=.4 for r in primary)>=3)
with (OUT/"COMPARACION_V51.csv").open("w",newline="",encoding="utf8") as fh:
 w=csv.DictWriter(fh,list(records[0]));w.writeheader();w.writerows(records)
sha_names=("PREREG_V51_ENDOGENOUS_FOUR_ROLES.md",
 "AMENDMENT_V51_TERMINAL_MEASURES.md",
 "v51_endogenous_roles.py","v51_frozen_audits.py","v51_summarize.py",
 "test_v51_endogenous_roles.py","test_v51_frozen_audits.py")
sha={x:hashlib.sha256((ROOT/x).read_bytes()).hexdigest() for x in sha_names}
(OUT/"METRICAS_V51.json").write_text(json.dumps(dict(
 models=records,hypotheses=hyp,curves=curves,
 heldout_by_environment=holdout_by_seed,sha256=sha,
 neural_training_agent_rounds_max=8*1500*12*48*48,
 heldout_worlds=8*2*6*6*24,
 donor_source="private V47 frozen donation policies, pretrained with exact opponent gradient, no new donation learning",
 role_source="private agent-specific MLP from random initialization",
 instruction="K4 teams exogenous, free role selection and no quotas or social rewards",
 original_training_commit="43421942b36cc7e992de6ef0d2bacd508a10aacb"),indent=2),encoding="utf8")
fmt=lambda x:f"{x:.4f}"
def tbl(items,header):
 return "\n".join(["| "+" | ".join(header)+" |",
 "| "+" | ".join(["---"]*len(header))+" |"]+
 ["| "+" | ".join(map(str,row))+" |" for row in items])
report=["# V51 — Aprendizaje de cuatro ocupaciones complementarias en equipos sociales",
"",
"Ocho poblaciones de48 personas, organizadas exógenamente en12 cliques K4, una conexión permanente a cada uno de los otros3 miembros. Cada individuo escoge libremente entre cuatro profesiones mediante una MLP privada con parámetros independientes y recompensa exclusivamente alimentaria personal. Los actores ocupacionales parten de pesos aleatorios, aprenden durante1500 actualizaciones con12 mundos, horizonte48 y posibilidad de cambiar de profesión cada8 rondas pagando0,015 por modificación. **No existe objetivo de equilibrio ocupacional, reparto profesional planificado ni premio colectivo por especializarse.**",
"",
"Las políticas de regalar son **anteriores y congeladas**: LOLA20 y control NL procedentes de V47, que aprendieron por interés privado en encuentros diádicos con gradiente de aprendizaje ajeno exacto. Las donaciones no se entrenan en V51. La estructura de equipos K4 es una condición externa que favorece disponer de tres vecinos estables; no se modela elección de la red.",
"",
"## Evaluación final sobre seis semillas ambientales reservadas",
"",
tbl([[r["name"],r["init"],
 fmt(r["learned_food"]),fmt(r["learned_occupational_full"]),
 fmt(r["learned_terminal_occupational_full"]),
 fmt(r["learned_material_full"]),fmt(r["gifts_per_person"]),
 fmt(r["best_random_role_food"]),
 f'{r["advantage_vs_best_random"]:+.4f}',
 fmt(r["relocated_terminal_occupational_full"])] for r in records],
 ["Modelo","Inicio","Comida","Balance medio",
  "Balance terminal","Tres bienes recibidos",
  "Dones/pers.","Mejor azar profes.","Δ vs azar","Balance terminal reubicado"]),
 "",
 "Los12 equipos de4 miembros se consideran funcionalmente equilibrados cuando contienen exactamente las cuatro profesiones distintas. Se informa por separado su fracción promediada durante48 rondas y la fracción de equipos equilibrados al terminar la ronda48. El alimento medio es la media por persona-ronda y puede diferir del alimento terminal.",
 "",
 "Los controles preservan pesos y decisiones de regalo, pero sustituyen la elección aprendida de oficio por conservación de ocupación inicial, cambios aleatorios a tasas0,15/0,35/0,60 y reasignación de políticas profesionales **dentro de cada equipo K4** sin reentrenamiento. Ningún control recibe cuota de profesiones ni recompensa colectiva.",
 "",
 "## Hipótesis preregistradas",
 "",
 tbl([[k,"cumple" if v else "falsada"] for k,v in hyp.items()],
 ["Criterio","Resultado"]),
 "",
 "H51a exigía que≥3/4 modelos LOLA20 alcanzasen≥50% de equipos con cuatro profesiones al final y alimento medio≥0,55 desde un inicio monolítico. H51b exigía ventaja alimentaria≥+0,05 sobre el mejor cambio de profesiones aleatorio. H51c exigía que ningún control NL alcanzase simultáneamente esos dos criterios. H51d exigía≥40% de equipos profesionales completos al reasignar internamente las políticas de elección profesional.",
 "",
 "## Validez y enmienda",
 "",
 "El preregistro inicial no distinguía con precisión «al final» de la media temporal. Antes de evaluar los checkpoints finales se añadió la métrica terminal y se preservó el estimando temporal original, sin cambiar ni umbrales ni políticas; véase AMENDMENT_V51_TERMINAL_MEASURES.md. El commit de código usado por los entrenamientos ya activos difiere solo por las tres métricas terminales añadidas posteriormente al evaluador; no se modificó el aprendizaje.",
 "",
 "[Inferencia] Un resultado favorable mostraría que las recompensas individuales pueden inducir especialización complementaria cuando una política cooperativa preaprendida proporciona bienes útiles. La interpretación sigue condicionada a los equipos K4 externos y la reciprocidad heredada. Una reubicación fallida sugeriría convenciones posicionales y limitaría la generalización a nuevas agrupaciones.",
 "",
 "## Límites",
 "",
 "No hemos demostrado la aparición simultánea desde cero de cooperación y división del trabajo: el donante LOLA fue entrenado previamente y el cálculo de gradientes del compañero es un recurso extraordinario del laboratorio. Los equipos K4 no compiten por nuevos miembros, no eligen vecinos, no existe rotación intraepisodio y tampoco se han evaluado sociedades de120 personas en esta configuración.",
 "",
 "## Código y pruebas",
 "",
 "Preregistro, enmienda, motor de profesión privada, auditor de políticas congeladas, ocho snapshots finales con parámetros/Adam y series longitudinales, seis semillas ambientales por condición, controles y archivos JSON; CSV de comparación y SHA256:",
 *[f"{k}: {v}" for k,v in sha.items()]]
(OUT/"RESULTADOS_INTEGRALES_V51.md").write_text("\n".join(report),encoding="utf8")
print("V51_REPORT_OK",len(records),hyp)
for r in records:
 if r["init"]=="monolith":
  print(r["name"],"food",round(r["learned_food"],4),
   "terminal_complete",round(r["learned_terminal_occupational_full"],3),
   "delta_vs_random",round(r["advantage_vs_best_random"],4),
   "relocated",round(r["relocated_terminal_occupational_full"],3))
