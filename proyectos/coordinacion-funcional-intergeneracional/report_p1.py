"""Report, audit and vector plots for P0 and P1 first-cohort holdouts."""
from pathlib import Path
import json,hashlib,statistics,math
ROOT=Path(__file__).resolve().parent
p0=json.loads((ROOT/"results_p0"/"heldout_once.json").read_text(encoding="utf-8"))
p1=json.loads((ROOT/"results_p1"/"P1_RESULTS.json").read_text(encoding="utf-8"))
known=json.loads((ROOT/"results_p0"/"known_validation.json").read_text(encoding="utf-8"))
assert p0["locked_source"]["train_k"]==[2,3,4]
assert p1["lock"]["train_k"]==[2,3,4]
assert set(z["k"] for z in p0["test_outcomes"])==set(z["k"] for z in p1["test_raw"])=={5,6,7,8}
assert len(p0["test_outcomes"])==240 and len(p1["test_raw"])==120
rows=[]
for k in (5,6,7,8):
 p0lear=next(r for r in p0["summary"] if r["k"]==k and r["policy"]=="learned")
 p0manual=next(r for r in p0["summary"] if r["k"]==k and r["policy"]=="minority")
 p1old=next(r for r in p1["test_summary"] if r["k"]==k and r["mode"]=="P0_same_cohort")
 p1new=next(r for r in p1["test_summary"] if r["k"]==k and r["mode"]=="P1_k_scaled")
 p1manual=next(r for r in p1["test_summary"] if r["k"]==k and r["mode"]=="manual_minority")
 rows.append({"k":k,
  "P0_original_success":p0lear["stable_count"],"P0_manual_success":p0manual["stable_count"],
  "P1_control_success":p1old["stable_count"],"P1_scaled_success":p1new["stable_count"],
  "P1_manual_success":p1manual["stable_count"],
  "P1_control_mean_TV":p1old["mean_tv"],"P1_scaled_mean_TV":p1new["mean_tv"],
  "P1_manual_mean_TV":p1manual["mean_tv"]})
fmt=lambda x,d=3:f"{x:.{d}f}".replace(".",",")
# Graph 1: success rates, matched cohort and seeds only.
W,H=900,440
L,R,T,B=82,30,70,95
groups=[("Original, misma cohorte","P1_control_success","#9b9b9b"),
 ("Normalización por k","P1_scaled_success","#222222"),
 ("Heurística manual","P1_manual_success","#566579")]
xg=lambda i:L+60+i*190
yb=lambda v:H-B-v/10*(H-T-B)
fig=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
 '<rect width="100%" height="100%" fill="#fff"/>',
 '<text x="40" y="35" font-family="Arial" font-size="19" font-weight="600" fill="#222">Generalización intercolectiva — funciones inéditas</text>']
for v in (0,2,4,6,8,10):
 y=yb(v);fig.append(f'<line x1="{L}" x2="{W-R}" y1="{y:.1f}" y2="{y:.1f}" stroke="#dedede" stroke-dasharray="3 4"/>')
 fig.append(f'<text x="{L-12}" y="{y+4}" text-anchor="end" font-family="Arial" font-size="12" fill="#555">{v}</text>')
for i,row in enumerate(rows):
 xx=xg(i)
 for j,(label,key,col) in enumerate(groups):
  v=row[key];x=xx+j*42
  fig.append(f'<rect x="{x}" y="{yb(v):.1f}" width="33" height="{H-B-yb(v):.1f}" fill="{col}"/>')
  fig.append(f'<text x="{x+16.5}" y="{yb(v)-8:.1f}" text-anchor="middle" font-family="Arial" font-size="13" fill="#333">{v}/10</text>')
 fig.append(f'<text x="{xx+58}" y="{H-B+26}" font-family="Arial" font-size="14" text-anchor="middle" fill="#333">k={row["k"]}</text>')
