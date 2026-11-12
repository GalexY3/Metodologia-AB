# V27. Prevalencia empírica de soluciones cooperativas entre diez inicializaciones neuronales

Campaña preregistrada el 12/11/2026. Seis nuevas semillas entrenadas en GALEXY_TRAVEL con el código original V23, sin importar pesos anteriores, y evaluadas con seis semillas ambientales y modelos congelados. Se integran las cuatro semillas V23 originales entrenadas en GPU. Los 10 entrenamientos comparten arquitectura, REINFORCE individual, curso de coste de regalo 0,01→0,12 hasta u800, 1400 actualizaciones, anillo grado dos, 24 personas, dos profesiones, lote20 y horizonte48. Diferencias de hardware y PyTorch quedan declaradas.

## Resultados por inicialización

| Modelo | Hardware entrenamiento | Alimento | Mejor aleatorio | Ventaja | Donaciones | Enlaces complem. | Causal regalo | Personas positivas | Éxito doble |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v27_CPU_REP_s7311 | GalexY_travel_CPU | 0.200 | 0.200 | +0.000 | 0.0% | 91.5% | -0.120 | 0/24 | False |
| v27_CPU_REP_s8311 | GalexY_travel_CPU | 0.362 | 0.272 | +0.089 | 28.6% | 91.6% | +0.439 | 8/24 | True |
| v27_CPU_REP_s9311 | GalexY_travel_CPU | 0.414 | 0.300 | +0.114 | 37.5% | 91.6% | +0.119 | 10/24 | True |
| v27_CPU_REP_s10311 | GalexY_travel_CPU | 0.200 | 0.200 | +0.000 | 0.0% | 95.3% | -0.121 | 0/24 | False |
| v27_CPU_REP_s11311 | GalexY_travel_CPU | 0.605 | 0.428 | +0.177 | 75.0% | 91.6% | +0.278 | 18/24 | True |
| v27_CPU_REP_s12311 | GalexY_travel_CPU | 0.522 | 0.370 | +0.152 | 57.1% | 99.7% | +0.434 | 16/24 | True |
| v23_SMOOTH_s3111 | DESKTOP_I4SULKD_GPU | 0.613 | 0.408 | +0.205 | 73.4% | 99.8% | +0.344 | 18/24 | True |
| v23_SMOOTH_s4111 | DESKTOP_I4SULKD_GPU | 0.698 | 0.462 | +0.236 | 87.7% | 91.6% | +0.694 | 19/24 | True |
| v23_SMOOTH_s5111 | DESKTOP_I4SULKD_GPU | 0.399 | 0.278 | +0.120 | 36.6% | 91.1% | +0.375 | 11/24 | True |
| v23_SMOOTH_s6111 | DESKTOP_I4SULKD_GPU | 0.534 | 0.368 | +0.166 | 62.9% | 99.8% | +0.098 | 16/24 | True |

## Criterio de éxito previamente fijado

El criterio doble requiere alimento de la política congelada >0,05 por encima del mejor control de movilidad aleatoria entre tres tasas predefinidas, y retorno propio medio causal positivo al forzar una donación inicial. La sensibilidad social adicional exige retorno negativo al retirar el historial social en evaluación.

El criterio doble se observa en **8/10** inicializaciones; de ellas, **4/6** en el segundo ordenador. El intervalo Wilson binomial 95% descriptivo sobre diez modelos es **[0.490, 0.943]**. No debe interpretarse como estimación representativa de todos los espacios de parámetros, grafos o sociedades humanas. Las mismas seis semillas ambientales por evaluación no equivalen a replicaciones independientes del entrenamiento.

## Qué se ha aprendido sobre la robustez

La misma intervención de coste y algoritmo no conduce necesariamente a soluciones cooperativas. Registrar fallos y soluciones débiles sirve para estudiar cuencas de atracción, dependencia de trayectoria, sensibilidad al azar y barreras de exploración; la proporción encontrada depende de la arquitectura y los hiperparámetros congelados. [Inferencia] La alta variabilidad es compatible con un problema de coordinación de múltiples agentes y no permite describir el éxito como garantizado ni universal.

El criterio de éxito no exige abastecimiento completo, ni estabilidad en redes reconectadas o N120/k4. El proyecto general continúa abierto. Para su reproducción se conservan las seis carpetas runs/v27_CPU_REP_s*, sus redes inicializadas individualmente, historias, estados finales y JSON de tests de roles y auditoría contrafactual.

## Integridad y procedencia

Preregistro PREREG_V27_INDEPENDENT_NEURAL_SEEDS.md; entrenador V23 idéntico al commit de referencia 210fc99a; evaluación v23_joint_holdout.py y causal v23_joint_audit.py. Los modelos de GPU se recuperan de results/METRICAS_V23.json, y los nuevos de results/v23_joint_holdout_v27_*.json y results/v23_joint_audit_v27_*.json. No se han cambiado las semillas de evaluación en función del resultado.

Hash del preregistro:
31a8e518057dde516ec7bd11eee3402ac5c05aa6c27e71587c4d5a804ec66c4d