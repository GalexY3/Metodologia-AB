"""Generate version-controlled V12 report from verified experiment outputs."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent
gate=json.loads((ROOT/"V12_GATES.json").read_text(encoding="utf-8"))
rob=json.loads((ROOT/"V12_ROBUSTNESS.json").read_text(encoding="utf-8"))
rep=json.loads((ROOT/"V12B_ANALYSIS.json").read_text(encoding="utf-8"))
test=json.loads((ROOT/"V12_TEST_AUDIT.json").read_text(encoding="utf-8"))
assert rep["audit"]["status"]=="PASS"
assert test["all_test100"] and test["eligible_seeds"]==gate["eligible_for_lesions"]
seeds=gate["eligible_for_lesions"]
r={row["seed"]:row for row in rob["paired_changes"]}
b={row["seed"]:row for row in rep["per_seed"]}
R=rob["summary"]
B=rep["overall"]
f=lambda x:f"{x:.2f}".replace(".",",")
lines=[
 "# V12 — Grokking, robustez y reconstrucción neuronal en una segunda cohorte",
 "",
 "**Fecha de ejecución: 9 de noviembre de 2026. Equipo: GALEXY_TRAVEL. Estado: réplica exploratoria con protocolos fijados antes de los resultados; no es identificación causal ni prueba de equivalencia.**",
 "",
 "## Objeto y diseño",
 "",
 "La investigación compara dos historias de adquisición de una capacidad funcional perfecta sobre datos finitos: generalización tardía tras memorizar (grupo A), y generalización más rápida y sin una meseta larga postmemorización según nuestros criterios operativos (grupo B). El objetivo no es medir si una red más inteligente se recupera mejor; ambas alcanzan 100% antes de la lesión. Se estudia si difiere la vulnerabilidad y la recuperación al inutilizar neuronas internas.",
 "",
 "La tarea consiste en determinar la paridad de los tres primeros de 30 bits de entrada. Se entrenaron redes MLP ReLU con 300 neuronas ocultas. La misma partición nueva de datos, con semilla 20261110, contiene 500 ejemplos de entrenamiento, 1.000 de validación y 2.000 de test reservado. Se utilizaron diez semillas independientes de inicialización, 10–19, compartidas entre los dos tratamientos.",
 "",
 "En la fase de adquisición, el grupo A recibió regularización L1 de 0,00001 y el B de 0,001 durante 6.000 pasos. Solo los pares que cumplieron criterios de trayectoria y conservaron 100% en train y validación pasaron a una fase de 4.000 pasos con un optimizador nuevo y L1 común de 0,0001. **El L1 histórico distinto sigue siendo un potencial factor causal confusor**; la igualación posterior pone a prueba la persistencia de las diferencias, no aísla el grokking como intervención independiente.",
 "",
 "Los criterios se fijaron antes de entrenar la nueva cohorte en [PREREG_V12.md](PREREG_V12.md). Los del estudio de reparación se fijaron antes de ejecutar sus nuevas máscaras en [PREREG_V12B.md](PREREG_V12B.md).",
 "",
 "## Selección de parejas",
 "",
 f"De las diez parejas predefinidas, solo **{len(seeds)}** cumplieron los criterios operativos en ambos grupos: **{', '.join(str(s) for s in seeds)}**. Se conservaron las exclusiones de las otras cinco, que no cumplieron principalmente el criterio de latencia inferior a 1.000 pasos para el control rápido. No se sustituyeron semillas a posteriori. Las diez redes elegibles conservaron 100% de precisión de validación después de la regularización compartida.",
 "",
 "## V12A: robustez inmediata ante ablación",
 "",
 "A cada modelo elegible se le aplicaron 100 máscaras físicas compartidas por pareja (semillas 3101–3200), cada una desactivando 90 de 300 unidades ocultas. Se midió el deterioro inmediato de precisión y pérdida de validación; en esta fase no hubo recuperación. La unidad independiente de análisis es el par de redes, no cada máscara.",
 "",
 "![Diferencia de vulnerabilidad antes y después de un entrenamiento común](FIG_V12_ROBUSTNESS.svg)",
 "",
 "| Semilla | Daño A menos B antes (pp) | Daño A menos B después (pp) | Cambio (pp) |",
 "|---|---:|---:|---:|"
]
for seed in seeds:
 row=r[seed]
 lines.append(f"| {seed} | {f(row['before_difference'])} | {f(row['after_difference'])} | {f(row['change_after_minus_before'])} |")
lines += [
 "",
 f"La diferencia media de daño A−B pasó de **{f(R['before_gap']['mean'])} a {f(R['after_gap']['mean'])} puntos porcentuales**; el desplazamiento medio fue **{f(R['change_after_minus_before']['mean'])} pp**. Una diferencia negativa significa que A resiste más que B. La diferencia se desplazó hacia cero o más allá en las cinco parejas, aunque en una se invirtió de signo, y la brecha absoluta se redujo en cuatro de las cinco. La prueba de inversión de signos bilateral, limitada por n=5, da **p={str(R['signflip_two_sided_exploratory']).replace('.',',')}**; es exploratoria y no una prueba de equivalencia.",
 "",
 "La atenuación descriptiva reproduce lo observado en V11 con una partición de datos e inicializaciones distintas. También se midió concentración efectiva de contribuciones neuronales; sus datos por modelo están en [V12_ROBUSTNESS.json](V12_ROBUSTNESS.json).",
 "",
 "## V12B: reparación bajo el mismo régimen final",
 "",
 "Se utilizó un conjunto nuevo de diez máscaras por pareja (semillas 3201–3210), también de 90/300 neuronas. Las redes dañadas y sus controles intactos siguieron aprendiendo con AdamW nuevo, tasa 0,001 y la misma penalización L1=0,0001 durante 500 actualizaciones. El análisis se realizó exclusivamente sobre entrenamiento y validación. Los controles sin lesión conservaron 100% de validación.",
 "",
 "La medida primaria fue el área acumulada del déficit de precisión en relación con el control intacto (AUC). Una AUC menor representa menor deterioro durante los 500 pasos, combinando intensidad y duración del déficit. Se diferenció de la resistencia inmediata y del tiempo de retorno a al menos 99% de precisión.",
 "",
 "![Déficit acumulado por pareja de modelos](FIG_V12B_RECOVERY.svg)",
 "",
 "| Semilla | AUC A (tardío) | AUC B (rápido) | A menos B |",
 "|---|---:|---:|---:|"
]
for seed in seeds:
 row=b[seed]
 lines.append(f"| {seed} | {f(row['auc_A'])} | {f(row['auc_B'])} | {f(row['auc_A_minus_B'])} |")
lines += [
 "",
 f"El daño inicial de validación fue de **{f(B['mean_initial_damage_A_pp'])} pp en A** y **{f(B['mean_initial_damage_B_pp'])} pp en B**. La AUC media por par fue **{f(B['mean_AUC_A'])} en A** frente a **{f(B['mean_AUC_B'])} en B**, con una diferencia A−B de **{f(B['mean_paired_AUC_A_minus_B'])}**. Pero el signo fue heterogéneo: A tuvo menor déficit en **{B['favor_A_seeds']} de 5** semillas y B en **{B['favor_B_seeds']} de 5**. La prueba exacta bilateral sobre pares dio **p={str(B['exact_signflip_p_two_sided_exploratory']).replace('.',',')}**.",
 "",
 f"En las máscaras que efectivamente redujeron la precisión inicial más de 2 pp, se alcanzó el umbral de 99% en **{B['recovered_A']}/{B['damaged_A']}** lesiones A y **{B['recovered_B']}/{B['damaged_B']}** lesiones B. Esas máscaras son subobservaciones anidadas y las tasas no se pueden tratar como replicaciones independientes ni como estimaciones causales. También pueden estar dañando funciones diferentes a pesar de eliminar las mismas neuronas nominales.",
 "",
 "El mayor déficit medio del grupo A se encuentra muy influido por la semilla 11. En esta réplica, no tenemos evidencia consistente de que una transición tardía confiera mejor capacidad de reconstrucción; tampoco se ha demostrado que la empeore universalmente.",
 "",
 "## Test reservado y control de fuga de información",
 "",
 f"Después de fijar los pares y cerrar los análisis de validación, se ejecutó un único control sobre test: **{len(test['results'])} combinaciones** (cinco pares, dos grupos y dos momentos), todas con **100% de precisión sobre 2.000 ejemplos reservados**. Los resultados de test no se usaron para seleccionar semillas, dosis, máscaras o hiperparámetros. Esto acredita capacidad de generalización sobre los casos observados, no sobre todas las 2³⁰ combinaciones posibles.",
 "",
 "## Interpretación, incertidumbre y límites",
 "",
 "**Resultado replicado:** la diferencia de robustez entre modelos que inicialmente tenían historias distintas se atenúa considerablemente después de compartir un régimen de regularización final, con el rendimiento al 100% en ambos. **Resultado no demostrado:** una mayor velocidad de reparación producida específicamente por haber experimentado grokking.",
 "",
 "La regularización L1 inicial es una explicación rival importante porque actúa directamente sobre la concentración y geometría de los parámetros. Incluso después de compartir L1, las condiciones difieren en su trayectoria y en su estado interno, y una intervención posterior común puede reorganizarlas. Tampoco puede afirmarse ontológicamente que el grupo B nunca experimentó ningún mecanismo de grokking; la categoría es una clasificación operacional por la latencia de generalización.",
 "",
 "Solo cinco pares superaron el filtro, por lo que hay incertidumbre considerable. Las 100 máscaras de robustez y las diez de reparación por red no multiplican el número de réplicas de aprendizaje. El test reservado fue consultado una vez después de cerrar la selección, pero el tratamiento original procede de ensayos exploratorios anteriores. Las conclusiones se limitan a esta arquitectura, tarea, regularización y tipos de lesión. La falta de significación no demuestra equivalencia.",
 "",
 "## Dictamen provisional",
 "",
 "En estas dos cohortes computacionales, **la robustez superior inicialmente asociada al grokking tardío es en buena parte reversible mediante entrenamiento posterior compartido**. No encontramos una ventaja de recuperación funcional uniforme y repetible. Una interpretación parsimoniosa es que la organización actual condicionada por la regularización importa al menos tanto como la historia observable de adquisición, pero esa explicación mecanicista requiere nuevas intervenciones para contrastarse.",
 "",
 "Un siguiente estudio con mayor pretensión causal debería manipular el calendario de aprendizaje independientemente de la penalización final, aumentar réplicas de redes y tareas, y medir también pérdida, márgenes, identidad de casos dañados y gradientes de recuperación. No se declara originalidad científica ni un hallazgo publicable confirmado.",
 "",
 "## Evidencia y continuidad",
 "",
 "Archivos de fase 1 y 2: carpeta [v12_runs](v12_runs). Ensayos de recuperación: carpeta [v12b_repair](v12b_repair). Selección: [V12_GATES.json](V12_GATES.json). Robustez: [V12_ROBUSTNESS.json](V12_ROBUSTNESS.json). Reparación y auditoría: [V12B_RAW.json](V12B_RAW.json) y [V12B_ANALYSIS.json](V12B_ANALYSIS.json). Test: [V12_TEST_AUDIT.json](V12_TEST_AUDIT.json). Los scripts de entrenamiento, análisis y generación del informe se versionan junto a las evidencias.",
 "",
 "Antecedentes principales: Google PAIR (2023), https://pair.withgoogle.com/explorables/grokking/; Varma et al. (2023), https://arxiv.org/abs/2309.02390; Liang y Li (2026), https://proceedings.mlr.press/v337/liang26b.html. Los estudios existentes no deben confundirse con una demostración previa de nuestro contraste exacto.",
]
(ROOT/"REPORT_V12.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
print("REPORT_V12",len(lines),"lines",flush=True)
