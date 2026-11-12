"""Reproducible V21/V22 report assembled from frozen raw experiment outputs."""
from __future__ import annotations
import json,csv,hashlib,statistics
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
RES=ROOT/"results"
LONG=["v21_LONG_SMOOTH_s3111","v21_LONG_SMOOTH_s4111",
      "v21_LONG_CONST_s3111","v21_LONG_CONST_s4111",
      "v21_LONG_ABRUPT_s3111","v21_LONG_ABRUPT_s4111"]
MIX=["v21_MIX_s3111","v21_MIX_s4111","v21_MIX_s5111","v21_MIX_s6111"]
ROLE=["v22_DONOR3111_ROLE7111","v22_DONOR3111_ROLE8111",
      "v22_DONOR4111_ROLE7111","v22_DONOR4111_ROLE8111"]
assert len(ROLE)==4
def read(p):return json.loads(p.read_text("utf8"))
def table(rows,headers):
 return "\n".join(["| "+" | ".join(headers)+" |",
       "| "+" | ".join(["---"]*len(headers))+" |"]
        +["| "+" | ".join(map(str,r))+" |" for r in rows])
def fmt(n):return f"{n:+.3f}"
records21=[]
for name in LONG+MIX:
 folder=ROOT/"runs"/name
 status=read(folder/("targeted_status.json"))
 assert status["state"]=="completed" and status["updates"]==(1600 if name in LONG else 600),name
 file=folder/("v21_history.jsonl" if name in LONG else "v20_history.jsonl")
 entry=json.loads(file.read_text("utf8").splitlines()[-1])
 assert entry["update"]==status["updates"]
 p=RES/("v20_allagents_"+name+".json")
 causal=read(p)
 assert len(causal["scenarios"])==9 and causal["checkpoint"]==status["updates"],name
 lookup={(x["k"],x["topology"],x["mode"]):x for x in causal["scenarios"]}
 scores=entry.get("eval",entry.get("high_cost"))
 rec=dict(name=name,epoch=status["updates"],
     food=scores["trained_normal"]["food"],
     gifts=scores["trained_normal"]["gift"],
     food_ood=scores["ood_normal"]["food"])
 for key,task in (("ring",(2,"ring")),("rewired",(2,"rewired")),("k3",(3,"ring"))):
  for mode in ("normal","scramble","no_social"):
   rec[key+"_"+mode]=lookup[(task[0],task[1],mode)]["mean_total"]
  rec[key+"_positive"]=lookup[(task[0],task[1],"normal")]["positive_agents"]
 records21.append(rec)
records22=[]
bootstrap={}
for name in ROLE:
 folder=ROOT/"runs"/name
 status=read(folder/"role_status.json")
 assert status["state"]=="completed" and status["updates"]==600
 audit=read(RES/("v22_holdout_"+name+".json"))
 assert audit["checkpoint"]==600 and len(audit["rows"])==54
 assert len(audit["seeds"])==6 and audit["worlds_per_seed"]==24
 for degree,topo,initial in ((2,"ring","monolith"),(2,"rewired","monolith"),
                              (4,"ring","monolith"),(2,"ring","random")):
  sel={x["condition"]:x for x in audit["rows"] if
       x["degree"]==degree and x["topology"]==topo and x["init"]==initial}
  best_random=max((x for k,x in sel.items() if k.startswith("random")),
                key=lambda x:x["food"])
  learned=sel["learned"]
  row=dict(model=name,degree=degree,topology=topo,init=initial,
       food=learned["food"],opposite=learned["opposite_links"],
       exactly_balanced=learned["balanced"],
       random_best=best_random["food"],random_label=best_random["condition"],
       gain_vs_best=learned["food"]-best_random["food"],
       fixed=sel["fixed"]["food"],
       permuted=sel["relocated_people"]["food"],
       gifthidden=sel["gift_signals_hidden"]["food"],
       bothhistoryhidden=sel["role_and_gift_donation_history_hidden"]["food"])
  records22.append(row)
  a=np.asarray([v["mean_food"] for v in learned["by_seed"]])
  b=np.asarray([v["mean_food"] for v in best_random["by_seed"]])
  assert len(a)==6 and len(b)==6
  diff=a-b
  rng=np.random.default_rng(802112)
  indices=rng.integers(0,len(diff),size=(10000,len(diff)))
  dist=diff[indices].mean(1)
  bootstrap[f"{name}|{degree}|{topo}|{initial}"]=dict(
     paired_seed_differences=diff.tolist(),
     mean=float(diff.mean()),
     descriptive_bootstrap_95=np.quantile(dist,[.025,.975]).tolist(),
     note="Resamples only 6 environmental seed clusters; selected best of four fixed random rates, uncertainty not over training seeds.")
