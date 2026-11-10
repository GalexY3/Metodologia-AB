"""V3B inspectable analytical report and 3x2 figures from sealed eval.

Never re-evaluate models or alter parameters. Reports all 3 cohorts.
"""
from pathlib import Path
import json,statistics,math,html
ROOT=Path(__file__).resolve().parent
DATA=ROOT/"holdout_v3b"
d=json.loads((DATA/"SUMMARY.json").read_text(encoding="utf-8"))
assert d["n_training_cohorts"]==3 and d["n_condition_task_seed_batches"]==54
raw=d["condition_summary"]
modes=("C1","C2","C3","random_always","random_T24","stay")
names={"C1":"Sin mensajes (C1)","C2":"Con mensajes (C2)",
    "C3":"C2 sin mensajes en test (C3)",
    "random_always":"Aleatorio continuo",
    "random_T24":"Aleatorio 24 turnos y parar",
    "stay":"Nadie cambia"}
palette={"C1":"#C0813B","C2":"#295C95","C3":"#7D5DA0",
         "random_always":"#AD8C3D","random_T24":"#238476","stay":"#979DA7"}
fmt=lambda x,n=4:f"{x:.{n}f}".replace(".",",")
groups=[]
for k in (2,3,4):
 for mode in modes:
  rs=[r for r in raw if r["k"]==k and r["condition"]==mode]
  assert len(rs)==3
  avg=lambda key:statistics.mean(v[key] for v in rs)
  groups.append({"k":k,"mode":mode,
   "train_seeds":[v["training_seed"] for v in rs],
   "test_worlds":sum(v["test_worlds"] for v in rs),
   "D":avg("average_final_D"),
   "D_AUC":avg("average_D_AUC"),
   "ratio":avg("ratio_final_D_to_IID"),
   "D_IID":avg("random_IID_D_exact"),
   "churn":avg("average_last10_churn"),
   "stable":sum(v["stable_count"] for v in rs),
   "exact":sum(v["exact_count"] for v in rs),
   "send":avg("average_send_rate"),
   "seedwise_D":[v["average_final_D"] for v in rs]})
p=DATA/"AGGREGATES.json"
p.write_text(json.dumps({"protocol":"PREREG_V3B_C1C2.md",
 "note":"Three independent policy training seeds; 300 test worlds per task per mode are nested",
 "groups":groups,
 "paired_seed_k":d["paired_differences"]},
 ensure_ascii=False,indent=2),encoding="utf-8")
print("AGGREGATES_WRITTEN",p,flush=True)

