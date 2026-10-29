# SRC104 — auditoría de hoja original recibida: integridad, esquema, reciprocidad y valores ausentes

**Clasificación:** inspección descriptiva de calidad de una copia XLSX aportada expresamente por el investigador. NONCYCLE / NONCONFIRMATORY / NO NEW MODEL TESTS. Fecha 2026-10-29. **HEAD de partida verificado:** 2d679f62d04467c9648aa3062df6407c9c9aeb23. **STOP_R5_EXTERNAL sigue vigente**. Ningún identificador individual, fila original, fecha concreta de encuentro, nombre de audio ni voto de persona se introduce en este documento.

## 1. Identidad de archivo y cadena de procedencia

Copia aportada como **rspb20181634_si_001.xlsx**, 232.002 bytes, ZIP OOXML válido sin corrupción comprobable por zipfile.testzip, sin macros VBA ni vínculos externos de libro registrados.

SHA-256 de **esta copia recibida**: **91c0bb93e699cc003ad32a11c51d38da6018cf9851b613822ecb19ef5618be00**. El valor proviene de lectura real del archivo local; **no** es el hash autenticado de los bytes originales en Figshare, porque no se consiguió descargar allí el fichero ni un checksum oficial. Por ello, la coincidencia con la versión publicada es **consistente por tamaño y estructura**, pero no está demostrada bit a bit. La ficha original SRC104 ya identificaba el suplemento de autores como **rspb20181634supp1.xlsx** (~226,56 KiB = 232.002 bytes); la diferencia de **nombre** debe preservarse, sin renombrar la copia como si se hubiera descargado desde el DOI.

Fuente del depósito original: https://doi.org/10.6084/m9.figshare.7410575.v1 ; artículo https://doi.org/10.1098/rspb.2018.1634 . Se conserva la licencia **CC BY 4.0 declarada en la ficha original del ítem Figshare**. La licencia de material publicado no garantiza por sí misma que la redistribución de registros románticos potencialmente enlazables cumpla minimización, finalidad, privacidad o RGPD. Esta auditoría **no redistribuye el XLSX** y no consta custodia/autenticación forense frente al repositorio editorial.

## 2. Hojas y granularidad comprobadas, sin seudorreplicación

| Hoja presente | Rango observado | Clase |
|---|---|---|
| Table S1a | A1:K87 | Resultados/modelos publicados, no encuentros independientes |
| Table S1b | A1:Q368 | Coeficientes/resultados publicados |
| Table S2 | A1:G89 | Medias marginales publicadas |
| Table S3 | A1:I49 | Regresiones/resúmenes publicados |
| Raw annotated data | **A1:AD727** | **726 filas x 30 campos**: observaciones segmentadas de voces, NO 726 encuentros únicos |

La quinta hoja contiene las variables originales relevantes **Group, Date, Participant ID, Sex, Round, Time segment, Dates_ID, Chose_date, Chosen_by_date, Chosen_both_match** junto a información individual y 10 campos acústicos. **Cada encuentro dirigido de un participante con una contraparte se repite exactamente tres veces**, una por segmento temporal de voz. Tras agrupar por sesión + respondente + Dates_ID, quedan **242 registros de encuentro dirigido**, **30 IDs de participantes con voz** en **dos sesiones**. Las triples filas de audio **no** son réplicas de decisiones ni 726 díadas independientes.

El par de variables de voto indica si el respondente eligió a su cita y si la cita eligió al respondente; no reemplazar esta semántica por `A_{ij}` solicitud secuencial y `R_{ji}` respuesta condicional sin puente específico. La columna Chosen_both_match registra el producto/estado de coincidencia, NO formación comprobada de una unión.

## 3. Reconstrucción por claves y conflicto adversarial

**Algoritmo de auditoría de claves, sin experimento:** para cada encuentro dirigido deduplicado por 3 segmentos, formar clave (Group, Date, Participant ID, Dates_ID); buscar el registro **inverso** (mismo Group+Date, Participant ID=Dates_ID y Dates_ID=Participant ID). No usar Round como clave principal: **32 de las 116 díadas enlazadas tienen un valor de Round diferente entre sus dos registros**. Esto puede reflejar numeración relativa de cada participante; no se afirma que el libro tenga error de cronología real.

**Resultados de auditoría, sin publicar ninguna fila:**

- **116 díadas** tienen ambos registros dirigidos de persona y contraparte.
- **101/116 díadas** reproducen de modo coherente el voto entre la perspectiva de uno y la columna «elegido por la cita» de la otra persona.
- **15/116 díadas** tienen al menos una **discordancia de sí/no** entre ambas perspectivas. **No corregidas**, no atribuir automáticamente a error de participante: pueden proceder de transcripción, claves, codificación o una variable mal interpretada.
- **2 de las 116** presentan además desacuerdo en el indicador de match mutuo al comparar los dos registros (normalizando el texto/número). La comprobación interna dentro de cada registro completo sí da siempre match = Chose_date × Chosen_by_date.
- **10 claves de pareja** tienen una sola perspectiva en la hoja; de ellas, **8** mencionan Dates_ID de dos valores que no aparecen en la columna Participant ID de sujetos grabados, y **2** aluden a una persona grabada pero carecen del registro inverso.
- Se observan **126 claves de pareja no ordenadas** si se admiten las 116 enlazadas y las 10 de un único lado; **no** confundir con 126 encuentros acreditados por partes bilaterales.

