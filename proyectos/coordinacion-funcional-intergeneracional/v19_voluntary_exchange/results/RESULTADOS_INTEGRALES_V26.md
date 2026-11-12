# V26. Duración de memoria relacional y reciprocidad en economía de cuatro profesiones

Exploración preregistrada 12/11/2026 sobre el fracaso de V25. Se conservó íntegramente el motor de recompensa y el actor neuronal de producción de hasta tres bienes por trabajador. El único parámetro cambiado es el decaimiento de la memoria privada de favores entre vecinos: δ=0,94 y δ=0,99, frente al control histórico V25 δ=0. En cada configuración se reentrenaron desde pesos aleatorios dos semillas neuronales 3111 y 4111, 1000 actualizaciones, 48 personas, 4 profesiones, grado de red 6. Coste final unitario 0,04 tras currículo barato 0,002.

La memoria almacena por vecino un rastro de ayuda recibida y aplica max(ayuda actual, δ×ayuda previa). Su efecto es informacional y no crea productos nuevos ni recompensa a donantes de manera externa. La semivida formal es log(0,5)/log(δ) rondas.

## Evaluación congelada frente al control histórico

| Modelo | δ | Semivida | V25 δ0 alimento | V26 alimento | Cambio | Regalos/ronda | Cobertura | Sin historial |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v26_M94_N48_C04_s3111 | 0.94 | 11.2 | 0.2026 | 0.2012 | -0.0015 | 0.0119 | 0.0035 | 0.2014 |
| v26_M94_N48_C04_s4111 | 0.94 | 11.2 | 0.2018 | 0.2019 | +0.0002 | 0.0178 | 0.0053 | 0.2026 |
| v26_M99_N48_C04_s3111 | 0.99 | 69.0 | 0.2026 | 0.2016 | -0.0010 | 0.0157 | 0.0045 | 0.2020 |
| v26_M99_N48_C04_s4111 | 0.99 | 69.0 | 0.2018 | 0.2009 | -0.0008 | 0.0096 | 0.0028 | 0.2010 |

## Efecto causal individual de forzar la donación inicial

| Modelo | Retorno causal V25 | Retorno causal V26 | Personas positivas | Sin historial | Red reconectada |
| --- | --- | --- | --- | --- | --- |
| v26_M94_N48_C04_s3111 | -0.0391 | -0.0461 | 0/48 | -0.0399 | -0.0445 |
| v26_M94_N48_C04_s4111 | -0.0402 | -0.0473 | 0/48 | -0.0400 | -0.0478 |
| v26_M99_N48_C04_s3111 | -0.0391 | -0.0475 | 0/48 | -0.0398 | -0.0470 |
| v26_M99_N48_C04_s4111 | -0.0402 | -0.0482 | 0/48 | -0.0401 | -0.0470 |

Las estimaciones causales corresponden a un regalo inicial impuesto en uno de tres slots, dejando libres las otras decisiones, en mundos emparejados. Seis semillas ambientales por condición y ocho mundos por semilla. El coste inmediato exacto equivale a -0,04 y todos los agentes se auditan. La eliminación del historial social durante inferencia es ablación informacional, no ausencia de memoria en entrenamiento.

## Evolución durante el currículo

