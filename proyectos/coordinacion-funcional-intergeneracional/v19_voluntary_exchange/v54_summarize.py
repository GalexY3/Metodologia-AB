"""V54 preregistered analysis: k=2..12 fixed N120, matched policies & seeds."""
from __future__ import annotations
import csv,hashlib,json,math
from pathlib import Path
import numpy as np
from v54_k_scaling import ROOT,N,KS,H,CONTROLS,TECHS
from v54_frozen_audits import SEEDS,INIT
OUT=ROOT/"results"
MODELS=[(k,method,dseed,rseed)
 for k in KS for method in ("LOLA20","NL")
 for dseed,rseed in ((3111,7111),(4111,8111))]
assert len(MODELS)==32
def load(p):return json.loads(Path(p).read_text(encoding="utf8"))
def model_name(k,method,dseed,rseed):
 return f"v54_K{k}_{method}_D{dseed}_R{rseed}"
summaries=[];trajectory={};rawdata={}
for k,method,dseed,rseed in MODELS:
 name=model_name(k,method,dseed,rseed)
 folder=ROOT/"runs"/name
 status=load(folder/"v54_status.json")
 spec=load(folder/"v54_spec.json")
 report=load(OUT/f"v54_holdout_{name}.json")
 assert status["state"]=="completed" and spec["updates"]==status["updates"]==1400
 assert spec["n"]==120 and spec["k"]==k and spec["role_seed"]==rseed
 assert spec["method"]==method and spec["donor_seed"]==dseed
 assert len(report["rows"])==2*3*6==36
 assert list(report["seeds"])==list(SEEDS)
 history=[json.loads(line) for line in (folder/"v54_history.jsonl").read_text(encoding="utf8").splitlines()]
 assert [x["update"] for x in history]==[1,200,400,600,800,1000,1200,1400]
 trajectory[name]=history
 rawdata[name]=report["rows"]
 def find(init,tech,base):
  candidates=[r for r in report["rows"] if
   r["init"]==init and r["technology"]==tech and r["baseline"]==base]
  assert len(candidates)==1
  return candidates[0]
 for init in INIT:
  score=find(init,"ELASTIC","learned")
  fixed3=find(init,"FIXED3","learned")
  price=find(init,"PER_LINK04","learned")
  oracle=find(init,"ELASTIC","oracle_roles")
  rand=[find(init,"ELASTIC",r) for r in CONTROLS if r.startswith("random_")]
  best=max(rand,key=lambda x:x["food"])
  for r in report["rows"]:
   if k>=5 and r["technology"]=="FIXED3":
    assert r["full"]<=3/(k-1)+1e-6
  row=dict(name=name,k=k,method=method,donor_seed=dseed,role_seed=rseed,init=init,
    learned_food=score["food"],learned_full=score["full"],
    learned_terminal_role_balance=score["terminal_balance"],
    learned_temporal_role_balance=score["group_complete"],
    learned_gifts_per_link=score["gifts_per_link"],
    learned_gifts_per_person=score["gifts_per_person"],
    learned_coverage=score["coverage"],
    learned_moves_per_person=score["move_per_person"],
    oracle_role_food=oracle["food"],
    regret_to_oracle=oracle["food"]-score["food"],
    best_random_role_food=best["food"],
    best_random_role_balance=best["terminal_balance"],
    advantage_over_best_random=score["food"]-best["food"],
    fixed3_food=fixed3["food"],fixed3_full=fixed3["full"],
    fixed3_terminal_role_balance=fixed3["terminal_balance"],
    fixed3_gifts_per_person=fixed3["gifts_per_person"],
    perlink04_food=price["food"],perlink04_full=price["full"],
    occupancy_random_probability=math.factorial(k)/(k**k))
  summaries.append(row)
def rows_for(k,method,init="monolith"):
 return [r for r in summaries if r["k"]==k and r["method"]==method and r["init"]==init]
h={}
h["h54a_six_of_eight_k_both_seeds_high_balance_food"]=sum(
  all(r["learned_terminal_role_balance"]>=.8 and r["learned_food"]>=.65
      for r in rows_for(k,"LOLA20"))
  for k in KS)>=6
h["h54b_at_least_one_k_ge8_below_80_percent"]=any(
   r["learned_terminal_role_balance"]<.8 for r in summaries
   if r["k"]>=8 and r["method"]=="LOLA20" and r["init"]=="monolith")
h["h54c_six_of_eight_k_both_seeds_gain_10pct"]=sum(
 all(r["advantage_over_best_random"]>=.10 for r in rows_for(k,"LOLA20"))
 for k in KS)>=6
h["h54d_all_nl_food_below_0_30"]=all(
 r["learned_food"]<=.30 for r in summaries
 if r["method"]=="NL")
