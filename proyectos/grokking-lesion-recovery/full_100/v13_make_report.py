"""Prepare a durable V13 report from the audited JSON, no test access."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent
r=json.loads((ROOT/"V13_ANALYSIS.json").read_text(encoding="utf-8"))
assert r["audit"]["status"]=="PASS" and r["audit"]["n_lesioned_runs"]==360
rows=r["dose_summary"]
fmt=lambda v,d=1: f"{v:.{d}f}".replace(".",",")
doc=[
"# V13 — Curva de dosis de ablación neuronal y recuperación funcional",
"",
"**Equipo:** GALEXY_TRAVEL. **Fecha:** 9 de noviembre de 2026. **Estado:** exploratorio, condicionado por el diseño V10–V12. No constituye un experimento causal del grokking.",
"",
"## La pregunta",
"",
"Si dos redes llegan al 100% de acierto mediante trayectorias diferentes y posteriormente comparten el mismo régimen de regularización, ¿cómo cambian su resistencia y su capacidad de recuperación al eliminar porcentajes cada vez mayores de neuronas ocultas?",
"",
"Se entiende por **eliminación** fijar permanentemente a cero la contribución de las neuronas dañadas. El aprendizaje posterior actualiza pesos **supervivientes**: no crece ninguna neurona nueva. Esta es una simulación de reorganización funcional tras ablación, no de regeneración biológica.",
"",
"## Diseño auditable",
"",
"Cinco parejas de modelos elegibles heredadas de V12 (semillas 11, 12, 13, 14 y 18), tarea de paridad de 3 bits relevantes entre 30 y MLP con 300 neuronas ReLU. El brazo A muestra grokking tardío con L1 inicial 1e-5; el B alcanza el 100% más rápidamente con L1 inicial 0,001. Ambos fueron después entrenados durante 4.000 actualizaciones con L1 común 0,0001, terminando con 100% de precisión en validación. **La regularización histórica desigual sigue siendo confusora de cualquier efecto causal de grokking.**",
"",
"Se predefinieron nueve dosis, 10–90% en intervalos del 10%, y cuatro máscaras anidadas por red y dosis, compartidas dentro de cada pareja. En total 360 reconstrucciones con AdamW nuevo LR 0,001, WD=0, CE + L1=0,0001, horizonte fijo de 500 actualizaciones, más controles intactos. Se midió train/val; no se consultó el test de V13. Protocolo en [PREREG_V13_DOSE.md](PREREG_V13_DOSE.md), código en [v13_dose.py](v13_dose.py), registros y auditoría en [V13_ANALYSIS.json](V13_ANALYSIS.json).",
"",
"Las máscaras son observaciones anidadas; la unidad independiente es el **par de redes** (n=5). Máscaras mayores contienen los índices de dosis menores dentro de cada semilla, favoreciendo comparaciones longitudinales de dosis.",
"",
"## 1. Robustez inmediata",
"",
"![Daño funcional inicial según dosis](FIG_V13_DAMAGE.svg)",
"",
"| Neuronas destruidas | Daño A, tardío (pp) | Daño B, rápido (pp) | Diferencia A−B (pp) |",
"|---|---:|---:|---:|",
]
for q in rows:
 doc.append(f"| {q['percent']:.0f}% | {fmt(q['initial_damage_A_pp'])} | {fmt(q['initial_damage_B_pp'])} | {fmt(q['mean_damage_diff_A_minus_B_pp'])} |")
doc += [
"",
"El daño medio aumenta con el número de neuronas eliminadas, pero **dos máscaras con la misma dosis pueden producir efectos muy diferentes**. Algunas destruyen gran parte del rendimiento incluso al 10% y otras apenas lo alteran. Los porcentajes nominales no son equivalentes a una intensidad de daño funcional igual. Por interacciones entre unidades, el acierto de una red particular tampoco tiene que ser monótono al ampliar una máscara.",
"",
"## 2. Recuperación observada hasta 500 actualizaciones",
"",
"![Recuperación por dosis](FIG_V13_RECOVERY.svg)",
"",
"| Dosis | Recuperaron A / lesión efectiva A | Recuperaron B / lesión efectiva B |",
"|---|---:|---:|",
]
for q in rows:
 doc.append(f"| {q['percent']:.0f}% | {q['A_masks_recovered_given_damage']}/{q['A_masks_damaged_gt2pp']} | {q['B_masks_recovered_given_damage']}/{q['B_masks_damaged_gt2pp']} |")
doc += [
"",
"Para distinguir robustez de reconstrucción, se consideran como **lesionadas efectivamente** las ejecuciones cuya precisión cayó inicialmente más de dos puntos porcentuales. La recuperación exige dos observaciones consecutivas con precisión de validación ≥99%. Las ramas que no llegaron dentro de 500 pasos se consideran **censuradas**: eso no es prueba de irreversibilidad absoluta.",
"",
"Con 80% de neuronas eliminadas, solo 5/20 casos efectivos en A y 4/20 en B recuperaron. Con 90%, 0/20 en A y 1/20 en B. La evidencia describe un régimen de recuperación difícil bajo estas restricciones temporales y de optimización, no un umbral general de muerte irreparable. Un seguimiento V13B con máscaras nuevas y 2.000 pasos fue registrado después de observar este resultado, y se documenta aparte.",
"",
"## 3. Déficit acumulado durante la reparación",
"",
"![AUC del déficit](FIG_V13_AUC.svg)",
"",
"| Dosis | AUC A | AUC B | A−B | Redes favorables A / B |",
"|---|---:|---:|---:|---:|",
]
for q in rows:
 doc.append(f"| {q['percent']:.0f}% | {fmt(q['mean_auc_A'])} | {fmt(q['mean_auc_B'])} | {fmt(q['mean_auc_diff_A_minus_B'])} | {q['n_seeds_favor_A']} / {q['n_seeds_favor_B']} |")
doc += [
"",
"La AUC integra el déficit de acierto de la red dañada respecto a su propio control intacto desde 0 hasta 500 pasos; **menor significa menor déficit acumulado**. Combina magnitud del daño inicial y velocidad de reparación; para valorar recuperabilidad condicional también se registró AUC normalizada por daño en máscaras que efectivamente lesionaron ambos brazos.",
"",
"**No emerge una ventaja uniforme por trayectoria.** Para ninguna de las nueve dosis se repite el mismo signo A−B en las cinco semillas. Todas las pruebas exploratorias exactas de inversión de signos arrojan p≥0,25; tampoco corrigen multiplicidad entre las nueve dosis. En dosis de 60–70% se recuperan más lesiones del brazo A, pero esa diferencia varía por red y no demuestra un efecto propio del grokking.",
"",
"## Dictamen principal",
"",
"**La dosis de destrucción y la identidad funcional de las unidades dañadas tienen una asociación clara con la recuperabilidad.** Redes con 100% inicial pueden quedarse sin recuperar el 99% en 500 pasos cuando pierden 80–90% de las unidades. La distinta distribución interna de funciones explica por qué el mismo porcentaje puede representar daños muy diferentes, aunque para atribuir mecanismos concretos harían falta intervenciones adicionales.",
"",
"**No se acredita que el grokking mejore o empeore causalmente la recuperación.** Hay cinco parejas independientes, resultados mixtos por dosis, L1 histórica diferente y una tarea artificial específica. Tampoco se ha probado ausencia de todo efecto de trayectoria ni equivalencia entre modelos.",
"",
"**Siguiente falsador:** [PREREG_V13B_LONG_RECOVERY.md](PREREG_V13B_LONG_RECOVERY.md) fija una extensión exploratoria a 2.000 pasos ante 90% de ablación, con otras máscaras. Si algunas redes tardan más pero sí se recuperan, la escasa recuperación V13 a 500 pasos refleja en parte un límite temporal; si no, solo puede concluirse que no recuperan bajo las condiciones y horizonte estudiados.",
"",
"## Evidencias y reproducción",
"",
"Datos crudos en la carpeta v13_dose_runs, con CSV de los 51 estados temporales y JSON por lesión, controles por red y listado completo de neuronas enmascaradas. Scripts: v13_dose.py, v13_analyze.py, v13_figures.py y v13_make_report.py. **Auditoría automática local PASS, 360/360 lesiones, máscaras emparejadas y anidadas, ningún error de cardinalidad, no finitos ni metadatos detectado**. No equivale a auditoría científica independiente.",
]
(ROOT/"REPORT_V13.md").write_text("\n".join(doc)+"\n",encoding="utf-8")
print("REPORT_V13_DONE",len(doc),"lines",flush=True)
