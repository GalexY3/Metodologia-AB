"""V44 preregistered evaluation of dyadic reciprocity learned from scratch.

All network parameters independent per individual; no pretrained contracts,
enforced punishment or group rewards. Six *new* heldout seeds after amendment.
"""
from __future__ import annotations
import csv,json,hashlib
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent;OUT=ROOT/"results"
NAMES=[f'v44_{length}_{signal}_s{seed}' for seed in (3111,4111)
 for length in ("SHORT","LONG") for signal in ("SOC","NOSOC")]
def read(p):return json.loads(p.read_text("utf8"))
def f(x):return f"{x:.4f}"
def sign(x):return f"{x:+.4f}"
def table(rows,heads):
 return "\n".join(["| "+" | ".join(heads)+" |",
 "| "+" | ".join(["---"]*len(heads))+" |"]+
 ["| "+" | ".join(map(str,row))+" |" for row in rows])
rows=[];trajectories={};byseed={}
for name in NAMES:
 folder=ROOT/"runs"/name
 spec=read(folder/"v44_spec.json")
 status=read(folder/"v44_status.json")
 assert status["state"]=="completed" and status["updates"]==spec["updates"]==1000
 held=read(OUT/("v44_holdout_"+name+".json"))
 ca=read(OUT/("v44_causal_"+name+".json"))
 assert len(held["by_seed"])==len(ca["by_seed"])==6
 assert len(held["seeds"])==len(ca["seeds"])==6
 assert set(held["seeds"])=={980101,980107,980109,980121,980131,980137}
 history=[json.loads(z) for z in (folder/"v44_history.jsonl").read_text().splitlines()]
 assert [z["update"] for z in history]==[1,200,400,600,800,1000]
 x=held["metrics"];sensitivity=held["sensitivity"]
 assert ca["mean_immediate"]==ca["mean_immediate"] and abs(ca["mean_immediate"]+.04)<1e-5
 if spec["partner_info"]=="no":assert sensitivity["mean"]==0
 trajectories[name]=history
 byseed[name]=dict(held=held["by_seed"],causal=ca["by_seed"])
 r=dict(model=name,seed=spec["seed"],q=spec["q"],
  partner_information=spec["partner_info"]=="yes",
  food=x["food"],donations=x["gifts"],mutual=x["mutual"],
  active_lifetime=x["lifetime"],causal=ca["mean_total"],
  causal_immediate=ca["mean_immediate"],
  causal_future=ca["mean_future"],
  positive_agents=ca["positive_agents"],
  behavioral_response_to_partner=sensitivity["mean"],
  positive_response_agents=sensitivity["positive"],
  learned_food_u1=history[0]["development"]["food"],
  learned_food_u200=history[1]["development"]["food"],
  learned_food_u400=history[2]["development"]["food"],
  learned_food_u600=history[3]["development"]["food"],
  learned_food_u800=history[4]["development"]["food"],
  learned_food_u1000=history[5]["development"]["food"])
 rows.append(r)
by={r["model"]:r for r in rows}
comp=[]
for seed in (3111,4111):
 for horizon in ("SHORT","LONG"):
  social=by[f"v44_{horizon}_SOC_s{seed}"]
  no=by[f"v44_{horizon}_NOSOC_s{seed}"]
  comp.append(dict(seed=seed,contrast=horizon+"_social_minus_nosocial",
    food=social["food"]-no["food"],
    donations=social["donations"]-no["donations"],
    mutual=social["mutual"]-no["mutual"],
    causal=social["causal"]-no["causal"]))
 for info in ("SOC","NOSOC"):
  long=by[f"v44_LONG_{info}_s{seed}"]
  short=by[f"v44_SHORT_{info}_s{seed}"]
  comp.append(dict(seed=seed,contrast=info+"_long_minus_short",
    food=long["food"]-short["food"],
    donations=long["donations"]-short["donations"],
    mutual=long["mutual"]-short["mutual"],
    causal=long["causal"]-short["causal"]))
socs=[by[f"v44_LONG_SOC_s{seed}"] for seed in (3111,4111)]
criteria=dict(
 h44a=any(r["causal"]>0 and r["positive_agents"]>=24 and r["mutual"]>.25
   for r in socs),
 h44b=all(by[f"v44_LONG_SOC_s{seed}"]["mutual"]>by[f"v44_LONG_NOSOC_s{seed}"]["mutual"]
   and by[f"v44_LONG_SOC_s{seed}"]["causal"]>by[f"v44_LONG_NOSOC_s{seed}"]["causal"]
   for seed in (3111,4111)),
 h44c=all(r["positive_agents"]<24 for r in rows if r["q"]==.2))
with (OUT/"COMPARACION_V44.csv").open("w",newline="",encoding="utf8") as fh:
 w=csv.DictWriter(fh,list(rows[0]));w.writeheader();w.writerows(rows)
with (OUT/"CONTRASTES_V44.csv").open("w",newline="",encoding="utf8") as fh:
 w=csv.DictWriter(fh,list(comp[0]));w.writeheader();w.writerows(comp)
hashnames=("PREREG_V44_DYADIC_RECIPROCITY.md",
 "AMENDMENT_V44_HELDOUT_SEEDS.md","v44_private_dyads.py",
 "v44_frozen_audits.py","v44_summarize.py","test_v44_dyads.py",
 "test_v44_causal.py")
sha={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in hashnames}
(OUT/"METRICAS_V44.json").write_text(json.dumps(dict(
 models=rows,contrasts=comp,criteria=criteria,sha256=sha,
 trajectories=trajectories,by_seed=byseed,
 max_training_person_rounds=8*1000*16*48*48,
 heldout_environment_seeds=6,
 heldout_worlds_per_environment=32,
 causal_worlds_per_environment=8),indent=2),encoding="utf8")
