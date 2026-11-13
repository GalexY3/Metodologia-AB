# V46 — Cooperación aprendida mediante modelización diferenciable del aprendizaje ajeno

36 políticas poblacionales entrenadas desde logitos privados aleatorios (0.05×normal), con 48 agentes independientes, 24 parejas complementarias fijas, duración máxima48, supervivencia q0,95 o control q0,20, coste privado c0,04 y valor de recepción v0,55/3. Un actor dispone de cinco logitos privados para el primer regalo y los cuatro estados de memoria de una ronda. Cada actor maximiza su propio retorno esperado exacto; no se comparte recompensa ni se impone un contrato o sanción. Hay un componente crucial de laboratorio: se conocen las funciones de recompensa y las políticas del compañero para calcular exactamente los gradientes contrafactuales.

Se compara NL exacto (gradiente miope privado), LOLA one-step exacto (diferencia a través de la actualización esperada del otro) y LOOK de parada del gradiente (anticipa el cambio ajeno, pero impide la derivada de influencia). Todas las redes son tabulares de cinco logitos y tienen una representación más estrecha y más interpretable que las MLP de V44–V45. Se calculan expectativas con un proceso de Markov de cuatro estados y horizonte finito48, y se contrasta el cálculo con una implementación Monte Carlo independiente.

## Resultados principales q0,95 al final de 1000 actualizaciones

| Método | Alimento | Donaciones | Mutuas | Retorno causal propio | Individuos positivos (media) | Reciprocadores tipo TFT |
| --- | --- | --- | --- | --- | --- | --- |
| NL α=0 | 0.2002 | 0.0017 | 0.0000 | -0.0310 | 0.0/48 | 0.0/48 |
| LOLA α=1 | 0.3413 | 0.9856 | 0.9716 | +0.0287 | 25.8/48 | 2.8/48 |
| LOLA α=5 | 0.3246 | 0.8696 | 0.7563 | +0.1303 | 42.0/48 | 5.0/48 |
| LOLA α=20 | 0.3387 | 0.9678 | 0.9500 | +0.3204 | 45.0/48 | 33.2/48 |
| LOOK α=1 | 0.2002 | 0.0017 | 0.0000 | -0.0312 | 0.0/48 | 0.0/48 |
| LOOK α=5 | 0.2002 | 0.0016 | 0.0000 | -0.0318 | 0.0/48 | 0.0/48 |
| LOOK α=20 | 0.2002 | 0.0013 | 0.0000 | -0.0346 | 0.0/48 | 0.0/48 |

**Interpretación operativa:** «retorno causal propio» = J_i(forzar una donación en el turno inicial)−J_i(prohibirla), con el compañero libre y las políticas futuras congeladas. J_i incluye propio alimento y descuento temporal, con supervivencia q. Un retorno positivo de ese primer acto muestra que las respuestas condicionales futuras del compañero compensan el coste inmediato. No prueba estabilidad evolutiva bajo sustitución reiterada ni aprendizaje de instituciones.

## Todas las cuatro semillas iniciales de los tratamientos principales

| Semilla | Método | α | Alimento | Mutuas | Retorno causal | Agentes positivos | Positivos tras reemparejar |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 3111 | NL | 0 | 0.2002 | 0.0000 | -0.0311 | 0/48 | 0.0/48 |
| 4111 | NL | 0 | 0.2002 | 0.0000 | -0.0309 | 0/48 | 0.0/48 |
| 5111 | NL | 0 | 0.2002 | 0.0000 | -0.0310 | 0/48 | 0.0/48 |
| 6111 | NL | 0 | 0.2002 | 0.0000 | -0.0310 | 0/48 | 0.0/48 |
| 3111 | LOLA | 1 | 0.3416 | 0.9753 | +0.0284 | 26/48 | 26.0/48 |
| 4111 | LOLA | 1 | 0.3421 | 0.9831 | +0.0289 | 27/48 | 27.0/48 |
| 5111 | LOLA | 1 | 0.3405 | 0.9610 | +0.0307 | 25/48 | 25.0/48 |
| 6111 | LOLA | 1 | 0.3409 | 0.9668 | +0.0268 | 25/48 | 24.7/48 |
| 3111 | LOLA | 5 | 0.3248 | 0.7578 | +0.1318 | 40/48 | 40.2/48 |
| 4111 | LOLA | 5 | 0.3255 | 0.7651 | +0.1224 | 42/48 | 41.9/48 |
| 5111 | LOLA | 5 | 0.3240 | 0.7513 | +0.1466 | 43/48 | 43.1/48 |
| 6111 | LOLA | 5 | 0.3243 | 0.7510 | +0.1202 | 43/48 | 43.2/48 |
| 3111 | LOLA | 20 | 0.3369 | 0.9384 | +0.3018 | 48/48 | 48.0/48 |
| 4111 | LOLA | 20 | 0.3415 | 0.9755 | +0.3143 | 44/48 | 44.0/48 |
| 5111 | LOLA | 20 | 0.3394 | 0.9539 | +0.3283 | 46/48 | 45.9/48 |
| 6111 | LOLA | 20 | 0.3370 | 0.9321 | +0.3374 | 42/48 | 40.8/48 |