for j,(label,key,col) in enumerate(groups):
 x=70+j*267
 fig.append(f'<rect x="{x}" y="385" width="17" height="12" fill="{col}"/>')
 fig.append(f'<text x="{x+24}" y="396" font-family="Arial" font-size="11.5" fill="#333">{label}</text>')
fig.append('<text x="450" y="426" text-anchor="middle" font-size="12" font-family="Arial" fill="#555">Éxito = TV ≤ 0,06 y cambios ≤ 5 % durante diez pasos; 10 semillas por k</text>')
fig.append("</svg>")
(ROOT/"FIG_P1_HELDOUT.svg").write_text("\n".join(fig),encoding="utf-8")

# Graph 2: continuous distances; control must be on same cohort and test seeds.
W,H=900,410;L,R,T,B=85,35,65,80
ymax=.43
x=lambda i:L+75+190*i
y=lambda v:H-B-v/ymax*(H-T-B)
parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
'<rect width="100%" height="100%" fill="#fff"/>',
'<text x="40" y="35" font-family="Arial" font-size="19" fill="#222" font-weight="600">Desequilibrio funcional tras extrapolar a nuevos k</text>']
for q in (0,.1,.2,.3,.4):
 yy=y(q)
 parts.append(f'<line x1="{L}" x2="{W-R}" y1="{yy:.1f}" y2="{yy:.1f}" stroke="#ddd" stroke-dasharray="4 4"/>')
 parts.append(f'<text x="{L-10}" y="{yy+5:.1f}" text-anchor="end" font-family="Arial" font-size="12" fill="#555">{str(q).replace(".",",")}</text>')
for label,key,col in (("Original","P1_control_mean_TV","#9b9b9b"),("Escalado por k","P1_scaled_mean_TV","#222222"),("Regla manual","P1_manual_mean_TV","#566579")):
 line=" ".join(f"{x(i):.1f},{y(r[key]):.1f}" for i,r in enumerate(rows))
 parts.append(f'<polyline points="{line}" fill="none" stroke="{col}" stroke-width="3"/>')
 for i,r in enumerate(rows):parts.append(f'<circle cx="{x(i):.1f}" cy="{y(r[key]):.1f}" r="5" fill="{col}"/>')
for i,r in enumerate(rows):
 parts.append(f'<text x="{x(i)}" y="{H-B+25}" text-anchor="middle" font-family="Arial" font-size="14" fill="#333">k={r["k"]}</text>')
for j,(label,_,col) in enumerate((("Original","", "#9b9b9b"),("Escalado por k","", "#222222"),("Regla manual","", "#566579"))):
 xx=105+j*250
 parts.append(f'<line x1="{xx}" x2="{xx+32}" y1="375" y2="375" stroke="{col}" stroke-width="3"/>')
 parts.append(f'<text x="{xx+42}" y="379" font-family="Arial" font-size="12" fill="#333">{label}</text>')
parts.append('<text x="450" y="408" text-anchor="middle" font-family="Arial" font-size="11.5" fill="#555">Distancia TV media, último periodo de 10 pasos. Menor = más equilibrio; 0 = distribución perfecta</text>')
parts.append("</svg>")
(ROOT/"FIG_P1_TV.svg").write_text("\n".join(parts),encoding="utf-8")

