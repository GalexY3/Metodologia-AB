# V21–V22. Reciprocidad y formación endógena de división ocupacional

## Alcance y procedencia

Ronda exploratoria del 12/11/2026 en la rama research/aldea-v19-voluntary-exchange-20261111, derivada de V20 commit 31d553db. Las poblaciones tienen 24 agentes con políticas neuronales privadas y recompensas individuales; no hay profesor de ocupaciones, planificador central ni funciones de recompensa global. La política de donación voluntaria de V22 está preentrenada en V21 y permanece congelada durante el aprendizaje de profesiones. No se ha investigado aún aprendizaje simultáneo desde cero de ambos subsistemas.

V21 prolonga 6 modelos de 600 a 1600 actualizaciones a coste 0,12 y prepara otros 4 modelos mixtos de 600 actualizaciones en dos redes alternadas. V22 entrena cuatro nuevas redes ocupacionales durante 600 actualizaciones sobre dos políticas donantes preentrenadas y congeladas. El actor ocupacional puede cambiar entre dos profesiones cada ocho rondas, pagando 0,015 raciones por movimiento. Se entrena desde situaciones monolíticas o aleatorias mediante REINFORCE sobre alimento individual descontado.

## V21. Cambios longitudinales de cooperación

| Política | Alimento u1600 | Retorno u600 | Retorno u1600 | Agentes positivos | Retorno reconectada | Retorno k3 | Retorno sin señales sociales |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v21_LONG_SMOOTH_s3111 | 0.707 | +0.228 | +0.727 | 24/24 | +0.279 | +0.532 | -0.118 |
| v21_LONG_SMOOTH_s4111 | 0.630 | +0.037 | +0.465 | 22/24 | +0.156 | +0.396 | -0.119 |
| v21_LONG_CONST_s3111 | 0.565 | +0.231 | +0.483 | 18/24 | +0.189 | +0.355 | -0.121 |
| v21_LONG_CONST_s4111 | 0.200 | -0.121 | -0.120 | 0/24 | -0.120 | -0.120 | -0.120 |
| v21_LONG_ABRUPT_s3111 | 0.632 | +0.059 | +0.215 | 24/24 | +0.072 | +0.107 | -0.116 |
| v21_LONG_ABRUPT_s4111 | 0.488 | +0.099 | +0.503 | 14/24 | +0.115 | +0.366 | -0.119 |

Estos retornos son contrafactuales de forzar una donación inicial. Se estiman en mundos nuevos, con 24/24 personas, seis semillas de ambiente, 32 mundos por semilla y 48 rondas. Sus signos no se infieren de la tasa media de donaciones. Persisten respuestas negativas al quitar o alterar las señales sociales. Los modelos longitudinales graduales mejoran, aunque solo existen dos semillas neuronales por familia en esta campaña.

## V21. Pérdida de eficacia con entrenamiento mixto de redes

| Entrenamiento mixto | Alimento control circular | Alimento mixto | Diferencia | Retorno causal reconectada | Agentes positivos reconectada |
| --- | --- | --- | --- | --- | --- |
| v21_MIX_s3111 | 0.572 | 0.544 | -0.028 | +0.157 | 20/24 |
| v21_MIX_s4111 | 0.356 | 0.295 | -0.060 | +0.004 | 9/24 |
| v21_MIX_s5111 | 0.349 | 0.200 | -0.149 | -0.120 | 0/24 |
| v21_MIX_s6111 | 0.416 | 0.202 | -0.214 | -0.119 | 0/24 |

El resultado no apoya la hipótesis de que exponer al agente a grafos circulares y aleatorios durante la misma ventana de 600 actualizaciones mejore automáticamente la cooperación fuera de la red de referencia. Dos políticas mixtas vuelven al no intercambio.

## V21. Redundancia de información para reciprocidad

