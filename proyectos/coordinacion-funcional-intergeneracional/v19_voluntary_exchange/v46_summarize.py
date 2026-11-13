"""V46 reproducible aggregate report across 36 exact-gradient populations."""
from __future__ import annotations
import csv,hashlib,json,statistics
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent;OUT=ROOT/"results"
SEEDS=(3111,4111,5111,6111)
TREATMENTS=[(q,method,alpha,seed)
 for q,groups,seeds in (
 (.95,[("NL",0),("LOLA",1),("LOLA",5),("LOLA",20),
    ("LOOK",1),("LOOK",5),("LOOK",20)],SEEDS),
 (.2,[("NL",0),("LOLA",1),("LOLA",5),("LOLA",20)],SEEDS[:2]))
 for method,alpha in groups for seed in seeds]
assert len(TREATMENTS)==36
def name(q,method,alpha,seed):
 return f"v46_{'Q95' if q==.95 else 'Q20'}_{method}{alpha or ''}_s{seed}"
def read(p):return json.loads(p.read_text(encoding="utf8"))
def f(x):return f"{x:.4f}"
def plus(x):return f"{x:+.4f}"
def table(rows,columns):
 return "\n".join(["| "+" | ".join(columns)+" |",
 "| "+" | ".join(["---"]*len(columns))+" |"]+
 ["| "+" | ".join(map(str,row))+" |" for row in rows])
rows=[];curves={};validation={}
for q,method,alpha,seed in TREATMENTS:
 key=name(q,method,alpha,seed)
 path=ROOT/"runs"/key
 assert read(path/"v46_status.json")["state"]=="completed",key
 data=read(OUT/("v46_audit_"+key+".json"))
 spec=data["spec"];out=data["analytic"]
 assert spec["q"]==q and spec["method"]==method and spec["alpha"]==alpha
 history=[json.loads(line) for line in (path/"v46_history.jsonl").read_text().splitlines()]
 assert [h["update"] for h in history]==[1,200,400,600,800,1000]
 curves[key]=history
 transfer=data["transfer_mean"]
 tft=0
 p=np.array(out["policy_logits"])
 pi=1/(1+np.exp(-p))
 tft_mask=(pi[:,0]>.7)&(pi[:,1]<.3)&(pi[:,2]>.7)&(pi[:,3]<.3)&(pi[:,4]>.7)
 tft=int(tft_mask.sum())
 response_conditional=float((pi[:,2]-pi[:,1]).mean())
 response_coop=float((pi[:,4]-pi[:,3]).mean())
 row=dict(model=key,seed=seed,q=q,method=method,alpha=alpha,
   food=out["food"],donations=out["gifts"],mutual=out["mutual"],
   causal=out["causal"],positive_agents=out["positive_agents"],
   initial_gift_probability=out["mean_initial_gift"],
   p_CC=out["mean_CC"],p_DD=out["mean_DD"],
   tft_like_agents=tft,response_if_other_gave_after_own_D=response_conditional,
   response_if_other_gave_after_own_C=response_coop,
   mc_food=data["mc"]["food"],mc_mutual=data["mc"]["mutual"],
   worst_mc_difference=max(data["monte_carlo_discrepancies"].values()),
   transfer_food=transfer["food"],
   transfer_mutual=transfer["mutual"],
   transfer_causal=transfer["causal"],
   transfer_positive_agents=transfer["positive_agents"],
   transfer_fraction_at_least24=data["transfer_fraction_with_24_positive"])
 rows.append(row)
 validation[key]=dict(max_abs_differences=data["monte_carlo_discrepancies"],
  holdout_worlds_per_seed=data["holdout_worlds_per_seed"],
  holdout_seeds=data["holdout_environment_seeds"],
  transfer_seeds=data["transfer_seeds"],
  transfer_min_positive=min(x["positive_agents"] for x in data["transfer"]),
  transfer_max_positive=max(x["positive_agents"] for x in data["transfer"]))
by={r["model"]:r for r in rows}
contrasts=[]
for seed in SEEDS:
 base=by[name(.95,"NL",0,seed)]
 for alpha in (1,5,20):
  a=by[name(.95,"LOLA",alpha,seed)]
  b=by[name(.95,"LOOK",alpha,seed)]
  for typ,comp in (("LOLA_minus_NL",base),("LOLA_minus_LOOK",b)):
   contrasts.append(dict(seed=seed,alpha=alpha,contrast=typ,
    food=a["food"]-comp["food"],donations=a["donations"]-comp["donations"],
    mutual=a["mutual"]-comp["mutual"],
    causal=a["causal"]-comp["causal"],
    positive_agents=a["positive_agents"]-comp["positive_agents"]))
