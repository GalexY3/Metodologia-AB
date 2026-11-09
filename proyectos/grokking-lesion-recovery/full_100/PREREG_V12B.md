# V12B — réplica prospectiva de reconstrucción postlesión en segunda partición

Registro fijado 2026-11-09 **antes de realizar ensayos de recuperación V12B**, y después de observar robustez V12. Esta fase es un control de recuperación prospectivo con respecto a sus nuevas máscaras, pero las condiciones generales proceden de V10–V11 y no es demostración causal de grokking.

**Cohorte bloqueada:** solo los cinco pares elegibles V12, semillas `[11,12,13,14,18]`, que cumplieron historia operativa y rendimiento train/val 100% al paso6000 y 10000. Misma partición nueva de 20261110; no consultar test antes de cerrar robustez y recuperación en validación.

**Modelos de partida:** checkpoints del paso 10000 de `v12_runs/seed*_prior*/ck_010000.pt`, después de 4000 pasos con L1 común λ=.0001 y AdamW LR=.001. Dos historias A L1 previa 1e-5 con grokking tardío; B L1 previa .001 con generalización más rápida. Ambas 300 unidades y misma inicialización semilla a semilla.

**Lesión:** mascarilla pos-ReLU permanente, 90 de 300 neuronas ocultas. Diez semillas de máscara NUEVAS `3201..3210`, disjuntas del estudio de robustez `3101..3200`; misma identidad de 90 unidades dentro de cada pareja; ningún emparejamiento condicionado por acierto o recuperación.

**Continuación/reaprendizaje:** optimizer AdamW nuevo e idéntico para redes intactas y dañadas, LR=.001 WD=0, pérdida CE de los 500 patrones de entrenamiento más penalización explícita L1 λ=.0001 (mantener regularización final común durante todo el periodo); 500 actualizaciones, medir train/val cada10. Las redes intactas son controles para distinguir reparación de cambios generales en precisión. Ningún gradiente ni métrica test durante el experimento.

**Resultados principales fijados:** (a) daño inmediato en puntos porcentuales de validación, (b) AUC del déficit de accuracy respecto al modelo intacto en 0..500 actualizaciones (menor AUC implica menor déficit), (c) actualización hasta al menos dos evaluaciones consecutivas con accuracy validación>=.99, con censura al paso500; (d) pérdida CE val; (e) AUC normalizada por lesión inicial en máscaras que produzcan daño >2pp en ambos brazos, estrictamente sensibilidad y no estimando principal. Informar diferencia pareada A−B por semilla agregando sus diez máscaras, y luego a través de cinco semillas como únicas unidades de réplica independiente. No excluir máscaras sin daño del resultado aleatorio total: indicarlas como robustez, no regeneración instantánea.

**Criterios de interpretación:** evaluar señal de AUC y heterogeneidad entre semillas; p exacto bilateral por inversión de signos solo exploratorio y condicionado a cinco réplicas. No inferir ausencia de efecto universal por p elevado. Como L1 inicial ha diferido, el efecto causal del fenómeno abstracto 'grokking' **no está identificado** aun con el control L1 final común.

**Test sellado:** al terminar y congelar análisis V12B validación, ejecutar una vez el audit `v12_test_audit.py` sobre checkpoints finales de pares elegibles; no usar test para seleccionar dosis, máscaras ni modelos.