| Política | Completa | Sin receptor directo | Sin donación pública vecinal | Sin ambos | Sin señales sociales |
| --- | --- | --- | --- | --- | --- |
| v21_LONG_SMOOTH_s3111 | +0.704 | +0.384 | +0.392 | -0.120 | -0.122 |
| v21_LONG_SMOOTH_s4111 | +0.461 | +0.338 | +0.233 | -0.114 | -0.117 |

Las dos políticas prolongadas retienen retorno positivo al quitar separadamente cada uno de los dos canales informativos, pero pierden ese beneficio cuando se retiran conjuntamente. [Inferencia] Resultado compatible con redundancia funcional de señales interpersonales, sin implicar una institución social plenamente interiorizada.

## Réplica de V20 en el segundo ordenador

La réplica en GalexY Travel usó exactamente el código y pesos congelados de V20 en PyTorch CPU 2.15.0, con 16 mundos por semilla (frente a 24/32 en el PC principal). Por tanto, verifica reproducibilidad entre plataformas, no independencia del código.

| Política V20 | Retorno normal CPU | Sin memoria directa CPU | Sin señal pública CPU | Sin observación social CPU |
| --- | --- | --- | --- | --- |
| v20_SMOOTH_s3111 | +0.252 | +0.181 | -0.014 | -0.123 |
| v20_SMOOTH_s4111 | +0.029 | -0.007 | -0.064 | -0.123 |
| v20_CONST_s3111 | +0.231 | +0.130 | +0.020 | -0.120 |

## V22. Evaluación congelada sobre seis semillas y 144 sociedades por condición

Los agentes empiezan con un único oficio, sin cuota deseada programada. El control aleatorio representa la mayor alimentación media de cuatro probabilidades de movilidad preestablecidas (0,02, 0,15, 0,35, 0,60), evaluadas en los mismos escenarios. Esta elección a posteriori del mejor control se reporta para no subestimar al azar.

| Política | Red | Alimento aprendido | Mejor aleatorio | Ganancia | Enlaces complementarios | Repartos exactos |
| --- | --- | --- | --- | --- | --- | --- |
| v22_DONOR3111_ROLE7111 | ring/d2 | 0.691 | 0.421 | +0.271 | 91.4% | 63.9% |
| v22_DONOR3111_ROLE7111 | rewired/d2 | 0.520 | 0.417 | +0.103 | 70.9% | 8.3% |
| v22_DONOR3111_ROLE7111 | ring/d4 | 0.428 | 0.399 | +0.030 | 52.4% | 8.3% |
| v22_DONOR3111_ROLE8111 | ring/d2 | 0.695 | 0.421 | +0.275 | 91.4% | 54.2% |
| v22_DONOR3111_ROLE8111 | rewired/d2 | 0.524 | 0.417 | +0.107 | 75.2% | 16.7% |
| v22_DONOR3111_ROLE8111 | ring/d4 | 0.457 | 0.399 | +0.058 | 55.8% | 16.7% |
| v22_DONOR4111_ROLE7111 | ring/d2 | 0.607 | 0.381 | +0.226 | 91.4% | 66.7% |
| v22_DONOR4111_ROLE7111 | rewired/d2 | 0.443 | 0.378 | +0.065 | 62.5% | 1.4% |
| v22_DONOR4111_ROLE7111 | ring/d4 | 0.355 | 0.351 | +0.004 | 50.5% | 4.2% |
| v22_DONOR4111_ROLE8111 | ring/d2 | 0.621 | 0.381 | +0.240 | 99.7% | 96.5% |
| v22_DONOR4111_ROLE8111 | rewired/d2 | 0.424 | 0.378 | +0.046 | 62.8% | 4.2% |
| v22_DONOR4111_ROLE8111 | ring/d4 | 0.343 | 0.351 | -0.008 | 47.4% | 3.5% |

En la red circular de grado 2, los cuatro modelos forman muchos enlaces interprofesionales y superan todos los controles aleatorios. La tasa exacta 12/12 del modelo DONOR4111_ROLE8111 supera el 96% sobre mundos independientes. En redes aleatorias también se observan ventajas frente a la movilidad aleatoria, pero son menores; en redes circulares de grado 4 una de las cuatro políticas pierde incluso frente al control aleatorio.

