# V30. Coaprendizaje de intercambios contractuales voluntarios con cuatro profesiones

Informe experimental fechado 12/11/2026. Tras el fracaso de V25 y V26, V30 cambia de forma explícita el régimen institucional. Mantiene donaciones propuestas voluntariamente, dos políticas neuronales privadas por persona, división ocupacional endógena y recompensa estrictamente propia, pero los bienes se entregan y pagan solamente en las parejas donde ambas partes se han propuesto donar mutuamente en la misma ronda. No hay intercambio obligatorio ni planeación de profesiones. El mecanismo de liquidación **se programó como regla externa** y no debe presentarse como una institución inventada por los agentes.

Dos semillas neuronales por tratamiento, n=48, k=4, grado seis, 700 actualizaciones, 12 mundos por actualización, 48 rondas, coste unitario final 0,04, programa inicial de coste reducido hasta u300, transición a precio final entre u300 y 500, y 200 actualizaciones adicionales a precio final. Comparación emparejada frente a entregas unilaterales costosas aprendidas con la misma arquitectura, semillas y calendario.

## Evaluación congelada fuera de muestra

| Política | Alimento | Propuestas/pers. | Contratos efectivos/pers. | Fracción aceptada | Cobertura | Mejor rol aleatorio | Ventaja sobre aleatorio | Bloqueo de contratos |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v30_MUTUAL_C04_s3111 | 0.3440 | 2.9667 | 1.0962 | 36.9% | 0.3357 | 0.3328 | +0.0113 | 0.1997 |
| v30_MUTUAL_C04_s4111 | 0.3428 | 2.9665 | 1.0919 | 36.8% | 0.3330 | 0.3319 | +0.0110 | 0.1997 |
| v30_UNILATERAL_C04_s3111 | 0.2025 | 0.0211 | 0.0211 | 100.0% | 0.0065 | 0.2004 | +0.0020 | 0.1998 |
| v30_UNILATERAL_C04_s4111 | 0.2027 | 0.0229 | 0.0229 | 100.0% | 0.0070 | 0.2008 | +0.0019 | 0.1998 |

Los controles incluyen seis semillas ambientales reservadas, doce mundos por semilla y condición, rol fijo, movilidad aleatoria a varias tasas, bloqueo total de propuestas, ablación de historial social, traslado de personas y red reconectada. El número de propuestas no equivale a la cantidad de bienes: una propuesta no aceptada no se ejecuta ni genera coste. La tasa de aceptación cuenta unidades acordadas por propuesta emitida; las propuestas repetidas a un mismo vecino se liquidan como máximo una vez.

## Causalidad individual de ofrecer un contrato

| Política | Retorno total | Efecto inmediato | Efecto futuro | Agentes positivos | Sin historial | Red reconectada |
| --- | --- | --- | --- | --- | --- | --- |
| v30_MUTUAL_C04_s3111 | +0.0330 | +0.0327 | +0.0004 | 48/48 | +0.0332 | +0.0334 |
| v30_MUTUAL_C04_s4111 | +0.0346 | +0.0325 | +0.0022 | 48/48 | +0.0328 | +0.0328 |
| v30_UNILATERAL_C04_s3111 | -0.0393 | -0.0400 | +0.0007 | 0/48 | -0.0399 | -0.0401 |
| v30_UNILATERAL_C04_s4111 | -0.0397 | -0.0400 | +0.0003 | 0/48 | -0.0400 | -0.0400 |

Intervenir en una oferta individual al comienzo de la simulación cambia la probabilidad de celebrar un contrato solamente si el vecino también ha ofertado. En el régimen unilateral forzar la oferta ocasiona de manera inmediata −0,04 sin beneficiar simultáneamente al donante. En el régimen contractual el efecto puede ser positivo de inmediato porque un acuerdo genera dos entregas recíprocas y ambas partes reciben un bien potencialmente útil. Esto es **un juego institucionalmente diferente**; la comparación no identifica un mayor altruismo en las políticas.

En k=4 la primera nueva categoría material recibida vale 0,55/3 ≈0,1833 raciones, antes de bonificación de 0,25 por completar las tres. Un contrato que aporta exactamente una categoría complementaria útil a cada parte tiene ganancia material inmediata de 0,1833−0,04≈0,1433 por persona. Una oferta no correspondida no se liquida ni tiene coste. La regla institucional hace que el intercambio beneficioso sea compatible con el interés propio inmediato y puede evitar el problema de reciprocidad diferida de V25. No hay garantía de que la política aprenda a encontrar socios compatibles o de que todos los agentes ganen.

## Dependencia social, identidades y redes

| Política | Alimento circular | Sin historial | Personas permutadas | Red reconectada | Potencial material | Oráculo constructivo |
| --- | --- | --- | --- | --- | --- | --- |
| v30_MUTUAL_C04_s3111 | 0.3440 | 0.3401 | 0.3365 | 0.3427 | 0.9995 | 0.8800 |
| v30_MUTUAL_C04_s4111 | 0.3428 | 0.3394 | 0.3297 | 0.3374 | 0.9998 | 0.8800 |
| v30_UNILATERAL_C04_s3111 | 0.2025 | 0.2025 | 0.2014 | 0.2012 | 0.9986 | 0.8800 |
| v30_UNILATERAL_C04_s4111 | 0.2027 | 0.2027 | 0.2018 | 0.2016 | 0.9928 | 0.8800 |

La política construida a mano para el oráculo requiere simultaneidad de propuestas mutuas, tres contratos de especialidades distintas por persona y roles balanceados. Su máximo físico a este coste es 0,88. La política programada se usa **únicamente** para comprobar factibilidad y no entrena a los agentes. La distancia entre el alimento conseguido y ese techo revela las oportunidades de mejora de selección de socios y estabilización ocupacional.

## Inferencia estadística y limitaciones

Solo hay dos semillas neuronales por tratamiento. Cada media de evaluación usa seis semillas ambientales y doce mundos por semilla; estos mundos no son replicaciones independientes de redes entrenadas. El bootstrap descriptivo de ventajas mutuo–unilateral se hace sobre las seis semillas ambientales emparejadas y no captura incertidumbre entre arquitecturas, tamaños poblacionales ni nuevas semillas de entrenamiento.

No se declara OBJETIVO COMPLETADO aunque existan mejoras: sigue pendiente la prueba preregistrada de N120/k4 (V31), robustez frente a socios sustituídos, y distinguir emergencia de formas de reciprocidad de una regla contractual creada por el diseñador. Los resultados institucionales no sustituyen los negativos de V24–V26.

## Reproducción

Scripts v30_consensual.py y v30_frozen_audits.py, tests test_v30_barter.py, preregistro PREREG_V30_CONSENSUAL_EXCHANGE.md; configuraciones, modelos y estados en runs/v30_*; mediciones originales results/v30_holdout_v30_*.json y results/v30_causal_v30_*.json.

## SHA256
v30_consensual.py: 6cb46706df94775c6729ea1767a7aeff280e9d5e9def01afbbe0cc80def721a7
v30_frozen_audits.py: 9508fd8b690499a3aac140d313d80e74d05266e2490f3c0a7902e7c8c5f4ced9
test_v30_barter.py: f5be53e56c24434d2f67153eb2f9c3a1c347dfe3611ae7519ca2d13080dc2e06
PREREG_V30_CONSENSUAL_EXCHANGE.md: 5776d41d6875611c370f9a3df0ce7ed7a71316b5eed2a49cd7035fd3c2b37642