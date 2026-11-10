# V4 y V4-D — Auditoría del supuesto fallo de recompensa

**Fecha:** 10/11/2026. **Carácter:** auditoría posterior a V4 original y experimento correctivo exploratorio prefijado antes de su entrenamiento (véase PREREG_V4_DELTA500.md).

## Veredicto

**No se encontró el bug matemático propuesto por Gemini**: los agentes no se paralizaron y no hay impedimento de gradiente causado por recompensas negativas cuando se utiliza una línea base de ventaja. El rediseño de señal diferencial es legítimo como intervención experimental, pero el test piloto de 500 actualizaciones NO produjo aprendizaje de coordinación estable. La evaluación exploratoria reservada confirmó cero soluciones exactas y cero sociedades estables en los modelos estocásticos. Tampoco se observa ventaja consistente del canal de mensajes. No se han lanzado 10.000 nuevas actualizaciones delta: no existe evidencia del piloto que justifique esa inversión computacional.

La recompensa original `r=−D_new−0.03*churn` supone penalización 0,03/N por un cambio individual, frente a 1/N mejora en `−D_new` si su intervención reduce D en esa cuantía: 3% del beneficio. El churn registrado a 10.000 actualizaciones es C1≈0,880 y C2≈0,883, cerca del 0,9 uniforme. Por ello fue falso predecir que los modelos se habían inmovilizado. Aceptar la crítica como bug habría provocado un diagnóstico equivocado.

## Evaluación V4-D: recompensa diferencial pura tras 500 actualizaciones

**Configuración:** N36, diez estados disponibles, objetivo endógeno k2..4, hidden64, modelos θ_i independientes, seed421, batch12, T32, Adam .001, gamma .98, 500 updates, C1 sin mensajes y C2 con mensajes. Recompensa única para todos: r=N[D_old−D_new]. Los checkpoints y scripts se bloquean mediante SHA256 antes de abrir test. Las 100 sociedades de cada condición y k pertenecen a una sola cohorte de entrenamiento, no son 100 experimentos de aprendizaje independientes.

| Objetivo | D C1 sin mensajes | D C2 con mensajes | D azar continuo | Estados usados C2 | Exactos C2 | Estables C2 | Churn C2 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2 de 10 | 0,6525 | 0,6497 | 0,6583 | 9,70/10 | 0/100 | 0/100 | 90,2% |
| 3 de 10 | 0,5281 | 0,5256 | 0,5175 | 9,76/10 | 0/100 | 0/100 | 90,1% |
| 4 de 10 | 0,4078 | 0,4086 | 0,4003 | 9,74/10 | 0/100 | 0/100 | 90,1% |

## La selección greedy no implica cooperación

Aquí se muestran las evaluaciones de selección determinista del color con mayor logit. Se usan políticas C2 con recompensa diferencial a 500 updates, políticas C2 originales de recompensa de nivel a 10000 updates y una red C2 sin entrenar. **Los tres grupos proceden de evaluaciones exploratorias de distinta fase y algunas de distintas semillas de mundo; no sirven como experimento causal aislado sobre la recompensa.**

| k | C2 sin entrenar (greedy) | C2 delta 500 (greedy) | C2 nivel 10000 (greedy) |
|---|---:|---:|---:|
| 2 | 0,5169 | 0,5597 | 0,5669 |
| 3 | 0,3897 | 0,4008 | 0,4356 |
| 4 | 0,2936 | 0,2903 | 0,3219 |

Ninguna condición greedy alcanzó reparto exacto ni estabilidad en sus 100 sociedades por k. Elegir siempre la salida con mayor logit puede reducir el churn por construcción o por sesgo inicial, por lo que una mejora respecto a muestrear estocásticamente no demuestra una negociación aprendida. El control posthoc de la red sin entrenar es indispensable para evitar esa falacia.

## Comparación de DESARROLLO estrictamente a la misma actualización 500

El checkpoint V4 original a 10.000 incluye registros de DESARROLLO en actualización 500 y la V4-D delta usa igual seed, batches, N/k/hidden y mundos de desarrollo. Aun así, son muestras pequeñas y los algoritmos tienen distribuciones de acciones distintas.

| Condición | Recompensa | k2 D | k3 D | k4 D | churn de entrenamiento |
|---|---|---:|---:|---:|---:|
| C1 | nivel original | 0,6736 | 0,5174 | 0,4306 | 88,1% |
| C1 | diferencial pura | 0,6771 | 0,5191 | 0,4323 | 89,8% |
| C2 | nivel original | 0,6719 | 0,5156 | 0,4288 | 88,5% |
| C2 | diferencial pura | 0,6771 | 0,5156 | 0,4340 | 89,6% |

## Consecuencias metodológicas

1. La crítica de Gemini acierta al reclamar comparar formas de recompensa, pero se equivoca en el supuesto hundimiento de toda acción por recompensa negativa y en la parálisis inducida. La nueva recompensa N ΔD tampoco es exactamente potential-based shaping invariante a política para gamma=.98, cuya forma aditiva teórica es gamma Phi(s')−Phi(s).
2. La señal de refuerzo compartido entre 36 aprendices independientes sigue mostrando una relación señal-ruido insuficiente con estos presupuestos, aunque no se ha identificado causalmente la fuente. Aumentar capacidad neuronal sin cambiar el procedimiento de entrenamiento puede mantener el problema.
3. Los diez estados disponibles han solucionado el falso positivo de acercarse al reparto uniforme de k colores preseleccionados: el ruido ya no resuelve el objetivo. Ahora es preciso aprender tanto la extinción de etiquetas sobrantes como la regulación de cuotas entre etiquetas supervivientes.
4. No reutilizar condiciones de test para elegir checkpoints, ni atribuir resultados de una sola semilla de entrenamiento a robustez poblacional. Para el siguiente experimento, preregistrar un método de aprendizaje colectivo con mayor eficiencia de muestra (p.ej., lotes mucho mayores con la misma recompensa compartida, tratamiento explícito del crédito temporal, o búsqueda poblacional de políticas individuales mediante fitness de equipo), manteniendo C1 y C2 como controles.

**Archivos inspectables:** `holdout/LOCK.json`, `holdout/SUMMARY.json`; `holdout_delta500/LOCK.json`, `holdout_delta500/SUMMARY.json`; `untrained_greedy_control/LOCK.json`, `untrained_greedy_control/SUMMARY.json`; `runs/tenstates_N36_H64_seed421_{C1,C2}_u500` (config, weights, training logs); `test_delta_reward.py` (5/5 tests).
