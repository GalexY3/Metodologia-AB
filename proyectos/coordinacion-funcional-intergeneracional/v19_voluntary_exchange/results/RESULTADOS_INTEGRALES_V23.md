# V23. Coaprendizaje de reciprocidad y ocupaciones desde cero

Estudio fechado 12/11/2026, sobre el commit V21-V22 18d617c6. Ambos actores privados de cada uno de los 24 individuos se inicializan aleatoriamente y aprenden conjuntamente con REINFORCE sobre alimento individual descontado, sin imitación, actor congelado previo, reparto planificado de profesiones ni recompensa conjunta. Dos profesiones, anillo grado 2, coste de movilidad 0,015 cada ocho rondas, gamma 0,995, 1400 actualizaciones. Coste final de donación 0,12 para todos. Cuatro semillas de currículo progresivo, dos de coste alto constante y dos sin historial de donaciones.

## Resultado fuera de muestra con seis semillas ambientales y 24 mundos por semilla

| Modelo | Alimento | Donaciones | Enlaces de oficios distintos | Repartos 12/12 | Mejor control aleatorio | Ganancia | Retorno causal | Agentes positivos |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v23_SMOOTH_s3111 | 0.613 | 73.4% | 99.8% | 97.9% | 0.408 | +0.205 | +0.344 | 18/24 |
| v23_SMOOTH_s4111 | 0.698 | 87.7% | 91.6% | 6.9% | 0.462 | +0.236 | +0.694 | 19/24 |
| v23_SMOOTH_s5111 | 0.399 | 36.6% | 91.1% | 45.8% | 0.278 | +0.120 | +0.375 | 11/24 |
| v23_SMOOTH_s6111 | 0.534 | 62.9% | 99.8% | 99.3% | 0.368 | +0.166 | +0.098 | 16/24 |
| v23_CONSTANT_s3111 | 0.441 | 41.6% | 76.9% | 0.0% | 0.340 | +0.101 | +0.305 | 12/24 |
| v23_CONSTANT_s4111 | 0.200 | 0.0% | 56.4% | 0.0% | 0.200 | +0.000 | -0.120 | 0/24 |
| v23_NOSOC_s3111 | 0.200 | 0.0% | 99.8% | 97.2% | 0.200 | +0.000 | -0.119 | 0/24 |
| v23_NOSOC_s4111 | 0.200 | 0.0% | 91.7% | 18.1% | 0.200 | +0.000 | -0.120 | 0/24 |

El mejor control aleatorio se obtiene entre tres probabilidades predefinidas de cambio ocupacional: 0,15; 0,35 y 0,60. Se selecciona la mayor alimentación de cada una, sin reajustar el modelo; esto es conservador frente a un solo control pero la selección afecta la inferencia de intervalos. El resultado se evalúa sobre políticas congeladas y semillas ambientales no entrenadas.

## Auditoría de donación inicial forzada (todas las personas)

| Modelo | Normal | Sin memoria social de donaciones | Identidades sociales alteradas | Grafo reconectado | Anillo grado 4 | Inicio ocupacional aleatorio |
| --- | --- | --- | --- | --- | --- | --- |
| v23_SMOOTH_s3111 | +0.344 | -0.116 | -0.112 | +0.019 | +0.184 | +0.174 |
| v23_SMOOTH_s4111 | +0.694 | -0.126 | -0.132 | +0.129 | +0.310 | +0.313 |
| v23_SMOOTH_s5111 | +0.375 | -0.116 | -0.119 | -0.003 | +0.075 | +0.366 |
| v23_SMOOTH_s6111 | +0.098 | -0.122 | -0.105 | -0.051 | +0.045 | +0.052 |
| v23_CONSTANT_s3111 | +0.305 | -0.111 | -0.128 | +0.055 | +0.196 | +0.189 |
| v23_CONSTANT_s4111 | -0.120 | -0.120 | -0.120 | -0.120 | -0.120 | -0.120 |
| v23_NOSOC_s3111 | -0.119 | -0.120 | -0.120 | -0.119 | -0.120 | -0.118 |
| v23_NOSOC_s4111 | -0.120 | -0.120 | -0.120 | -0.119 | -0.119 | -0.120 |