report=[
 "# V44. ¿Aprenden los individuos a devolver favores en relaciones repetidas sin contratos?",
 "",
 "Ocho entrenamientos privados REINFORCE independientes desde cero de 48 actores con parámetros no compartidos, organizados en24 parejas profesionales complementarias fijas. No existe contrato, intercambio condicional material, maestro, recompensa grupal ni norma de reciprocidad programada. Cada individuo puede donar o rechazar una sola unidad unilateral en cada turno. Pago propio =0,20+0,55/3×recibe−0,04×envía. Experimento factorial q0,20 (relación corta) vs q0,95 (larga), con vs sin información del regalo previo del compañero, dos semillas neuronales por celda, 1000 actualizaciones.",
 "",
 "Se conservan los mismos valores materiales del componente simple de V25 y el planteamiento oracular de V42, pero V44 examina el aprendizaje real de conductas condicionadas, no el equilibrio supuesto de una norma ya conocida.",
 "",
 "## Prueba final fuera de muestra",
 "",
 table([[r["model"],str(r["q"]),"sí" if r["partner_information"] else "no",
 f(r["food"]),f(r["donations"]),f(r["mutual"]),
 sign(r["causal"]),f'{r["positive_agents"]}/48',
 sign(r["behavioral_response_to_partner"]),str(r["positive_response_agents"])]
 for r in rows],
 ["Modelo","Continuidad","Ve pasado otro","Alimento",
 "Fracción regalos","Fracción reciprocidad mutua",
 "Retorno causal regalar","Agentes positivos",
 "Sensibilidad a regalo previo","Sensibilidad positiva (n)"]),
 "",
 "El ensayo final reevalúa los checkpoints u1000 sobre seis semillas nuevas (980101,980107,980109,980121,980131,980137), 32 mundos por semilla para alimento y8 para el experimento causal de cada persona. La **enmienda explícita** AMENDMENT_V44_HELDOUT_SEEDS.md reemplaza las semillas inicialmente propuestas porque algunas fueron consultadas en desarrollo durante el entrenamiento. Ninguno de los ocho modelos se selecciona por rendimiento intermedio.",
 "",
 "## Contrastes preregistrados y causalidad",
 "",
 table([[r["contrast"],str(r["seed"]),sign(r["food"]),
 sign(r["donations"]),sign(r["mutual"]),sign(r["causal"])] for r in comp],
 ["Contraste","Semilla neuronal","Δ comida","Δ regalos",
 "Δ regalos mutuos","Δ retorno causal"]),
 "",
 "El efecto causal impone únicamente el regalo del individuo sujeto en t0, manteniendo libre al compañero y dejando que ambos aprendidos reaccionen durante el resto del episodio. Los calendarios de supervivencia de cada mundo y la aleatoriedad neuronal se emparejan en los dos brazos. Se presenta ganancia propia futura descontada y contribución inmediata -0,04: aunque una sociedad reciba algo más de alimento, contribuir podría seguir perjudicando a quien lo hace.",
 "",
 "La variable de sensibilidad conductual mantiene fijos regalo propio previo y alimento previo, modifica solamente la señal de que el otro regaló en la ronda anterior, y mide variación de probabilidad neuronal de donar. Es un contraste de política bajo observaciones controladas, no efecto causal longitudinal por sí solo. Si es negativa, el actor es menos generoso al observar que su pareja donó antes, lo cual contradice una reciprocidad positiva simple.",
 "",
 "## Hipótesis",
 "",
 table([[k,"cumple" if v else "no cumple"] for k,v in criteria.items()],
 ["Criterio preregistrado","Resultado"]),
 "",
 "H44a requería ≥24 individuos privados causalmente positivos y ≥25% de donación mutua en al menos un modelo de relación larga con observación social. H44b exigía que ambas políticas de relación larga con señal del otro superasen sus controles sin señal en tasa de mutuo regalo y retorno causal. H44c predecía que ninguna de las relaciones muy breves (q0,20) conseguiría ≥24 individuos con retorno privado positivo.",
 "",
 "## Interpretación y límites",
 "",
 "[Inferencia] Una relación duradera ofrece oportunidades materiales de reciprocidad, pero por sí sola no obliga a que el aprendizaje distribuido descubra un mecanismo de respuesta contingente beneficioso. La diferencia respecto a V42 es explícita: aquel experimento imponía una norma contrafactual idealizada; V44 no la contiene y solo recompensa comida propia.",
 "",
 "Las24 parejas, oficios complementarios y disponibilidad de observar el regalo anterior están fijados externamente. Por ello incluso una eventual coordinación exitosa no demostraría división ocupacional endógena ni origen autónomo de instituciones. Solo dos semillas neuronales por tratamiento y seis ambientales para la prueba final; no extrapolar a todas las sociedades.",
 "",
 "## Reproducción y SHA256",
 "",
 "Scripts v44_private_dyads.py y v44_frozen_audits.py, tests test_v44_dyads.py y test_v44_causal.py, inicializaciones y estados finales de Adam runs/v44_*, datos originales results/v44_{holdout,causal}_*.json, CSV/JSON agregados y preregistro con enmienda.",
 *[f'{k}: {v}' for k,v in sha.items()]]
(OUT/"RESULTADOS_INTEGRALES_V44.md").write_text("\n".join(report),encoding="utf8")
print("V44_REPORT_OK",len(rows),criteria)
for r in rows:
 print(r["model"],"food",round(r["food"],4),
 "mutual",round(r["mutual"],4),
 "causal",round(r["causal"],4),
 "positive",r["positive_agents"])
