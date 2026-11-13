# V44. ¿Aprenden los individuos a devolver favores en relaciones repetidas sin contratos?

Ocho entrenamientos privados REINFORCE independientes desde cero de 48 actores con parámetros no compartidos, organizados en24 parejas profesionales complementarias fijas. No existe contrato, intercambio condicional material, maestro, recompensa grupal ni norma de reciprocidad programada. Cada individuo puede donar o rechazar una sola unidad unilateral en cada turno. Pago propio =0,20+0,55/3×recibe−0,04×envía. Experimento factorial q0,20 (relación corta) vs q0,95 (larga), con vs sin información del regalo previo del compañero, dos semillas neuronales por celda, 1000 actualizaciones.

Se conservan los mismos valores materiales del componente simple de V25 y el planteamiento oracular de V42, pero V44 examina el aprendizaje real de conductas condicionadas, no el equilibrio supuesto de una norma ya conocida.

## Prueba final fuera de muestra

| Modelo | Continuidad | Ve pasado otro | Alimento | Fracción regalos | Fracción reciprocidad mutua | Retorno causal regalar | Agentes positivos | Sensibilidad a regalo previo | Sensibilidad positiva (n) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v44_SHORT_SOC_s3111 | 0.2 | sí | 0.2005 | 0.0031 | 0.0000 | -0.0401 | 0/48 | -0.0010 | 5 |
| v44_SHORT_NOSOC_s3111 | 0.2 | no | 0.2004 | 0.0031 | 0.0000 | -0.0401 | 0/48 | +0.0000 | 0 |
| v44_LONG_SOC_s3111 | 0.95 | sí | 0.2149 | 0.1036 | 0.0118 | -0.0434 | 0/48 | -0.0210 | 4 |
| v44_LONG_NOSOC_s3111 | 0.95 | no | 0.2166 | 0.1161 | 0.0149 | -0.0411 | 0/48 | +0.0000 | 0 |
| v44_SHORT_SOC_s4111 | 0.2 | sí | 0.2004 | 0.0031 | 0.0000 | -0.0402 | 0/48 | -0.0008 | 8 |
| v44_SHORT_NOSOC_s4111 | 0.2 | no | 0.2004 | 0.0031 | 0.0000 | -0.0402 | 0/48 | +0.0000 | 0 |
| v44_LONG_SOC_s4111 | 0.95 | sí | 0.2135 | 0.0939 | 0.0092 | -0.0431 | 0/48 | -0.0205 | 3 |
| v44_LONG_NOSOC_s4111 | 0.95 | no | 0.2148 | 0.1033 | 0.0103 | -0.0405 | 0/48 | +0.0000 | 0 |

El ensayo final reevalúa los checkpoints u1000 sobre seis semillas nuevas (980101,980107,980109,980121,980131,980137), 32 mundos por semilla para alimento y8 para el experimento causal de cada persona. La **enmienda explícita** AMENDMENT_V44_HELDOUT_SEEDS.md reemplaza las semillas inicialmente propuestas porque algunas fueron consultadas en desarrollo durante el entrenamiento. Ninguno de los ocho modelos se selecciona por rendimiento intermedio.

## Contrastes preregistrados y causalidad

| Contraste | Semilla neuronal | Δ comida | Δ regalos | Δ regalos mutuos | Δ retorno causal |
| --- | --- | --- | --- | --- | --- |
| SHORT_social_minus_nosocial | 3111 | +0.0000 | +0.0001 | +0.0000 | -0.0000 |
| LONG_social_minus_nosocial | 3111 | -0.0018 | -0.0125 | -0.0032 | -0.0024 |
| SOC_long_minus_short | 3111 | +0.0144 | +0.1005 | +0.0118 | -0.0033 |
| NOSOC_long_minus_short | 3111 | +0.0162 | +0.1130 | +0.0149 | -0.0010 |
| SHORT_social_minus_nosocial | 4111 | +0.0000 | +0.0000 | +0.0000 | +0.0000 |
| LONG_social_minus_nosocial | 4111 | -0.0014 | -0.0094 | -0.0012 | -0.0026 |
| SOC_long_minus_short | 4111 | +0.0130 | +0.0908 | +0.0092 | -0.0029 |
| NOSOC_long_minus_short | 4111 | +0.0144 | +0.1002 | +0.0103 | -0.0002 |

