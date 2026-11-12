# V25. Capacidades productivas multiplicadas y cooperación con cuatro profesiones

Experimento exploratorio 12-11-2026 derivado del teorema V24. Frente al modelo V24, ahora cada persona puede elegir de modo voluntario y dirigido hasta **tres entregas por ronda**, a cualquier vecino, con coste pagado por regalo y sin obligación de distribuirlas. No se emplearon profesores, políticas iniciales preentrenadas, cuotas ocupacionales ni funciones de bienestar colectivo. Las políticas de roles y donaciones tienen parámetros neuronales privados y se entrenan simultáneamente con retornos propios.

N=48, cuatro profesiones, red circular de grado 6, 1000 actualizaciones × 12 mundos × 48 rondas para cada una de cuatro condiciones factoriales. Dos semillas neuronales por cada coste unitario final: 0,12 o 0,04. Precio de entrenamiento 0,002 hasta la actualización 500; aumenta hasta el precio final entre las actualizaciones 500 y 800, permanece constante hasta 1000. Evaluaciones de desarrollo siempre usan precio final.

## Resultado congelado fuera de muestra

| Política | Precio/unidad | Alimento | Regalos/persona/ronda | Cobertura material | Plenitud | Entregas útiles | Complementariedad potencial | Sin regalos | Oráculo físico |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v25_N48_C12_s3111 | 0.12 | 0.1999 | 0.0032 | 0.0010 | 0.0000 | 0.9113 | 0.9996 | 0.1998 | 0.6400 |
| v25_N48_C12_s4111 | 0.12 | 0.1999 | 0.0031 | 0.0009 | 0.0000 | 0.8795 | 0.9996 | 0.1998 | 0.6400 |
| v25_N48_C04_s3111 | 0.04 | 0.2026 | 0.0220 | 0.0068 | 0.0000 | 0.9334 | 0.9998 | 0.1998 | 0.8800 |
| v25_N48_C04_s4111 | 0.04 | 0.2018 | 0.0164 | 0.0048 | 0.0000 | 0.8839 | 1.0000 | 0.1998 | 0.8800 |

Seis semillas ambientales reservadas y 16 mundos por semilla y condición, pesos congelados. El oráculo constructivo (0,64 a precio 0,12; 0,88 a precio 0,04) es una asignación explícitamente programada SOLO para demostrar la factibilidad material del entorno, no una política que las redes aprendieran ni un target de entrenamiento. La tasa de entregas útiles se calcula como bienes distintos realmente recibidos divididos entre unidades físicas enviadas.

## Comparaciones con controles

| Política | Normal | Sin historial de ayuda | Personas trasladadas | Mejor movilidad aleatoria | Tasa aleatoria | Donaciones bloqueadas |
| --- | --- | --- | --- | --- | --- | --- |
| v25_N48_C12_s3111 | 0.1999 | 0.1999 | 0.1994 | 0.1988 | role_random_035 | 0.1998 |
| v25_N48_C12_s4111 | 0.1999 | 0.1999 | 0.1994 | 0.1990 | role_random_035 | 0.1998 |
| v25_N48_C04_s3111 | 0.2026 | 0.2027 | 0.2014 | 0.2007 | role_random_060 | 0.1998 |
| v25_N48_C04_s4111 | 0.2018 | 0.2018 | 0.2008 | 0.2002 | role_random_060 | 0.1998 |

Se comparan roles aprendidos con roles fijos, tres tasas de movimiento ocupacional aleatorio y traslado conjunto de las políticas privadas a otras posiciones. La eliminación del historial social en inferencia no implica un reentrenamiento; equivale a una ablación informacional congelada. El bloqueo de todas las donaciones define una línea base física de 0,20 menos costes de movimiento.

## Auditoría causal individual

| Política | Retorno 1 regalo inicial | Personas positivas | Sin información social | Red reconectada | Roles aleatorios | Roles equilibrados |
| --- | --- | --- | --- | --- | --- | --- |
| v25_N48_C12_s3111 | -0.1200 | 0/48 | -0.1201 | -0.1197 | -0.1200 | -0.1200 |
| v25_N48_C12_s4111 | -0.1202 | 0/48 | -0.1200 | -0.1199 | -0.1202 | -0.1202 |
| v25_N48_C04_s3111 | -0.0391 | 0/48 | -0.0399 | -0.0398 | -0.0392 | -0.0392 |
| v25_N48_C04_s4111 | -0.0402 | 0/48 | -0.0400 | -0.0408 | -0.0402 | -0.0402 |

Se fuerza solo una de las tres oportunidades de donación del primer turno para cada individuo y se compara con prohibir esa donación. Las otras dos oportunidades y todos los actos futuros siguen siendo estocásticos bajo redes entrenadas congeladas. Seis semillas ambientales, ocho mundos por semilla y 48 individuos, con control de coste inmediato exacto. Una diferencia de retorno media no equivale a que la mayoría de personas gane.

## Historial del currículo