with (RES/"COMPARACION_V21.csv").open("w",encoding="utf8",newline="") as fh:
 w=csv.DictWriter(fh,fieldnames=list(records21[0]));w.writeheader();w.writerows(records21)
with (RES/"COMPARACION_V22.csv").open("w",encoding="utf8",newline="") as fh:
 w=csv.DictWriter(fh,fieldnames=list(records22[0]));w.writeheader();w.writerows(records22)

legacy={n:read(RES/("v20_allagents_"+n+".json")) for n in (
 "v20_SMOOTH_s3111","v20_SMOOTH_s4111",
 "v20_CONST_s3111","v20_CONST_s4111",
 "v20_ABRUPT_s3111","v20_ABRUPT_s4111")}
def v20_return(name,mode="normal"):
 return next(x["mean_total"] for x in legacy[name]["scenarios"]
      if x["k"]==2 and x["topology"]=="ring" and x["mode"]==mode)
longtab=[]
for x in records21[:6]:
 previous=x["name"].replace("v21_LONG_","v20_")
 longtab.append([x["name"],f"{x['food']:.3f}",
                 fmt(v20_return(previous)),fmt(x["ring_normal"]),
                 f"{x['ring_positive']}/24",fmt(x["rewired_normal"]),
                 fmt(x["k3_normal"]),
                 fmt(x["ring_no_social"])])
roletab=[]
for x in records22:
 if x["init"]=="monolith":
  roletab.append([x["model"],x["topology"]+f"/d{x['degree']}",
              f"{x['food']:.3f}",f"{x['random_best']:.3f}",
              fmt(x["gain_vs_best"]),f"{x['opposite']:.1%}",
              f"{x['exactly_balanced']:.1%}"])
reptab=[]
for n in ["v21_LONG_SMOOTH_s3111","v21_LONG_SMOOTH_s4111"]:
 audit=read(RES/("v21_reputation_"+n+".json"))
 assert len(audit["rows"])==18
 sm={x["mode"]:x for x in audit["rows"] if x["k"]==2 and x["topology"]=="ring"}
 reptab.append([n]+[fmt(sm[m]["mean_total"]) for m in (
 "normal","no_direct_identity","no_public_offer",
 "no_both_except_receipt","no_social")])
mix=[]
for n in MIX:
 a=next(x for x in records21 if x["name"]==n)
 prev=read(ROOT/"runs"/n/"v20_history.jsonl") if False else None
 prev_name=n.replace("v21_MIX_","v20_SMOOTH_")
 hist=json.loads((ROOT/"runs"/prev_name/"v20_history.jsonl").read_text("utf8").splitlines()[-1])
 ring=hist["high_cost"]["trained_normal"]["food"]
 mix.append([n,f"{ring:.3f}",f"{a['food']:.3f}",
                fmt(a["food"]-ring),fmt(a["rewired_normal"]),
                f"{a['rewired_positive']}/24"])
sha_paths=[
 "v21_longitudinal.py","v21_reputation_census.py","v22_occupations.py",
 "v22_frozen_holdout.py","test_v22_occupations.py",
 "v20_all_agents_causal.py","targeted_gifts.py",
 "PREREG_V21_LONGITUDINAL.md","PREREG_V21B_TOPOLOGIES.md",
 "PREREG_V22_ENDOGENOUS_OCCUPATIONS.md"]
