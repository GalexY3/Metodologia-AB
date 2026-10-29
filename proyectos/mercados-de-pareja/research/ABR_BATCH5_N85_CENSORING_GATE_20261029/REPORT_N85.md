# N85 · Supervivencia y censura en ESBM v2 — prueba congelada

Fecha: 2026-10-29. PRE-FREEZE COMMIT 25b9442346bb00b4598389129fbf84ff7ef7a487. Código audit_n85.js (Git blob 51bb177f77d647ad2bf8c3ac4f7cd2338cb213e1, SHA256 3edead1eb61e6315f6893e671095fb97848af838c06760fd97e0475efce74d9f), contrato PREREG_N85.md. Fuente esbm_dynamic.py blob 5fc9f63fd44ff81ce9ff6c900ba6bf24153356f2.

**Naturaleza:** 1 ciclo técnico formal/sintético ejecutado con resultado que evidencia una limitación, grado científico 0/3. NO ejecución de esbm_dynamic.py en Python, NO nueva muestra humana ni validación externa.

## A–J y resultados

Pregunta: sesgo al interpretar la media sobre relaciones terminadas como duración media bajo censura a derecha. Comparador competente: Kaplan–Meier RMST a 16 ticks y verdad analítica geométrica, no media ingenua. Diseño: 50.000 uniones sintéticas iniciadas en t0 para hazard constante 0.048,0.12,0.21, intentos de disolución t1..15, censura en 16; PRNG fijo 72a6e119; tolerancias y controles fijados antes de ejecución. Todas las aserciones y guardas contra fuente Python real pasaron.

| Hazard fijo | Terminadas | Censuradas | Media solo terminadas | KM RMST16 | RMST verdad analítica |

|---:|---:|---:|---:|---:|---:|

| 0.048 | 25982 | 24018 | 7.081 | 11.365 | 11.350 |

| 0.12 | 42660 | 7340 | 5.775 | 7.276 | 7.256 |

| 0.21 | 48496 | 1504 | 4.315 | 4.666 | 4.652 |

El estimador original de duración completada omite censuradas y responde a otro estimando. Esta limitación **ya estaba descrita en THEORY_V2.md**, así que N85 NO descubre por primera vez sesgo por censura; proporciona valores de contraste y una prueba reproducible independiente para una futura reparación.

**Límites R1–R5:** solo procesos sintéticos con riesgo constante, todos nacen en t0; el código Python completo contiene heterogeneidad y formación escalonada. No sustituir estos valores por medidas del modelo original ni por hechos sobre relaciones humanas. No hay validación causal, originalidad 2/3, holdout humano ni cambio CT2. Propuesta de reparación: exportar duración, evento/censura y tick de comienzo por unión; calcular RMST condicionado a definición explícita de cohorte y censura. Reejecutar el Python original y comparadores antes de declarar reparación operativa.

**Registros:** RESULTS_N85.json, LEDGER_N85.json, U134 sobre P-UNION-DURATION sin cambio. 97 SOURCES / 30 PRIORS / 134 UPDATES. 19/40 AB-R válidos, 21 sin consumir; N86–N87 liberados (2), N88–N106 reservados (19). CT2 ordinal 7/100 sin subida. Madurez 38.95% aproximada, +0.1 puntos solo QA.

**Estado:** STOP_R5 para cualquier tesis empírica nueva; no autores, permisos aceptados, SSJY, OSF/Essex/Stanford/Gist, microdatos públicos ni merge a main.