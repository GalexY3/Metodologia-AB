# Puerta externa R5 — dos nuevos estudios originales con votos reales; licencias y ficheros no verificados

**Fecha 2026-10-29 · Tipo POST_HOC_DOCUMENTARY_NONCYCLE · HEAD verificado al inicio `3cfb23b91f21ee103c3db21821fddc470098c3e5`.** Dictamen: **dos nuevos originales de cohortes candidatas** (`SRC105`, `SRC106`), SIN datos originales descargados, SIN nueva evidencia discriminante de ESBM, SIN liberación de `STOP_R5_EXTERNAL`. Ningún ciclo N93–N106 abierto, simulado o completado; no se aceptaron licencias ni contactaron autores/participantes.

## 1. SRC105 — Emanuel Jauk y colaboradores (2016), elecciones bilaterales originales en Graz

**Primario**: Jauk, Neubauer, Mairunteregger, Pemp, Sieber y Rauthmann (2016), [*How Alluring Are Dark Personalities? The Dark Triad and Attractiveness in Speed Dating*](https://doi.org/10.1002/per.2040), *European Journal of Personality* 30, 125–138. [Copia íntegra del artículo alojada en web académica](https://scottbarrykaufman.com/wp-content/uploads/2016/01/Jauk_et_al-2016-European_Journal_of_Personality.pdf). El artículo original, §§Method/Participants, Speed dating, Procedure, comunica **90 participantes**, 46 mujeres y 44 hombres, en **tres eventos presenciales** (proporciones 14:11, 19:18, 13:15) y **691 encuentros reales de tres minutos** (`14×11+19×18+13×15=691`). Cada persona emitió tras la cita una decisión **sí/no de volver a verla**, separada de escalas de atractivo subjetivo; solo mutuamente afirmativos recibían información de contacto. Se conservaron tres grupos/eventos y se estimaron efectos SRM de actor/receptor y reciprocidad con votos verdaderos; esto es **prior art específico** de ESBM v2, no una nueva teoría original.

**Repositorio original identificable**: [proyecto OSF del autor](https://osf.io/j4fcb/) y [código fuente/documentación de R `codebook`](https://rubenarslan.github.io/codebook/articles/codebook_sav.html), que documenta expresamente dos archivos SAV del estudio `DarkTriadDate_person.sav` (unidad individual) y **`DarkTriadDate_dyad.sav`** (unidad relación/encuentro) e incluye glosario de variables; las variables de pareja previamente conocida fueron filtradas para análisis derivado. La documentación de `codebook` es auxiliar, **no** un estudio humano distinto. No se ha obtenido el archivo SAV completo ni auditado si conserva dos decisiones independientes emparejables, IDs por evento, orden, filtros, lagunas o valores originales. El ejemplo de R documenta un subconjunto individual para demostración; **no es sustituto de la tabla de díadas**.

**Derechos**: ni el artículo ni la página del ejemplo de R acreditan **licencia de reutilización de los SAV originales**. El metadato de ejemplo `requiresSubscription=True` es propio de la distribución descrita y no demuestra acceso concedido o requisitos resueltos. OSF no se ha intentado de nuevo, de acuerdo con las vías anteriores agotadas; no se ha aceptado ninguna licencia. Graz Hofer 2021 `SRC083` es otra publicación/cohorte potencial, pero **independencia de individuos no cotejada**; la coincidencia institucional y de un coautor obliga a cautela.

## 2. SRC106 — Hall, Hart y Lambert (2026), nueva serie original con decisión de segunda cita

**Primario**: Hall, Hart y Lambert, [*Do Narcissistic People Have More Dating Success? Evidence From a Speed-Dating Study*](https://doi.org/10.1111/jopy.70059), *Journal of Personality*, publicado por primera vez el **19 de febrero de 2026**. La **página original Wiley**, Methods, informa de **129 estudiantes** en **ocho eventos de speed dating**, con evaluaciones de cada cita y **decisión explícita de querer una segunda cita**. El *Data Availability Statement* dice que los datos de resultados están disponibles en [OSF, enlace publicado por el editor](https://osf.io/tn9mj/?view_only=3f9ff1f5fa604089ac66f2de3058df01).

**Límites**: la disponibilidad editorial **no demuestra** licencia concreta de los ficheros, posibilidad de copia o existencia de una tabla con dos yes/no nativos enlazados por persona, pareja y evento. No se ha visitado OSF ni descargado bytes porque esa vía general ya fue agotada y el usuario no autoriza reiterar intentos fallidos. Los 129 participantes y ocho eventos **no son equivalentes** al tamaño de una muestra de díadas independientes; sus resultados ya se publicaron y no son un nuevo holdout pre-outcome. En ausencia de fechas, códigos de participantes y esquema, independencia absoluta de otros estudios **no verificada**. No se infiere duración real de una relación ni causalidad.

## 3. Fuentes evaluadas y descartadas como nueva liberación

- **SRC104 Pisanski**: no se encontró código primario de asignación entre `Round`/`Dates_ID` y cuadernillos originales distinto de los métodos y el suplemento ya auditados. Siguen los **15 conflictos** y el dictamen de incompatibilidad **condicional 38>36** del informe anterior; no alterar hojas, voces, ID o votos, ni declarar limpia la cohorte.
- **Jauk (SRC105)**: mejor documentación de 3 eventos y elección efectivamente bilateral, pero licencia/datos originales siguen sin comprobar.
- **Hall (SRC106)**: mejor oportunidad documental por 8 eventos y depósito expresamente afirmado en editorial; falta igualmente la prueba de licencia, estructura, IDs y derechos, por lo que no se presenta como accesible/reutilizable.
- **French, Bolton y Meltzer 2024**, artículo original de virtual speed dating DOI `10.1111/pere.12548`, documenta decisiones, pero el editor declara **datos disponibles solo previa petición al autor**; materiales OSF son guía del protocolo, no base abierta, por lo que se excluye como acceso legal inmediato.
- **Finn, O'Nell y Sánchez, corpus Blink Date de conversación/segunda cita, 2025–26**: depósito CC BY4 publicado en catálogo NLM, pero outcome distribuido es **binario compuesto de si hubo segunda cita**, no dos votos nativos personales. El podcast original recoge deseos separados, pero no se ha acreditado que los publique como columnas individuales; no sirve para R5 con votos bilaterales independientes.
- **CRAN `codebook` `darktriad.sav`** es muestra DEMOSTRATIVA de origen SRC105 y centrada en personas, no datos dyádicos de 691 encuentros, no corresponde contabilizarlo como nuevo estudio o dataset confirmatorio.

## 4. Matriz de puertas duras, independencia y originalidad ESBM

| Condición | Jauk 2016 | Hall 2026 | Puerta |
|---|---|---|---|
| Encuentros reales con oportunidades | 691 citas, 3 eventos, método original | 8 eventos, 129 personas, método original | Documento **sí**, roster completo aún NO |
| Decisiones nativas individuales después de la cita | **Sí, en paper original** | **Sí, decisión propia en paper original** | Join dos partes en datos **NO auditado** |
| Ficheros originales identificados | 2 SAV nombrados, OSF según `codebook` | OSF citado explícitamente por editor | **Sin bytes/ID/sha** |
| Licencia específica de microdatos | **NO verificada** | **NO verificada** | **NO liberada** |
| Cohorte no solapada con registro | Descripción compatible con cohorte nueva, solapamiento real no auditado | Ídem | **NO demostrado sobre individuos** |
| Predicción exclusiva ESBM frente B0/B1/SRM/B2/B4/B6 | SRM y atracción bilateral ya literatura | Sin novedad ESBM | **NO** |
| Holdout independiente y presupuesto igual | Resultados originales publicados | Resultados originales publicados | **NO** |
| Contracto A–J y SHA antes de outcomes | No existe, auditoría posterior | No existe | **NO** |

**Falsador operacional y única puerta hacia un ciclo AB-R:** fuente original cuya licencia y consentimiento permiten investigar los datos, ficheros obtenidos legalmente con SHA, esquema real de oportunidad + actor + contraparte + dos decisiones propias (no un sí/sí agregado), integridad de join, identificación de sesiones/orden cuando se evalúe historia, hipótesis distintiva ESBM congelada ex ante que compita con B0/B1/SRM/B2/B4/B6 con la misma información y verdadero holdout independiente. Si no se cumple todo, no abrir N93 ni descontar saldo. Las ocho cohortes reportadas no dan licencia implícita ni potencia confirmatoria sin diseños/supuestos.

## 5. Registro y cierre

Dos fuentes primarias nuevas **SRC105 y SRC106**, sin acceso nuevo a microdatos. `U165` `P-DYADIC_ACCESS` y `U166` `P-NOVELTY`, **ambos NO_CHANGE_WITH_REASON**, 0 nueva probabilidad posterior, hallazgos de grado 0 por insuficiencia de identidad causal. **106 SOURCES / 30 PRIORS / 166 UPDATES**, **26/40 ciclos válidos históricos**, **N93–N106 14 reservados/0 abiertos**, **0 nuevos válidos, inválidos o de planificación**, **STOP_R5_EXTERNAL**, **CT2 ordinal 7/100**, madurez ponderada **41.20%**. ESBM v2 sigue siendo un modelo computacional **integrador no calibrado, sin originalidad predictiva o causal acreditada**. Ningún dato personal, archivo original o registro sensible ha sido publicado. Nada de este expediente sustituye el preregistro A–J o autoriza estudios humanos.

