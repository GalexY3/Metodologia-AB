# V36. Adopción contractual aprendida en redes de escasez local de especialistas

Cuatro entrenamientos desde pesos independientes de cada uno de los 48 habitantes. Condiciones factoriales posteriores a V32 y V34: grado4, cuatro profesiones, elección privada del contrato frente a donaciones unilaterales, sesgos institucionales iniciales 0 y −2, dos semillas neuronales por sesgo. Las mismas políticas independientes y funciones de recompensa V32, 1000 actualizaciones y precio final c=0,04. El único cambio respecto a V32 es la topología de grado4. El mecanismo contractual como posibilidad económica es exógeno; su selección individual es endógena.

## Generalización y comparación profesional contra los tres controles aleatorios

| Modelo | Alimento | Adopción | Mejor rol aleatorio | Ventaja roles g4 | Ventaja roles g6 | Aumento ventaja | Causal elegir contrato | Personas positivas |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v36_D4_MODENEUTRAL_s3111 | 0.3748 | 0.9998 | 0.3352 | +0.0396 | +0.0108 | +0.0288 | +0.2824 | 48/48 |
| v36_D4_MODENEUTRAL_s4111 | 0.3746 | 0.9998 | 0.3381 | +0.0365 | +0.0141 | +0.0224 | +0.2821 | 48/48 |
| v36_D4_MODERARE_s3111 | 0.3777 | 0.9997 | 0.3173 | +0.0604 | +0.0273 | +0.0331 | +0.2829 | 48/48 |
| v36_D4_MODERARE_s4111 | 0.3782 | 0.9997 | 0.3268 | +0.0514 | +0.0236 | +0.0278 | +0.2813 | 48/48 |

En ambos grados, el comparador ocupacional es el mejor de tres tasas preestablecidas de cambio aleatorio de oficio 0,15, 0,35 y 0,60. Las evaluaciones de grado6 para tasas 0,15 y 0,60 se realizaron adicionalmente con los checkpoints V32 congelados, dejando intactos los resultados V32 originales. De este modo los cambios de ventaja ocupacional no se deben a haber escogido un control más fácil en una condición que en otra.

## Contrastes de institución y transferencia

| Modelo | Modo aprendido | Unilateral forzado | Contrato forzado | Modo aleatorio | Sin regalos | Red reconectada | Personas permutadas |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v36_D4_MODENEUTRAL_s3111 | 0.3748 | 0.4800 | 0.3754 | 0.3827 | 0.1998 | 0.3478 | 0.3432 |
| v36_D4_MODENEUTRAL_s4111 | 0.3746 | 0.4741 | 0.3751 | 0.3806 | 0.1997 | 0.3481 | 0.3399 |
| v36_D4_MODERARE_s3111 | 0.3777 | 0.4934 | 0.3778 | 0.3875 | 0.1998 | 0.3251 | 0.3097 |
| v36_D4_MODERARE_s4111 | 0.3782 | 0.4929 | 0.3788 | 0.3877 | 0.1997 | 0.3393 | 0.3349 |

Las intervenciones de modo conservan las políticas donantes y ocupacionales congeladas. La auditoría causal fuerza en una persona la elección contractual frente a unilateral al comienzo del episodio, manteniendo libres sus decisiones posteriores y las del resto. La mejora puede venir de la contraprestación inmediata del contrato; no implica que surja por sí misma la regla que la garantiza. Los resultados se agrupan en seis semillas ambientales y doce mundos por semilla.

## Interpretación, selección exploratoria y límites

[Inferencia] Un barrio de menos vecinos aumenta la necesidad adaptativa de encontrar especialidades distintas y puede favorecer que la organización ocupacional aprendida tenga más valor que el azar, mientras las redes privadas aprenden a adoptar contratos. Las cifras de ventaja sobre el mejor control aleatorio y su cambio entre grados deben leerse conjuntamente con el efecto causal de adoptar y el número de contratos físicos por persona.

Esta hipótesis se concibió **después de observar** la ventaja de reducir el grado en V34. Es selección exploratoria de un mecanismo, no confirmación ciega independiente. Solo hay cuatro semillas de entrenamiento distribuidas en dos predisposiciones. No equivale a población abierta con incorporación generacional, ni a libre invención de normas. Aunque la ventaja ocupacional supere +0,05, sigue faltando N120, cambios de grafo y robustez a la pérdida de agentes entrenados.

## Reproducibilidad

Preregistro, scripts, checkpoints y auditorías de todas las personas bajo resultados results/v32_{causal,holdout}_v36_*.json, benchmarks del grado6 results/v36_DEGREE6_REFERENCE_CONTROLS.json, CSV y METRICAS_V36.json. Se conservan trazas de todas las evaluaciones, especificaciones y estado de los tres optimizadores por individuo.
SHA256:
PREREG_V36_SCARCITY_ADOPTION.md: 65c2d1a01de5b56857ddfa3fa70a6065a92eacbf09cbb8fd409a0a4c52e18e89
v36_degree4_adoption.py: 83f11202e9c9a37bb6f4caccb89b5c2714d58291f74da7734628c89a65d6103d
v36_frozen_audits.py: 6d42ec524efba6ba01bd52e5bbcddefd820b7b8781d578a7938935776bb78371
v36_reference_degree6.py: e133c759efd90e30f0082ddf54bbad9df3f7625c0c8d4b8d2dd5d0af44924f1a
v36_summarize.py: 3833d1593913e7d9c6f6a67e38f5bbb33c99b9c865461fcea599bb030f87a82f