# V14B — ¿la convergencia procede de seguir aprendiendo o de reiniciar AdamW?

**Protocolo exploratorio fijado tras analizar V14**, antes de las nuevas continuaciones V14B. V14 mostró que cuatro mil pasos adicionales reducen casi por igual la brecha de robustez, tanto con L1 histórico original como con L1 igualado o cruzado. En V14 se creó un optimizador AdamW nuevo en cada rama: aún es posible que parte de esa convergencia proceda de reiniciar su estado (momentos adaptativos), no de la mera continuidad del entrenamiento.

## Comparación emparejada desde los mismos pesos

Se usan exclusivamente cinco parejas de redes iniciales elegibles de V12 (semillas 11,12,13,14,18), checkpoints al paso 6000 con 100% de train/val, tarea paridad3/30 y MLP de 300 unidades. Para cada una de las diez redes, se preserva su L1 de adquisición original (grupo A 1e-5; B .001) y se realizan **4000 actualizaciones adicionales** con el mismo conjunto train y CE+L1.

- Brazo V14 *optimizer reset*: ya ejecutado, AdamW nuevo con LR=.001 y wd=0, mismo L1 original.
- Brazo V14B *optimizer continuation*: partir de los mismos pesos **y restaurar exactamente los momentos, contador y demás estado de AdamW** del checkpoint 6000, manteniendo LR=.001, wd=0 y el mismo L1 original.

No elegir modelos basándose en vulnerabilidad. Verificar estado optimizer disponible; no inventar su restauración si archivo es incompleto. Guardar al paso10000, curva train/val cada500 y protocolo.

El gate de comparación exige train y validación=100% en al menos tres últimas mediciones. Reportar fallos de gate como resultados. No consultar test. El estado de optimizer solo se altera según intervención predefinida.

## Medición de robustez y mecanismo

Aplicar las MISMAS 100 máscaras físicas nuevas de V14 semillas4301..4400 (90/300 neuronas), en cada modelo y en cada rama; los resultados de V14 están congelados antes de V14B. Esta reutilización es un **control post hoc de continuidad del optimizador**, no confirmación con máscaras independientes. Medir daño inmediato val accuracy, CE, concentración de importancia neuronal y margen correcto de clasificación (media, mediana y decil10). Comparar diferencias A−B antes del entrenamiento, después del entrenamiento con optimizer nuevo y después del optimizer original, primero por red y después por 5 pares.

**Estimando:** efecto causal computacional del estado de optimizer reiniciado frente al conservado para el mismo modelo, objetivos y duración, no efecto causal del grokking como tal. Si conservar AdamW también reduce brecha, se debilita explicación de artefacto de reset; si solo el reset reduce brecha, este es un mecanismo rival fuerte. Las inferencias sobre márgenes y concentración son exploratorias y no causalmente identificadas por sí mismas.

La coincidencia de 100% accuracy no garantiza igual margin ni igual función fuera de la muestra. Las máscaras están anidadas, no n=500 independiente; el tratamiento L1 temprano sigue confundiendo historia A/B.