El efecto causal impone únicamente el regalo del individuo sujeto en t0, manteniendo libre al compañero y dejando que ambos aprendidos reaccionen durante el resto del episodio. Los calendarios de supervivencia de cada mundo y la aleatoriedad neuronal se emparejan en los dos brazos. Se presenta ganancia propia futura descontada y contribución inmediata -0,04: aunque una sociedad reciba algo más de alimento, contribuir podría seguir perjudicando a quien lo hace.

La variable de sensibilidad conductual mantiene fijos regalo propio previo y alimento previo, modifica solamente la señal de que el otro regaló en la ronda anterior, y mide variación de probabilidad neuronal de donar. Es un contraste de política bajo observaciones controladas, no efecto causal longitudinal por sí solo. Si es negativa, el actor es menos generoso al observar que su pareja donó antes, lo cual contradice una reciprocidad positiva simple.

## Hipótesis

| Criterio preregistrado | Resultado |
| --- | --- |
| h44a | no cumple |
| h44b | no cumple |
| h44c | cumple |

H44a requería ≥24 individuos privados causalmente positivos y ≥25% de donación mutua en al menos un modelo de relación larga con observación social. H44b exigía que ambas políticas de relación larga con señal del otro superasen sus controles sin señal en tasa de mutuo regalo y retorno causal. H44c predecía que ninguna de las relaciones muy breves (q0,20) conseguiría ≥24 individuos con retorno privado positivo.

## Interpretación y límites

[Inferencia] Una relación duradera ofrece oportunidades materiales de reciprocidad, pero por sí sola no obliga a que el aprendizaje distribuido descubra un mecanismo de respuesta contingente beneficioso. La diferencia respecto a V42 es explícita: aquel experimento imponía una norma contrafactual idealizada; V44 no la contiene y solo recompensa comida propia.

Las24 parejas, oficios complementarios y disponibilidad de observar el regalo anterior están fijados externamente. Por ello incluso una eventual coordinación exitosa no demostraría división ocupacional endógena ni origen autónomo de instituciones. Solo dos semillas neuronales por tratamiento y seis ambientales para la prueba final; no extrapolar a todas las sociedades.

## Reproducción y SHA256

Scripts v44_private_dyads.py y v44_frozen_audits.py, tests test_v44_dyads.py y test_v44_causal.py, inicializaciones y estados finales de Adam runs/v44_*, datos originales results/v44_{holdout,causal}_*.json, CSV/JSON agregados y preregistro con enmienda.
PREREG_V44_DYADIC_RECIPROCITY.md: 845d3e7236ca2924bd9a0c93c3bcbe271906eceb48b71fb0e5e5a9099f13e0da
AMENDMENT_V44_HELDOUT_SEEDS.md: 9e5e07504eb20d2f1dfdb499754ab4cfe817d3648794919c6d6604e8fd1ba6b3
v44_private_dyads.py: 0f855b08e82427dcda27aeb0e00f6a90a56a6358ea93c62a11a320dbcc83bd94
v44_frozen_audits.py: c3309d4102959473b621149d7447aaac0350a658c8820b196b83241110c61d96
v44_summarize.py: 965e2a14f85de84ae9bab9c37577d09646e9bf4044a34548630ce1efbb5a7097
test_v44_dyads.py: a1925c706f56d60f77f6eabc664584b3c5a41a1ba0c9cbb54fb10e47279a9b61
test_v44_causal.py: 56eddf53fffd598029edea8b21b315e51cf6b86125963e28bbc7978ffda32772