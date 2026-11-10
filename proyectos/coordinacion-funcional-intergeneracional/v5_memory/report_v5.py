"""Rebuild summary report from the locked V5 holdout, no new simulations."""
import json
from pathlib import Path
R=Path(__file__).resolve().parent
H=R/"holdout"
raw=json.loads((H/"SUMMARY.json").read_text(encoding="utf-8"))
records=raw["rows"]
def find(k,variant,kind):
 result=[v for v in records if v["k"]==k and v["variant"]==variant and v["kind"]==kind]
 if len(result)!=1:raise AssertionError((k,variant,kind))
 return result[0]
def n(x,d=4):return f"{x:.{d}f}".replace(".",",")
lines=[
 "# V5 — Memoria temporal y capacidad neuronal en cooperación multiagente",
 "",
 "**Experimento exploratorio de 10/11/2026**, posterior a los resultados V4. Protocolo congelado en [PREREG_V5.md](PREREG_V5.md), implementación en [agents_memory.py](agents_memory.py), entrenamiento en [train_v5.py](train_v5.py), y evaluación con bloqueo de pesos/código en [evaluate_v5.py](evaluate_v5.py).",
 "",
 "Los cuatro modelos tienen N=36 políticas individuales distintas, diez estados disponibles y objetivo k=2/3/4 estados seleccionados espontáneamente a cuotas iguales, con comunicaciones locales permitidas y recompensa exclusivamente colectiva. Solo se cambian memoria de 1 u 8 turnos y ancho H64/H128 de dos capas neuronales ocultas, sin planificación explícita ni acceso al censo mundial. Un único entrenamiento seed521 por arquitectura, 150 actualizaciones ×12 mundos ×32 turnos. Evaluación con pesos congelados en 100 sociedades nuevas por k, 100 turnos por sociedad. Los mundos de test NO son 100 replicaciones independientes de entrenamiento.",
 "",
 "## Evaluación principal: comportamiento estocástico entrenado",
 "",
 "| k | Memoria | Hidden | Distancia D | D / referencia IID10 | Estados usados, media | Exactos | Estables | Churn último tramo |",
 "|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
for k in (2,3,4):
 for m,h in ((1,64),(1,128),(8,64),(8,128)):
  row=find(k,f"W{m}_H{h}_trained","sample")
  lines.append(f"| {k} | {m} | {h} | {n(row['D_final'])} | {n(row['ratio_iid10'],3)} | {n(row['occupied_final'],2)} | {row['n_exact_final']}/100 | {row['n_stable10']}/100 | {n(100*row['churn_last10'],1)}% |")
for k in (2,3,4):
 row=find(k,"baseline","random_always")
 lines.append(f"Azar uniforme continuo (k={k}): D={n(row['D_final'])}, estados ocupados={n(row['occupied_final'],2)}, estabilidad={row['n_stable10']}/100.")
lines += ["",
 "## Comparación con los mismos modelos SIN entrenar (selección greedy)",
 "",
 "| k | Memoria | Hidden | D sin entrenar | D entrenado | Soluciones exactas entrenadas |",
 "|---:|---:|---:|---:|---:|---:|"]
for k in (2,3,4):
 for m,h in ((1,64),(1,128),(8,64),(8,128)):
  a=find(k,f"W{m}_H{h}_untrained","greedy")
  b=find(k,f"W{m}_H{h}_trained","greedy")
  lines.append(f"| {k} | {m} | {h} | {n(a['D_final'])} | {n(b['D_final'])} | {b['n_exact_final']}/100 |")
lines += ["",
 "## Ablación de memoria con los pesos W8 congelados",
 "",
 "La intervención no_history borra el historial de W8 antes de cada turno, manteniendo arquitectura, pesos y comunicaciones intactos. Una diferencia demuestra dependencia funcional de esa entrada en una política concreta, con posible cambio de distribución; no prueba necesidad universal de memoria.",
 "",
 "| k | Hidden | D W8 normal | D W8 sin historial | Diferencia sin−con |",
 "|---:|---:|---:|---:|---:|"]
for k in (2,3,4):
 for h in (64,128):
  a=find(k,f"W8_H{h}_trained","sample")
  b=find(k,f"W8_H{h}_trained","no_history")
  lines.append(f"| {k} | {h} | {n(a['D_final'])} | {n(b['D_final'])} | {n(b['D_final']-a['D_final'])} |")
lines += ["",
 "## Curvas 0..100 turnos",
 "",
 "Los gráficos incluyen todas las sociedades de cada grupo, no seleccionan una submuestra favorable. D=0 expresa la cuota exacta con solo k estados ocupados.",
 ""]
for k in (2,3,4):
 lines += [f"### Objetivo {k} estados",f"![Evolución temporal k={k}](FIG_V5_k{k}.svg)",""]
lines += [
 "## Interpretación y límites",
 "",
 "La distancia D mide el desajuste de los diez conteos con el mejor subconjunto de exactamente k colores. D bajo no demuestra estabilidad si el churn continúa elevado. El control sin entrenamiento detecta sesgos arquitectónicos que producen repartos aparentes sin aprendizaje. W1/W8 es memoria temporal explícita y no GRU/LSTM ni deliberación o planificación simbólica.",
 "",
 "Un solo entrenamiento por condición y un presupuesto corto de 150 actualizaciones impiden concluir universalmente sobre la capacidad de aprender estrategias. Si existe una señal favorable, hace falta replicar sobre varios seeds de pesos e intervenir sobre la memoria manteniendo fija la política y las condiciones iniciales. C1 sin mensajes no está incluido en este factorial, por lo que no se atribuye ninguna diferencia a la comunicación.",
 "",
 "Todos los JSON individuales, las curvas y los hashes de cierre están disponibles en [holdout](holdout). Los pesos y registros integrales se encuentran en runs/W{1,8}_H{64,128}_C2_seed521_u150.",
 ""]
(R/"REPORT_V5.md").write_text("\n".join(lines),encoding="utf-8")
print("REPORT_WRITTEN",len(lines),"lines",flush=True)