| Modelo | Actualización | Coste al entrenar | Alimento test coste final | Donaciones/persona test final |
| --- | --- | --- | --- | --- |
| v25_N48_C12_s3111 | 1 | 0.0020 | 0.1820 | 1.5046 |
| v25_N48_C12_s3111 | 250 | 0.0020 | 0.2239 | 0.7351 |
| v25_N48_C12_s3111 | 500 | 0.0020 | 0.2336 | 1.1791 |
| v25_N48_C12_s3111 | 750 | 0.1003 | 0.2007 | 0.0178 |
| v25_N48_C12_s3111 | 1000 | 0.1200 | 0.1999 | 0.0036 |
| v25_N48_C12_s4111 | 1 | 0.0020 | 0.1842 | 1.5015 |
| v25_N48_C12_s4111 | 250 | 0.0020 | 0.2313 | 1.0676 |
| v25_N48_C12_s4111 | 500 | 0.0020 | 0.2230 | 0.7137 |
| v25_N48_C12_s4111 | 750 | 0.1003 | 0.2003 | 0.0156 |
| v25_N48_C12_s4111 | 1000 | 0.1200 | 0.1999 | 0.0035 |
| v25_N48_C04_s3111 | 1 | 0.0020 | 0.3021 | 1.5024 |
| v25_N48_C04_s3111 | 250 | 0.0020 | 0.2829 | 0.7372 |
| v25_N48_C04_s3111 | 500 | 0.0020 | 0.3286 | 1.1888 |
| v25_N48_C04_s3111 | 750 | 0.0337 | 0.2309 | 0.2424 |
| v25_N48_C04_s3111 | 1000 | 0.0400 | 0.2027 | 0.0221 |
| v25_N48_C04_s4111 | 1 | 0.0020 | 0.3039 | 1.4988 |
| v25_N48_C04_s4111 | 250 | 0.0020 | 0.3166 | 1.0670 |
| v25_N48_C04_s4111 | 500 | 0.0020 | 0.2797 | 0.7110 |
| v25_N48_C04_s4111 | 750 | 0.0337 | 0.2116 | 0.0998 |
| v25_N48_C04_s4111 | 1000 | 0.0400 | 0.2019 | 0.0176 |

## Interpretación causal y límites matemáticos

V24 demostró que el sistema anterior de una unidad por persona era estructuralmente incapaz de abastecer completamente a todos los individuos con k=4. V25 elimina esa restricción ofreciendo k−1 oportunidades materiales, pero esto no implica que las políticas puedan coordinar su uso con reciprocidad. El regalo repetido hacia un mismo vecino puede ser redundante y la donación voluntaria debe tener retorno propio suficientemente positivo. El bloqueo de donaciones, la ablación informacional y la auditoría contrafactual permiten distinguir capacidad, acción y reciprocidad.

Los intervalos bootstrap se calculan sobre seis semillas ambientales emparejadas, no sobre millones de inicializaciones de aprendizaje; dos semillas de cada precio no bastan para afirmar prevalencia universal. El gasto contributivo máximo de la condición 0,12 es 0,36 por persona y en 0,04 es 0,12, por lo que son problemas de decisión distintos y se reportan por separado.

## Resultado de la hipótesis

El progreso frente a V24 debe evaluarse sobre mejoras DURADERAS después de la subida al coste final, no por ventajas transitorias del período de entrenamiento barato ni por el oráculo programado. La interpretación queda limitada a las condiciones y grupos realmente auditados. El objetivo general no se considera completado mientras el aprendizaje conjunto no generalice robustamente a cuatro profesiones y diferentes inicializaciones.

## Código, artefactos y verificaciones

Entrenador v25_multi_capacity.py, evaluación v25_holdout.py, contraste forzado v25_causal_audit.py, test_v25_capacity.py, preregistro PREREG_V25_PRODUCTION_CAPACITY.md, checkpoints y logs en runs/v25_N48_*, datos JSON de los ocho escenarios por modelo en results/v25_causal_*.json y datos de movilidad en results/v25_holdout_*.json.

Hash SHA256 del código y preregistros:
v25_multi_capacity.py: 2f968ce9e24be31a42f3500f2c446702947bcad5382bea4660c3b074f1cc37b7
v25_holdout.py: 5fe1494e7e5399f455d8abf23ead77bdcbf9ff22c3f15e2a424b5ba0b3d7fdc8
v25_causal_audit.py: ef4cc8910a363525e6c28dced0db183695344af41be8dfc3204bc3d86a249d81
v25_summarize.py: 598eb7b4d0920d18bcd2422fd17a031ec54e33a4db9892ad42b4ae31aefec9ad
test_v25_capacity.py: f3a09ca5f46e1eb01a7d29e8edcd758d193d6a7b903676e74b92c7a369b6c1a8
PREREG_V25_PRODUCTION_CAPACITY.md: adcd9fcf611fb8b2a92cf038742e0fb4ff51e50d7151cb8b15bb49b1c36e5986
V24_TEOREMA_FACTIBILIDAD.md: 77417f353b2f55656c7c26cb07eede228cca323898212f8686c34f0162b0f2f3