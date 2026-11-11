# V18 — Conservación del aprendizaje de coordinación y generalización social

## Metodología

N=120 redes independientes con pesos propios y recompensa estrictamente individual r=min(n_j/(N/k),(N/k)/n_j). El profesor es un protocolo programado que enseña a comprometer, fundar y consolidar profesiones; la regularización en RL **introduce** supervisión de esa política. El presente estudio prueba mantenimiento y modificación de una convención aprendida, NO emergencia espontánea de cooperación.

Los experimentos separan 350, 700, 1.200 y 1.600 actualizaciones. Se congelaron los pesos antes de medir 12 configuraciones M/k por política sobre cuatro semillas nuevas con 24 sociedades cada una. También se intervinieron mensajes, y un banco independiente en el segundo ordenador varió grado 4/8/16 y red circular/reconectada.

Total de registros de evaluación congelada compilados: 684 condiciones modelo×tarea×comunicación, 65664 ejecuciones de sociedades. Una sociedad contiene 120 individuos; no equivale a 120 observaciones independientes.

## Rendimiento de los checkpoints, mensajes normales

| Modelo | Alimentación | Repartos exactos | Tasa exacta |
|---|---:|---:|---:|
| Profesor 1 | 0.9254 | 232/1152 | 20.14% |
| Profesor 2 | 0.9248 | 234/1152 | 20.31% |
| RL puro 1 | 0.8066 | 1/1152 | 0.09% |
| RL puro 2 | 0.8071 | 0/1152 | 0.00% |
| Sintético, 350 pasos, semilla 1 | 0.9454 | 301/1152 | 26.13% |
| Sintético, 350 pasos, semilla 2 | 0.9487 | 309/1152 | 26.82% |
| Sintético, 700 pasos | 0.8821 | 78/1152 | 6.77% |
| En trayectoria, 700 pasos, semilla 1 | 0.9416 | 293/1152 | 25.43% |
| En trayectoria, 700 pasos, semilla 2 | 0.9449 | 323/1152 | 28.04% |
| En trayectoria, 1600 pasos, semilla 1 | 0.9320 | 240/1152 | 20.83% |
| En trayectoria, 1600 pasos, semilla 2 | 0.9316 | 218/1152 | 18.92% |

## Propiedades temporales

La pérdida de coordinación desde estados atrapados no equivale a grokking: se monitoriza simultáneamente el comportamiento en las tareas conocidas y en M72/k8 no entrenada. La política entrenada sin el término de conservación pierde rápidamente la organización; penalizar desvíos respecto al profesor en estados sintéticos únicamente retrasa la pérdida. Aplicar la penalización sobre las observaciones realmente visitadas la retrasa más.

| Entrenamiento | Actualización | Comida trampa 2×60 | Repartos exactos en 48 mundos | Comida OOD M72/k8 |
|---|---:|---:|---:|---:|
| v18_LONG_BC0_s6111 | 0 | 0.9256 | 4/48 | 0.8872 |
| v18_LONG_BC0_s6111 | 200 | 0.7500 | 0/48 | 0.8706 |
| v18_LONG_BC0_s6111 | 400 | 0.7248 | 0/48 | 0.8299 |
| v18_LONG_BC0_s6111 | 600 | 0.7335 | 0/48 | 0.8081 |
| v18_LONG_BC0_s6111 | 800 | 0.7501 | 0/48 | 0.8037 |
| v18_LONG_BC0_s6111 | 1000 | 0.7459 | 0/48 | 0.7883 |
| v18_LONG_BC0_s6111 | 1200 | 0.7500 | 0/48 | 0.8091 |
| v18_LONG_BC3_s6111 | 0 | 0.9256 | 4/48 | 0.8872 |
| v18_LONG_BC3_s6111 | 200 | 0.9353 | 13/48 | 0.9384 |
| v18_LONG_BC3_s6111 | 400 | 0.8682 | 2/48 | 0.9300 |
| v18_LONG_BC3_s6111 | 600 | 0.8099 | 3/48 | 0.8870 |
| v18_LONG_BC3_s6111 | 800 | 0.7716 | 2/48 | 0.8346 |
| v18_LONG_BC3_s6111 | 1000 | 0.7562 | 1/48 | 0.8232 |
| v18_LONG_BC3_s6111 | 1200 | 0.7346 | 0/48 | 0.7881 |
| v18_LONG_BC10_s6111 | 0 | 0.9256 | 4/48 | 0.8872 |
| v18_LONG_BC10_s6111 | 200 | 0.9330 | 14/48 | 0.9283 |
| v18_LONG_BC10_s6111 | 400 | 0.8996 | 14/48 | 0.9289 |
| v18_LONG_BC10_s6111 | 600 | 0.8763 | 10/48 | 0.9036 |
| v18_LONG_BC10_s6111 | 800 | 0.7941 | 2/48 | 0.8641 |
| v18_LONG_BC10_s6111 | 1000 | 0.7517 | 0/48 | 0.8410 |
| v18_LONG_BC10_s6111 | 1200 | 0.7306 | 0/48 | 0.8252 |
| v18_ON_ALL_LONG_3_s6111 | 700 | 0.9327 | 8/48 | 0.9127 |
| v18_ON_ALL_LONG_3_s6111 | 875 | 0.9218 | 6/48 | 0.9096 |
| v18_ON_ALL_LONG_3_s6111 | 1050 | 0.9074 | 8/48 | 0.9134 |
| v18_ON_ALL_LONG_3_s6111 | 1225 | 0.9138 | 9/48 | 0.9083 |
| v18_ON_ALL_LONG_3_s6111 | 1400 | 0.9086 | 2/48 | 0.8999 |
| v18_ON_ALL_LONG_3_s6111 | 1575 | 0.9011 | 5/48 | 0.9021 |
| v18_ON_ALL_LONG_3_s6111 | 1600 | 0.9017 | 8/48 | 0.8998 |
| v18_ON_ALL_LONG_3_s7111 | 700 | 0.9300 | 8/48 | 0.9100 |
| v18_ON_ALL_LONG_3_s7111 | 875 | 0.9115 | 5/48 | 0.9103 |
| v18_ON_ALL_LONG_3_s7111 | 1050 | 0.9362 | 10/48 | 0.9238 |
| v18_ON_ALL_LONG_3_s7111 | 1225 | 0.9144 | 8/48 | 0.9183 |
| v18_ON_ALL_LONG_3_s7111 | 1400 | 0.9091 | 4/48 | 0.9055 |
| v18_ON_ALL_LONG_3_s7111 | 1575 | 0.9249 | 8/48 | 0.9016 |
| v18_ON_ALL_LONG_3_s7111 | 1600 | 0.9040 | 6/48 | 0.9114 |

