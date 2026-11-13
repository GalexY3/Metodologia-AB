"""V49 experimental summary: direct vs public reputational signal causal effects."""
from pathlib import Path
import csv,json,hashlib,numpy as np
R=Path(__file__).resolve().parent;O=R/"results"
seeds=(3111,4111,5111,6111)
methods=("NL","LOLA5","LOLA20")
rates=(.25,.60,1.)
modes=("carry","public","scrambled","public_noise20")
rows=[]
for seed in seeds:
 for method in methods:
  name=f"v47_Q95_{method}_s{seed}"
  doc=json.loads((O/f"v49_public_{name}.json").read_text("utf8"))
  assert len(doc["rows"])==12 and len(doc["seeds"])==6
  for d in doc["rows"]:
   assert len(d["by_seed_holdout"])==len(d["by_seed_causal"])==6
   assert abs(d["causal_initial"]+.04)<1e-9
   rows.append(dict(model=name,seed=seed,method=method,rate=d["rate"],
     mode=d["mode"],food=d["food"],gifts=d["gifts"],
     mutual=d["mutual"],causal=d["causal"],positive_agents=d["positive_agents"],
     partners=d["distinct_partners"]))
assert len(rows)==144
def q(seed,method,rate,mode):
 return next(x for x in rows if x["seed"]==seed and x["method"]==method and
 x["rate"]==rate and x["mode"]==mode)
checks=dict(
 h49a=sum(q(s,"LOLA20",1.,"public")["positive_agents"]>=24
  and q(s,"LOLA20",1.,"public")["mutual"]>=.25 for s in seeds)>=3,
 h49b=sum(q(s,"LOLA20",1.,"public")["causal"]-
  q(s,"LOLA20",1.,"carry")["causal"]>=.05 for s in seeds)>=3,
 h49c=sum(q(s,"LOLA20",1.,"public")["causal"]-
  q(s,"LOLA20",1.,"scrambled")["causal"]>=.05 for s in seeds)>=3,
 h49d=sum(q(s,"LOLA20",1.,"public")["causal"]-
  q(s,"LOLA20",1.,"public_noise20")["causal"]>=.015 for s in seeds)>=3)
aggregate={}
for method in methods:
 for rate in rates:
  for mode in modes:
   samples=[q(s,method,rate,mode) for s in seeds]
   aggregate[f"{method}|{rate}|{mode}"]=dict(
    food=float(np.mean([x["food"] for x in samples])),
    mutual=float(np.mean([x["mutual"] for x in samples])),
    causal=float(np.mean([x["causal"] for x in samples])),
    positive_agents=[x["positive_agents"] for x in samples])
pairs=[]
for method in methods:
 for rate in rates:
  for seed in seeds:
   p=q(seed,method,rate,"public")
   for control in ("carry","scrambled","public_noise20"):
    c=q(seed,method,rate,control)
    pairs.append(dict(method=method,rate=rate,seed=seed,
      contrast="public_minus_"+control,
      food=p["food"]-c["food"],
      mutual=p["mutual"]-c["mutual"],
      private_causal=p["causal"]-c["causal"]))
with (O/"COMPARACION_V49.csv").open("w",newline="",encoding="utf8") as f:
 w=csv.DictWriter(f,list(rows[0]));w.writeheader();w.writerows(rows)
with (O/"CONTRASTES_V49.csv").open("w",newline="",encoding="utf8") as f:
 w=csv.DictWriter(f,list(pairs[0]));w.writeheader();w.writerows(pairs)
sha_names=("PREREG_V49_PUBLIC_REPUTATION.md","v49_public_reputation.py",
 "test_v49_public_reputation.py","v49_summarize.py")
sha={k:hashlib.sha256((R/k).read_bytes()).hexdigest() for k in sha_names}
(O/"METRICAS_V49.json").write_text(json.dumps(dict(
 rows=rows,aggregates=aggregate,hypotheses=checks,contrasts=pairs,sha256=sha,
 n_models=12,n_conditions=144,n_seeds=6,
 n_holdout_paths=12*3*4*6*128,
 n_individual_t0_counterfactual_paths=12*3*4*6*8*48,
 constraints="Frozen V47 models; all observations exogenously supplied; one partner at a time and complementary occupations assigned."),indent=2),encoding="utf8")
def tbl(records,head):
 return "\n".join(["| "+" | ".join(head)+" |","| "+" | ".join(["---"]*len(head))+" |"]+
 ["| "+" | ".join(map(str,record))+" |" for record in records])
