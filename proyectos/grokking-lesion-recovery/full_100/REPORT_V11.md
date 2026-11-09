# Informe V11 — control adversarial de regularización, robustez y recuperación al 100 %

Fecha de cierre local 2026-11-09. **Estado: exploratorio, no confirmatorio.** Cinco pares de redes MLP de 300 unidades ocultas entrenadas para predecir la paridad de los 3 primeros de 30 bits. El usuario plantea comparar la restauración funcional de redes que generalizaron tardíamente (grokking) con otras que alcanzaron el mismo 100% de acierto mediante una trayectoria más continua.

## Qué puede interpretarse y qué no

El contraste inicial V10B/V10C usaba regularizaciones L1 distintas desde el inicio: A λ=1e-5, B λ=0.001. Ambas alcanzaron 100% de precisión en muestras de entrenamiento, validación y prueba, pero con tiempos muy distintos para generalizar. V10B observó mayor robustez de A; V10C, tras seleccionar máscaras que producían daños iniciales próximos, favoreció recuperación A en 4 de 5 semillas, con discrepancias entre máscaras y bajo n efectivo.

V11 responde a una objeción central: **la propia regularización puede explicar diferencias de distribución neuronal y de daño independientemente de la presencia de grokking**. La manipulación V11 introduce **4.000 actualizaciones compartidas** después de completar ambas capacidades, con igual L1=0.0001, un nuevo AdamW para ambos, misma función CE+L1 y mismo conjunto de datos. Como contracontrol se prueba también continuar sin L1. Se seleccionó el checkpoint original del paso 5000 donde ambas condiciones estaban al 100% en los conjuntos evaluados.

No identifica el efecto causal *puro* del grokking, porque la regularización anterior difiere y el nuevo entrenamiento cambia las representaciones. Se considera prueba de persistencia frente a homogeneización del entorno posterior.

## V11 — robustez inmediata con 100 máscaras por modelo

Con 90/300 neuronas eliminadas mediante máscaras aleatorias nuevas 2001–2100, la diferencia en puntos porcentuales de daño **A−B** fue:

| Periodo de entrenamiento común L1=0.0001 | Diferencia media A−B en daño (pp) | Semillas elegibles, ambas con 100% validación |
|---|---:|---:|
| Antes, paso5000 | −11.1568 | 5/5 |
| Después de 2000 pasos, paso7000 | −1.6144 | 5/5 |
| Después de 4000 pasos, paso9000 | −0.4830 | 5/5 |

Una diferencia negativa señala mayor robustez A. Las cinco semillas redujeron sustancialmente su diferencia inicial, y al final el signo difirió entre redes. La medida de concentración de contribuciones pasó de una diferencia de número efectivo de neuronas A−B +14.30 (inicio) a alrededor de −1.07 (final). Las redes se hicieron más parecidas en cómo distribuyen la función.

**Contracontrol λ=0**: la condición A mantuvo test de validación cercano a 100% en varias semillas; la condición B empezó a perder generalización aun con training100% (seed0 90.2%, seed1 98%, seed2 82.9%, seed3 99.8%, seed4 84.5% al paso9000). Al dejar de ser 100%-vs-100% este brazo pierde elegibilidad para lesionado comparativo. El deterioro es consistente con reversión a sobreajuste al retirar regularización, tal como se ha descrito en literatura sobre grokking.

**Interpretación V11:** la ventaja de resistencia por historia/régimen histórico **no persiste bajo un periodo suficiente de regularización final idéntica** en esta muestra. Esto respalda como explicación rival que el estado organizativo actual dependiente de la regularización es una variable más próxima que haber vivido una transición tardía. No prueba ausencia universal de efectos históricos.

## V11B — reparación SIN regularización, control diagnóstico

Se ejecutaron 100 lesiones con 90/300 neuronas, máscaras nuevas 2101–2110 y cinco pares de redes ya normalizadas por L1 común. Reparación y control sin lesión, ambos con AdamW nuevo LR=.001 y λ=0, horizonte500.

Resultados exploratorios: pérdida inicial media A=24.566pp, B=21.782pp. AUC del déficit medio A=16.485, B=25.124, diferencia A−B=−8.639, pero signos de ventaja cambiaron entre semillas. Más importante: **el control intacto también perdió en ciertos casos 1–2pp de precisión durante 500 pasos** por retirar la regularización. Por consiguiente esta configuración puede confundir reconstrucción y de-generalización espontánea y se considera diagnóstico, no comparación decisiva.

