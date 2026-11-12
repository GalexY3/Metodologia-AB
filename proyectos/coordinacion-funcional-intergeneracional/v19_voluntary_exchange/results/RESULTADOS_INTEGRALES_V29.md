# V29. Destinatarios recordados, incentivos y sociabilidad privada con cuatro profesiones

Campaña preregistrada el 12/11/2026. Doce entrenamientos desde cero: dos versiones de registro privado del destinatario anterior (solo primer slot propuesto vs todos los destinatarios de regalos efectivamente entregados), dos costos finales de 0,04 y 0,01, grado4 contra grado6 y dos controles entrenados sin señales de ayuda recibida. Se mantiene la capacidad de tres regalos unilaterales, profesión aprendida, N48/k4, REINFORCE individual, parámetros privados y entrenamiento de 850 actualizaciones por inicialización.

La corrección de memoria no modifica recompensas, producción ni transmisión física: 70 tests del directorio de investigación verificaron la conservación junto con otras invariantes. El precio c=0,01 es un entorno más favorable que el coste c=0,04, no una mejora directa de la inteligencia social del actor.

## Evaluación congelada fuera de muestra

| Modelo | Precio | Memoria | Grado | Alimento | Regalos/pers. | Cobertura | Mejor rol aleatorio | Ganancia | Retorno causal | Individuos positivos |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v29_L_D6_C04_s3111 | 0.04 | legacy | 6 | 0.2027 | 0.0229 | 0.0070 | 0.2007 | +0.0019 | -0.0395 | 0/48 |
| v29_L_D6_C04_s4111 | 0.04 | legacy | 6 | 0.2020 | 0.0184 | 0.0054 | 0.2004 | +0.0016 | -0.0404 | 0/48 |
| v29_L_D6_C01_s3111 | 0.01 | legacy | 6 | 0.3389 | 0.9542 | 0.2581 | 0.2976 | +0.0413 | -0.0017 | 21/48 |
| v29_L_D6_C01_s4111 | 0.01 | legacy | 6 | 0.2649 | 0.4459 | 0.1233 | 0.2474 | +0.0175 | -0.0121 | 10/48 |
| v29_P_D6_C04_s3111 | 0.04 | precise | 6 | 0.2021 | 0.0188 | 0.0057 | 0.2004 | +0.0017 | -0.0398 | 0/48 |
| v29_P_D6_C04_s4111 | 0.04 | precise | 6 | 0.2017 | 0.0157 | 0.0047 | 0.2002 | +0.0015 | -0.0401 | 0/48 |
| v29_P_D6_C01_s3111 | 0.01 | precise | 6 | 0.2871 | 0.5889 | 0.1644 | 0.2618 | +0.0253 | -0.0101 | 7/48 |
| v29_P_D6_C01_s4111 | 0.01 | precise | 6 | 0.2312 | 0.2004 | 0.0607 | 0.2222 | +0.0090 | -0.0135 | 8/48 |
| v29_P_D4_C04_s3111 | 0.04 | precise | 4 | 0.2027 | 0.0209 | 0.0069 | 0.2003 | +0.0025 | -0.0397 | 0/48 |
| v29_P_D4_C04_s4111 | 0.04 | precise | 4 | 0.2023 | 0.0178 | 0.0059 | 0.2003 | +0.0020 | -0.0397 | 0/48 |
| v29_P_D6_C01_s3111_NOSOC | 0.01 | precise | 6 | 0.2982 | 0.6452 | 0.1879 | 0.2744 | +0.0237 | -0.0095 | 1/48 |
| v29_P_D6_C01_s4111_NOSOC | 0.01 | precise | 6 | 0.3018 | 0.6851 | 0.1951 | 0.2819 | +0.0199 | -0.0095 | 1/48 |

Para los modelos marcados NOSOC en el nombre, el resultado principal usa evaluación sin señales sociales, ya que durante entrenamiento los actores no dispusieron de ellas. Para el resto se muestra evaluación normal; ambos modos se preservan por separado en CSV. Seis semillas ambientales y doce mundos por semilla, pesos finales congelados en actualización850, sin selección retrospectiva del mejor checkpoint.

## Comparación factorial por semilla y coste

| Cambio de mecanismo | Precio | Semilla | Cambio alimento | Cambio causal |
| --- | --- | --- | --- | --- |
| precise-minus-legacy | 0.04 | 3111 | -0.0005 | -0.0002 |
| precise-minus-legacy | 0.04 | 4111 | -0.0003 | +0.0003 |
| precise-minus-legacy | 0.01 | 3111 | -0.0517 | -0.0084 |
| precise-minus-legacy | 0.01 | 4111 | -0.0337 | -0.0014 |
| degree4-minus-6 | 0.04 | 3111 | +0.0006 | +0.0001 |
| train-nosocial-minus-social-at-nosocial-eval | 0.01 | 3111 | +0.0066 | +0.0002 |
| degree4-minus-6 | 0.04 | 4111 | +0.0006 | +0.0004 |
| train-nosocial-minus-social-at-nosocial-eval | 0.01 | 4111 | +0.0699 | +0.0006 |

Las comparaciones de memoria y topología son pareadas por semilla neuronal, pero solo se ensayaron dos inicializaciones en cada brazo. La ausencia de beneficio causal de donar aun cuando la alimentación se mantiene por encima de 0,20 impide identificar reciprocidad privada autosostenible: pueden existir donaciones no rentables individualmente que elevan el promedio de sus vecinos.

## Interpretación

[Inferencia] El colapso a c=0,04 persiste aun reconociendo todas las personas a las que se enviaron bienes realmente, y con vecinos más concentrados. Una intervención de precio muy bajo mantiene algunos flujos materialmente útiles pero tampoco establece retorno causal positivo en promedio. El control sin historial social puede tener producción colectiva material positiva cuando el precio es muy reducido, lo que impide interpretar cualquier donación como evidencia de aprendizaje de reciprocidad condicionada.

La diferencia entre retornos causales privados y alimento social debe mostrarse siempre: la población puede beneficiarse en promedio de una estrategia que los individuos dejan de elegir cuando la capacitación refuerza su interés personal. Esta tensión se relaciona con la estructura de juego voluntario repetido y el problema de bienes públicos.

## Incertidumbre y reproducibilidad

Doce redes distintas agrupadas por un factorial con solo dos semillas por brazo; los mundos de seis semillas ambientales se comparten dentro del mismo entrenamiento y no son doce réplicas de una supuesta población de redes. La prueba causal impone un regalo en uno de los tres slots frente a impedirlo, dejando todas las otras decisiones aprendidas y estocásticas. Los archivos originales se conservan en runs/v29_* y results/v25_causal_v29_*.json / results/v25_holdout_v29_*.json.

**No se alcanza el criterio de cooperación privada causal robusta con donaciones unilaterales para N48/k4.** Este fracaso coexiste con el éxito institucional V30 y debe conservarse sin fusionar sus mecanismos.

## SHA256
v29_train.py: cff2ccc626e4ecb9e48b9c8d62579806c1ae9b9bc10f9bbcf81ad508e12870c0
v29_eval.py: 568c400a7890e686faa56625b2b03e04986f5c76527fc44c5617c65d0b1d03ce
v29_summarize.py: 683cf209301dc38f8ea384b47774857d83616cc6132afd52ffd0bf44eb53cf33
test_v29_feedback.py: 599dc649f2d1f17e7ea2710933d856033a6009bb6b5e998fe293a08e72b6f7e7
PREREG_V29_RELATIONAL_FEEDBACK.md: a3b8e6fba0ddc53d803f2e49a0d15d910eb31a5078e93a3b9417c1281acdac20