hashes={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in sha_paths}
report=[
 "# V21–V22. Reciprocidad y formación endógena de división ocupacional",
 "",
 "## Alcance y procedencia",
 "",
 "Ronda exploratoria del 12/11/2026 en la rama research/aldea-v19-voluntary-exchange-20261111, derivada de V20 commit 31d553db. Las poblaciones tienen 24 agentes con políticas neuronales privadas y recompensas individuales; no hay profesor de ocupaciones, planificador central ni funciones de recompensa global. La política de donación voluntaria de V22 está preentrenada en V21 y permanece congelada durante el aprendizaje de profesiones. No se ha investigado aún aprendizaje simultáneo desde cero de ambos subsistemas.",
 "",
 "V21 prolonga 6 modelos de 600 a 1600 actualizaciones a coste 0,12 y prepara otros 4 modelos mixtos de 600 actualizaciones en dos redes alternadas. V22 entrena cuatro nuevas redes ocupacionales durante 600 actualizaciones sobre dos políticas donantes preentrenadas y congeladas. El actor ocupacional puede cambiar entre dos profesiones cada ocho rondas, pagando 0,015 raciones por movimiento. Se entrena desde situaciones monolíticas o aleatorias mediante REINFORCE sobre alimento individual descontado.",
 "",
 "## V21. Cambios longitudinales de cooperación",
 "",
 table(longtab,["Política","Alimento u1600","Retorno u600","Retorno u1600",
               "Agentes positivos","Retorno reconectada","Retorno k3",
               "Retorno sin señales sociales"]),
 "",
 "Estos retornos son contrafactuales de forzar una donación inicial. Se estiman en mundos nuevos, con 24/24 personas, seis semillas de ambiente, 32 mundos por semilla y 48 rondas. Sus signos no se infieren de la tasa media de donaciones. Persisten respuestas negativas al quitar o alterar las señales sociales. Los modelos longitudinales graduales mejoran, aunque solo existen dos semillas neuronales por familia en esta campaña.",
 "",
 "## V21. Pérdida de eficacia con entrenamiento mixto de redes",
 "",
 table(mix,["Entrenamiento mixto","Alimento control circular",
           "Alimento mixto","Diferencia","Retorno causal reconectada",
           "Agentes positivos reconectada"]),
 "",
 "El resultado no apoya la hipótesis de que exponer al agente a grafos circulares y aleatorios durante la misma ventana de 600 actualizaciones mejore automáticamente la cooperación fuera de la red de referencia. Dos políticas mixtas vuelven al no intercambio.",
 "",
 "## V21. Redundancia de información para reciprocidad",
 "",
 table(reptab,["Política","Completa","Sin receptor directo",
    "Sin donación pública vecinal","Sin ambos","Sin señales sociales"]),
 "",
 "Las dos políticas prolongadas retienen retorno positivo al quitar separadamente cada uno de los dos canales informativos, pero pierden ese beneficio cuando se retiran conjuntamente. [Inferencia] Resultado compatible con redundancia funcional de señales interpersonales, sin implicar una institución social plenamente interiorizada.",
 "",
 "## V22. Evaluación congelada sobre seis semillas y 144 sociedades por condición",
 "",
 "Los agentes empiezan con un único oficio, sin cuota deseada programada. El control aleatorio representa la mayor alimentación media de cuatro probabilidades de movilidad preestablecidas (0,02, 0,15, 0,35, 0,60), evaluadas en los mismos escenarios. Esta elección a posteriori del mejor control se reporta para no subestimar al azar.",
 "",
 table(roletab,["Política","Red","Alimento aprendido","Mejor aleatorio",
 "Ganancia","Enlaces complementarios","Repartos exactos"]),
 "",
 "En la red circular de grado 2, los cuatro modelos forman muchos enlaces interprofesionales y superan todos los controles aleatorios. La tasa exacta 12/12 del modelo DONOR4111_ROLE8111 supera el 96% sobre mundos independientes. En redes aleatorias también se observan ventajas frente a la movilidad aleatoria, pero son menores; en redes circulares de grado 4 una de las cuatro políticas pierde incluso frente al control aleatorio.",
 "",
 "## V22. Dependencia de la identidad y de las condiciones iniciales",
 "",
 "En el anillo original, reasignar a personas completas con sus pesos privados de donación y movilidad a nuevas posiciones reduce el rendimiento respecto al escenario conocido. La cooperación ocupacional incorpora, por tanto, componentes dependientes de identidad y topología. Desde ocupaciones iniciales aleatorias, los cuatro modelos también mejoran frente a controles de movilidad y a dejar roles fijos, aunque con menor precisión que desde un único oficio.",
 "",
 "## Incertidumbre y dependencia estadística",
 "",
 "Hay 6 clústeres ambientales de evaluación por condición y 24 mundos por clúster; no son 144 replicaciones independientes de entrenamiento. Las 4 políticas V22 solo representan 2 donantes preentrenados por 2 inicializaciones ocupacionales. Se calcularon intervalos bootstrap descriptivos sobre las seis semillas ambientales, conservando el contraste emparejado. Esos intervalos no sustituyen replicaciones entre nuevas semillas neuronales ni extrapolación a nuevas escalas N o k. Datos en METRICAS_V21_V22.json.",
 "",
 "## Próximos falsadores",
 "",
 "1. Aprendizaje simultáneo desde cero de donación y ocupación, sin policy donante preentrenada; 2. Transferencia y reaprendizaje tras pérdida de personas o reconfiguración radical de la red; 3. Escala N=120, k=4 y poblaciones heterogéneas; 4. Separar convenios locales de memorizar índices de identidad; 5. Conservar el retorno individual causal positivo al modificar canales informativos y costes.",
 "",
 "**Conclusión:** se ha simulado una organización ocupacional funcional emergente a partir de decisiones privadas de movilidad, apoyada en reciprocidad voluntaria previamente aprendida. No se declara OBJETIVO COMPLETADO en su sentido general, porque el módulo donante es preentrenado, se limita a dos profesiones y 24 agentes, y la generalización relacional presenta límites.",
 "",
 "## Recursos y hashes",
 "",
 "Checkpoints longitudinales en runs/v21_LONG_*/; modelos mixtos en runs/v21_MIX_*/; políticas ocupacionales en runs/v22_DONOR*_ROLE*/. Auditorías individuales en results/v20_allagents_v21_*.json; mecanismos en results/v21_reputation_*.json; evaluación ocupacional en results/v22_holdout_*.json. Código y preregistros disponibles en la misma carpeta.",
 "",
 "```",
 *[f"{name}: {digest}" for name,digest in hashes.items()],
 "```",
 ]
(RES/"RESULTADOS_INTEGRALES_V21_V22.md").write_text("\n".join(report),encoding="utf8")
(RES/"METRICAS_V21_V22.json").write_text(json.dumps(
 dict(v21=records21,v22=records22,bootstrap=bootstrap,sha256=hashes,
      training_agent_periods_v21_long=6*1000*16*32*24,
      training_agent_periods_v21_mixed=4*600*16*32*24,
      training_agent_periods_v22=4*600*24*48*24,
      holdout_societies_v22=4*54*6*24),indent=2),encoding="utf8")
print("SUMMARY_OK",'long',len(LONG),'mixed',len(MIX),'role',len(ROLE),
      'V22holdoutWorlds',4*54*6*24)
for r in records22:
 if r['init']=='monolith' and r['topology']=='ring' and r['degree']==2:
  b=bootstrap[f"{r['model']}|2|ring|monolith"]
  print("CI",r['model'],round(b['mean'],4),
        [round(x,4) for x in b['descriptive_bootstrap_95']])