success_by_alpha={}
for alpha in (1,5,20):
 successes=[]
 food_advantages=[]
 for seed in SEEDS:
  r=by[name(.95,"LOLA",alpha,seed)]
  b=by[name(.95,"NL",0,seed)]
  successes.append(r["causal"]>0 and r["positive_agents"]>=24 and r["mutual"]>.25)
  food_advantages.append(r["food"]>b["food"])
 success_by_alpha[str(alpha)]=dict(
  passes=sum(successes),food_better=sum(food_advantages),
  successes=successes,food_advantages=food_advantages,
  meets_preregistered=(sum(successes)>=3 and sum(food_advantages)>=3))
hypotheses=dict(
 h46_primary_any_lola_alpha=any(x["meets_preregistered"] for x in success_by_alpha.values()),
 h46_lookahead_20_does_not_replicate_lola=all(
   by[name(.95,"LOOK",20,seed)]["positive_agents"]<24 for seed in SEEDS),
 h46_low_horizon_negative_control=all(
   by[name(.2,"LOLA",alpha,seed)]["positive_agents"]<24
   for seed in SEEDS[:2] for alpha in (1,5,20)),
 h46_analytic_vs_monte_carlo_all36=all(r["worst_mc_difference"]<.015 for r in rows),
 h46_lola20_partner_reassignment_robust=all(
   by[name(.95,"LOLA",20,seed)]["transfer_fraction_at_least24"]>=.9
   for seed in SEEDS))
assert hypotheses["h46_analytic_vs_monte_carlo_all36"]
with (OUT/"COMPARACION_V46.csv").open("w",newline="",encoding="utf8") as handle:
 w=csv.DictWriter(handle,list(rows[0]));w.writeheader();w.writerows(rows)
with (OUT/"CONTRASTES_V46.csv").open("w",newline="",encoding="utf8") as handle:
 w=csv.DictWriter(handle,list(contrasts[0]));w.writeheader();w.writerows(contrasts)
source_names=("PREREG_V46_EXACT_OPPONENT_SHAPING.md",
 "AMENDMENT_V46_FROZEN_AUDITS.md","v46_exact_opponent_shaping.py",
 "v46_frozen_audits.py","v46_batch_audit.py","v46_summarize.py",
 "test_v46_opponent_shaping.py","test_v46_frozen_audits.py")
sha={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in source_names}
aggregates={}
for method,alpha in (("NL",0),("LOLA",1),("LOLA",5),("LOLA",20),
  ("LOOK",1),("LOOK",5),("LOOK",20)):
 subset=[by[name(.95,method,alpha,seed)] for seed in SEEDS]
 aggregates[f"{method}{alpha}"]=dict(
  food_mean=float(np.mean([x["food"] for x in subset])),
  donations_mean=float(np.mean([x["donations"] for x in subset])),
  mutual_mean=float(np.mean([x["mutual"] for x in subset])),
  causal_mean=float(np.mean([x["causal"] for x in subset])),
  positive_agents_mean=float(np.mean([x["positive_agents"] for x in subset])),
  tft_like_agents_mean=float(np.mean([x["tft_like_agents"] for x in subset])),
  transfer_positive_mean=float(np.mean([x["transfer_positive_agents"] for x in subset])),
  range_causal=[min(x["causal"] for x in subset),
    max(x["causal"] for x in subset)])
(OUT/"METRICAS_V46.json").write_text(json.dumps(dict(
 schema="V46 complete all frozen policies and independent holdout",
 model_rows=rows,contrasts=contrasts,
 aggregate_by_method=aggregates,success_by_alpha=success_by_alpha,
 hypotheses=hypotheses,curves=curves,validation=validation,sha256=sha,
 training_checkpoints=36,neural_seeds_primary=list(SEEDS),
 heldout_environment_seeds=[990101,990107,990109,990121,990131,990137],
 pairing_transfer_seeds=[991101,991107,991109,991121,991131,991137,
  991141,991149,991153,991159,991163,991171],
 note="Exact own-objective gradient, no private opponent future reward transferred. Overlap of 48 fixed paired policies is not evidence of spontaneous network/role formation."),indent=2),encoding="utf8")