Se utilizan exactamente las semillas3111,4111,5111 y6111 en cada condición primaria y se conservan todos los checkpoints finalizados, incluidos los que no dan cooperación. La elección de α se fijó antes de los entrenamientos; no se elige retrospectivamente la semilla o paso con mejor resultado.

## Control mecanístico: anticipación frente a modelación del aprendizaje ajeno

La variante LOOK no deriva a través de la actualización esperada del compañero: el paso anticipado se considera fijo al calcular el gradiente propio. Comparar LOLA con LOOK del mismo α y semilla separa la influencia explícita sobre el aprendizaje ajeno de la simple expectativa de una política rival más entrenada. Los contrastes emparejados completos de alimentación, mutualidad y retorno causal se guardan en CONTRASTES_V46.csv.

## Control negativo de relaciones breves (q0,20)

| Semilla | Método | α | Donaciones | Mutuas | Retorno causal | Individuos positivos |
| --- | --- | --- | --- | --- | --- | --- |
| 3111 | NL | 0 | 0.0023 | 0.0000 | -0.0388 | 0/48 |
| 4111 | NL | 0 | 0.0023 | 0.0000 | -0.0388 | 0/48 |
| 3111 | LOLA | 1 | 0.0023 | 0.0000 | -0.0389 | 0/48 |
| 4111 | LOLA | 1 | 0.0023 | 0.0000 | -0.0389 | 0/48 |
| 3111 | LOLA | 5 | 0.0023 | 0.0000 | -0.0394 | 0/48 |
| 4111 | LOLA | 5 | 0.0023 | 0.0000 | -0.0394 | 0/48 |
| 3111 | LOLA | 20 | 0.0133 | 0.0006 | -0.0054 | 0/48 |
| 4111 | LOLA | 20 | 0.0134 | 0.0006 | -0.0053 | 0/48 |

El efecto de la modelación del otro no se interpreta como moralidad o preferencia social aprendida: la recompensa propia no contiene alimento de terceros. En relaciones de duración breve q0,20, la ventaja futura de recibir regalos puede ser demasiado pequeña para compensar el coste de contribuir, como anticipa la deducción matemática V42 bajo una norma oracular idealizada.

## Prueba física externa y cambio de compañero

Cada uno de los 36 checkpoints congelados fue reproducido en seis semillas ambientales reservadas (990101,990107,990109,990121,990131,990137) mediante una segunda implementación Monte Carlo independiente de la recursión Markov analítica, con 128 sociedades-mundo por semilla, 768 por política. Se exigió error absoluto<0,015 en alimento, tasa de donaciones y regalos mutuos. La intervención causal principal sigue siendo el cálculo exacto (no se extrae del ruido Monte Carlo).

Además se evaluaron12 emparejamientos completos independientes de las48 políticas congeladas en cada condición, sin reentrenar. Estos emparejamientos permutan quién es vecino de quién entre episodios: no conceden movilidad de socios durante una interacción y tampoco tienen cuatro profesiones aprendidas de manera autónoma.

| Modelo | Alimento reemparejado | Mutuas reemparejadas | Retorno causal | Agentes positivos (media) | Fracción de redes ≥24 |
| --- | --- | --- | --- | --- | --- |
| v46_Q95_LOLA5_s3111 | 0.3169 | 0.6610 | +0.1060 | 40.2/48 | 1.0000 |
| v46_Q95_LOLA5_s4111 | 0.3171 | 0.6663 | +0.0961 | 41.9/48 | 1.0000 |
| v46_Q95_LOLA5_s5111 | 0.3159 | 0.6501 | +0.1137 | 43.1/48 | 1.0000 |
| v46_Q95_LOLA5_s6111 | 0.3185 | 0.6795 | +0.1006 | 43.2/48 | 1.0000 |
| v46_Q95_LOLA20_s3111 | 0.3346 | 0.9212 | +0.3084 | 48.0/48 | 1.0000 |
| v46_Q95_LOLA20_s4111 | 0.3349 | 0.9013 | +0.3127 | 44.0/48 | 1.0000 |
| v46_Q95_LOLA20_s5111 | 0.3340 | 0.8942 | +0.3117 | 45.9/48 | 1.0000 |
| v46_Q95_LOLA20_s6111 | 0.3274 | 0.8351 | +0.2850 | 40.8/48 | 1.0000 |

