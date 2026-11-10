# V3B-L — evaluación nueva, fijada después de 600 actualizaciones y antes de abrir resultados

Fecha 2026-11-10. El experimento es **exploratorio posterior** a la observación negativa del test de 120 actualizaciones (PREREG_V3B_C1C2.md); no se presentará como una hipótesis preconfirmada del diseño inicial. Se inspeccionaron solo las curvas de DESARROLLO de los 600 pasos de optimización (mismas semillas de desarrollo k=2,3,4). Ningún test nuevo se abrió todavía.

**Pesos congelados:** seed 311, checkpoints `runs/v3b_seed311_C1_updates600/FINAL_MODEL.pt` y `runs/v3b_seed311_C2_updates600/FINAL_MODEL.pt`. Ambos: 600 updates, batch12, 24 ticks, hidden24, lr.002, gamma.99, entropy.003, escalado ventaja10, clipping por θ_i; 7200 sociedades de entrenamiento por condición. Ningún crédito individual, crítico central ni peso compartido.

**Test completamente nuevo:** k2,3,4, 100 sociedades por k y condición, red6×6 N36, horizonte120 ticks. Seed de entorno `2690000+100*k`; la misma inicialización física para todas las condiciones por k. Condiciones C1,C2,C3 (C2 sin mensajes en test) y controles random_always, random_T24, stay. Acción probabilística estocástica; ningún gradiente ni selección de checkpoint; presentar todas.

**Métricas predefinidas:** D al final y D media en últimos diez, media de D temporal (AUC), cociente de desequilibrio respecto a expectativa IID exacta, D=0 exacta, tiempo y criterio de estabilidad D≤0,06 y churn≤0,05 durante últimos diez turnos; número de mensajes y coincidencias. El éxito en una sola cohorte de entrenamiento no constituye generalización entre parámetros de agentes independientes.

**Bloqueo técnico:** archivo LOCK.json con SHA256 de script evaluador, política, entorno y modelos antes de ejecutar. Archivos JSON independientes por k y condición; no sobrescribir. El test largo no se usará para elegir hiperparámetros ni lanzar un nuevo checkpoint ocultamente.
