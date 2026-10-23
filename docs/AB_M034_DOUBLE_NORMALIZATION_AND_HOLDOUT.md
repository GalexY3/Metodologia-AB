# AB-M034 — Instrumentación coherente de la evaluación y selección adaptativa
Fecha 2026-10-22 | Estado PROPUESTA (no modifica AB 3.2.1).

**Anomalía real:** la primera ejecución de 45 decisiones transformó la entrada de evaluación dos veces frente a la de entrenamiento. El hecho de compartir este sesgo entre brazos no garantiza conservar su ranking. Se archivaron los archivos `INVALID_DOUBLE_SCALE_*`; se reparó la aplicación de transformaciones y se reejecutó desde C01 con decisiones recalculadas. La doble normalización afectaba en este experimento principalmente los elementos cerca del clipping: el cambio numérico fue pequeño, pero eso no legitima conservar los números antiguos.

**Propuesta:** para cada procedimiento que transforme información, verificar invariantemente que `transform(train)` y `transform(eval)` usan los mismos parámetros ajustados solo al train, y que ninguna transformación extra es aplicada sólo a evaluación; comprobar predicciones sobre un subconjunto idéntico de train y eval en una prueba de identidad.

**Hallazgo negativo relacionado:** una meta-política escogida por validación pierde en heldout Digits aunque gane en Breast y Diabetes. Añadir gate opcional para probar coste de selección, múltiples dominios y riesgo de selección sobre validación reutilizada. Esto amplía O2 y AB-M030, no demuestra mejor rendimiento de AB.

**Alcance:** los datos proceden de scikit-learn; 45 decisiones secuenciales sobre cuatro dominios no equivalen a 45 replicaciones. `verify.py` comprueba invariantes relevantes, pero no reemplaza una revisión científica externa.
