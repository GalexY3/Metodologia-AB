# V11B — recuperación bajo regularización compartida y misma precisión
Congelado 2026-11-09 **después de analizar resistencia V11**, antes de ejecutar ningún ensayo de reparación con los nuevos checkpoints. Sigue siendo exploratorio.

**Motivo:** la diferencia de daño medio A−B tras quitar 90 neuronas pasó de −11,1568pp antes de continuación común a −0,4830pp tras 4000 pasos compartidos de L1=1e-4, con el 100% validación en los 5 pares. Ahora queremos separar **robustez inicial** y **velocidad de reparación**, evitando elegir solo casos que favorecen un grupo.

**Hipótesis rivales:** H_memoria: persiste diferencia de reparación pese a igual precisión y 4000 pasos comunes; H_normalizacion: desaparece diferencia de reparación en promedio de pares. No se hace inferencia causal sobre el grokking: λ histórica sigue siendo diferente, y postselección de checkpoint a paso9000 se decidió tras V11.

**Diseño fijado:** las cinco parejas originales seed 0..4, checkpoint de `v11_common_runs` a paso 9000 y λ común=1e-4 en los dos brazos; 100% train+val de cada red. Dosis 90/300, máscaras físicas idénticas por parejas y máscaras NUEVAS **semillas 2101..2110** (10 por pareja), no usadas para calibrar V11. Reparación 500 actualizaciones mediante optimizador nuevo AdamW lr=.001 weight_decay=0, **sin término L1** para ambos; control sin lesión mismo optimizador y duración, 10 actualizaciones entre mediciones. Si quitar L1 altera la precisión del control, el AUC de déficit respecto a control y CE sirven de diagnóstico y se reconoce esta vulnerabilidad. Reportar AUC de déficit valid respecto a control y AUC normalizada por daño inicial **solo para máscaras con >2pp de lesión en ambos**; no interpretar recovery=0 cuando no hubo daño. Registrar tiempos a 99% validación en dos mediciones consecutivas y censura de no recuperados. El tiempo de reparación no equivale a robustez inicial.

**Evaluación:** medias sobre máscaras por semilla, diferencias emparejadas por semilla, sin tratar 50 máscaras como n independiente. Analizar sesgo de daño inicial; no descartar en resultado total ninguna máscara por daño; ofrecer sensibilidad restringida a doble lesión >2pp sin considerarla aleatoria confirmatoria.

**Conclusión válida máxima:** si ambas recuperaciones son parecidas, no hay evidencia de una ventaja residual reproducible después de un entrenamiento final común; si difieren, podrían ser efectos residuales de la L1 histórica y de las representaciones, no grokking causal.

**No transferir como conocimiento confirmado de grokking** y guardar resultados completos con informe transparente, incluidas inversiones de signo.
