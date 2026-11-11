"""Produce V20 report from frozen artifacts; never fabricate missing rows."""
from __future__ import annotations
import csv,hashlib,json,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parent
NAMES=[f"v20_{regime}_s{seed}" for regime,seeds in (
 ("SMOOTH",(3111,4111,5111,6111)),
 ("CONST",(3111,4111,5111,6111)),
 ("ABRUPT",(3111,4111))) for seed in seeds]
ROWS=[]
for name in NAMES:
 p=ROOT/"runs"/name
 status=json.loads((p/"targeted_status.json").read_text("utf8"))
 assert status["state"]=="completed" and status["updates"]==600,name
 h=[json.loads(x) for x in (p/"v20_history.jsonl").read_text("utf8").splitlines() if x.strip()]
 assert h[-1]["update"]==600,name
 audit=json.loads((ROOT/"results"/("v20_allagents_"+name+".json")).read_text("utf8"))
 assert audit["checkpoint"]==600 and len(audit["scenarios"])==9,name
 frozen={f"{x['k']}_{x['topology']}_{x['mode']}":x for x in audit["scenarios"]}
 tr=h[-1]["high_cost"]["trained_normal"]
 abl=h[-1]["high_cost"]["trained_no_social"]
 ood=h[-1]["high_cost"]["ood_normal"]
 record=dict(name=name,regime=name.split("_")[1],seed=int(name.split("s")[-1]),
    cost_final=h[-1]["training_cost"],food_dev=tr["food"],
    giving_dev=tr["gift"],no_social_dev=abl["food"],
    ood_dev=ood["food"])
 for task,label in (("2_ring","train"),("2_rewired","rewired"),("3_ring","k3")):
  for mode in ("normal","scramble","no_social"):
   z=frozen[f"{task}_{mode}"]
   record[f"{label}_{mode}_net"]=z["mean_total"]
  record[f"{label}_positive_agents"]=frozen[f"{task}_normal"]["positive_agents"]
  record[f"{label}_even"]=frozen[f"{task}_normal"]["mean_even"]
  record[f"{label}_odd"]=frozen[f"{task}_normal"]["mean_odd"]
 ROWS.append(record)
out=ROOT/"results"
with (out/"COMPARACION_V20.csv").open("w",encoding="utf8",newline="") as f:
 w=csv.DictWriter(f,fieldnames=list(ROWS[0]))
 w.writeheader();w.writerows(ROWS)
smooth={r["seed"]:r for r in ROWS if r["regime"]=="SMOOTH"}
constant={r["seed"]:r for r in ROWS if r["regime"]=="CONST"}
abrupt={r["seed"]:r for r in ROWS if r["regime"]=="ABRUPT"}
food_dif=[smooth[s]["food_dev"]-constant[s]["food_dev"] for s in smooth]
metric=lambda x:f"{x:+.3f}"
def table(arr,headers):
 lines=["| "+" | ".join(headers)+" |","| "+" | ".join(["---"]*len(headers))+" |"]
 lines.extend("| "+" | ".join(map(str,row))+" |" for row in arr)
 return "\n".join(lines)
regime_table=[]
for r in ROWS:
 regime_table.append([r["name"],f"{r['food_dev']:.3f}",
          f"{r['giving_dev']:.3f}",
          metric(r["train_normal_net"]),
          f"{r['train_positive_agents']}/24",
          metric(r["rewired_normal_net"]),
          metric(r["k3_normal_net"])])
contrast=[]
for seed in smooth:
 contrast.append([seed,
    f"{constant[seed]['food_dev']:.3f}",
    f"{smooth[seed]['food_dev']:.3f}",
    f"{abrupt[seed]['food_dev']:.3f}" if seed in abrupt else "—",
    metric(smooth[seed]["food_dev"]-constant[seed]["food_dev"])])
mechanisms=[]
for seed in (3111,4111):
 name=f"v20_SMOOTH_s{seed}"
 dd=json.loads((out/("v20_mechanisms_"+name+".json")).read_text("utf8"))
 mechanisms.append([seed]+[metric(next(x for x in dd["rows"] if x["mode"]==mode)["causal"]["mean_total"])
           for mode in ("normal","no_direct_identity","no_public_offer","no_both_except_receipt")])
hashes={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in (
 "v20_curriculum.py","v20_all_agents_causal.py","v20_mechanism_ablation.py",
 "targeted_gifts.py","train_targeted.py")}