| Modelo | Actualización | Precio de entrenamiento | Alimento a precio final | Regalos a precio final |
| --- | --- | --- | --- | --- |
| v26_M94_N48_C04_s3111 | 1 | 0.0020 | 0.3027 | 1.5041 |
| v26_M94_N48_C04_s3111 | 250 | 0.0020 | 0.2765 | 0.7262 |
| v26_M94_N48_C04_s3111 | 500 | 0.0020 | 0.2649 | 0.5694 |
| v26_M94_N48_C04_s3111 | 750 | 0.0337 | 0.2064 | 0.0541 |
| v26_M94_N48_C04_s3111 | 1000 | 0.0400 | 0.2012 | 0.0118 |
| v26_M94_N48_C04_s4111 | 1 | 0.0020 | 0.3037 | 1.4930 |
| v26_M94_N48_C04_s4111 | 250 | 0.0020 | 0.2763 | 0.6738 |
| v26_M94_N48_C04_s4111 | 500 | 0.0020 | 0.2887 | 0.8261 |
| v26_M94_N48_C04_s4111 | 750 | 0.0337 | 0.2283 | 0.2428 |
| v26_M94_N48_C04_s4111 | 1000 | 0.0400 | 0.2020 | 0.0183 |
| v26_M99_N48_C04_s3111 | 1 | 0.0020 | 0.3034 | 1.5013 |
| v26_M99_N48_C04_s3111 | 250 | 0.0020 | 0.2911 | 0.7854 |
| v26_M99_N48_C04_s3111 | 500 | 0.0020 | 0.3143 | 1.0115 |
| v26_M99_N48_C04_s3111 | 750 | 0.0337 | 0.2128 | 0.1059 |
| v26_M99_N48_C04_s3111 | 1000 | 0.0400 | 0.2016 | 0.0157 |
| v26_M99_N48_C04_s4111 | 1 | 0.0020 | 0.3033 | 1.4862 |
| v26_M99_N48_C04_s4111 | 250 | 0.0020 | 0.3012 | 0.9102 |
| v26_M99_N48_C04_s4111 | 500 | 0.0020 | 0.2660 | 0.5599 |
| v26_M99_N48_C04_s4111 | 750 | 0.0337 | 0.2036 | 0.0319 |
| v26_M99_N48_C04_s4111 | 1000 | 0.0400 | 0.2010 | 0.0101 |

## Incertidumbre y limites

Los contrastes de alimentación de V26 frente a V25 se emparejan por seis semillas ambientales idénticas. Los intervalos bootstrap descriptivos se estiman sobre los seis clústeres, no entre entrenamientos. Existen solo dos inicializaciones neuronales por duración de memoria, y dos por control δ=0; no se debe declarar una regularidad poblacional universal.

La existencia de roles potencialmente complementarios no permite inferir intercambio real, y una tasa de donaciones no certifica beneficio individual futuro. La auditoría causal y el bloqueo de señales informativas son los falsadores decisivos. Ningún hallazgo de N48/k4 justificaría por sí solo declarar el objetivo completo sin replicación en N120 y múltiples topologías.

## Reproducibilidad

Código exacto V25 preservado sin modificaciones. Los wrappers V26 inyectan exclusivamente el parámetro C.memory_decay en entornos de entrenamiento y evaluación. Archivos runs/v26_M*/v25_spec.json registran memory_decay; pesos y estados Adam en joint_latest.pt, logs en v25_history.jsonl, escenarios de prueba JSON results/v25_holdout_v26_*.json, audit JSON results/v25_causal_v26_*.json. Pruebas de persistencia test_v26_memory.py.

Hash SHA256 del código y preregistros:
v26_memory_train.py: be3c944a7e1ba9391015198cafbd070403b6f211e46ab813a56ab940be3f0b18
v26_memory_holdout.py: 7938a2328a2c6432bd197b42e1fac36a7c4203429b2e4bda621c1059b1e480e4
v26_memory_causal.py: 572f5dbc892076a4608bc7bdaba75c4f0bf85fdd815f72f5f66416034757f6fe
v26_summarize.py: 2dc78b606bbc034380af883ffa1946f4ec04c40b9339f414eb42fa6943cfecfd
test_v26_memory.py: 6b1f80652fadc5d1992df5a892371306b3116faf8a3ba450902c780e100ad8e2
PREREG_V26_LONG_MEMORY.md: 66f3bef7d9b52e702f814b03c3f4541f307d7ac8804dd986f4d412ab7f4f02cb
v25_multi_capacity.py: 2f968ce9e24be31a42f3500f2c446702947bcad5382bea4660c3b074f1cc37b7