# V33. Aprendizaje prolongado del reparto profesional en economías contractuales

Experimento de continuación preregistrado 12/11/2026. Dos checkpoints V30 ya entrenados desde cero durante 700 actualizaciones fueron continuados por 1400 actualizaciones adicionales a coste fijo final0,04. Cada semilla original se bifurcó en una condición de continuar entrenando donante y actor ocupacional y otra que congeló el donante y entrenó exclusivamente la elección de profesión. Esta es una comparación de cuatro ramas de dos modelos iniciales; las ramas no son inicializaciones independientes.

## Evaluación congelada en sociedades nuevas

| Modelo | Tratamiento | Alimento u700 | Alimento u2100 | Cambio comida | Azar rol u700 | Azar rol u2100 | Ventaja rol u700 | Ventaja rol u2100 | Mejora de ventaja |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v33_JOINT_s3111 | joint | 0.3440 | 0.3472 | +0.0032 | 0.3328 | 0.3356 | +0.0113 | +0.0116 | +0.0004 |
| v33_JOINT_s4111 | joint | 0.3428 | 0.3503 | +0.0075 | 0.3319 | 0.3371 | +0.0110 | +0.0132 | +0.0022 |
| v33_ROLE_ONLY_s3111 | role_only | 0.3440 | 0.3439 | -0.0002 | 0.3328 | 0.3328 | +0.0113 | +0.0111 | -0.0002 |
| v33_ROLE_ONLY_s4111 | role_only | 0.3428 | 0.3427 | -0.0001 | 0.3319 | 0.3319 | +0.0110 | +0.0109 | -0.0001 |

La comparación ocupacional utiliza el mayor alimento de tres tasas de movilidad aleatoria preestablecidas, con las mismas políticas de donación congeladas en el punto evaluado. Los roles profesionales iniciales son monolíticos y la recompensa propia incluye la penalización por cambiar de oficio. Las valoraciones se repiten en seis semillas ambientales reservadas y doce mundos por semilla y condición.

## Mecanismo y límites

En ROLE_ONLY el vector completo de parámetros neuronales donantes al actualizar2100 es bit a bit idéntico al del checkpoint del que se partió (comprobación programática realizada durante la síntesis). En JOINT ambos actores cambiaron pesos. Por tanto, el efecto de ROLE_ONLY no puede atribuirse a mejora del actor donante; el contraste es una prolongación focalizada del aprendizaje laboral.

Una mejora pequeña o nula del rendimiento ocupacional pese al entrenamiento prolongado indica que la arquitectura y la función objetivo quizá permitan ya pocas ventajas adicionales en un anillo de seis vecinos, donde las especialidades complementarias son relativamente accesibles. Esta interpretación exige el contraste topológico V34, pues más tiempo no es equivalente a una red con mayores necesidades de organización.

## Reproducción y criterios

Script v33_continue_barter.py, preregistro PREREG_V33_OCCUPATION_LONG_TRAINING.md, cuatro checkpoints con Adam y trazas runs/v33_*, controles JSON results/v30_holdout_v33_*.json, CSV y METRICAS_V33.json. Fuente histórica V30 y oráculo físico quedan conservados. El criterio fuerte preregistrado requería +0,05 comida de la especialización frente al mejor azar. Las conclusiones no se transfieren por sí solas a N120 ni a vínculos reconectados.

SHA256:
v33_continue_barter.py: acdb1d88a9d492b553af7b9c2faaf8db438c4274e829de050cdba955db71c5f7
v33_summarize.py: 2c275e2fabb9b58783b847da18dcbdca4395c162b0a96446612fd6d67ff30c33
PREREG_V33_OCCUPATION_LONG_TRAINING.md: 572aa2c6b1ce231e6fd3465a39b4388ee44a40ca80a7027ca27ec70ed6fd1287