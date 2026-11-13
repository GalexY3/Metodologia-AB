# V45 — ¿La generosidad inicial favorece aprender una reciprocidad estable?

Ocho nuevos entrenamientos, dos semillas neuronales y dos logitos iniciales exógenos+1,5 (~82% donar) y+3,0 (~95% donar), cruzados con la observación o no del regalo previo del compañero. Se mantiene el motor diádico V44, 24 parejas complementarias, q0,95, coste0,04, actor privado por cada una de48 personas, REINFORCE sin recompensas grupales, contratos ni normas de reciprocidad programadas, 1000 actualizaciones. Los cuatro modelos V44-LONG de logit inicial0 actúan como comparador histórico pareado por semilla, observación y arquitectura. Cambia únicamente el sesgo inicial de regalar.

## Evaluación congelada con seis ambientes nuevos

| Modelo | Sesgo inicial | Prob. inicial | Donación u1 | Donación final | Alimento final | Mutual final | Efecto privado donar | Agentes positivos | Respuesta al otro |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v45_B15_SOC_s3111 | 1.5 | 0.8176 | 0.8144 | 0.1094 | 0.2157 | 0.0117 | -0.0457 | 0/48 | -0.0395 |
| v45_B15_NOSOC_s3111 | 1.5 | 0.8176 | 0.8148 | 0.1557 | 0.2223 | 0.0257 | -0.0408 | 0/48 | +0.0000 |
| v45_B30_SOC_s3111 | 3.0 | 0.9526 | 0.9523 | 0.3441 | 0.2493 | 0.1745 | -0.0483 | 0/48 | -0.0622 |
| v45_B30_NOSOC_s3111 | 3.0 | 0.9526 | 0.9525 | 0.4607 | 0.2660 | 0.2699 | -0.0402 | 0/48 | +0.0000 |
| v45_B15_SOC_s4111 | 1.5 | 0.8176 | 0.8161 | 0.1075 | 0.2154 | 0.0119 | -0.0461 | 0/48 | -0.0366 |
| v45_B15_NOSOC_s4111 | 1.5 | 0.8176 | 0.8156 | 0.1218 | 0.2175 | 0.0132 | -0.0411 | 0/48 | +0.0000 |
| v45_B30_SOC_s4111 | 3.0 | 0.9526 | 0.9525 | 0.1962 | 0.2281 | 0.0722 | -0.0489 | 0/48 | -0.0613 |
| v45_B30_NOSOC_s4111 | 3.0 | 0.9526 | 0.9525 | 0.3450 | 0.2494 | 0.1440 | -0.0399 | 0/48 | +0.0000 |

## Comparación frente a actores idénticos inicializados sin predisposición

| Modelo | Δ causal respecto V44 neutral | Δ comida | Δ donaciones |
| --- | --- | --- | --- |
| v45_B15_SOC_s3111 | -0.0023 | +0.0008 | +0.0058 |
| v45_B15_NOSOC_s3111 | +0.0002 | +0.0057 | +0.0396 |
| v45_B30_SOC_s3111 | -0.0048 | +0.0345 | +0.2405 |
| v45_B30_NOSOC_s3111 | +0.0009 | +0.0494 | +0.3446 |
| v45_B15_SOC_s4111 | -0.0030 | +0.0019 | +0.0136 |
| v45_B15_NOSOC_s4111 | -0.0006 | +0.0026 | +0.0185 |
| v45_B30_SOC_s4111 | -0.0058 | +0.0147 | +0.1023 |
| v45_B30_NOSOC_s4111 | +0.0005 | +0.0346 | +0.2417 |

Comparar cambios netos de política en actualización1000 y no confundir alta comida inicial de una población que dona mucho con cooperación estable por incentivos individuales. Las distribuciones de duración son iguales entre condiciones; el único parámetro inicial distinto es la constante del logito Bernoulli, no la función de recompensa propia.

## Criterios preregistrados

| Criterio | Resultado |
| --- | --- |
| h45a_at_least_2_high_start_private_positive | no cumple |
| h45b_social_high_start_causal_improvement | no cumple |
| h45c_conditional_response_if_success | no aplicable |
| h45d_descriptive_start_bias_implemented | cumple |
| h45c_applicable | no cumple |

H45a exige que al menos dos modelos del grupo+3,0 obtengan retorno propio causal positivo para≥24/48 individuos y tasa de donación mutua>25%. H45b exige ventaja causal≥+0,025 contra las dos referencias neuronales neutrales con historia social. H45c, solo aplicable en caso de H45a, exige respuesta positiva al regalo del compañero y mayor alimento que el control correspondiente sin señal. H45d comprueba el sesgo inicial y describe su evolución.

## Validez y alcance

[Inferencia] Si el incentivo privado de donar sigue siendo negativo después del entrenamiento, incluso partiendo de una población inicialmente generosa, la dificultad parece implicar la construcción de una contingencia creíble de reciprocidad y no solamente la ausencia de una oportunidad inicial de contribuir. Un eventual éxito, por su parte, mostraría aprendizaje condicionado a una predisposición cooperativa externa y no altruismo que surgió enteramente sin ayuda.

La evaluación utiliza 6 semillas ambientales reservadas (980101,980107,980109,980121,980131,980137), pesos finales congelados,32 mundos por semilla y8 mundos en intervenciones forzadas de cada uno de los48 agentes. Las redes no comparten parámetros y no reciben retribución por la comida del grupo. El nombre y sesgo inicial se verifican en v45_status.json de cada entrenamiento.

## Código y reproducción

Preregistro, wrapper v45_bootstrap_dyads.py, entrenamiento original V44, tests, especificación de los ocho tratamientos, checkpoints por actor, auditor v44_frozen_audits.py, CSV y series completas, SHA256:
PREREG_V45_BOOTSTRAP_RECIPROCITY.md: 394386bc1f7b7e69532e99287f191815aa7121c0165c349b9efed7c484a180a2
v45_bootstrap_dyads.py: 351a44fccda0dbc8d2a46d81644c58b85b18a891c310ead434cfb5d7ad3ca726
v45_summarize.py: 704489826955207f7c895bd7cb66db9b2eebd529c4e30f6704586484f084cd8b
test_v45_bootstrap.py: 7d11d3d89cf53fda9877fe9511a3b9ac8a7885dd32d9b50813686484a8d42e8e