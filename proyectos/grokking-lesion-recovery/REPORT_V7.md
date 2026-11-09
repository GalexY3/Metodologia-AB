# Estado del experimento de daño y recuperación a capacidad equiparada

**Fecha:** 2026-11-09. **Ámbito:** piloto exploratorio computacional. **PC:** DESKTOP-I4SULKD, Python/PyTorch CPU en la ejecución observada. **Carpeta:** `C:\Programación\grokking_lesion_20261109`.

## Pregunta correcta del investigador

Comparar dos sistemas con igual nivel de acierto y arquitectura, uno que adquiere esa competencia mediante semigrokking tardío y otro que aprende gradualmente sin haber experimentado grokking, para estudiar si la **historia de adquisición** influye sobre robustez y capacidad de reconstrucción tras una lesión neuronal permanente.

**Respuesta al corte: la comparación principal A semigrokking genuino vs B sin grokking no se ha conseguido todavía**. Ninguna comparación de este piloto demuestra la influencia causal del grokking.

## Qué se ha ejecutado

1. Laboratorio MLP de 300 neuronas, primer barrido y lesiones: 16 condiciones iniciales, 15 lesiones; primeros resultados y restricciones en `analysis.json` y `REPORT.md`. Un checkpoint de 64,20% cayó hasta 43,19% tras lesión 30/300 y recuperó el 95% de su precisión inicial en 90 actualizaciones para una máscara; no es semigrokking vs gradual.
2. V4 mezcló suma modular y etiquetas aleatorias y probó varios valores de weight decay. El decaimiento elevado WD6 generó generalización progresiva pero redujo accuracy train, impidiendo pareja justa con los demás.
3. V5 ensayó schedules low→high/ high→low sobre la misma tarea, pero los endpoints finales no quedaron emparejados. No aceptados.
4. V6 separó 150 neuronas para la rama modular y 150 para la rama de etiquetas aleatorias, mismo conjunto de datos para todas las condiciones y una arquitectura total de **300 unidades ocultas**. La rama aleatoria crea un techo conocido de precisión global cerca de **61%** y la rama modular puede generalizar completamente. **Esto no es semigrokking intrínseco de Varma et al.**, y se usa únicamente como instrumento de factibilidad de comparación bajo competencia parcial.
5. V7 congeló seeds 0,1,2, weight decay de la rama modular 1.0 vs 2.5, y checkpoint paso 22000, bajo `PILOT_V7_PREREG.md`. Las seis redes terminaron con 100% train y 100% de validación para la rama modular; dentro de cada pareja por seed la precisión global de validación es idéntica:
   - seed0: 61,25% vs 61,25%;
   - seed1: 61,25% vs 61,25%;
   - seed2: 60,625% vs 60,625%.
   Las seis redes son compatibles con generalización tardía, aunque su latencia varía: **WD=2.5 NO se clasifica válidamente como control no-grokking**.
6. V7 realizó **30 ensayos de lesión** (3 seeds × 2 WD × 5 máscaras emparejadas). Cada lesión inutilizó 60 de las 150 neuronas de la rama modular y ninguna de la aleatoria: 20% de la red total, 40% de la rama funcional estudiada. Se entrenó nuevamente durante 650 actualizaciones con **el mismo optimizador nuevo AdamW** (lr 0.001, decay 0.1), y con una continuación sin lesión desde cada checkpoint. Se observó robustez inmediata y recuperación en validación. **Las cinco máscaras de una red no cuentan como cinco modelos independientes.**
7. V8 inicializó las representaciones modulares con componentes seno/coseno como posible control gradual. Esta inicialización no eliminó la fase de generalización tardía en los ensayos observados. WD10–20 de V6 bloqueó aprendizaje; tampoco proporciona control.

## Resultados V7: referencia sólida de factibilidad, no prueba de la hipótesis principal

Medida principal de recuperación exploratoria: área bajo la diferencia `accuracy_clean_validación(control sin lesión) - accuracy_clean_validación(lesionada)` integrada en 650 actualizaciones, en unidades de fracción × actualizaciones. **Menor AUC significa menor déficit acumulado respecto al control no lesionado.** También se analiza el momento en que la red lesionada vuelve a ≥95% de su propia precisión clean anterior a la lesión.

| Semilla | AUC con WD1.0 | AUC con WD2.5 | Diferencia A−B | Daño inmediato limpio WD1.0 / WD2.5 | Recuperaciones WD1.0 / WD2.5 |
|---|---:|---:|---:|---|---|
| 0 | 33.52 | 18.60 | +14.92 | 25.31 / 25.21 pp | 4/5 / 5/5 |
| 1 | 10.53 | 10.05 | +0.48 | 18.65 / 16.25 pp | 5/5 / 5/5 |
| 2 | 8.40 | 11.43 | −3.03 | 14.58 / 22.08 pp | 5/5 / 5/5 |