La verificación directa de un registro parcial que diga «Chosen_by_date=1» no sustituye un voto verificable en la fila del otro individuo. La cadena para un test confirmatorio queda incompleta. **No se generaron ni corrigieron datos, no se imputaron votos, no se ejecutó modelo ESBM ni se analizaron sus efectos.**

## 4. Faltantes y estructura sensible

Los 242 registros de encuentro dirigido tienen **241** con Chose_date y Chosen_by_date binarios observados, y **1** sin ambos votos ni indicador de coincidencia. No hay ausencia de claves Group, Date, Participant ID, Dates_ID, Sex o Time segment; la variación de tipo en Round (números 10 y 11 almacenados algunas veces como texto) exige normalizar **solo para QA**, nunca para forzar un join discutible.

Faltantes **a nivel de 242 registros dirigidos, no de 726 filas**: Age=12; Height=12; Weight=31; Match_score=1; Total matches=1; Chose_date=1; Chosen_by_date=1; Chosen_both_match=1; Dates_desirability_score=6; Dates_choosiness_score=6; previous-speed-dating count=18; months-since-last-relationship=34.

El archivo contiene identificadores seudónimos, datos individuales sobre vida sentimental, calendarios y nombres de archivos de voz. Bajo ninguna circunstancia incluir registros/identificadores, respuestas por persona, fechas concretas o el XLSX íntegro en un repositorio visible por otros. El hash identifica un artefacto, **no autoriza** su redistribución. La existencia de la licencia del Figshare de origen no sustituye evaluación de datos potencialmente sensibles y condiciones de privacidad.

## 5. Interpretación y puertas científicas

**Hallazgo documental/QA positivo:** había una vía legal efectiva por adjunto del investigador y sí hay campos nativos que remiten a la elección de ambos lados; no se deben tratar 726 filas como muestras independientes, ni afirmar ausencia de estructura de identificación. SRC104 está en una cohorte humana original distinta por descripción, aunque falta checksum original para autenticar exactamente el artefacto editorial.

**Hallazgo documental/QA negativo y decisivo:** la reciprocidad **no es perfectamente reproducible** al cruzar las dos direcciones: 15 conflictos en 116 díadas y 10 claves con un solo lado. No tratar los 116 como 116 decisiones recíprocas limpias ni imponer al algoritmo que un voto contradicho por la otra fila sea verdad sin regla previa. El match binario dentro de un mismo registro no valida la consistencia entre dos personas. Se excluye cualquier «reparación» post hoc en pos de significación.

**B0 composición/eligibilidad** y **B2 similitud**: los datos contienen participantes/eventos y algunas covariables, pero no un mapa completo y verificado de personas voluntariamente elegibles en todos los momentos ni exposición aleatoria. **B1/SRM** puede representar heterogeneidad actor–receptor–díada y es un control necesario si se llega a modelar; **B4** puede utilizar contexto, cupos y tiempo si se valida su significado, pero Round no es inmediatamente comparable entre los dos registros. **B6** requiere historial temporal válido y decisiones anteriores verdaderas; las tres tomas de voz dentro de una misma cita NO son tres decisiones secuenciales. El conjunto es de solo **dos eventos**, sin potencia por mercados ni variación de política independiente; la tesis ESBM sigue siendo integradora y no una ley causal validada.

**R5 continúa bloqueado**: se obtuvo una copia y se auditaron su esquema y calidad, pero faltan reconciliación de fuentes para los conflictos, archivo original canónico/hash editorial, diseño de identificación, nueva predicción incremental frente B0/B1/B2/B4/B6, suficientes mercados y holdout independiente. Un artefacto publicado/anterior a prerregistro NO se convierte en holdout virgen por ser nuevo para el asistente. Incluso resolver estos 15 conflictos no desbloquea automáticamente ningún ciclo.

## 6. Contabilidad y decisión

Fuente **SRC104** actualizada con SHA-256 de copia y auditoría estructural; **no** añadir una segunda fuente ni un nuevo estudio por las hojas suplementarias. **U159** amplía cualitativamente P-DYADIC_ACCESS (se han leído bytes de segunda fuente humana original, pero con join parcialmente inconsistente y sin validación). **U160** registra P-OPPORTUNITY como NO_CHANGE_WITH_REASON (no aleatorización de oportunidades/política ni evidencia causal). Priors 30; fuentes 104; revisiones 160. **0 AB-R válidos/ inválidos/ planning nuevos; N93–N106 siguen reservados; 26/40 válidos históricos; CT2 7/100 ordinal; madurez ponderada 41.20% sin cambios; STOP_R5_EXTERNAL.**

No se alteran el código original esbm_dynamic.py ni THEORY_V2, los informes adversos N83/N88–N92, los parámetros, las puntuaciones o el ledger histórico. **NO_PREREGISTRATION / NO_CONFIRMATORY_TEST / NO_CYCLE.**

