# V32. Coaprendizaje endógeno de adopción contractual, dones y profesiones

Campaña preregistrada el 12-11-2026. N48, cuatro profesiones, 48 rondas, 1000 actualizaciones, seis semillas ambientales fuera de muestra, dos inicializaciones neuronales por tratamiento. Tres políticas privadas sin pesos compartidos por persona se inician aleatoriamente: ocupación, regalo dirigido y selección cada ronda entre intercambiar unilateralmente o por contrato recíproco. Cada una se entrena por retorno propio descontado. La institución contractual es una opción predefinida y su adopción es endógena; no se ha demostrado que las reglas institucionales fuesen inventadas espontáneamente.

## Preferencia contractual aprendida y controles congelados

| Política | Prob. inicial contrato | Adopción final | Alimento aprendido | Modo unilateral forzado | Modo contractual forzado | Modo aleatorio forzado | Rol aleatorio | Sin regalos |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v32_MODENEUTRAL_s3111 | 0.5000 | 0.9998 | 0.3440 | 0.4774 | 0.3441 | 0.3785 | 0.3218 | 0.1997 |
| v32_MODENEUTRAL_s4111 | 0.5000 | 0.9998 | 0.3454 | 0.4835 | 0.3452 | 0.3813 | 0.3198 | 0.1998 |
| v32_MODERARE_s3111 | 0.1192 | 0.9997 | 0.3463 | 0.4710 | 0.3465 | 0.3767 | 0.3071 | 0.1998 |
| v32_MODERARE_s4111 | 0.1192 | 0.9997 | 0.3477 | 0.4761 | 0.3471 | 0.3790 | 0.3125 | 0.1997 |

Se diferencia el efecto de la institución (dos formas diferentes de liquidar bienes) del efecto de la política neuronal que decide cuándo adoptarla. Las comparaciones de modo forzado utilizan exactamente las políticas finales congeladas de los otros dos subsistemas. Una política que elige contratar siempre puede converger hacia uso de una posibilidad del entorno sin aportar nuevo conocimiento sobre invención autónoma de instituciones.

## Intervención causal sobre la elección del contrato

| Política | Efecto total de elegir contrato | Efecto inmediato | Efecto futuro | Personas positivas | Sin historial social | Red reconectada |
| --- | --- | --- | --- | --- | --- | --- |
| v32_MODENEUTRAL_s3111 | +0.2438 | +0.2488 | -0.0050 | 48/48 | +0.2497 | +0.2520 |
| v32_MODENEUTRAL_s4111 | +0.2595 | +0.2472 | +0.0123 | 48/48 | +0.2470 | +0.2529 |
| v32_MODERARE_s3111 | +0.2682 | +0.2454 | +0.0228 | 48/48 | +0.2460 | +0.2499 |
| v32_MODERARE_s4111 | +0.2651 | +0.2482 | +0.0169 | 48/48 | +0.2476 | +0.2507 |

Cada intervención cambia únicamente si un individuo elige contrato frente a donación unilateral al inicio de un episodio, con 47 turnos posteriores de acciones aprendidas bajo políticas congeladas. Se emparentan estados y secuencias pseudoaleatorias, se fuerza cada persona por separado y se informa la proporción que obtiene retorno positivo. La elección contractual no es un regalo obligatorio: una propuesta no correspondida no se ejecuta.

## Robustez y organización ocupacional

| Política | Circular | Red reconectada | Personas permutadas | Sin historia social | Contratos/pers. | Cobertura efectiva | Disponibilidad potencial | Roles 12/12/12/12 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v32_MODENEUTRAL_s3111 | 0.3440 | 0.3420 | 0.3371 | 0.3407 | 1.1039 | 0.3363 | 0.9996 | 0.0000 |
| v32_MODENEUTRAL_s4111 | 0.3454 | 0.3356 | 0.3315 | 0.3414 | 1.1041 | 0.3381 | 0.9995 | 0.0139 |
| v32_MODERARE_s3111 | 0.3463 | 0.3247 | 0.3201 | 0.3401 | 1.1189 | 0.3408 | 1.0000 | 0.0000 |
| v32_MODERARE_s4111 | 0.3477 | 0.3263 | 0.3260 | 0.3411 | 1.1209 | 0.3433 | 1.0000 | 0.0000 |

La cuestión ocupacional no se resuelve por una elevada adopción del contrato. Se exige una diferencia positiva frente a inmovilidad y movilidad aleatoria a igual régimen de donación. La tasa de roles exactamente balanceados no es una condición necesaria para economías complementarias locales, pero sirve para detectar si la distribución adquirida depende de convenciones de posición.

## Inferencia y límites

La evaluación agrupa seis semillas ambientales, doce mundos por semilla y políticas congeladas. Los intervalos descriptivos de alimento entre elección aprendida y modo aleatorio se calculan agrupando por semilla, no contando los individuos ni los mundos como entrenamientos independientes. Solo hay cuatro inicializaciones neuronales, dos por sesgo inicial. La regla de contrato sigue siendo un mecanismo material exógeno; incluso si la adopción es individualmente rentable, no acredita origen endógeno de normas.

El objetivo general sigue abierto hasta contrastar escalas N120, topologías alternativas, reemplazos de personas y una división del trabajo que supere ampliamente controles ocupacionales, de forma no reducible a una institución preprogramada.

## Reproducción

Especificaciones, historiales, pesos y estados del optimizador en runs/v32_*.py y runs/v32_MODE*/; datos originales results/v32_holdout_*.json y results/v32_causal_*.json. Auditor v32_frozen_audits.py, entrenamiento v32_institution_choice.py, pruebas test_v32_institution.py.

SHA256 de código y preregistro:
v32_institution_choice.py: 231b2e8d8756f995948c8a40fa45f5cf022d454a17224a2ca1e04b384548e8e0
v32_frozen_audits.py: 18b05cd97ea6fd32a7e610024ae6a0fd7bba7219711d5cb742b5524d47440421
v32_summarize.py: b01f0e69c854a40ee44e6d9d1e9f1f56b9c3eac1e8d1534de63a495f54503b65
test_v32_institution.py: 7a865edd277d0dc72e7ed12640f75d4098a152ba72e54c1554cc64e043055f7a
PREREG_V32_ENDOGENOUS_CONTRACT_ADOPTION.md: 33917249c08792bdf0967e56c418caaa41cb4d74d50d5de916ca8958f1dffac4