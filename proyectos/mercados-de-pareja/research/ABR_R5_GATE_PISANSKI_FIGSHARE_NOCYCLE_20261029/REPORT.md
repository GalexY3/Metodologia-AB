# Puerta R5 — nueva fuente original Pisanski et al. 2018 y archivo Figshare (SRC104)

**Tipo:** hallazgo documental primario, NO_AB_CYCLE; fecha 2026-10-29, HEAD de partida 1d253b5201dea0ca1d717ccd36a61dbafb83684c. **AB-DECIDE: STOP_R5_EXTERNAL**. La cohorte y depósito son diferentes de otras fuentes registradas según el artículo; la independencia a nivel de identificadores no ha podido contrastarse. No hubo ejecución, modelos, análisis ni acceso a datos humanos originales.

## 1. Prueba y licencia del depósito original

Artículo original: [Pisanski, Oleszkiewicz, Plachetka, Gmiterek y Reby, *Voice pitch modulation in human mate choice* (2018)](https://doi.org/10.1098/rspb.2018.1634), [PMC6304053](https://pmc.ncbi.nlm.nih.gov/articles/PMC6304053/). Sus apartados Methods §2(a)–(b), Data Accessibility y suplemento fueron comprobados. Los **30 adultos** de 20–40 años participaron en **dos** eventos de citas rápidas en cafetería, de **6 minutos** por encuentro, organizados con una empresa. Después de cada cita real **ambos** escribieron su propia respuesta **sí/no** para otra cita. Según el artículo, el 14% de citas produjo interés mutuo; es una cifra de autores, no una estimación nueva ni verificación de una relación. No atribuir automáticamente un país a la cafetería si el método no especifica ubicación exacta.

Depósito original del suplemento de los autores: [Figshare versión 1](https://doi.org/10.6084/m9.figshare.7410575.v1), colección [Figshare](https://doi.org/10.6084/m9.figshare.c.4320851). La ficha verificable de Figshare identifica **dataset con raw data y tablas** y **licencia explícita CC BY 4.0 del ítem**; PMC enlaza **rspb20181634supp1.xlsx**, aproximadamente **226,56 kB**. Esto es mejor evidencia de derechos del **depósito específico** que una licencia atribuida únicamente a la publicación. No implica permiso automático de redistribuir filas íntimas si permiten reidentificar personas; aplicar protección y finalidad legales antes de tratamiento.

## 2. Fallo documentado de acceso al fichero, no ocultar

El enlace suplementario en PMC lleva a una pantalla «Preparing to download...»; el intento de descarga normal falló. Figshare redirige a un sitio no accesible por el lector web y su API no devolvió contenido. No se burlaron medidas de acceso, no se aceptaron licencias ni se contactó a nadie. **No se obtuvo ni inspeccionó archivo XLSX**: sin bytes, SHA256, hojas, diccionario, recuento de filas, códigos de evento, asignación de parejas, doble sí/no enlazable, ausencia/pérdida de respuesta u orden secuencial comprobados. Que las decisiones existieran en los folletos originales **no** prueba que ambas sobrevivan juntas en la hoja compartida. No inventar diadas leídas ni ejecutar test.

## 3. Relevancia y límites de identificación

Este candidato cumple **solo a nivel del método publicado** las condiciones de encuentros genuinamente realizados y dos decisiones nativas independientes: es superior conceptualmente a conjoint hipotético y recomendación ofrecida sin visualización. Sin embargo, los votos son **simultáneos después del encuentro**, mientras que ESBM v2 condiciona la respuesta a la solicitud unilateral. No hay prueba de mismo estimando, matching exclusivo observado, política exógena, aprendizaje por rechazo ni duración real. Dos eventos y n=30 son claramente insuficientes para demostrar efecto por aleatorización de muchos mercados independientes. No hay predicción exclusiva de ESBM frente a **B0 composición, B1/SRM actor-target, B2 homofilia, B4 congestión y B6 historia**, todos con el mismo presupuesto informativo.

Candidatos descartados sin duplicar registro: Harvard Dataverse [Bhargava–Fisman CC0, DOI 10.7910/DVN/27893](https://doi.org/10.7910/DVN/27893) puede reutilizar Columbia original, no se demostró otra cohorte; UNC Dataverse [Study I 2005](https://doi.org/10.15139/S3/HK7KZQ) y [Study II 2007](https://doi.org/10.15139/S3/52MIJO) corresponden a Northwestern 2005/07 ya en SRC084/SRC090 y catálogo indica derechos de reutilización limitados, no acceso nuevo; otros estudios encontrados solo redistribuyen Columbia, son corpus de conversaciones no románticas, o fueron investigados anteriormente. **No repetir vías agotadas ni SSJY.**

## 4. Evaluación de puertas R5

| Requisito | Estado y evidencia |
|---|---|
| Originalidad documental de cohorte | **CANDIDATA**: publicación independiente de autores y protocolo de dos eventos; identidad de participantes no auditada |
| Encuentros reales | **MÉTODO PUBLICADO SÍ**, denominador individual XLSX no inspeccionado |
| Dos sí/no nativos | **MÉTODO PUBLICADO SÍ**, correspondencia de ambas decisiones por díada **NO COMPROBADA** |
| Permiso específico de dato | **METADATOS FIGSHARE CC BY 4.0**, sin distribución de datos íntimos |
| Archivo/filas/ID/hash | **NO**, descarga no disponible; cero filas originales inspeccionadas |
| Holdout confirmatorio | **NO**, dos eventos, ya tratados por autores; sin plan independiente |
| Predicción exclusiva de ESBM frente B0/B1/B2/B4/B6 | **NO**, ESBM se mantiene marco integrador sin originalidad acreditada |
| Contrato A–J y SHA antes de outcomes | **NO**; este informe no es preregistro |
| Puerta R5 y plazas N93–N106 | **STOP**, ninguna abierta ni consumida |

## 5. Prior y siguiente puerta técnica

Nuevo **SRC104**, **U157 en P-DYADIC_ACCESS** y **U158 en P-OPPORTUNITY**, ambos **NO_CHANGE_WITH_REASON**. Si un acceso público directo normal permite obtener el XLSX posteriormente, registrar hash y comprobar **ID del evento, respondente, contraparte, dos votos originales por fecha y ausencias** sin copiar filas identificables a Git. Si falla el join, descartar posibilidad de prueba; si funciona, plantear únicamente exploración y no reabrir N93–N106 sin predicción incremental frente a rivales y evidencia independiente con A–J y código SHA congelados antes de outcomes. El reconocimiento de CC BY4 no sustituye obligaciones éticas ni RGPD. No afirmar replicación nueva ni 1/3–3/3.

**Cierre verificado antes del commit:** 104 SOURCES / 30 PRIORS / 158 UPDATES; 26/40 ciclos válidos históricos, **0 ciclos nuevos**, 14 N93–N106 reservados, 0 abiertos, **CT2 ordinal 7/100**, madurez ponderada **41.20%**, STOP_R5_EXTERNAL.