## V11C — reparación manteniendo la regularización común (control decisivo en este piloto)

Se registró antes de ejecutar con `PREREG_V11C.md`. Los mismos pares finales V11 a paso9000; máscaras nuevas 2111–2120 (diez por pareja), siempre las mismas 90 neuronas eliminadas para cada par. Reparación y control intacto durante 500 pasos con **λ=0.0001 en ambos** y el mismo optimizador fresco AdamW LR=.001. Todos los controles intactos permanecieron en 100% validación.

| Indicador (media sobre 5 redes por grupo) | A, grokking tardío | B, aprendizaje rápido |
|---|---:|---:|
| Precisión prelesión (en validación) | 100 % | 100 % |
| Pérdida inmediata tras lesión | 22.660 pp | 24.416 pp |
| Déficit acumulado de precisión (AUC; menor mejor) | 17.394 | 20.876 |
| Lesiones con pérdida inicial >2 pp | 41 de 50 | 43 de 50 |
| Lesiones recuperadas a >=99% en 500 pasos, entre lesionadas | 40 de 41 | 39 de 43 |

La diferencia media emparejada de AUC A−B es **−3.483**, pero la dirección es heterogénea: en **2 de 5 semillas** A posee menor AUC, en **3 de 5** B posee menor AUC. No se identificó una ventaja uniforme de reconstrucción. La diferencia A−B de AUC normalizada por el daño inicial cuando ambas lesiones superan 2pp es aproximadamente **−1.529**, prácticamente centrada en cero. La prueba exploratoria exacta de inversión de signos sobre las cinco diferencias por red proporciona p bilateral=0.6875: **no existe evidencia suficiente para rechazar la ausencia de diferencia media**, pero no equivale a una prueba de equivalencia.

Los datos de máscaras no son réplicas independientes de redes. La unidad independiente es el par de semillas (n=5), no las 50 perturbaciones emparejadas. Esta y todas las auditorías V11 son **locales, no validaciones independientes**.

## Conclusión provisional clara y susceptible de refutación

**La ventaja inicial de robustez del grupo que pasó por grokking tardío se atenúa casi totalmente después de un entrenamiento común que conserva el 100% en ambos. En ese régimen posterior común, tampoco encontramos evidencia reproducible de mayor velocidad de reconstrucción.** La interpretación de V10C como ventaja específica de *haber pasado por grokking* no queda respaldada por la prueba adversarial V11.

Este es un hallazgo metodológico negativo de los **modelos y condiciones estudiados**. No demuestra que la historia de adquisición nunca importe, ni equivale a demostrar estadísticamente equivalencia, ni acredita que L1 sea el único mecanismo causal. Para una hipótesis general hay que repetir sobre nuevos pares y particiones, manipular trayectoria y regularización de forma factorial sin usar test para selección, y separar mejor clases de errores dañados, CE/márgenes y dosis funcionales. El protocolo de Google PAIR documenta explícitamente que la trayectoria de grokking depende de L1 y de otras condiciones, lo que hace especialmente importante este confusor.

## Archivos y reproducción

- `PREREG_V11.md`, `v11_equalize.py`, `v11_common_runs/`, `v11_robustness.py`, `V11_ROBUSTNESS.json`.
- `PREREG_V11B.md`, `v11b_repair.py`, `v11b_analysis.py`, `v11b_repair/`, `V11B_RAW.json`, `V11B_ANALYSIS.json`.
- `PREREG_V11C.md`, `v11c_repair.py`, `v11c_analysis.py`, `v11c_repair/`, `V11C_RAW.json`, `V11C_ANALYSIS.json`.
- `parity_runs/` con checkpoints originales 5000/8000, necesarios para derivar cohortes. El snapshot portátil conserva checkpoints intermedios 5000 para reproducir V11; no modifica datos originales.
- Toda la investigación está en `C:\Programación\grokking_lesion_20261109`, con copia portátil en GitHub `GalexY3/Metodologia-AB`, rama `research/grokking-lesion-v10-portable-20261109`, ruta `proyectos/grokking-lesion-recovery`.

## Lecturas pertinentes

- Google PAIR (2023): https://pair.withgoogle.com/explorables/grokking/ documenta regularización L1 y posibilidad de vuelta a memorización.
- Liang y Li (2026): https://proceedings.mlr.press/v337/liang26b.html estudian *unlearning* antes/después del grokking. No equivale a nuestra ablación física permanente.
