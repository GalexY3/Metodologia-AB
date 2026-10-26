# PF-FOCUS20R · informe de cierre de los 20 ciclos AB autorizados

**Fecha:** 26/10/2026. **Programa:** Politics Fantasy League, continuación de BR10P (10/10) y AUDIT5Q (5/5). **Ejecución final: 20/20 fichas A–J formalmente concluidas**, bajo el [preregistro de 20 objetivos](PREREG.json) ya existente en el repositorio.

**Balance según [ledger](LEDGER.json): 18 aceptaciones técnicas/documentales delimitadas y dos STOP_R5.** No son veinte experimentos estadísticamente independientes, veinte hallazgos sociológicos ni veinte casos con personas reales. Los dos STOP_R5 corresponden al checksum firmado por el emisor y las condiciones jurídicas de reutilización por clase de dato. El resto describe controles concretos de una misma fuente electoral histórica, pruebas de software y gobernanza del alcance.

## Resultado principal: corregir lo que significa «candidatura»

El PDF oficial [BOE-A-2023-15066](https://www.boe.es/boe/dias/2023/06/27/pdfs/BOE-A-2023-15066.pdf), de 27/06/2023, contiene 52 secciones provinciales del Congreso. La extracción sistemática produce **25 secciones de ordinales continuos, con 263 rótulos**; dentro de estas, **16 secciones (155 rótulos)** sin avisos conocidos y **nueve (108 rótulos)** con avisos de candidaturas *no proclamadas*. Un rótulo en una sección avisada **no es automáticamente una candidatura rechazada**, pero tampoco puede darse por acreditada su proclamación individual sin interpretar el aviso original. Este cambio semántico se impuso en [API](../../src/politics_fantasy/nomination_atlas.py), [UI](../../src/politics_fantasy/web/app.js) y las regresiones. Se preserva el nombre histórico de campo `n_candidacies` por compatibilidad, **con etiqueta de advertencia y campos específicos para distinguir 263 encabezados de proclamaciones validadas (desconocido)**.

## Recuperación original de las secciones en cuarentena

La salida íntegra del extractor autenticado en GitHub Actions había quedado en logs aunque el snapshot versionado solo retenía la parte de 25 secciones aceptadas. En [CI 40333527364](https://github.com/GalexY3/Metodologia-AB/actions/runs/40333527364) se reconstruyeron **47/47 fragmentos JSON en orden**, con validación de integridad sintáctica, coincidencia exacta de las filas de las 25 secciones aceptadas y verificación de fuente por PDF original. Se recuperaron **27 secciones con secuencia incompleta, 278 encabezados observados no certificados** y sus ordinales ausentes. Todos los IDs registrados en cuarentena son distintos y disjuntos de los aceptados.

El [sidecar de cuarentena](../../data/observatory/boe_2023_quarantine_unresolved.json) conserva identificador, fuente SHA-256, ejecución de procedencia, posiciones y avisos sin nombres de personas, puntuaciones o afiliaciones atribuidas. La [auditoría de calidad](../../src/politics_fantasy/nomination_quality.py) exige coincidencia de SHA, exclusión mutua, tamaño, tipado y ausencia de campos de identidad arbitrarios. La ruta de lectura [`/api/official-nominations`](../../src/politics_fantasy/server.py) y la vista Atlas exponen **solo** la triage de secciones y ordinales, no equivalen a un registro legal.

## Reproducción y auditoría adversarial

La ejecución [40334678838](https://github.com/GalexY3/Metodologia-AB/actions/runs/40334678838) completó sus **tres trabajos** de forma satisfactoria, incluida reextracción del PDF oficial 4.298.580 bytes SHA-256 `d1c179fcfab9889df272753ad3d44513f86cec703805219834b7d048ef0eda20`, cotejo por programa `MATCH_ORIGINAL_BOUNDED`, Node/Python y navegador. El original se vuelve a obtener por HTTPS verificado sin desactivar TLS.

La prueba de Chromium ampliada falló primero porque el test intentaba leer detalles colapsados y luego por una selección ambigua de los 28 elementos `summary` anidados. Ambos fallos se diagnosticaron mediante **logs reales**, se repararon el oráculo y el selector, y la ejecución [40336524912](https://github.com/GalexY3/Metodologia-AB/actions/runs/40336524912) terminó con los **tres trabajos exitosos**. El navegador abre mediante teclado el desplegable de cuarentena y comprueba datos de Burgos. También se mantiene la prueba HTTP de Host malicioso. La prueba de integridad de fuente comprende casos negativos de SHA diferente, datos de identidad sensibles añadidos y número de observaciones alterado. **No** es una auditoría de seguridad ni de accesibilidad integral.

## Dictamen AB y riesgo de inferencia

Los 20 ciclos fueron exploración/documentación/QA **adaptativas sobre un documento ya conocido**, no replicación de 20 experimentos. El control de selección exige mantener las hipótesis como prospectivas solo si se contrastan con material independiente. El resultado más importante es reparar la diferencia entre *presencia de texto*, *integridad de la extracción*, *condición jurídica de proclamación* e *identidad legal/individual*. El siguiente cuello de botella no se resuelve multiplicando tests: hace falta interpretación por candidatura de los avisos, resolución de las posiciones omitidas y padrón auténtico de partidos y cargos temporales.

**Bloqueos que continúan:** (a) 27 secciones con ordinales sin resolver; (b) nueve secciones con avisos no adjudicados individualmente; (c) registro RPP y reconciliación jurídica, coaliciones y roles personales con fecha; (d) eventos políticos atribuibles y first_public_at; (e) autenticación/autorización multiusuario y despliegue seguro; (f) condiciones de reutilización por fuente y firma del emisor independientes. Ningún encabezado de 2023 se convierte en mérito, influencia causal, militancia individual o estado político 2026 por analogía.

## Madurez del producto y destino de las evidencias

PFL-V1 revisión 3 **permanece en 36,350 %**, nueve sublíneas y 36 hitos, sin modificación del scope ni manipulación de gates; siguen los seis bloqueos críticos para el lanzamiento. No se altera VSDS **1/3**, CT2 multiactor **20/100**, CT2 predictiva **24/100**, ni se reclama N1/N2/N3 nuevo (**0/0/0**). El 36,35% es un indicador de madurez bajo rúbrica, no de probabilidad de lanzamiento ni de tiempo consumido.

**Archivos:** [preregistro](PREREG.json) · [ledger con 20 fichas A–J](LEDGER.json) · [resultados y hechos verificables](RESULTS.json) · [actualización acumulativa de priors](PRIORS_DELTA.md) · [atlas fuente y límites](../../docs/BOE_NOMINATION_ATLAS_2023.md). Se aconseja revisar/combinar posteriormente con la PR #11 de ingeniería sobre revisiones de eventos y CSP, conservando la separación de cambios.

**Decisión J de cierre:** `CLOSE_PF-FOCUS20R_20_OF_20; STOP_R5_FURTHER_SAME_SOURCE_BATTERIES; NEXT_EVIDENCE_NEW_ORIGINAL_ENTITY_ID_REGISTRY`. No hay ciclos autorizados pendientes en la campaña 35=10+5+20.