El agente obligado a dar asume exactamente -0,12 de alimento en la primera ronda frente al brazo emparejado sin donación. Se estima su retorno propio futuro con las políticas de roles y donaciones congeladas. Seis semillas ambientales por escenario, 12 mundos por semilla, 24 focos individuales. Conservar signo negativo y personas con retorno desfavorable; no interpretar magnitudes como una probabilidad de cooperación universal.

## Controles mecanísticos y transferencia

| Modelo | Normal | Sin historial social | Personas reasignadas | Donaciones bloqueadas |
| --- | --- | --- | --- | --- |
| v23_SMOOTH_s3111 | 0.613 | 0.565 | 0.491 | 0.200 |
| v23_SMOOTH_s4111 | 0.698 | 0.613 | 0.471 | 0.200 |
| v23_SMOOTH_s5111 | 0.399 | 0.386 | 0.273 | 0.200 |
| v23_SMOOTH_s6111 | 0.534 | 0.526 | 0.474 | 0.200 |
| v23_CONSTANT_s3111 | 0.441 | 0.411 | 0.377 | 0.200 |
| v23_CONSTANT_s4111 | 0.200 | 0.200 | 0.200 | 0.200 |
| v23_NOSOC_s3111 | 0.200 | 0.200 | 0.200 | 0.200 |
| v23_NOSOC_s4111 | 0.200 | 0.200 | 0.200 | 0.200 |

Las redes aprendidas con escaso historial social forman a veces distribuciones ocupacionales casi perfectas y simultáneamente dejan de donar: la complementariedad de puestos no equivale a cooperación material. La permutación de políticas privadas entre posiciones reduce la alimentación. La generalización a red reconectada es desigual y dos de cuatro semillas progresivas pierden retorno causal positivo.

## Estructura de dependencia estadística

Las seis semillas ambientales son unidades de agrupamiento de la evaluación, pero no equivalen a seis entrenamientos nuevos. Se empleó bootstrap descriptivo de contrastes emparejados por esas seis semillas; los intervalos no cubren variación sobre infinitas inicializaciones de redes. Solo existen cuatro semillas neuronales principales y dos por control negativo.

Se ejecutaron 258.048.000 transiciones agente-ronda de entrenamiento; se registraron 55.296 trayectorias mundo-condición para evaluación de alimento y 165.888 pares contrafactuales mundo-persona, cada uno con dos brazos. Estas cifras describen el trabajo computacional y no multiplican el tamaño muestral efectivo de entrenamientos.

## Conclusión

[Inferencia] V23 demuestra que, bajo este modelo artificial específico, políticas privadas de contribución voluntaria y movilidad ocupacional pueden aprenderse conjuntamente desde pesos aleatorios y producir beneficios individuales causales en más de una inicialización. Quedan límites de dependencia de identidades, transferencia a redes reconectadas y escala de más profesiones. No se declara OBJETIVO COMPLETADO: la condición multiescala k=4/N=120 requiere superar nuevas pruebas.

## Archivos para reproducción

Entrenador v23_joint_cold.py; auditor causal v23_joint_audit.py; holdout v23_joint_holdout.py; logs y checkpoints conjuntos en runs/v23_*/; resultados originales en results/v23_joint_audit_*.json y results/v23_joint_holdout_*.json. Pruebas unitarias con test_v23_joint.py.

Hashes SHA256:
v23_joint_cold.py: d3b3f9d8e2c6d97dc497cca3d4cf42bb7a845e58553c15f5f0c26745157b8c9f
v23_joint_audit.py: 1b0dc47d07fb9ce65ec6c4332b792af13bbd1a6e523e096cde143d2a5a7d60c6
v23_joint_holdout.py: b15a5f2eb74fae153a89c8bff30e0b3bcf977e26c4a016cba0142c65e2df8f5e
test_v23_joint.py: adca1604d0983d3c7ba218330fe48b97c8af341a674a3682c76f079e538797af
PREREG_V23_JOINT_COLD_START.md: c7fb45dceed3f714ff9e186c0bcc73189e8596fcedda9088c35a17eb76251171