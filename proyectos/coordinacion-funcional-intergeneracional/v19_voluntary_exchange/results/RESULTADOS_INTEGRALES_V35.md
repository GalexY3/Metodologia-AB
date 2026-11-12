# V35. Resiliencia de sociedades contractuales con 120 personas

Evaluación de las cuatro políticas finales V31 con pesos congelados y seis semillas ambientales por política, dieciséis mundos por semilla, cuatro condiciones y cuarenta y ocho rondas. En total 96 condiciones de semilla/política/choque, 1536 trayectorias de mundo y 8.847.360 transiciones agente-ronda. Son cuatro entrenamientos neuronales distintos, no 1536 redes independientes. Todos los mundos parten de ocupaciones monolíticas y sostienen contratos voluntarios exógenamente disponibles.

Se interviene entre las decisiones ocupacionales y las propuestas de la ronda 25. **Enmienda técnica declarada** en AMENDMENT_V35_SHOCK_ORDER.md: el preregistro ubicaba la intervención antes de las decisiones, pero el actor de profesiones habría revertido inmediatamente la reasignación en esa misma ronda. El orden revisado, idéntico para los cuatro grupos, impone el choque después de la decisión ocupacional ordinaria y antes de intercambiar; se verificó con test de humo previo a las corridas de seis semillas. No se incorporó la prueba de humo a la muestra.

## Resultados principales

| Política | Coste | Choque | Comida previa | Comida 25–32 | Comida 41–48 | Excedente conservado | Supera ≥85% |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v31_N120_MUTUAL_C04_s3111 | 0.04 | control | 0.3417 | 0.3430 | 0.3433 | 100.0% | sí |
| v31_N120_MUTUAL_C04_s3111 | 0.04 | rewire | 0.3417 | 0.3377 | 0.3374 | 95.9% | sí |
| v31_N120_MUTUAL_C04_s3111 | 0.04 | roles | 0.3417 | 0.3378 | 0.3433 | 100.0% | sí |
| v31_N120_MUTUAL_C04_s3111 | 0.04 | newcomers | 0.3417 | 0.3080 | 0.3078 | 75.2% | no |
| v31_N120_MUTUAL_C04_s4111 | 0.04 | control | 0.3415 | 0.3439 | 0.3451 | 100.0% | sí |
| v31_N120_MUTUAL_C04_s4111 | 0.04 | rewire | 0.3415 | 0.3412 | 0.3424 | 98.1% | sí |
| v31_N120_MUTUAL_C04_s4111 | 0.04 | roles | 0.3415 | 0.3374 | 0.3452 | 100.0% | sí |
| v31_N120_MUTUAL_C04_s4111 | 0.04 | newcomers | 0.3415 | 0.3089 | 0.3098 | 75.7% | no |
| v31_N120_MUTUAL_C12_s3111 | 0.12 | control | 0.2521 | 0.2535 | 0.2540 | 100.0% | sí |
| v31_N120_MUTUAL_C12_s3111 | 0.12 | rewire | 0.2521 | 0.2473 | 0.2475 | 87.9% | sí |
| v31_N120_MUTUAL_C12_s3111 | 0.12 | roles | 0.2521 | 0.2450 | 0.2541 | 100.0% | sí |
| v31_N120_MUTUAL_C12_s3111 | 0.12 | newcomers | 0.2521 | 0.2388 | 0.2391 | 72.4% | no |
| v31_N120_MUTUAL_C12_s4111 | 0.12 | control | 0.2527 | 0.2540 | 0.2547 | 100.0% | sí |
| v31_N120_MUTUAL_C12_s4111 | 0.12 | rewire | 0.2527 | 0.2484 | 0.2484 | 88.5% | sí |
| v31_N120_MUTUAL_C12_s4111 | 0.12 | roles | 0.2527 | 0.2446 | 0.2547 | 100.1% | sí |
| v31_N120_MUTUAL_C12_s4111 | 0.12 | newcomers | 0.2527 | 0.2400 | 0.2397 | 72.5% | no |