## Criterios preregistrados

| Prueba | Resultado |
| --- | --- |
| h46_primary_any_lola_alpha | cumple |
| h46_lookahead_20_does_not_replicate_lola | cumple |
| h46_low_horizon_negative_control | cumple |
| h46_analytic_vs_monte_carlo_all36 | cumple |
| h46_lola20_partner_reassignment_robust | cumple |

Criterio primario: α>0 con retorno propio causal positivo y al menos24/48 agentes positivos y tasa mutua>0,25 en al menos tres de cuatro semillas, además de alimentación superior a NL en al menos tres de cuatro semillas. El resultado se conserva incluso si aparecen después limitaciones de validez externa: nunca se confundirá con la meta global del proyecto.

## Sensibilidad conductual de las estrategias

El actor tiene cinco logitos separados (primera ronda; estados 00, 01, 10, 11, relativos a acciones anteriores de sí y su compañero). Una política tipo tit-for-tat responde más positivamente cuando la pareja donó en la ronda anterior, siempre controlando la acción propia pasada. El contador «grim_count» del entrenador original V46 codificaba indebidamente este patrón **tipo tit-for-tat** y no la norma irreversible grim-trigger del análisis V42: el contador correcto del informe es `tft_like_agents`, calculado ex novo a partir de los cinco logitos finales. Esta corrección terminológica no altera ninguna política, resultado causal ni gradiente.

## Límites y continuación

[Inferencia] La diferencia entre el gradiente miope y LOLA es compatible con la hipótesis de que los agentes cooperan por interés propio cuando optimizan cómo su comportamiento influye en el aprendizaje ajeno. Pero la observación requiere acceso al cálculo exacto de expectativas y gradientes de terceros; no se han demostrado capacidades reales de inferir ese modelo desde la interacción limitada, ni formación de normas sin esos recursos, ni división ocupacional endógena en poblaciones abiertas.

El optimizador real es Adam lr0,03, mientras α es la magnitud hipotética del paso de aprendizaje de la contraparte; estas escalas no coinciden en general. Las cuatro semillas iniciales constituyen replicación de laboratorio, no muestra estadística representativa de cualquier arquitectura o cultura. Los12 reemparejamientos no equivalen a redes dinámicas dentro de la misma trayectoria.

Fuentes teóricas: Foerster et al. (2018) *Learning with Opponent-Learning Awareness* https://arxiv.org/abs/1709.04326 y Letcher et al. (2019) *Stable Opponent Shaping in Differentiable Games* https://arxiv.org/abs/1811.08469. La segunda referencia discute problemas de convergencia de LOLA; no confundir nuestro éxito de entrenamiento con una demostración universal de estabilidad.

## Reproducción, controles de integridad y SHA256

Preregistro, enmienda de semillas y medición, scripts del motor matemático y de auditoría, archivos JSON sin agregación de cada escenario, CSV, 36 checkpoints con pesos y Adam, pruebas de gradientes privados mediante diferencias finitas y Bellman independiente. SHA256:
PREREG_V46_EXACT_OPPONENT_SHAPING.md: 2191638ac89c26a0439e0f30a5816c8ee391543ba88bbb04f3b3ecdae927e863
AMENDMENT_V46_FROZEN_AUDITS.md: c8e0fdd0cc0405fd1e7c41fad2f6c3a379bc4ca54751216a16b637ef3736c2d8
v46_exact_opponent_shaping.py: 23d5c35eb19637e79695d2d95f85468f3747188835e261799da8bfc7180f8dd4
v46_frozen_audits.py: 86856801ba20dac42a513593e141355f719c41cbc8455c90b9886826a25b657b
v46_batch_audit.py: d034e4d3de8920a49835944a3c788850d5aa5a93db2e1ee74429e783275bbe9f
v46_summarize.py: 9f06c63a4c466de15eaabe2cf85b1dd247e746753071171909164066c30bcc43
test_v46_opponent_shaping.py: 2b383dcc671125dc6997f7ad8c45ec5d7d2528ed10d82e6a1eacb404e7222798
test_v46_frozen_audits.py: e86920fc9e6efec038da311a5299e77599c9021a5e35758891471af5d0cc12e5