report=[
"# Coordinación funcional distribuida — P0/P1, factibilidad y extrapolación",
"",
"**Fecha de experimento:** 9 de noviembre de 2026. **Equipo:** DESKTOP-I4SULKD. **Estado:** experimento de simulación exploratorio sobre tareas sintéticas. No se usaron datos sociológicos observacionales ni se verificó el contenido de los PDF/DOCX que el usuario había mencionado en el texto pegado; el diseño disponible queda en QUEUE.md.",
"",
"## Problema social modelizado",
"",
"Cada comunidad está compuesta por 120 agentes que deben cubrir k funciones en proporciones aproximadamente 1/k. Hay una estructura fija de red de anillo con grado4. Un tick permite una conversación con máximo un vecino por agente. Los agentes saben k y su propio estado, y conservan recuerdos locales de las etiquetas de vecinos con quienes han hablado. No observan el censo global; la distancia al equilibrio se calcula fuera del modelo como resultado experimental.",
"",
"El estado de cada agente corresponde a una función (un color), y cada mensaje comunica un estado de función. La distribución inicial está sesgada: 70% de agentes empiezan en estado0, los demás se distribuyen entre las otras funciones. El éxito estricto requiere distancia de variación total TV≤0,06 y churn≤0,05 durante diez ticks consecutivos, con la evaluación final en esas condiciones. La diversidad funcional local se mide separadamente.",
"",
"## Dos hechos diferentes: coordinación y aprendizaje",
"",
"La heurística manually designed **minority** dirige cada agente a favorecer una función poco observada entre sus conversaciones, con pequeña bonificación por conservar su función. Consiguió estabilizar todos los casos conocidos de k2,3,4 (12/12 en cuatro semillas por k), mostrando que la tarea puede resolverse **de forma descentralizada bajo las reglas diseñadas**. No es aprendizaje autónomo de ese algoritmo.",
"",
"Los agentes de aprendizaje disponen de una política con tres pesos privados por individuo. Se entrena con recompensa de complementariedad LOCAL y REINFORCE, durante 24 episodios (8 por cada k=2,3,4), manteniendo pesos entre episodios. Los pesos no se actualizan en test; sí lo hace la memoria de observaciones. Las características de estado poco observado, permanencia e imitación se diseñaron explícitamente. Por tanto, una eventual generalización es aprendizaje de ponderaciones, no descubrimiento no guiado de conceptos de rareza.",
"",
"## P0 — primera evaluación y resultado negativo",
"",
"Con la representación original de frecuencia local `−f_local`, la política aprendida estabilizó 4/4 casos k2, 4/4 k3 y 0/4 k4 en el piloto conocido. Con el primer conjunto de test k5..8, semillas independientes, obtuvo **0/10 casos estables en cada k nuevo**. La regla manual obtuvo 9/10 k5, 4/10 k6, 2/10 k7, 4/10 k8. El éxito de la regla manual confirma parcialmente factibilidad, mientras el aprendizaje P0 falla la extrapolación.",
"",
"**Hipótesis correctiva registrada después de P0:** al aumentar k, cada color representa menos observaciones locales, pero la bonificación aprendida por conservar el estado no se reescala. Esto podría fijar a los agentes en asignaciones funcionalmente desequilibradas.",
"",
"## P1 — intervención de escala, cohorte nueva y test separado",
"",
"Se modificó exactamente una característica de la política REINFORCE: **`−frecuencia_local` pasa a `−k × frecuencia_local`**. El resto de la red, recompensas, interacciones y entrenamiento se mantuvo constante. Se entrenaron de cero P0 y P1 con los mismos episodios/semillas (cohorte seed20261110) y se abrieron otros datos test k5..8 con semillas 10000+100k+s. Ninguna se entrenó con k>4. El test quedó bloqueado por hashes de modelos y pesos antes de ejecutarse.",
"",
"![Éxitos de extrapolación por k](FIG_P1_HELDOUT.svg)",
"",
"| Funciones nuevas | P0, misma cohorte | P1 escalado por k | Heurística manual |",
"|---|---:|---:|---:|"]
for q in rows:
 report.append(f"| {q['k']} | {q['P1_control_success']}/10 | {q['P1_scaled_success']}/10 | {q['P1_manual_success']}/10 |")
report += [
"",
"![Distancia TV media en tareas nuevas](FIG_P1_TV.svg)",
"",
"| k | TV P0 original | TV P1 escalado | TV heurística |",
"|---|---:|---:|---:|"]
for q in rows:
 report.append(f"| {q['k']} | {fmt(q['P1_control_mean_TV'])} | {fmt(q['P1_scaled_mean_TV'])} | {fmt(q['P1_manual_mean_TV'])} |")