## Variación del tejido social, fuera de entrenamiento

Las redes se entrenaron con un círculo de 8 vecinos. El experimento de transferencia alteró el número de enlaces y usó una topología reconectada con las mismas políticas congeladas. Las métricas agregan cuatro tareas, 96 sociedades por tarea y combinación.

| Semilla | Red | Grado | Profesor: comida | Profesor: exactos | Regularizada λ3: comida | Regularizada λ3: exactos |
|---|---|---:|---:|---:|---:|---:|
| 1 | ring | 4 | 0.9482 | 114/384 | 0.9348 | 60/384 |
| 1 | ring | 8 | 0.9340 | 95/384 | 0.9453 | 100/384 |
| 1 | ring | 16 | 0.7946 | 44/384 | 0.9348 | 92/384 |
| 1 | rewired | 4 | 0.7120 | 18/384 | 0.9235 | 58/384 |
| 1 | rewired | 8 | 0.7594 | 23/384 | 0.9297 | 70/384 |
| 1 | rewired | 16 | 0.7956 | 22/384 | 0.9178 | 43/384 |
| 2 | ring | 4 | 0.9515 | 115/384 | 0.9397 | 77/384 |
| 2 | ring | 8 | 0.9411 | 102/384 | 0.9502 | 113/384 |
| 2 | ring | 16 | 0.7941 | 24/384 | 0.9438 | 101/384 |
| 2 | rewired | 4 | 0.7003 | 17/384 | 0.9308 | 78/384 |
| 2 | rewired | 8 | 0.7574 | 22/384 | 0.9318 | 70/384 |
| 2 | rewired | 16 | 0.7923 | 26/384 | 0.9286 | 55/384 |

## Límites causales

La prueba conserva una fuente externa explícita de política de coordinación y redes independientes. El éxito de regularización NO demuestra que cooperación o normas sociales aparezcan por aprendizaje individual sin profesor. La reducción al retirar los mensajes refleja también el mecanismo programado de consenso; no basta para afirmar deliberación o reciprocidad.

El número exacto de grupos y la alimentación pueden divergir por configuración. Los resultados de desarrollo revisados para elegir λ están sujetos a selección de hiperparámetros; el bootstrap descriptivo por escenario está en RESULTADOS_V18.md y results/v18_statistics.json.

No se ha observado una transición tardía que cumpla los criterios de grokking: la evidencia principal es retención parcial y adaptación de una política previamente enseñada.

## Archivos de evidencia

Los registros se mantienen en results/frozen_initial.json, frozen_sweep.json, frozen_onpolicy.json, frozen_long.json, v18_topology.json y sus scripts de evaluación. Los parámetros entrenados y optimizadores están en runs/ (V18) y en los runs/v18_* del directorio V17. Todos los informes se derivan de esos JSON.