## V22. Dependencia de la identidad y de las condiciones iniciales

En el anillo original, reasignar a personas completas con sus pesos privados de donación y movilidad a nuevas posiciones reduce el rendimiento respecto al escenario conocido. La cooperación ocupacional incorpora, por tanto, componentes dependientes de identidad y topología. Desde ocupaciones iniciales aleatorias, los cuatro modelos también mejoran frente a controles de movilidad y a dejar roles fijos, aunque con menor precisión que desde un único oficio.

## Incertidumbre y dependencia estadística

Hay 6 clústeres ambientales de evaluación por condición y 24 mundos por clúster; no son 144 replicaciones independientes de entrenamiento. Las 4 políticas V22 solo representan 2 donantes preentrenados por 2 inicializaciones ocupacionales. Se calcularon intervalos bootstrap descriptivos sobre las seis semillas ambientales, conservando el contraste emparejado. Esos intervalos no sustituyen replicaciones entre nuevas semillas neuronales ni extrapolación a nuevas escalas N o k. Datos en METRICAS_V21_V22.json.

## Próximos falsadores

1. Aprendizaje simultáneo desde cero de donación y ocupación, sin policy donante preentrenada; 2. Transferencia y reaprendizaje tras pérdida de personas o reconfiguración radical de la red; 3. Escala N=120, k=4 y poblaciones heterogéneas; 4. Separar convenios locales de memorizar índices de identidad; 5. Conservar el retorno individual causal positivo al modificar canales informativos y costes.

**Conclusión:** se ha simulado una organización ocupacional funcional emergente a partir de decisiones privadas de movilidad, apoyada en reciprocidad voluntaria previamente aprendida. No se declara OBJETIVO COMPLETADO en su sentido general, porque el módulo donante es preentrenado, se limita a dos profesiones y 24 agentes, y la generalización relacional presenta límites.

## Recursos y hashes

Checkpoints longitudinales en runs/v21_LONG_*/; modelos mixtos en runs/v21_MIX_*/; políticas ocupacionales en runs/v22_DONOR*_ROLE*/. Auditorías individuales en results/v20_allagents_v21_*.json; mecanismos en results/v21_reputation_*.json; evaluación ocupacional en results/v22_holdout_*.json. Código y preregistros disponibles en la misma carpeta.

```
v21_longitudinal.py: 363cd17610eae55c80c5e10c11dde5a6fc2381e6d5f8e0bffebafe71ea743bae
v21_reputation_census.py: 1a3e012c4943f8a23a3aafbd2cb76c4a1eaa5063db6a317e7478defaeecf59f8
v22_occupations.py: dfd40a60c11546f1349830596251dc8c808bf869503b43715a7619b5e59585dd
v22_frozen_holdout.py: fed5e42414271396bbbba4ae11c255bbae2d5826631f20429b701bb96bb85fb8
test_v22_occupations.py: 36f6a981a253e0bd1e9b93d38b05c12cb7a9c1290be4214ab620836e7c756158
v21_travel_replay.py: e5f5933b44cedbf10352fc23587c4370852be72e465ec6968c2c312dd39aeea9
v20_all_agents_causal.py: 2ab65c7e973890d0e171e3f06ec20cf7f5083c7f6fed26fcf49820cf026bd33a
targeted_gifts.py: 7fa22d46016595fd87b8b0bf5a9edae1f5472cb8e2f95c85e42d9e350ffa8527
PREREG_V21_LONGITUDINAL.md: 86c85028bb5c572ecceccd8e630a6652a413711781ee8598371794007e349d8f
PREREG_V21B_TOPOLOGIES.md: 2a82573312f7647fc8c9885fdc926bed6a75066ac04b019831fccf0c245d5c63
PREREG_V22_ENDOGENOUS_OCCUPATIONS.md: 4e570752d6cde9afadc5d7ce07da66e9ad0d17b4bbe09ebea449d9c5214c8dd0
```