h["h54e_fixed3_conservation_bound_valid"]=all(
 r["fixed3_full"]<=3/(r["k"]-1)+1e-6 for r in summaries if r["k"]>=5)
with (OUT/"COMPARACION_V54.csv").open("w",newline="",encoding="utf8") as handle:
 writer=csv.DictWriter(handle,list(summaries[0]));writer.writeheader();writer.writerows(summaries)
sha_names=("PREREG_V54_K_SCALING.md","v54_k_scaling.py",
 "v54_frozen_audits.py","v54_summarize.py",
 "test_v54_k_scaling.py","test_v54_frozen_audits.py")
sha={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in sha_names}
(OUT/"METRICAS_V54.json").write_text(json.dumps(dict(
 rows=summaries,hypotheses=h,trajectories=trajectory,raw_per_environment=rawdata,
 source_sha256=sha,neural_training_runs=32,total_training_updates=32*1400,
 fixed_population=120,heldout_environment_seeds=SEEDS,
 total_frozen_cells=32*2*3*6,worlds_per_seed=24,
 n_frozen_environment_worlds=32*2*3*6*6*24,
 caveat="LOLA donation policies pretrained on N48, resampled to 120 and frozen; learning only own occupational policy in external Kk teams; resource technology grows with k."),indent=2),encoding="utf8")
def tbl(rows,headers):
 return "\n".join(["| "+" | ".join(headers)+" |",
 "| "+" | ".join(["---"]*len(headers))+" |"]+
 ["| "+" | ".join(map(str,row))+" |" for row in rows])
