# N358: reparación de auditor independiente (posterior a JS, previa al segundo Python)

Primer preregistro/commit antes de cualquier resultado: `bd0b74ef08d121747790d1d9f8fc20cb5f3ccd7f`.

El script JS ha ejecutado **8/8** controles predefinidos con estados PASS, PASS, PASS, RESOURCE_HARD_WALL, RESOURCE_HARD_WALL, INVALID_WORKER_JSON, WORKER_FAILURE y RESOURCE_OUTPUT. Resultado SHA256 **`5040466f5517142808052aab9d17128d0f526307bb9a587a09758cdc8c5d2b45`**.

El auditor Python inicial, SHA `eb4c78ff6ecc3f3bd3635ed90f19617724156739dd80b9ae7d65117afb460479`, se detuvo ANTES de escribir su resultado con `ValueError: not enough values to unpack (expected 3, got 2)`. El primer script asumió tuplas `[a,b,w]`, pero el JSON de salida contiene objetos `{pair:[a,b], weight:w}`.

Se modifica únicamente la lectura Python del formato de aristas; no se cambia el algoritmo exacto, no se cambian los controles ni los umbrales. Se conserva el error inicial y el JSON original byte idéntico. El nuevo archivo de auditoría Python y este documento deberán publicarse en GitHub en commit **anterior** a la segunda ejecución de Python. No volver a ejecutar el instrumento JS.

Una sola plaza N358 si la auditoría completa resulta ejecutada válidamente; el fallo instrumental de Python no consume otra. Sin inferencia sociológica. CT2 7/100 y STOP_R5 humano.