report=[
 "# V46 — Cooperación aprendida mediante modelización diferenciable del aprendizaje ajeno",
 "",
 "36 políticas poblacionales entrenadas desde logitos privados aleatorios (0.05×normal), con 48 agentes independientes, 24 parejas complementarias fijas, duración máxima48, supervivencia q0,95 o control q0,20, coste privado c0,04 y valor de recepción v0,55/3. Un actor dispone de cinco logitos privados para el primer regalo y los cuatro estados de memoria de una ronda. Cada actor maximiza su propio retorno esperado exacto; no se comparte recompensa ni se impone un contrato o sanción. Hay un componente crucial de laboratorio: se conocen las funciones de recompensa y las políticas del compañero para calcular exactamente los gradientes contrafactuales.",
 "",
 "Se compara NL exacto (gradiente miope privado), LOLA one-step exacto (diferencia a través de la actualización esperada del otro) y LOOK de parada del gradiente (anticipa el cambio ajeno, pero impide la derivada de influencia). Todas las redes son tabulares de cinco logitos y tienen una representación más estrecha y más interpretable que las MLP de V44–V45. Se calculan expectativas con un proceso de Markov de cuatro estados y horizonte finito48, y se contrasta el cálculo con una implementación Monte Carlo independiente.",
 "",
 "## Resultados principales q0,95 al final de 1000 actualizaciones",
 "",
 table([[f"{m} α={a}",f(aggregates[f"{m}{a}"]["food_mean"]),
  f(aggregates[f"{m}{a}"]["donations_mean"]),
  f(aggregates[f"{m}{a}"]["mutual_mean"]),
  plus(aggregates[f"{m}{a}"]["causal_mean"]),
  f'{aggregates[f"{m}{a}"]["positive_agents_mean"]:.1f}/48',
  f'{aggregates[f"{m}{a}"]["tft_like_agents_mean"]:.1f}/48']
  for m,a in (("NL",0),("LOLA",1),("LOLA",5),("LOLA",20),
   ("LOOK",1),("LOOK",5),("LOOK",20))],
 ["Método","Alimento","Donaciones","Mutuas","Retorno causal propio",
  "Individuos positivos (media)","Reciprocadores tipo TFT"]),
 "",
 "**Interpretación operativa:** «retorno causal propio» = J_i(forzar una donación en el turno inicial)−J_i(prohibirla), con el compañero libre y las políticas futuras congeladas. J_i incluye propio alimento y descuento temporal, con supervivencia q. Un retorno positivo de ese primer acto muestra que las respuestas condicionales futuras del compañero compensan el coste inmediato. No prueba estabilidad evolutiva bajo sustitución reiterada ni aprendizaje de instituciones.",
 "",
 "## Todas las cuatro semillas iniciales de los tratamientos principales",
 "",
 table([[str(r["seed"]),r["method"],str(r["alpha"]),
  f(r["food"]),f(r["mutual"]),
  plus(r["causal"]),f'{r["positive_agents"]}/48',
  f'{r["transfer_positive_agents"]:.1f}/48']
  for r in rows if r["q"]==.95 and r["method"] in ("NL","LOLA")],
 ["Semilla","Método","α","Alimento","Mutuas","Retorno causal",
  "Agentes positivos","Positivos tras reemparejar"]),
 "",
 "Se utilizan exactamente las semillas3111,4111,5111 y6111 en cada condición primaria y se conservan todos los checkpoints finalizados, incluidos los que no dan cooperación. La elección de α se fijó antes de los entrenamientos; no se elige retrospectivamente la semilla o paso con mejor resultado.",
 "",
 "## Control mecanístico: anticipación frente a modelación del aprendizaje ajeno",
 "",
 "La variante LOOK no deriva a través de la actualización esperada del compañero: el paso anticipado se considera fijo al calcular el gradiente propio. Comparar LOLA con LOOK del mismo α y semilla separa la influencia explícita sobre el aprendizaje ajeno de la simple expectativa de una política rival más entrenada. Los contrastes emparejados completos de alimentación, mutualidad y retorno causal se guardan en CONTRASTES_V46.csv.",
 "",
 "## Control negativo de relaciones breves (q0,20)",
 "",
 table([[str(r["seed"]),r["method"],str(r["alpha"]),
  f(r["donations"]),f(r["mutual"]),plus(r["causal"]),
  f'{r["positive_agents"]}/48']
  for r in rows if r["q"]==.2],
 ["Semilla","Método","α","Donaciones","Mutuas","Retorno causal",
 "Individuos positivos"]),
 "",
 "El efecto de la modelación del otro no se interpreta como moralidad o preferencia social aprendida: la recompensa propia no contiene alimento de terceros. En relaciones de duración breve q0,20, la ventaja futura de recibir regalos puede ser demasiado pequeña para compensar el coste de contribuir, como anticipa la deducción matemática V42 bajo una norma oracular idealizada.",
 "",
 "## Prueba física externa y cambio de compañero",
 "",
 "Cada uno de los 36 checkpoints congelados fue reproducido en seis semillas ambientales reservadas (990101,990107,990109,990121,990131,990137) mediante una segunda implementación Monte Carlo independiente de la recursión Markov analítica, con 128 sociedades-mundo por semilla, 768 por política. Se exigió error absoluto<0,015 en alimento, tasa de donaciones y regalos mutuos. La intervención causal principal sigue siendo el cálculo exacto (no se extrae del ruido Monte Carlo).",
 "",
 "Además se evaluaron12 emparejamientos completos independientes de las48 políticas congeladas en cada condición, sin reentrenar. Estos emparejamientos permutan quién es vecino de quién entre episodios: no conceden movilidad de socios durante una interacción y tampoco tienen cuatro profesiones aprendidas de manera autónoma.",
 "",
 table([[r["model"],f(r["transfer_food"]),
  f(r["transfer_mutual"]),plus(r["transfer_causal"]),
  f'{r["transfer_positive_agents"]:.1f}/48',
  f(r["transfer_fraction_at_least24"])]
   for r in rows if r["q"]==.95 and r["method"]=="LOLA" and r["alpha"] in (5,20)],
 ["Modelo","Alimento reemparejado","Mutuas reemparejadas","Retorno causal",
  "Agentes positivos (media)","Fracción de redes ≥24"]),
 "",
 "## Criterios preregistrados",
 "",
 table([[k,"cumple" if v else "no cumple"] for k,v in hypotheses.items()],
 ["Prueba","Resultado"]),
 "",
 "Criterio primario: α>0 con retorno propio causal positivo y al menos24/48 agentes positivos y tasa mutua>0,25 en al menos tres de cuatro semillas, además de alimentación superior a NL en al menos tres de cuatro semillas. El resultado se conserva incluso si aparecen después limitaciones de validez externa: nunca se confundirá con la meta global del proyecto.",
 "",
 "## Sensibilidad conductual de las estrategias",
 "",
 "El actor tiene cinco logitos separados (primera ronda; estados 00, 01, 10, 11, relativos a acciones anteriores de sí y su compañero). Una política tipo tit-for-tat responde más positivamente cuando la pareja donó en la ronda anterior, siempre controlando la acción propia pasada. El contador «grim_count» del entrenador original V46 codificaba indebidamente este patrón **tipo tit-for-tat** y no la norma irreversible grim-trigger del análisis V42: el contador correcto del informe es `tft_like_agents`, calculado ex novo a partir de los cinco logitos finales. Esta corrección terminológica no altera ninguna política, resultado causal ni gradiente.",
 "",
 "## Límites y continuación",
 "",
 "[Inferencia] La diferencia entre el gradiente miope y LOLA es compatible con la hipótesis de que los agentes cooperan por interés propio cuando optimizan cómo su comportamiento influye en el aprendizaje ajeno. Pero la observación requiere acceso al cálculo exacto de expectativas y gradientes de terceros; no se han demostrado capacidades reales de inferir ese modelo desde la interacción limitada, ni formación de normas sin esos recursos, ni división ocupacional endógena en poblaciones abiertas.",
 "",
 "El optimizador real es Adam lr0,03, mientras α es la magnitud hipotética del paso de aprendizaje de la contraparte; estas escalas no coinciden en general. Las cuatro semillas iniciales constituyen replicación de laboratorio, no muestra estadística representativa de cualquier arquitectura o cultura. Los12 reemparejamientos no equivalen a redes dinámicas dentro de la misma trayectoria.",
 "",
 "Fuentes teóricas: Foerster et al. (2018) *Learning with Opponent-Learning Awareness* https://arxiv.org/abs/1709.04326 y Letcher et al. (2019) *Stable Opponent Shaping in Differentiable Games* https://arxiv.org/abs/1811.08469. La segunda referencia discute problemas de convergencia de LOLA; no confundir nuestro éxito de entrenamiento con una demostración universal de estabilidad.",
 "",
 "## Reproducción, controles de integridad y SHA256",
 "",
 "Preregistro, enmienda de semillas y medición, scripts del motor matemático y de auditoría, archivos JSON sin agregación de cada escenario, CSV, 36 checkpoints con pesos y Adam, pruebas de gradientes privados mediante diferencias finitas y Bellman independiente. SHA256:",
 *[f"{name}: {digest}" for name,digest in sha.items()]]
(OUT/"RESULTADOS_INTEGRALES_V46.md").write_text("\n".join(report),encoding="utf8")
print("V46_REPORT_OK",len(rows),hypotheses,success_by_alpha)
for k,x in aggregates.items():
 print(k,"food",round(x["food_mean"],4),
    "mutual",round(x["mutual_mean"],4),
    "causal",round(x["causal_mean"],4),
    "positive",round(x["positive_agents_mean"],1),
    "transferpos",round(x["transfer_positive_mean"],1))
