# V37. Aprendizaje de recién llegados mediante retorno material individual en sociedades establecidas

Campaña preregistrada el 12/11/2026 tras el resultado de V35. Se conservan como incumbentes los cuatro modelos V31 con 120 personas y cuatro profesiones, a precios0,04 y0,12. En cada modelo se seleccionan por semilla30 posiciones fijas para nuevos habitantes inicializados sin transferir pesos de los antiguos. Los 90 residentes mantienen su política congelada; las nuevas personas aprenden por su alimento propio mediante REINFORCE durante700 actualizaciones de 12 mundos por corrida. En cada repetición hay 24 rondas con los residentes anteriores y 24 con las nuevas personas, desde la ronda25 hasta48.

El régimen contractual de mutuo consentimiento sigue disponible institucionalmente de modo externo; este experimento prueba aprendizaje individual de adaptación a una institución existente, no evolución natural de normas ni entrenamiento supervisado por residentes.

## Evaluación congelada y emparejada en seis ambientes nuevos

| Modelo | Precio | Control original | Nuevos sin entrenar | Nuevos entrenados | Nuevos crudos | Nuevos formados | Mejora nuevos | Cambio residentes | Excedente recuperado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v37_COHORT_C04_s3111 | 0.04 | 0.3433 | 0.3098 | 0.3440 | 0.2493 | 0.3434 | +0.0941 | +0.0143 | 100.5% |
| v37_COHORT_C04_s4111 | 0.04 | 0.3451 | 0.3080 | 0.3453 | 0.2490 | 0.3454 | +0.0964 | +0.0176 | 100.1% |
| v37_COHORT_C12_s3111 | 0.12 | 0.2540 | 0.2398 | 0.2536 | 0.2145 | 0.2544 | +0.0399 | +0.0051 | 99.2% |
| v37_COHORT_C12_s4111 | 0.12 | 0.2547 | 0.2386 | 0.2546 | 0.2138 | 0.2547 | +0.0408 | +0.0077 | 99.8% |

El control original no incorpora nuevos agentes; los brazos de reemplazo utilizan exactamente los mismos30 puestos y guardan la misma inicialización de sus redes nuevas. Para el contrafactual sin aprender se usan sus pesos iniciales guardados antes de cualquier actualización; para el brazo entrenado, los pesos después de700 actualizaciones. Se restablecen las semillas antes de cada brazo y las 24 rondas anteriores al choque se verifican iguales. No se aplica imitación ni recompensa grupal.

## Contraste de hipótesis preregistradas

| Criterio | Cumplimiento |
| --- | --- |
| H37a aumento de comida de nuevos ≥0,030 en todas las cuatro | sí |
| H37b excedente social recuperado ≥85% en 3/4, con caso caro | sí |
| H37c residentes no perjudicados por nuevos aprendidos en 4/4 | sí |

## Mecanismos y límites

[Inferencia] Si los nuevos mejoran más que los residentes por efecto del entrenamiento sobre su propio alimento, existe una vía de recuperación intergeneracional mediante adquisición individual de competencias dentro de una estructura social preexistente. Sin embargo, los mismos participantes de la cohorte pasan por cientos de episodios experimentales, por lo que la intervención representa aprendizaje acumulado por experiencia replicada, no adaptación completa dentro de un único episodio de 24 rondas. La identidad de los30 puestos es fija por modelo, una dimensión de dependencia contextual todavía sin resolver.

Los seis ambientes nuevos contienen16 mundos cada uno; estos mundos no son inicializaciones independientes de los modelos de entrenamiento. Los intervalos descriptivos bootstrap de ganancia de cohorte y recuperación se re-muestrean sobre seis semillas ambientales apareadas, no sobre los individuos. La variación de costes permite observar la sensibilidad de aprendizaje bajo beneficios económicos distintos.

## Reproducción

Preregistro PREREG_V37_NEWCOMER_RELEARNING.md, script de entrenamiento v37_train.py, auditor v37_audit.py, tests test_v37_cohorts.py, checkpoints de dos actores privados por cada cohorte en runs/v37_COHORT_*, snapshots iniciales guardados, historial y datos crudos por ronda y mundo en results/v37_holdout_v37_*.json. CSV y JSON agrupados en COMPARACION_V37.csv y METRICAS_V37.json.

SHA256:
PREREG_V37_NEWCOMER_RELEARNING.md: 394b0adc7961822d2e1496c98d52ab7fa0965bcc3cf9ce8f183f98b566faef7f
v37_train.py: c4b63dda5daebbdf76f7b74a044bf71e9077ea48fdee16ac2754e4ebde80b32b
v37_audit.py: f87e937e3a0721baafb40f5acb61713f61448b110b42931b57fafe35702de422
v37_summarize.py: 40601094f09c36f81e4d067a76a5db348023c6c0b2c2b815bda3d968d24a09bb
test_v37_cohorts.py: 857716866f9ea3cd4db019653f3599bc72de3a3267d604096e586e14e23fe5eb