El indicador de recuperación se calcula contra el control de cada semilla ambiental, (comida final de la condición−0,20)/(comida final del control−0,20), y luego se promedia entre las seis semillas ambientales. El criterio preregistrado exigía al menos 85% del excedente en ambas inicializaciones neuronales de cada coste. Es una medida del excedente, no de la comida total.

## Desigualdad entre residentes entrenados y recién llegados

| Política | Alimento 30 nuevos | Alimento 90 residentes | Brecha residentes−nuevos | Excedente social retenido |
| --- | --- | --- | --- | --- |
| v31_N120_MUTUAL_C04_s3111 | 0.2507 | 0.3268 | 0.0761 | 75.2% |
| v31_N120_MUTUAL_C04_s4111 | 0.2512 | 0.3293 | 0.0782 | 75.7% |
| v31_N120_MUTUAL_C12_s3111 | 0.2159 | 0.2469 | 0.0310 | 72.4% |
| v31_N120_MUTUAL_C12_s4111 | 0.2162 | 0.2475 | 0.0313 | 72.5% |

El choque de sustitución reemplaza el 25% de las redes neuronales privadas y asigna aleatoriamente su ocupación a los recién incorporados. Los 90 vecinos conservan pesos adquiridos. Ni los antiguos ni los nuevos actualizan sus parámetros durante estas 48 rondas. Por lo tanto, la caída expresa vulnerabilidad frente a sustitución no aprendida, no incapacidad general de integrar generaciones cuando pueden aprender.

## Interpretación y causalidad de los choques

[Inferencia] La reconexión del barrio social conserva buena parte del excedente, incluso al coste 0,12, pero perjudica más al beneficio a precio elevado. La reasignación de profesiones produce un deterioro inicial y desaparece después de nuevas decisiones ocupacionales. No atribuir recuperación del rol a aprendizaje de nuevos pesos: las políticas están congeladas. El shock de newcomers reduce el bienestar tanto de sustitutos como de residentes, y produce una brecha por competencia acumulada.

## Validez

Las seis semillas ambientales son pares condicionados a la misma inicialización neuronal. Los intervalos bootstrap descriptivos [2,5%,97,5%] de METRICAS_V35.json re-muestrean estas seis semillas, no los mundos individuales, y no caracterizan la incertidumbre sobre todas las posibles redes y poblaciones. No se midió reentrenamiento después del choque. El 85% fue definido antes del experimento: la sustitución NO pasa el criterio preregistrado.

La cooperación contractual sigue diferenciándose de reciprocidad unilateral sin ejecución mutua: los acuerdos privados voluntarios son aprendidos, la regla de entrega condicional se introdujo en el entorno. Se conserva abierto el objetivo general por faltar resiliencia intergeneracional y generalización fuerte de la especialización.

## Reproducción y SHA256

Preregistro, enmienda, código, tests y series de los 48 turnos de las seis semillas ambientales por condición se conservan en los archivos results/v35_shocks_v31_*.json; resumen CSV e informe en results/COMPARACION_V35.csv y results/METRICAS_V35.json.
v35_shock_audit.py: 8475397d019e412d774074dafd29e5e444a368c5098ceeee8c776088024113ed
test_v35_shocks.py: 8172a7536befaa85de6acbc5774e516efb7c15e67137768942e048625c7b4ddb
v35_summarize.py: 1ce313e75fc951fd9c8b87fbdf9ff930048342925d0ea537cb90a98d834ddd8a
PREREG_V35_SHOCK_RESILIENCE.md: abe1ab89eafb7ffaa4129087d0b04c5dacd04dc1bbb1278c7b885740d2bd8e7c
AMENDMENT_V35_SHOCK_ORDER.md: 4499646cdcec079f98ffe30024a36849729700f1a768e6e50f5b56ab505bdefa