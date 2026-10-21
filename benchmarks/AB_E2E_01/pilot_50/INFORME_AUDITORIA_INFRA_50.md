# AB-E2E-01 · Piloto de 50 comprobaciones de infraestructura

Fecha: 2026-10-21. Estado: **AUDITORÍA TÉCNICA COMPLETADA; COMPARACIÓN CIENTÍFICA NO INICIADA**.

## Resultado observado

- Casos automatizados ejecutados: **50**, de diez familias, cinco variantes por familia.
- Verificaciones superadas: **50**; fallos: **0**.
- Tiempo de cómputo de los 50 casos: **0.0529 segundos** en la máquina local. No incluye preparación, lectura de fuentes, documentación ni escrituras remotas; no permite inferir la duración de 50 ejecuciones LLM.
- Trayectorias científicas BixBench independientes: **0**. Preguntas BixBench resueltas: **0**. Puntuaciones oficiales obtenidas: **0**.

## Cobertura de la batería

| Familia de control | Superadas / ensayadas |
|---|---:|
| `deterministic_assignment` | 5/5 |
| `inventory_order_invariance` | 5/5 |
| `balanced_and_blinded` | 5/5 |
| `duplicate_task_id` | 5/5 |
| `insufficient_clusters` | 5/5 |
| `missing_grading` | 5/5 |
| `duplicate_grading` | 5/5 |
| `invalid_score` | 5/5 |
| `missing_arm` | 5/5 |
| `equal_scores_zero_effect` | 5/5 |

## Interpretación y amenazas a la validez

1. **No cuenta para el n = 240 del prerregistro.** Las pruebas emplean identificadores sintéticos, datos ficticios y el programa `benchmark_ab.py`; no ejecutan modelos. El resultado no respalda ni refuta A01 ni altera la estimación de efecto AB vs baseline.
2. Cada familia se repite sobre pequeñas variantes de un mismo escenario; **50 casos no equivalen a 50 estudios independientes**.
3. El test de cegamiento verifica que la columna `arm` no aparece en el manifiesto ni en el fichero de respuestas de ejemplo; **no demuestra que un grader real no pueda inferir el brazo** por estilo, contenido o metadatos indirectos.
4. La instrumentación no incluye ejecución de LLM, validación externa de grader, autenticación o descarga de cápsulas BixBench, control efectivo de presupuesto ni aislamiento de contextos.
5. Se comprueba el comportamiento en las familias seleccionadas; no se garantiza ausencia de defectos fuera de estos 50 casos. Las pruebas de `NaN`, `inf`, scores extremos y texto ilegible se incluyen como variantes adversariales.
6. No se ha abierto un conjunto de resultados empíricos para seleccionar o modificar el método; el prerregistro E2E v1 se mantiene intacto. Esta batería es **exploratoria de software**, diseñada después del prerregistro, y debe declararse así.

## AB-DECIDE

**PASS para los diez tipos comprobados de infraestructura. STOP respecto a cualquier pretensión de superioridad de AB.** Próximo paso: ejecutar agentes verdaderamente aislados, acceder a datos reales y calificaciones oficiales con recursos y presupuesto comparables. No reportar Δ, IC95% ni p como si existieran resultados reales.

## Reproducibilidad

`python audit_50.py` desde el directorio `AB_E2E_01` junto a `benchmark_ab.py`; requiere `numpy`. Los 50 resultados, duración individual y errores se archivan en `ledger_50.csv`; el resumen está en `summary.json`.
