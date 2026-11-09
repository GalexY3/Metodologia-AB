# Informe V10C — reconstrucción tras lesiones con daño inicial emparejado

Fecha: 2026-11-09. **Estado:** análisis de sensibilidad exploratorio, realizado después de V10B y no confirmatorio.

## Estimando preciso

Dos regímenes de adquisición de la misma capacidad (red MLP con 300 neuronas ocultas y tarea de paridad de tres bits relevantes entre treinta) alcanzaron 100% de precisión en los conjuntos de entrenamiento, validación y prueba. El grupo A tenía λ L1 = 1e-5 y mostró una meseta prolongada tras memorizar antes de generalizar; el grupo B λ L1 = 1e-3, adquirió una alta precisión de validación mucho antes, sin meseta prolongada según criterio operativo de V10B. Esto NO elimina la posibilidad de que el grupo B tenga otras transiciones; son categorías operativas, no ontológicas.

Tras el resultado V10B de **mayor robustez inmediata** en A frente a una misma lesión física, V10C explora la **recuperación condicional** a una pérdida inicial de capacidad semejante.

## Diseño y bloqueo antes de reparación

El plan `PREREG_V10C.md` quedó fijado antes de ejecutar las lesiones V10C. En cada una de las cinco parejas de semillas, se generaron 1000 máscaras nuevas numeradas 1001..2000 de 150/300 neuronas (50%). La misma máscara física se aplica a los dos modelos de cada pareja. Se eligieron las primeras cinco máscaras por orden numérico que causasen entre 10 y 40 puntos de pérdida en precisión de validación en **ambos** sistemas y una diferencia absoluta no superior a 5 puntos porcentuales. Se congeló `V10C_MASK_SCAN.json` **antes de observar recuperación alguna**.

Se admitieron suficientes máscaras en las cinco semillas. En total se ensayaron 25 pares de máscaras, 50 reconstrucciones; cada reconstrucción duró 400 actualizaciones, con AdamW nuevo idéntico en ambos grupos (lr .001, weight decay 0, sin L1 durante reparación), junto a un control sin lesión para cada red. Se registraron precisión y CE en entrenamiento/validación/test; las máscaras se seleccionaron **solo por daño inicial en validación**.

## Resultados exactos de la ejecución local

| Medida | Grupo A, grokking tardío | Grupo B, aprendizaje rápido |
|---|---:|---:|
| Exactitud antes de la lesión, train/val/test | 100% / 100% / 100% | 100% / 100% / 100% |
| Pérdida inmediata de exactitud de validación (media, pp) | 23,808 | 23,768 |
| Reconstrucciones que alcanzan >=99% durante el horizonte observado | 22/25 | 17/25 |

La medida central de comparación es el área bajo el déficit de precisión en validación respecto a la red intacta, integrada entre 0 y 400 pasos; **menor es mejor**.

| Semilla | AUC A | AUC B | A menos B |
|---|---:|---:|---:|
| 0 | 43,744 | 36,639 | +7,105 |
| 1 | 31,206 | 47,806 | −16,600 |
| 2 | 27,082 | 57,953 | −30,871 |
| 3 | 33,029 | 35,049 | −2,020 |
| 4 | 37,020 | 37,703 | −0,683 |

Promedio de diferencia A−B por semilla: **−8,614** unidades fracción-precisión × actualización. En 4 de 5 pares de semillas el déficit A es menor; en la semilla 0 B presenta mejor resultado. La diferencia media A−B de AUC **normalizada por pérdida inicial**, agregada primero dentro de cada semilla, es −34,984; el signo de esa variante tampoco es uniforme por semilla.

La superposición media de ejemplos erróneos tras la lesión, medida con índice de Jaccard, es **0,183**. Igualar el porcentaje de daño no iguala la identidad de la información dañada, las superficies de pérdida ni la dificultad de reparar cada caso.

## Interpretación y limitaciones críticas

La resistencia inicial superior en V10B y la recuperación condicional favorable a A en buena parte de V10C son observaciones separadas. La segunda **no es una demostración causal** de que el grokking confiera plasticidad. Los regímenes difieren en regularización L1, que puede afectar directamente a la concentración neuronal, parámetros, márgenes y geometría de reparación. El matching sobre daño observado es **post hoc** y puede introducir sesgos de selección/collider; se debe informar junto al efecto total de lesión aleatoria V10B.

Además, solo hay **cinco pares independientes de redes**; las 25 máscaras repetidas están anidadas dentro de esas cinco semillas, no constituyen n=25 independiente. La precisión del 100% fue comprobada en conjuntos de datos finitos; no se ha demostrado corrección sobre todos los 2^30 posibles vectores de entrada. Los datos de test se registraron ya en las etapas exploratorias, de modo que no son un holdout cerrado confirmatorio. La auditoría `V10C_MATCHED_ANALYSIS.json` confirma el cumplimiento del matching, masks emparejadas, etc. Es una auditoría automatizada **local, no independiente**.

**Dictamen:** resultado exploratorio alentador para estudiar dependencia de trayectoria, pero insuficiente para afirmar causalidad o un hallazgo original publicable. Próximo estudio correcto: replicación con semillas y partición nuevas, control de regularización independiente del timing de adquisición, matching por familias de lesiones y calibración de las pérdidas/márgenes, muestras de más arquitecturas y tareas, y evaluación de recuperación condicionada vs total. Conservar ambos resultados, sin escoger únicamente el favorable.

## Artefactos

- `PREREG_V10C.md` y `v10c_scan.py` — selección previa sin consultar los resultados de reparación.
- `V10C_MASK_SCAN.json` — 1000 candidatos por semilla y cinco máscaras seleccionadas por semilla.
- `v10c_repair.py` y `parity_matched_lesions/` — reconstrucciones, curvas completas y controles.
- `V10C_MATCHED_RAW.json` — mediciones individuales, máscaras y conjuntos de errores.
- `analyze_v10c.py` y `V10C_MATCHED_ANALYSIS.json` — auditoría y agregación por semilla.
- `V10_ANALYSIS.json` — experimento V10B con intensidad de daño físico igualada y sin selección en base al daño.
