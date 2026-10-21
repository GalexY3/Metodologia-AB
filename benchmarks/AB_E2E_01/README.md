# AB-E2E-01 — Benchmark preregistrado AB vs baseline competente

**Estado: PREPARADO, NO EJECUTADO CON AGENTES.** No hay resultados de superioridad de AB. El código implementa selección reproducible, cegamiento del grader y análisis pareado por cápsula, pero no ejecuta modelos LLM ni descarga datasets.

## Requisitos

Python 3.10+ y `numpy`. Datos de BixBench obtenidos legítimamente y un sistema de ejecución que pueda iniciar **contextos de agente separados** con el mismo modelo, herramientas y límites. Puntuador oficial BixBench o evaluadores externos ciegos. No colocar tokens ni credenciales en este repositorio.

## 1. Inventario de tareas

Crear `inventory.csv` con columnas `task_id,cluster_id,benchmark`. `cluster_id` debe ser la cápsula/cuaderno independiente, no la pregunta. Una fila por pregunta disponible, con IDs estables; no incluir las respuestas. Validar que existen 60 cápsulas distintas antes de confirmar. Registrar hash de dataset y versión.

## 2. Congelar selección y aleatorización

```bash
python benchmark_ab.py prepare --inventory inventory.csv --out runs --clusters 60 --replicas 2 --benchmark BixBench --seed AB-E2E-20261021-LOCKED-01
```

`assignments_RESTRICTED.csv` indica el brazo y **solo** lo utiliza el ejecutor; `grader_manifest_BLIND.csv` excluye el brazo. Los agentes deben empezar con contexto limpio en cada ejecución, usar `PROMPT_AB.txt` o `PROMPT_BASELINE.txt` y recibir el mismo dataset y presupuesto.

## 3. Envío ciego al evaluador

El ejecutor crea `submissions.csv` con `run_id,answer`, sin respuestas de referencia. Preparar fichero de evaluación:

```bash
python benchmark_ab.py blind --submissions submissions.csv --assignments runs/assignments_RESTRICTED.csv --out blind.csv
```

Un evaluador independiente puntúa cada `run_id` en [0,1], genera `scores.csv` con `run_id,score`, **sin acceso al brazo**. Un fallo o timeout se registra explícitamente con 0. No se admiten filas faltantes.

## 4. Análisis

```bash
python benchmark_ab.py analyze --assignments runs/assignments_RESTRICTED.csv --scores scores.csv --out analysis --replicas 2
```

La unidad inferencial es la cápsula. El análisis produce `cluster_results.csv` y `summary.json` con diferencia AB−baseline, bootstrap por cápsula y prueba de signos pareados. La inferencia es válida solo si el diseño real cumple los supuestos de aislamiento, aleatorización y evaluación ciega. El análisis estadístico no verifica por sí mismo la validez del grader.

## 5. Pruebas de infraestructura

```bash
python test_benchmark_ab.py
```

Utiliza exclusivamente respuestas ficticias para comprobar determinismo, agrupación, ocultación del brazo y rechazo de calificaciones incompletas. **Un test satisfactorio NO es un experimento sobre AB.**

## Limitaciones y próximos pasos

Se necesitan datos de benchmark, dos brazos de ejecución independientes, un grader ciego y un presupuesto real de llamadas al modelo. No ejecutar los dos brazos secuencialmente en el mismo contexto de conversación. Antes de publicar resultados, auditar fugas de respuesta, variación de modelo, coste, calibración del evaluador y pseudorreplicación. Ver `PREREGISTRO_AB_VS_BASELINE_v1.md`.
