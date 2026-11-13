"""V48 complete results and preregistered falsifiers."""
from pathlib import Path
import json,csv,hashlib,numpy as np
ROOT=Path(__file__).resolve().parent; OUT=ROOT/"results"
SEEDS=(3111,4111,5111,6111)
MODELS=("NL","LOLA5","LOLA20")
rows=[]
for seed in SEEDS:
 for method in MODELS:
  name=f"v47_Q95_{method}_s{seed}"
  z=json.loads((OUT/f"v48_dynamic_{name}.json").read_text("utf8"))
  assert len(z["rows"])==10 and len(z["seeds"])==6
  for r in z["rows"]:
   assert len(r["by_seed_holdout"])==len(r["by_seed_causal"])==6
   assert abs(r["causal_initial"]+.04)<1e-9
   rows.append(dict(model=name,seed=seed,method=method,
    rate=r["rate"],memory=r["memory"],food=r["food"],
    gifts=r["gifts"],mutual=r["mutual"],
    causal=r["causal"],positive_agents=r["positive_agents"],
    distinct_partners=r["distinct_partners"],
    causal_future=r["causal_future"],active_rounds=r["mean_lifetime"]))
assert len(rows)==120
def get(seed,method,rate,memory="carry"):
 return next(x for x in rows if x["seed"]==seed and x["method"]==method
  and x["rate"]==rate and x["memory"]==memory)
h=dict(
 h48a=sum(get(s,"LOLA20",.25)["positive_agents"]>=24
  and get(s,"LOLA20",.25)["mutual"]>=.25 for s in SEEDS)>=3,
 h48b=sum(get(s,"LOLA20",1.)["positive_agents"]>=24
  and get(s,"LOLA20",1.)["mutual"]>=.25 for s in SEEDS)>=3,
 h48c=sum(get(s,"LOLA20",.60,"carry")["causal"]-
  get(s,"LOLA20",.60,"reset")["causal"]>=.025 for s in SEEDS)>=3,
 h48d=all(get(s,"NL",rate)["positive_agents"]<24
 for s in SEEDS for rate in (0.,.60)))
with (OUT/"COMPARACION_V48.csv").open("w",encoding="utf8",newline="") as fh:
 w=csv.DictWriter(fh,list(rows[0]));w.writeheader();w.writerows(rows)
sources=("PREREG_V48_WITHIN_EPISODE_REMATCHING.md",
 "v48_within_episode_rewire.py","test_v48_dynamic_rewire.py","v48_summarize.py")
sha={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in sources}
group={}
for method in MODELS:
 for memory in ("carry","reset"):
  for rate in (0.,.05,.25,.6,1.):
   sub=[get(s,method,rate,memory) for s in SEEDS]
   group[f"{method}|{memory}|{rate}"]=dict(
    food=float(np.mean([x["food"] for x in sub])),
    mutual=float(np.mean([x["mutual"] for x in sub])),
    causal=float(np.mean([x["causal"] for x in sub])),
    positive_agents=[x["positive_agents"] for x in sub],
    distinct_partners=float(np.mean([x["distinct_partners"] for x in sub])))
(OUT/"METRICAS_V48.json").write_text(json.dumps(dict(
 rows=rows,group=group,hypotheses=h,sha256=sha,
 n_checkpoints=12,n_treatment_scenarios=120,
 n_holdout_world_paths=12*10*6*128,
 n_individual_t0_counterfactual_paths=12*10*6*8*48,
 n_heldout_seeds=6,
 scope="Frozen V47 policies, one new partner per round max, roles externally complementary; no dynamic retraining"),indent=2),encoding="utf8")
def tbl(rows,head):
 return "\n".join(["| "+" | ".join(head)+" |","| "+" | ".join(["---"]*len(head))+" |"]+
  ["| "+" | ".join(map(str,x))+" |" for x in rows])
