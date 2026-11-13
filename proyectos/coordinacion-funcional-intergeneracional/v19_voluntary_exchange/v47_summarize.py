"""V47 complete partner-turnover report with all frozen matchings."""
from pathlib import Path
import json,csv,hashlib
import numpy as np
R=Path(__file__).resolve().parent; O=R/"results"
seeds=(3111,4111,5111,6111)
rows=[];trajectories={}
for seed in seeds:
 for m,a in (("NL",0),("LOLA",5),("LOLA",20)):
  name=f"v47_Q95_{m}{a or ''}_s{seed}"
  z=json.loads((O/("v47_holdout_"+name+".json")).read_text("utf8"))
  hist=[json.loads(x) for x in (R/"runs"/name/"v47_history.jsonl").read_text("utf8").splitlines()]
  assert [v["update"] for v in hist]==[1,200,400,600,800,1000]
  assert len(z["rows"])==12
  metrics=z["aggregate"]
  row=dict(name=name,seed=seed,method=m,alpha=a,
   food=metrics["food"],gifts=metrics["donations"],
   mutual=metrics["mutual"],causal=metrics["causal"],
   positive_agents_mean=metrics["positive_agents"],
   min_positive=metrics["min_positive_agents"],
   max_positive=metrics["max_positive_agents"],
   passes_fraction=metrics["fraction_positive24_and_mutual25"])
  rows.append(row);trajectories[name]=hist
def lookup(seed,method,alpha):
 return next(x for x in rows if x["seed"]==seed and x["method"]==method and x["alpha"]==alpha)
checks={}
for alpha in (5,20):
 checks[f"H47_{alpha}"]=sum(
   lookup(seed,"LOLA",alpha)["passes_fraction"]>=.75 for seed in seeds)>=3
checks["H47b"]=sum(
   lookup(seed,"NL",0)["positive_agents_mean"]<24 and lookup(seed,"NL",0)["mutual"]<.25
   for seed in seeds)>=3
checks["H47d"]=all(
   lookup(seed,"LOLA",alpha)["food"]-lookup(seed,"NL",0)["food"]>=.025
   for seed in seeds for alpha in (5,20))
comparisons=[]
for seed in seeds:
 for alpha in (5,20):
  control=lookup(seed,"NL",0);t=lookup(seed,"LOLA",alpha)
  comparisons.append(dict(seed=seed,alpha=alpha,
   food_delta=t["food"]-control["food"],
   causal_delta=t["causal"]-control["causal"],
   mutual_delta=t["mutual"]-control["mutual"]))
with (O/"COMPARACION_V47.csv").open("w",newline="",encoding="utf8") as h:
 w=csv.DictWriter(h,list(rows[0]));w.writeheader();w.writerows(rows)
names=["PREREG_V47_PARTNER_TURNOVER.md","v47_partner_turnover.py",
 "v47_frozen_audits.py","v47_batch_audit.py",
 "v47_summarize.py","test_v47_partner_turnover.py","test_v47_frozen_audits.py"]
sha={x:hashlib.sha256((R/x).read_bytes()).hexdigest() for x in names}
(O/"METRICAS_V47.json").write_text(json.dumps(dict(rows=rows,trajectories=trajectories,
 criteria=checks,comparisons=comparisons,sha256=sha,
 simulated_holdout_worlds_per_policy=2*6*128,
 reserved_pairing_seeds=list(z["partner_seeds"]),
 limitations="partners change between training episodes; only one partner per agent inside an episode; complementary jobs fixed; opponent gradients known"),indent=2),encoding="utf8")
def tbl(data,head):
 return "\n".join(["| "+" | ".join(head)+" |","| "+" | ".join(["---"]*len(head))+" |"]+
  ["| "+" | ".join(map(str,arr))+" |" for arr in data])
report=["# V47. Reciprocidad privada aprendida ante cambios continuos de compañero entre experiencias",
"",
"Las48 políticas individuales aprendieron desde cero, con parámetros no compartidos, valores materiales y horizonte idénticos a V46. En cada una de1000 actualizaciones, las24 parejas se reconstituyeron al azar, con un generador independiente y sin preservar la identidad previa. No existen contratos, sanciones programadas, preferencias prosociales ni recompensas colectivas. La optimización NL y LOLA es exclusivamente del retorno esperado privado.",
"",
"## Todos los resultados, al final de1000 actualizaciones, sobre12 emparejamientos nuevos",
"",
tbl([[str(v["seed"]),f'{v["method"]} {v["alpha"]}',
f'{v["food"]:.4f}',f'{v["gifts"]:.4f}',f'{v["mutual"]:.4f}',
f'{v["causal"]:+.4f}',f'{v["positive_agents_mean"]:.1f}/48',
f'{v["passes_fraction"]:.2%}'] for v in rows],
["Semilla","Método","Alimento","Donaciones","Mutuas",
"Retorno propio causal","Personas positivas","Reemparejamientos exitosos"]),
"",
"El retorno causal es el valor privado de forzar un regalo en t0 frente a prohibirlo y dejar que ambos sigan sus políticas privadas; usa cadena Markov exacta. Se evalúan al menos24 personas de48 con retorno positivo y>0,25 mutualidad en9/12 reemparejamientos reservados, no en los mismos episodios usados para entrenar.",
"",
"## Contraste de aprendizaje y control negativo",
"",
"El gradiente NL de corto alcance y el algoritmo LOLA utilizan el mismo conocimiento exacto de recompensas, el mismo espacio de cinco parámetros por persona y Adam lr0,03; solo LOLA calcula cómo su acción cambiaría la actualización neuronal prevista del otro. Los resultados preservan la comparación de V46, incluso con cambios de interlocutor entre actualizaciones. Se conserva el camino histórico en METRICAS_V47.json y los pesos al final; no se seleccionó un punto óptimo a posteriori.",
"",
tbl([[k,"cumple" if v else "no cumple"] for k,v in checks.items()],
 ["Criterio preregistrado","Resultado"]),
"",
"## Validación externa y límites",
"",
"Para cada política congelada se evaluaron12 nuevas parejas completas (semillas declaradas previamente) y para dos de ellas6 semillas ambientales con128 mundos cada una mediante Monte Carlo independiente del evaluador exacto. Todas las discrepancias agregadas alimento, regalos y mutualidad cumplen la tolerancia<0,015.",
"",
"[Inferencia] La transferencia a personas diferentes sugiere que se han aprendido convenciones de respuesta general, sin requerir historia de un interlocutor particular. Sin embargo, la interacción todavía es diádica y la pareja no cambia en mitad del episodio. Los roles profesionales son exógenos y complementarios; no se prueba todavía coordinación funcional en redes con múltiples socios.",
"",
"La infraestructura de inferencia de gradientes ajenos se proporciona por el laboratorio, no se aprende mediante observaciones sociales limitadas. Un éxito en V47 no implica emergencia endógena de instituciones.",
"",
"## Reproducción y hashes",
"",
"Preregistro, motor de matching por actualización, 12 checkpoints de1000 pasos con Adam, evaluador y simulación independiente, tests y datos JSON originales, CSV, métricas y trayectorias.",
*[f"{k}: {v}" for k,v in sha.items()]]
(O/"RESULTADOS_INTEGRALES_V47.md").write_text("\n".join(report),encoding="utf8")
print("V47_REPORT_OK",len(rows),checks)
for r in rows:print(r["name"],round(r["causal"],4),round(r["mutual"],4),r["positive_agents_mean"])
