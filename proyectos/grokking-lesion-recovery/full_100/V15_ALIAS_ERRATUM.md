# V15 — errata de integridad y repetición obligatoria

**9 de noviembre de 2026.** En la primera ejecución de V15 se detectó un fallo de aislamiento del estado de AdamW antes de agregar o interpretar resultados.

## Hallazgo técnico verificable

En el entorno de GALEXY_TRAVEL (PyTorch 2.15.0+cpu), llamar a
\`opt.load_state_dict(original_state)\` desde un objeto que se pretende reutilizar comparte almacenamiento con los momentos y contadores originales. El diagnóstico examinó los punteros \`data_ptr()\` de las entradas \`step\`, \`exp_avg\`, \`exp_avg_sq\` de los cuatro tensores de parámetros: **12/12 tensores comparados compartían almacenamiento**.

Así, un experimento de recuperación con optimizador reanudado podía **modificar el estado de inicio de los experimentos siguientes**, contaminando el resultado y violando el diseño de lesiones emparejadas.

**Acción de integridad:** se detuvieron expresamente los procesos de V15 relacionados, PID 25748 y 7632, una vez verificados sus comandos. Los archivos ya escritos, 480 al momento de la cuarentena, se MOVIERON SIN BORRAR a \`C:\Programación\v15_invalid_optimizer_alias_20261109\`, fuera de la carpeta portable y del análisis/publicación. **Ninguno de esos datos es válido para V15 y no debe analizarse, mezclarse ni citarse como resultados científicos.**

## Reparación

Se modifica el código de V15 para que **cada** rama utilice
\`opt.load_state_dict(copy.deepcopy(original_state))\`
antes de crear un optimizador entrenable, y se incluye un control explícito de ausencia de punteros compartidos entre el estado original y el nuevo optimizador. El archivo \`v15_check_optimizer_alias.py\` demuestra la diferencia entre la carga insegura y la carga aislada. La prueba debe ejecutarse y aprobarse antes de repetir V15. La reconstrucción de los diez modelos desde V12 (V15_REBUILT con máximo error de pesos = 0) **no está afectada** por este problema; puede reutilizarse.

## Alcance de la errata

Afecta únicamente a la **primera ejecución inválida de V15** en la que se reutilizó el mismo objeto de estado de AdamW entre múltiples lesiones. Los experimentos V10–V14 ya auditados no reusaban así ese objeto en múltiples ramas y no hay evidencia de que sufrieran esta contaminación concreta. La interpretación de V14B como comparación de estados de optimizer sigue siendo técnicamente válida: en aquel script cada modelo y estado de optimizer se cargaron una vez desde disco para una única continuación, evitando contaminación entre corridas.

## Compromiso de reproducibilidad

Registrar los resultados de la nueva ejecución solo después de verificar: misma precisión/deterioro inicial entre ramas de optimizador, índices enmascarados iguales, tests de alias PASS, callbacks de control intacto y cardinalidad 240. Si alguno falla, V15 permanece NO VÁLIDO. Las corridas inválidas quedan preservadas únicamente como evidencia del bug, nunca como datos científicos.