f=lambda x:f"{x:.4f}"
report=["# V48 — Límites de reciprocidad al cambiar de compañero durante el episodio",
"",
"Doce checkpoints congelados V47 (NL, LOLA5, LOLA20 × cuatro semillas), cinco probabilidades de cambiar todo el emparejamiento bipartito entre rondas (0,0,05,0,25,0,60,1), dos regímenes de memoria (señal de antigua contraparte retenida o anulada cuando cambia). Se mantienen48 personas, 24 parejas profesionales complementarias en cada ronda, v0,55/3, c0,04, q0,95, máximo48 rondas, sin recompensas sociales, contratos, enseñanza, reentrenamiento ni selección posterior de políticas. La política da una donación unilateral al compañero actual, no al anterior.",
"",
"## Resultado central por tasa de cambio y método",
"",
tbl([[method,str(rate),memory,
 f(group[f"{method}|{memory}|{rate}"]["food"]),
 f(group[f"{method}|{memory}|{rate}"]["mutual"]),
 f(group[f"{method}|{memory}|{rate}"]["causal"]),
 ",".join(map(str,group[f"{method}|{memory}|{rate}"]["positive_agents"])),
 f(group[f"{method}|{memory}|{rate}"]["distinct_partners"])]
 for method in MODELS for rate in (0.,.05,.25,.6,1.) for memory in ("carry","reset")],
 ["Método","Reemparejar/ronda","Memoria","Comida","Mutualidad",
  "Retorno privado t0","Positivos por semilla","Contactos distintos"]),
"",
"## Hipótesis preregistradas",
"",
tbl([[key,"cumple" if value else "falsada"] for key,value in h.items()],
 ["Hipótesis","Resultado"]),
"",
"H48b, que exigía reciprocidad individualmente rentable bajo reemparejamiento total y memoria carry, queda falsada aunque los mismos actores sostengan un nivel alto de cooperación observada. H48c exigía diferencia≥0,025 por la señal carry frente a reset en r0,60, y no se cumple: la retención de señales anteriores no basta por sí sola para restaurar incentivos individuales.",
"",
"## Diseño causal",
"",
"En cada condición se simularon seis semillas ambientales reservadas con128 mundos para alimento/mutualidad y8 mundos para intervención individual. En cada mundo se crearon48 ramas por separado (una por individuo), con propuestas originales o forzadas en el primer turno. Para cada par de ramas se mantuvieron **exactamente iguales** el calendario de supervivencia, los emparejamientos de todos los turnos y las mismas muestras de uniformes para todas las decisiones libres posteriores. La primera donación tiene coste material−0,04 para el actor intervenido, y el retorno descontado propio evalúa el efecto sobre conductas futuras ajenas. La interpretación del promedio entre individuos se condiciona a las cuatro inicializaciones neuronales.",
"",
"## Interpretación",
"",
"[Inferencia] Las reglas conductuales de reciprocidad condicional pueden mantener bienes circulando incluso cuando los beneficios de una contribución ya no revierten hacia su autor. Esto distingue cooperación material colectiva de cooperación que constituye una mejor respuesta privada. Bajo relaciones nuevas en cada turno, contribuir puede ayudar a un compañero que a su vez donará a otro: la reciprocidad se convierte en externalidad difusa y el incentivo individual se debilita.",
"",
"El experimento no prueba que nuevas políticas, entrenadas directamente bajo cambio intraperíodo, hubieran aprendido lo mismo; solo mide transferencia congelada. Tampoco incluye más de una contraparte simultánea ni elección endógena de profesión. La condición de memoria carry arrastra la última conducta observada desde la relación anterior, por lo que no identifica públicamente al autor original de esa donación.",
"",
"## Reproducción",
"",
"El preregistro fijó exactamente las tasas, las semillas ambientales994101/107/109/121/131/137, las políticas y los criterios. Código v48_within_episode_rewire.py, tests test_v48_dynamic_rewire.py, todos los datos originales results/v48_dynamic_v47_Q95_*.json, CSV y JSON de métricas y este informe. Hashes:",
*[f"{s}: {hashval}" for s,hashval in sha.items()]]
(OUT/"RESULTADOS_INTEGRALES_V48.md").write_text("\n".join(report),encoding="utf8")
print("V48_REPORT_OK",len(rows),h)