f=lambda x:f"{x:.4f}"
report=["# V49 — Reputación individual auténtica y retorno privado de cooperación con nuevos compañeros",
"",
"Evaluación causal de12 políticas congeladas V47, formadas por48 personas y24 parejas profesionales complementarias exógenas en cada ronda, con parejas cambiantes a tasas0,25/0,60/1,00 y cuatro modalidades de información. No se reentrenó ninguna política. Recompensa propia0,20+(0,55/3)×regalo recibido−0,04×regalo enviado, supervivencia q0,95, gamma0,995, horizonte máximo48 y ninguna garantía contractual, recompensa grupal o docente.",
"",
"## Resultados comparados por método y régimen de información",
"",
tbl([[method,str(rate),mode,
 f(aggregate[f"{method}|{rate}|{mode}"]["food"]),
 f(aggregate[f"{method}|{rate}|{mode}"]["mutual"]),
 f(aggregate[f"{method}|{rate}|{mode}"]["causal"]),
 ",".join(map(str,aggregate[f"{method}|{rate}|{mode}"]["positive_agents"]))]
 for method in methods for rate in rates for mode in modes],
 ["Método","Cambio de pareja/ronda","Información",
 "Alimento","Mutuas","Retorno privado t0","Positivos por semilla"]),
"",
"**Lo que cambia realmente**: carry observa la donación que realizó mi compañero de la ronda anterior (no identifica al compañero actual); public observa la última donación efectuada por la persona que ahora es mi pareja, incluso si se hizo a otra persona; scrambled observa la última donación de otra persona de la misma clase ocupacional, con tasa marginal de donación similar pero atribuida incorrectamente; public_noise20 observa la señal individual real invertida con un error independiente del20%. Las reglas materiales y los pesos privados no varían entre estos escenarios.",
"",
"## Contrastes preregistrados bajo rotación total r1",
"",
tbl([[str(seed),method,
 f(q(seed,method,1.,"public")["causal"]-q(seed,method,1.,"carry")["causal"]),
 f(q(seed,method,1.,"public")["causal"]-q(seed,method,1.,"scrambled")["causal"]),
 f(q(seed,method,1.,"public")["causal"]-q(seed,method,1.,"public_noise20")["causal"])]
 for method in ("LOLA20","LOLA5","NL") for seed in seeds],
 ["Semilla","Método","Δ público−carry","Δ público−atribuido falso","Δ público−ruido20"]),
"",
"## Hipótesis fijadas antes de evaluación",
"",
tbl([[key,"cumple" if value else "falsada"] for key,value in checks.items()],
 ["Hipótesis","Resultado"]),
"",
"## Inferencia causal y validez",
"",
"Seis semillas ambientales independientes de entrenamiento,128 mundos por semilla para alimento/mutualidad y8 para el contraste forzar vs no forzar la primera donación individual, evaluando las48 personas en cada mundo. En cada pareja de intervenciones se reutilizaron exactamente las vidas de la sociedad, la identidad de parejas en cada ronda, las muestras uniformes para todas las decisiones libres, las fuentes aleatorias de atribución y la máscara de ruido. La diferencia alimentaria inmediata del donante es siempre−0,04. Los valores personales futuros recogen las reacciones condicionadas de futuros compañeros, y la estimación primaria de efecto propio está emparejada.",
"",
"Una sociedad puede tener prácticamente idéntico volumen de donaciones bajo public y scrambled, pero diferentes retornos causales privados: el registro correcto permite que la conducta de un individuo sea reconocida por nuevos compañeros. [Inferencia] Esto es consistente con un mecanismo de reciprocidad indirecta mediada por reputación, pero hay que distinguirlo de una norma reputacional inventada por los agentes.",
"",
"## Limitaciones",
"",
"El medio de publicidad de la conducta es **exógeno** y completamente fiel salvo el brazo explícito con ruido. Los agentes ya disponen de políticas entrenadas previamente bajo gradientes exactos de aprendizaje ajeno, y no se reentrenan con estos canales. Se mantiene una contraparte por ronda y especialidades complementarias asignadas exógenamente. No se demuestra emergencia de un sistema reputacional, de ocupaciones ni instituciones; el resultado identifica un mecanismo de información en un laboratorio restringido.",
"",
"## Reproducibilidad",
"",
"Preregistro, código v49_public_reputation.py, casos mecánicos test_v49_public_reputation.py, resultados JSON de las12 políticas y144 condiciones, CSV y matriz de contrastes, SHA256:",
*[f"{k}: {v}" for k,v in sha.items()]]
(O/"RESULTADOS_INTEGRALES_V49.md").write_text("\n".join(report),encoding="utf8")
print("V49_REPORT_OK",len(rows),checks)
