# N257–N276 · Preparación metodológica (NO EJECUTADA)

Fecha: 2026-10-30. Autorización: 20 ciclos AB-H PIVOT N257–N276.
Rama de origen: research/ab-h-esbm-polynomial-blossom-n237-n256-20261030.
HEAD de origen verificado: 7307f81174dab5050bf3f28f04235e7dc6666e74.

## Estado exacto
Este documento es **planificación previa, no prerregistro A–J completado**, no congelación de código instrumental, ni ejecución experimental. **Ciclos utilizados: 0/20. Quedan: 20/20.** No hay resultados nuevos de N257–N276. No marcar PASS/FAIL sin ejecución.

El informe anterior afirma 60/60 coincidencias de métricas y track histórico N144/T16/K7, pero no paridad de eventos individuales. N242 terminó SIGSEGV (-11) n143, N246 timeout 12s n144 casi completo. Fuente original SHA256 f7e6b84000720cbdf2ee0800c2b10d136185facd00e4622756cbb5f8d8254d0b. ZIP anterior ESBM_ABH_N237_N256_Blossom_60corridas.zip SHA256 349414236fb7d075e9c024efb7c56faf616fd46d79454963e30db6d832aa144c, no alojado íntegramente en GitHub.

## Puertas para comenzar un ciclo
1. Recuperar exactamente fuente C++ Boost, TS, wrapper Python, fixtures y recibos del ZIP anterior; verificar SHA por archivo frente a PREREG_AJ_SHA_FREEZE.json. Un nuevo instrumento sin esa cadena de custodia **no es reproducción literal** de los fallos.
2. Construir instrumento de comparación evento-a-evento que registre para cada semilla/escenario/tick: identidades y orden de exposición, propuestas dirigidas, respuestas, parejas no dirigidas, orden de empates, pesos y estado antes/después. Registrar primer punto de divergencia; no colapsar en métricas agregadas.
3. Preinscribir por cada N A–J (pregunta, rival, falsador, instrumentación y SHA, plan de ejecución, controles, independencia, tratamiento del prior, CT2/grado y decisión), además de política determinista de semillas, límites de tiempo/RAM, observaciones protegidas y reglas de detención.
4. Congelar código y hashes en commit GitHub anterior al primer outcome **de cada instrumento/serie**. Reparaciones requieren una nueva congelación prospectiva. No insertar resultados post hoc en un contrato retrospectivamente.
5. Distinguir objetivo lexicográfico cardinalidad+peso exacto de identidad de matching y de identidad de decisiones secuenciales. Para empates, comparación de conjuntos de emparejamientos óptimos cuando sea computable y política explícita de desempate; no declarar igualdad individual por sólo igualdad de objetivo.
6. Diagnóstico SIGSEGV: aislar primer fixture n143 original, minimización delta-debugging sin mutar el test, ejecutar sanitizers ASan/UBSan en binario de depuración, registrar backtrace y comparación NetworkX. Separar defecto del adaptador, del algoritmo y del entorno.
7. Diagnóstico timeout: conservar grafo n144 original, medir tiempo/RSS por fase con presupuesto preinscrito, reproducir con límites de seguridad, comparar implementación exacta alternativa y documentar casos irresueltos.
8. Contraste histórico: ejecutar cada escenario sólo si añade comparación individual predefinida; no repetir 60 agregados sin trazas.
9. R5 humano STOP; CT2 7/100. ESBM original y SRC104 intocables. Prohibido SSJY, licencias aceptadas, autores contactados, merges o CI costosa.
10. Tras resultados: añadir recibos inmutables, ledgers A–J, SOURCES/PRIORS/UPDATES explícitos, reportar fallos, CT2 sin inflación.

## Prioridad propuesta (no asignación de resultados)
Primero N257: replicador estricto de fixture N242 con sanitizer y diagnóstico; N258: N246 con perfilado; siguientes slots sólo según novedad instrumental, paridad individual y controles adversariales. No consumir cupos por pruebas redundantes.

Este documento no constituye prueba de depuración, paridad ni reproducibilidad completa.