report=[
 "# V20 — Dependencia de trayectoria y cooperación voluntaria dirigida",
 "",
 "Resultados exploratorios congelados el 11/11/2026. Las políticas y archivos originales permanecen en `runs/` y `results/`.",
 "",
 "## Contrato experimental",
 "",
 "Poblaciones de 24 agentes con redes neuronales privadas, sin parámetros compartidos, recompensas globales, profesor ni obligación de donar. Una donación cuesta 0,12 en el régimen final. El alimento se obtiene individualmente, según bienes recibidos y coste de donar. Las profesiones de entrenamiento están asignadas exógenamente y no se aprende aún la división del trabajo.",
 "",
 "Se compararon diez entrenamientos de 600 actualizaciones, con 16 mundos por actualización, horizonte de 32 períodos y 24 agentes por mundo; **73.728.000 transiciones individuales de entrenamiento** en total. Las rutas comparadas son coste alto constante, coste ascendente gradual y salto brusco tras un tramo inicial de bajo coste.",
 "",
 "## Rendimiento al finalizar el entrenamiento",
 "",
 table(contrast,["Semilla","Constante: alimento","Gradual: alimento","Brusco: alimento","Gradual menos constante"]),
 "",
 f"Ganancia descriptiva media gradual frente a constante sobre cuatro semillas: {statistics.mean(food_dif):+.3f} raciones. No es una estimación confirmatoria sobre la distribución de inicializaciones.",
 "",
 "## Censo causal de los 24 individuos",
 "",
 "La auditoría vectoriza, por cada mundo, 24 intervenciones distintas sobre la decisión inicial de donar o no donar. Incluye seis semillas de entorno, 24 mundos por semilla, dos potenciales tratamientos, tres regímenes de información y tres tareas (red circular k=2, reconectada k=2, circular k=3), durante 48 períodos. Hay **311.040 pares de trayectorias contrafactuales** en esta matriz (622.080 brazos); los mundos comparten estructura y no constituyen réplicas estadísticamente independientes.",
 "",
 "Cada retorno causal es la diferencia en el alimento descontado del individuo cuya donación inicial fue forzada; un resultado positivo indica retorno favorable en esa intervención, no el valor causal de toda la institución.",
 "",
 table(regime_table,["Política","Alimento desarrollo","Tasa donación","Retorno k2 circular","Agentes positivos","Retorno reconectada","Retorno k3"]),
 "",
 "En particular, la red gradual de semilla 3111 presenta retorno neto +0,228 y 22/24 agentes positivos; las otras tres semillas graduales tienen efectos mucho menores. En las tareas transferidas, buena parte de las políticas pierde el beneficio causal. La conclusión no puede generalizarse a cualquier inicialización, topología u objetivo.",
 "",
 "## Ablación del mecanismo: donación directa y reputación",
 "",
 "Los siguientes experimentos adicionales pertenecen al auditor anterior de seis agentes, todos de paridad par: ese muestreo no es representativo del censo individual y se conserva únicamente como prueba de mecanismo.",
 "",
 table(mechanisms,["Semilla","Información completa","Sin memoria del donante directo","Sin señal pública de generosidad","Sin ambas"]),
 "",
 "[Inferencia] El retorno por donar parece depender particularmente de la visibilidad de la generosidad de los vecinos, compatible con reputación y reciprocidad indirecta. Esa intervención no identifica por sí sola una motivación mental ni una norma social interiorizada.",
 "",
 "## Hallazgos negativos y riesgos de identificación",
 "",
 "El aumento brusco supera al gradual en alimentación en las dos semillas para las que se probó, pero no se observa una superioridad causal uniforme. Aumentar la alimentación no prueba mayor reciprocidad. El auditor original intervenía seis índices pares y sobrerrepresentaba una profesión: la auditoría de todos los individuos reduce considerablemente varios efectos medios.",
 "",
 "Los resultados de alimentación son evaluaciones de desarrollo. Los efectos causales proceden de pesos congelados y semillas ambientales separadas. Las diez políticas se examinaron inicialmente con cuatro semillas neuronales para dos tratamientos y dos para el tercero; no se ha cuantificado aún su comportamiento tras entrenamientos mucho mayores que 600 actualizaciones. Las pruebas fuera de distribución son cambios pequeños de red y k, no escalado de población.",
 "",
 "No se declara OBJETIVO COMPLETADO. Aunque hay realizaciones concretas de reciprocidad aprendida, todavía falta robustez entre inicializaciones, estabilidad temporal, escalado y elección endógena de ocupaciones.",
 "",
 "## Integridad y procedencia",
 "",
 "Código y modelos: `v20_curriculum.py`, `v20_mechanism_ablation.py`, `v20_all_agents_causal.py`; archivos de datos `runs/v20_*/v20_history.jsonl`, `runs/v20_*/targeted_latest.pt` y `results/v20_allagents_*.json`. Los ficheros del repositorio pueden incluir modificaciones de experimentos previos sin relación con V20: no incluir cambios ajenos al confirmar la campaña.",
 "",
 "SHA-256 de los programas usados",
 "",
 "```",
 *[f"{k}: {v}" for k,v in hashes.items()],
 "```",
 ""]
(out/"RESULTADOS_INTEGRALES_V20.md").write_text("\n".join(report),encoding="utf8")
(out/"METRICAS_V20.json").write_text(json.dumps(dict(rows=ROWS,hashes=hashes,training_individual_steps=73728000,
   matched_pairs=311040,metric="discounted own-food treatment effect"),indent=2),encoding="utf8")
print("V20_REPORT",len(ROWS),"models","food_improvement_avg",round(statistics.mean(food_dif),4),
      "report",str(out/"RESULTADOS_INTEGRALES_V20.md"))