La diferencia media por semilla de AUC WD1−WD2.5 es +4.12, con **cambio de signo entre semillas**; n independiente de modelos es 3 pares, no 15 pares. El resultado no acredita un efecto robusto. Además, al variar el daño inicial, una recuperación aparente más rápida puede deberse a una lesión menos perjudicial. Se guardaron AUC normalizada por daño y todas las curvas por máscara en `V7_ANALYSIS.json`.

El componente de organización interna se examinó sobre activaciones de la **rama limpia en entrenamiento**, sin usar las etiquetas de test. El *effective rank* calculado por entropía espectral fue WD1.0 / WD2.5: seed0 50.56 / 40.76, seed1 42.37 / 41.32 y seed2 43.23 / 45.94. La fracción de importancia ponderada por activación×norma de salida de las 30 neuronas más influyentes fue sistemáticamente menor en WD2.5 que WD1.0, aunque la recuperación **no** fue más rápida en todas las semillas. Métricas calculadas en `V7_MECHANISM_EXPLORATORY.json`. No se puede inferir mecanismo causal de estas medidas.

## Integridad y limitaciones

La auditoría local `V7_INTEGRITY_AUDIT.json` devolvió PASS: 30 archivos de lesiones, 15 parejas de máscaras iguales, 60/150 unidades limpias enmascaradas permanentemente, misma configuración de reparación y rejilla de 0 a 650 cada 10 pasos, sin valores no finitos y con checkpoints presentes. **No es una réplica independiente**. SHA256 del código queda en el archivo de auditoría.

Las métricas del test del montaje exploratorio se registran dentro del proceso original de entrenamiento, así que ese test **no es un holdout sellado confirmatorio**. Los pares se seleccionaron con condiciones examinadas previamente; los tres seeds del piloto son replicación interna de los settings exploratorios, no prueba estadística general. El contraste WD1 vs2.5 tiene un factor de confusión directo: la propia regularización influye sobre normas, representaciones y robustez, sin necesidad de invocar grokking. Condicionar en accuracy final también puede introducir sesgo de selección y bloquear mediadores.

## Estado del arte adversarial mínimo

Varma et al. (2023/2024) sobre semigrokking intrínseco por competencia de circuitos: https://arxiv.org/abs/2309.02390. Salah & Yevick (2026) sobre dropout/robustez y detectores del grokking: https://link.springer.com/article/10.1007/s11063-026-11843-4. Liang & Li (UAI 2026) sobre mejor *unlearning* postgrokking frente a pregrokking: https://proceedings.mlr.press/v337/liang26b.html. Son antecedentes pertinentes; **originalidad no acreditada**. Revisión en `PRIOR_ART_20261109.md`.

## Conclusiones y puerta científica real

**Resultado confirmado del piloto local:** es posible construir sistemas con la misma precisión condicional y agregada, lesionar sus unidades, cuantificar recuperación con un algoritmo común y observar una heterogeneidad importante incluso al emparejar máscaras. La diferencia inicial de recuperación entre WD1 y WD2.5 **no se replicó con signo uniforme** en las tres semillas.

**No conseguido:** construir un par genuino donde A presente semi-grokking de una operación homogénea y B alcance el mismo desempeño **sin** una transición de grokking, ambos en mesetas persistentes. Debe investigarse la región de tamaño crítico de muestra de los Transformers usados por Varma y explorar controles sin retardo en una tarea idéntica. Antes de inferir dependencia de trayectoria, exigir nueva cohorte de semillas reservadas, definición de periodo de estacionariedad independiente de la lesión, emparejamiento sin contaminación del test y análisis adversarial de alternativas por regularización, norma, estructura y diferencia de daño inicial.

El piloto actual **no es una demostración del nexo grokking→resiliencia**, pero sirve de infraestructura y contraejemplo a generalizaciones apresuradas.

## Archivos clave para continuidad

`PROTOCOL_V3_HISTORY_MATCHED.md` — objetivo original correctamente definido. `EXPLORATION_V4_DESIGN.md`, `PILOT_V7_PREREG.md`, `FOURIER_PROBE_PLAN.md` — preregistros exploratorios. `gated_v6.py` — trainer. `gated_lesion_v6.py` — perturbaciones. `v7_report.py` — agregación. `v7_mechanism_probe.py` — medidas mecanicistas. `v7_integrity_audit.py` — integridad. `V7_ANALYSIS.json`, `V7_MECHANISM_EXPLORATORY.json` y `V7_INTEGRITY_AUDIT.json` — resultados. `gated_runs/` y `gated_lesions/` — pesos, curvas y evidencias originales. No modificar retroactivamente corridas ni criterios.