def fmt(x):return f"{x:.4f}"
report=[
 "# V54 — Generalización de la especialización profesional de k=2 a k=12",
 "",
 "## Alcance de la prueba",
 "",
 "**32 entrenamientos neuronales** desde actores profesionales privados inicializados de cero (N120, exactamente igual en todos), con ocho k∈{2,3,4,5,6,8,10,12}, dos condiciones de dones preaprendidos (LOLA20 y NL) y dos semillas independientes (3111/7111 y4111/8111). Todos entrenan1400 actualizaciones, lote12, horizonte48, decisión ocupacional cada8 rondas, coste de cambio0,015 y recompensa exclusivamente alimentaria individual con REINFORCE, Adam0,003 y entropía0,01. Todos los actores ocupacionales tienen pesos diferentes por persona; **los regalos están congelados**, transferidos de los modelos V47 entrenados en 48 personas. Todos los agentes pueden elegir cualquiera de k profesiones. No existen cuotas ni recompensa por formar un grupo completo.",
 "",
 "La topología es externa y favorable: **120/k grupos cliques Kk**, de tamaño y grado k−1. N es constante, pero la conectividad y el número de opciones cambian necesariamente con k. La MLP de ocupaciones contiene un vector de información de dimensión2k+3 y salida de k opciones; el presupuesto de parámetros neuronales no es idéntico entre k. Estos factores limitan la atribución del efecto exclusivamente al tamaño de k.",
 "",
 "## Progreso de especialización y comida por k, inicio monolítico",
 "",
 tbl([[k,str(seed),method,
 fmt(next(r for r in rows_for(k,method) if r["donor_seed"]==seed)["learned_terminal_role_balance"]),
 fmt(next(r for r in rows_for(k,method) if r["donor_seed"]==seed)["learned_food"]),
 fmt(next(r for r in rows_for(k,method) if r["donor_seed"]==seed)["learned_full"]),
 fmt(next(r for r in rows_for(k,method) if r["donor_seed"]==seed)["advantage_over_best_random"])]
 for k in KS for method in ("LOLA20","NL") for seed in (3111,4111)],
 ["k","Donante semilla","Donante","Balance terminal",
 "Alimento medio","Cesta completa","Ventaja sobre mejor aleatorio"]),
 "",
 "### Benchmark azar y comparación material",
 "",
 tbl([[k,f"{100*math.factorial(k)/(k**k):.6f}%",
  fmt(float(np.mean([r["learned_food"] for r in rows_for(k,"LOLA20")]))),
  fmt(float(np.mean([r["oracle_role_food"] for r in rows_for(k,"LOLA20")]))),
  fmt(float(np.mean([r["fixed3_food"] for r in rows_for(k,"LOLA20")]))),
  fmt(float(np.mean([r["fixed3_full"] for r in rows_for(k,"LOLA20")]))),
  fmt(float(np.mean([r["perlink04_food"] for r in rows_for(k,"LOLA20")])))]
 for k in KS],["k","Equipos perfectos por azar i.i.d.",
 "Aprendida elástica","Oráculo roles","FIXED3 comida",
 "FIXED3 cesta completa","Coste 0,04 por vínculo comida"]),
 "",
 "La probabilidad de equilibrio casual para k personas y k profesiones elegidas independientemente con probabilidad uniforme es k!/k^k. El benchmark ORACLE_ROLES fija externamente una asignación perfecta y únicamente se usa al evaluar para comparar el alimento: nunca participa en los gradientes ni crea el aprendizaje.",
 "",
 "La tecnología de entrenamiento **ELASTIC** incrementa la capacidad potencial de ofrecer regalos con k, pero normaliza el coste total de regalar a todos los k−1 vecinos a0,12. Recompensa=0,20+0,55×tipos recibidos/(k−1)+0,25×I(cesta completa)−0,12/(k−1)×regalos entregados−0,015×cambio de oficio. Máximo de intercambio universal 0,88 para todos los k. Con k4 el pago coincide con la fórmula de V25/V51.",
 "",
 "Se evaluaron las mismas políticas profesionales y donantes congelados con dos alternativas tecnológicas. **FIXED3** solo admite tres entregas por trabajador y ronda, pagando0,04 por unidad; cuando k≥5 no pueden recibir todos una cesta completa simultáneamente, aunque algunos sí, con cota de cobertura plena≤3/(k−1). **PER_LINK04** permite k−1 regalos pero cada uno cuesta0,04, lo que hace crecer el coste total al aumentar k. Son contrafactuales fuera de distribución; las redes NO fueron reentrenadas para ellos.",
 "",
 "## Contrastes preregistrados",
 "",
 tbl([[key,"cumple" if flag else "falsada"] for key,flag in h.items()],
 ["Hipótesis","Resultado"]),
 "",
 "H54a exige al menos6 de8 valores k con ambas semillas LOLA20 con≥80% grupos profesionales completos y alimento≥0,65. H54b predecía una frontera de fracaso para al menos un k≥8: si no se observa se reporta falsada, sin ajustar los criterios. H54c pide ventaja alimentaria≥0,10 frente al mejor cambio ocupacional aleatorio en al menos6 k y ambas semillas. H54d pide alimento≤0,30 para todos los controles NL. H54e comprueba conservación de capacidad3, no ausencia absoluta de cestas completas.",
 "",
 "## Interpretación de mecanismos y reservas",
 "",
 "[Inferencia] La existencia de una política privada que dona a sus vecinos con probabilidad elevada hace que ocupar una especialidad faltante proporcione beneficio propio, lo cual genera incentivos para la diferenciación laboral. El número k por sí solo puede alargar el período de descubrimiento y reducir la probabilidad de configuración óptima accidental, sin volverla inaccesible bajo determinadas tecnologías y horizontes.",
 "",
 "El actor profesional observa la distribución de ocupaciones de sus vecinos y conoce su propia comida. Los modelos generaron las especialidades desde ocupaciones monolíticas y aleatorias. Sin embargo, los vecinos ya están organizados en cliques del tamaño exacto k y se heredan las estrategias de cooperación LOLA20; no se ha demostrado una elección espontánea del tamaño de los grupos, creación de vínculos, cooperación desde cero ni una población abierta que decida cuántas profesiones necesita realmente.",
 "",
 "## Protocolo de evaluación y reproducibilidad",
 "",
 "El checkpoint final u1400 se evaluó con seis semillas ambientales reservadas999201/207/209/221/231/237,24 mundos por semilla, dos estados iniciales (monolito,aleatorio), tres tecnologías y seis políticas de movilidad de oficios (aprendida, inmóvil,3 aleatorias y oráculo). No se seleccionaron los checkpoints de rendimiento máximo durante entrenamiento. Se conservan los historiales u1,200,400,600,800,1000,1200,1400, especificaciones por modelo, pesos y Adam, resultados completos por semilla y escena, CSV y JSON.",
 "",
 "El experimento responde a escalado de k dentro de una clase de economías, no a una ley universal de formación de profesiones. La diferencia entre política neuronal aprendida y mejor respuesta exacta también deberá estudiarse por separado, como hace el control mecanístico V54B.",
 "",
 "## Código e integridad",
 *[f"{file}: {hashval}" for file,hashval in sha.items()]]
(OUT/"RESULTADOS_INTEGRALES_V54.md").write_text("\n".join(report),encoding="utf8")
print("V54_REPORT_OK",len(summaries),"models",len(MODELS),"hypotheses",h)
for k in KS:
 x=rows_for(k,"LOLA20")
 print("k",k,"learnedfood",[round(v["learned_food"],4) for v in x],
  "terminalbalance",[round(v["learned_terminal_role_balance"],4) for v in x],
  "capacity3full",[round(v["fixed3_full"],4) for v in x])
