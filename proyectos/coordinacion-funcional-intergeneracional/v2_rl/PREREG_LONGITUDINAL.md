# V2-E — Curvas temporales completas para comparar modelos y aleatorios

**Fecha:** 2026-11-10. Registrado antes de empezar las nuevas trayectorias. El usuario pide ver el avance desde turno 0 hasta la meseta, incluidos aleatorios.

Se usan **exactamente los checkpoints finales ya existentes** de entrenamiento seeds221,222,223; no se reajustan políticas. N=120 en red 10×12, k=2,3,4, batch24 sociedades nuevas por semilla y k, 240 turnos. Seeds nuevos de entornos: 2040000 +1000·seed+100·k. Los escenarios de aprendizaje credit2 (recompensa de equipo + diferencial de entrenador) y credit0 (solo recompensa global) usarán las mismas condiciones iniciales, pero el motor de muestreo de acciones puede diferir. Se incluyen sin entrenamiento y en el mismo entorno «aleatorio continuo», «aleatorio 24 turnos, luego silencio» y «nadie cambia». El aleatorio con parada tiene una **regla temporal impuesta por el investigador**; no atribuir a él conducta adaptativa.

Métrica principal: D(t)=.5 Σ_c |n_c(t)/N-1/k|, TV. Para la visualización también P(t)=100·[1−D(t)/D(0)], valor 0 al inicio y 100 si D=0 exacta. El eje del porcentaje es *reducción del error relativo al inicial*, no porcentaje de decisiones correctas ni exactitud matemática. Unidades: 72 sociedades por k y condición, anidadas bajo tres cohortes de entrenamiento. Comparar la pendiente t=200..240 con el nivel t=160..200; describirla como *aproximación a meseta* cuando cambie poco, no como convergencia teórica demostrada.

Además se registra churn(t), distancia exacta al equilibrio y proporción de sociedades que cumplen criterio de D≤.06 y churn≤.05 en diez turnos consecutivos. Informar aleatorio continuo 0% de estabilidad cuando corresponda, pero no omitir su acercamiento numérico ni el baseline con parada. Se grafican curvas de D y P por k, sin seleccionar cohortes por éxito. Los límites de k≤4 y de políticas compartidas siguen vigentes.

**Control de integridad:** congelar hashes de código/checkpoints antes de ejecutar, no sobrescribir archivos, conservar curvas completas desde t=0. Distinguir modelos que siguen mejorando al paso 240 y *no* afirmar meseta si todavía hay pendiente no despreciable.