report += [
"",
"En el conocido k4, P1 pasó del 0/4 del control P0 al 4/4. En el test nuevo k5, P1 obtuvo 10/10 frente a 0/10 de P0; en k6, 6/10 frente a 0; en k7, 3/10 frente a 0; en k8, 1/10 frente a 0. Las tasas se obtuvieron tras haber fijado el factor k, no a partir de una búsqueda de los mejores ejemplos. **El efecto sigue siendo descriptivo de una sola cohorte de entrenamiento por condición**, con diez semillas de episodio por k.",
"",
"## Interpretación mecanicista",
"",
"[Inferencia] La intervención demuestra en este simulador que **la escala de la representación local** importa para la generalización a un número nuevo de roles. Una política puede aprender un comportamiento suficiente para k2/3 que no se transporta a k5..8, y mejorar sustancialmente al recibir una característica invariante en escala relativa. Esto no implica la existencia de grokking; no observamos el patrón de memorización temprana, generalización tardía y transición duradera.",
"",
"La normalización por k es **ingeniería de características introducida por el investigador**, no una generalización conceptual que el sistema descubra por sí mismo. La política conserva otros inductive biases y utiliza una recompensa local de complementariedad que el investigador definió. La extrapolación pierde fiabilidad al elevar k; un grado4 y una conversación por agente/tick limitan la información disponible. Variar el grado o el presupuesto comunicativo sería otra intervención, que necesitaría un nuevo protocolo.",
"",
"## Controles, auditoría y limitaciones",
"",
"El modelo pasó diez pruebas automáticas de invariantes, entre ellas restricciones de mensajería, reproducibilidad, cambios de estado legales para k nuevo y ausencia de censo global en la política. Los streams de emparejamiento y acciones son independientes, para que el mismo seed fije las mismas oportunidades de interacción en ambos brazos.",
"",
"Los resultados P0 y P1 no constituyen replicaciones independientes de muchos entrenamientos; la comparación tiene **una cohorte entrenada por brazo**, y los diez episodios por k solo reflejan variabilidad de condiciones iniciales y emparejamientos de esa política. Se requieren varias cohortes y otra familia de redes/tareas para una conclusión general. Las características de rareza y la recompensa local facilitan la coordinación; distinguir aprendizaje de ejecución de heurística permanece esencial.",
"",
"## Reproducción y continuación",
"",
"Archivos model.py, model_p1.py, pilot_known.py, heldout_k.py, experiment_p1.py, test_model.py y report_p1.py; protocolos PROTOCOL_V0.md, PROTOCOL_P1_SCALE.md y QUEUE.md. Datos exactos en results_p0 y results_p1, con hashes de políticas y seeds de test. El estudio G0 se documentará por separado; experimenta difusión intergeneracional de una **regla ya codificada** (PROTOCOL_TURNOVER_V0.md), no aparición emergente de grokking social.",
]
(ROOT/"REPORT_P0_P1.md").write_text("\n".join(report)+"\n",encoding="utf-8")
(ROOT/"RESULTS_P0_P1_AUDIT.json").write_text(json.dumps({
 "status":"PASS",
 "P0_novel_results":len(p0["test_outcomes"]),
 "P1_novel_results":len(p1["test_raw"]),
 "P1_initial_model_sha256":p1["lock"]["model_p0_sha256"],
 "P1_scaled_model_sha256":p1["lock"]["model_p1_sha256"],
 "new_seed_ranges_disjoint":set(z["seed"] for z in p0["test_outcomes"]).isdisjoint(set(z["seed"] for z in p1["test_raw"])),
 "P1_novel_k_train_excluded":set(p1["lock"]["train_k"]).isdisjoint(set(p1["lock"]["eval_k"])),
 "study_scope":"One policy-training cohort per arm; descriptive, local reward engineered"},ensure_ascii=False,indent=2),encoding="utf-8")
print("REPORT_P0_P1_DONE",len(rows),len(report),flush=True)