W,H=1010,530
L,R,T,B=100,45,65,130
def render(k,field):
 series={}
 for mode in modes:
  a=[json.loads((DATA/f"seed{s}_k{k}_{mode}.json").read_text(encoding="utf-8"))
     for s in (311,312,313)]
  key="D_curve_mean" if field=="D" else "churn_curve_mean"
  series[mode]=[statistics.mean(v[key][t] for v in a) for t in range(121)]
 if field=="D":
  minimum=0; maximum=max(.45,math.ceil(max(x[0] for x in series.values())*20)/20)
  title=f"k={k} · distancia al reparto equilibrado durante 120 turnos"
  subtitle="Variación total (D), menor es mejor. Línea punteada: esperanza IID."
 else:
  minimum=0;maximum=1.0
  title=f"k={k} · porcentaje de agentes que cambia color"
  subtitle="Rotación por turno: menor rotación puede significar estabilidad O inmovilidad sin solución."
 x=lambda t:L+(W-L-R)*(t/120)
 y=lambda v:T+(H-T-B)*(maximum-v)/(maximum-minimum)
 svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
 '<rect width="100%" height="100%" fill="#ffffff"/>',
 f'<text x="35" y="29" font-size="21" font-family="Arial" font-weight="bold" fill="#263747">{title}</text>',
 f'<text x="36" y="50" font-size="12" font-family="Arial" fill="#66717e">{subtitle}</text>']
 for j in range(6):
  v=minimum+(maximum-minimum)*j/5
  yy=y(v)
  svg.append(f'<line x1="{L}" x2="{W-R}" y1="{yy:.1f}" y2="{yy:.1f}" stroke="#e7ecef"/>')
  label=fmt(100*v,0)+"%" if field=="churn" else fmt(v,2)
  svg.append(f'<text x="{L-12}" y="{yy+4:.1f}" text-anchor="end" font-size="12" font-family="Arial" fill="#607080">{label}</text>')
 for t in range(0,121,20):
  svg.append(f'<text x="{x(t):.1f}" y="{H-B+25}" font-size="12" font-family="Arial" fill="#607080" text-anchor="middle">{t}</text>')
 if field=="D":
  floor=next(r for r in groups if r["k"]==k)["D_IID"]
  svg.append(f'<line x1="{L}" x2="{W-R}" y1="{y(floor):.1f}" y2="{y(floor):.1f}" stroke="#394553" stroke-width="1.5" stroke-dasharray="4 5"/>')
  svg.append(f'<text x="{W-R-5}" y="{y(floor)-6:.1f}" text-anchor="end" font-size="11" font-family="Arial" fill="#394553">Azar IID esperado = {fmt(floor)}</text>')
 for i,mode in enumerate(modes):
  pts=" ".join(f"{x(t):.2f},{y(a):.2f}" for t,a in enumerate(series[mode]))
  dash='5,4' if mode.startswith("random") else 'none'
  svg.append(f'<polyline points="{pts}" stroke="{palette[mode]}" stroke-width="{3 if mode=="C2" else 2}" stroke-dasharray="{dash}" stroke-linecap="round" stroke-linejoin="round" fill="none"/>')
  xx=L+(i%2)*420
  yy=H-72+(i//2)*22
  svg.append(f'<line x1="{xx}" x2="{xx+30}" y1="{yy}" y2="{yy}" stroke="{palette[mode]}" stroke-width="3" stroke-dasharray="{dash}"/>')
  svg.append(f'<text x="{xx+38}" y="{yy+4}" font-size="12" font-family="Arial" fill="#354554">{html.escape(names[mode])}</text>')
 svg.append(f'<text x="{L+(W-L-R)/2}" y="{H-B+49}" text-anchor="middle" font-family="Arial" font-size="12" fill="#657584">Turnos desde el estado inicial</text></svg>')
 dest=ROOT/f"FIG_V3B_k{k}_{field}.svg"
 dest.write_text("\n".join(svg),encoding="utf-8")
 print("FIGURE",dest.name,flush=True)

for k in (2,3,4):
 for field in ("D","churn"):render(k,field)
lines=[
"# V3B — Agentes individuales con recompensa colectiva: primera evaluación reservada",
"",
"**Fecha:** 10/11/2026. **Protocolo anterior al entrenamiento:** [PREREG_V3B_C1C2.md](PREREG_V3B_C1C2.md). **Código del test:** [evaluate_v3b.py](evaluate_v3b.py).",
"",
"## Resumen",
"",
"Se entrenaron seis poblaciones (3 semillas 311–313 × C1 sin mensajes/C2 con mensajes) mediante **120 actualizaciones, 12 mundos y 24 turnos por actualización** (1.440 episodios por población, 8.640 entre todas). Cada agente de cada población posee su propia política neuronal, entrenada sin compartir pesos ni gradientes con otros y sin premio específico por sus decisiones. La única recompensa es r=N(D_t−D_{t+1}), igual para todos los agentes del mundo. Todos pueden cambiar su propio color incluso sin recibir mensajes. Los mensajes de C2 incluyen color sugerido y snapshot del vecindario del emisor.",
"",
"Se bloquearon hashes de código y de los seis checkpoints finales en [holdout_v3b/LOCK.json](holdout_v3b/LOCK.json) ANTES de evaluar. Se emplearon 100 sociedades nuevas por semilla de entrenamiento, k y condición; por tanto hay 300 sociedades test por k×condición, pero **solo tres inicializaciones independientes del aprendizaje**.",
"",
"**Resultado principal: no se observó estabilidad sostenida en ninguna de las sociedades C1, C2 o C3** (0/300 por k), mientras el control aleatorio con parada programada al turno 24 sí consiguió estabilidad parcial. La diferencia C2–C1 en distancia es pequeña, varía de signo y no muestra ventaja consistente de comunicación bajo esta configuración. La distancia final se mantiene alrededor de la referencia aleatoria IID. No se ha demostrado emergencia de cooperación.",
"",
"## Comparación íntegra al turno 120",
"",
"| k | Condición | Distancia D | D / E[D_IID] | Estables (sobre 300) | D=0 exacta | Churn últimos 10 |",
"|---|---|---:|---:|---:|---:|---:|"]
for k in (2,3,4):
 for mode in modes:
  r=next(r for r in groups if r["k"]==k and r["mode"]==mode)
  lines.append(f"| {k} | {names[mode]} | {fmt(r['D'])} | {fmt(r['ratio'],3)} | {r['stable']}/300 | {r['exact']}/300 | {fmt(100*r['churn'],1)}% |")
lines += ["",
"## Evolución temporal",
"",
"Las curvas son medias descriptivas de tres cohortes y 100 sociedades por cohorte. Cada curva incluye el instante 0 y 120 turnos; no selecciona solo sociedades exitosas. Churn ≈ 50%, 67%, 75% en k2/3/4 es compatible con volver a elegir uniformemente entre k colores cada turno, una señal de que aún no se ha aprendido a conservar la distribución.",
""]
for k in (2,3,4):
 lines +=[f"### k={k}",
 f"![Distancia global en función del tiempo, k={k}](FIG_V3B_k{k}_D.svg)",
 f"![Churn en función del tiempo, k={k}](FIG_V3B_k{k}_churn.svg)",
 ""]
lines += [
"## Interpretación estricta",
"",
"Los sujetos C1 no disponen de canal de peticiones, pero observan los colores de sus vecinos y pueden cambiar voluntariamente su color. C2 añade información y propuestas dirigidas a un único vecino por emisor, con recepción múltiple. C3 reutiliza los pesos de C2 al bloquear mensajes en test, permitiendo siempre cambios voluntarios. Una diferencia de C3 respecto a C2 sería dependencia de entrada bajo cambio de distribución; no una prueba universal de necesidad de mensajes.",
"",
"El «0% aleatorio continuo» no implica que la asignación numérica sea mala: el control no deja de cambiar. El control aleatorio que se detiene en t=24 incorpora una regla temporal escrita por el investigador, distinta de aprendizaje. Por su parte, el objetivo D/E[D_IID]<1 no significa óptimo físico ni hiperuniformidad espacial. Evitar atribuir diferencias de 0,001 en D a una mejora replicada con tres cohortes.",
"",
"El entrenamiento REINFORCE se construyó con baseline leave-one-out de otros mundos del mismo k, igual para todos los individuos del mundo. No hubo crítico central entrenable ni atribuciones individuales de mérito. El código de los actores aplica un mismo scorer por candidato de color dentro de cada persona, pero cada persona tiene θ_i distinto. En este primer estudio se usa memoria W1: estado actual más último escalar de feedback, NO memorias recurrentes de varias rondas. Estudiar el crédito temporal y la memoria podría constituir otro experimento prospectivo, no una corrección retrospectiva de estos resultados.",
"",
"## Limitaciones y próximos contrastes",
"",
"El fracaso es específico del número de actualizaciones y el diseño de tarea, no demuestra imposibilidad teórica. La escasa variación del gradiente y el comportamiento estocástico casi uniforme sugieren una señal de aprendizaje débil, pero habría que probarlo con mediciones directas. Ya se registró un aumento del presupuesto a 600 actualizaciones [PREREG_V3B_LONGRUN.md](PREREG_V3B_LONGRUN.md), como análisis exploratorio posterior al resultado negativo.",
"",
"**Reproducibilidad:** resultados individuales en [holdout_v3b](holdout_v3b) con las 54 condiciones×cohorte×k; [SUMMARY.json](holdout_v3b/SUMMARY.json) y [AGGREGATES.json](holdout_v3b/AGGREGATES.json), pesos finales de seis experimentos en runs/v3b_seed{311,312,313}_{C1,C2}_updates120, cada uno con TRAINING_LOG.json y CONFIG.json.",
]
(ROOT/"REPORT_V3B_120.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
print("REPORT_DONE",len(lines),"rows",flush=True)
