# Mercados de pareja · revisión de acceso original distinto y prueba bilateral reciente (29/10/2026)

**Clase de registro:** puerta documental y auditoría R1–R5 de material científico realmente nuevo. **NO ciclo AB-R A–J. N83 NO ABIERTO.** Rama `research/ab-r-mercados-pareja-20261028`. Saldo anterior y final: **16 de 20 válidos; N83–N86 sin iniciar (4); STOP_R5; CT2 7/100 ordinal, no probabilidad**. En esta revisión: 0 ciclos válidos, 0 inválidos, 0 de planificación; 0 modelos y 0 simulaciones; 0 filas originales nuevas de resultados leídas; 0 aceptaciones de licencia; 0 contactos a autores; 0 SSJY.

## Contexto auditado y criterio de novedad

Se consultaron `AGENTS.md`, `README.md`, AB 3.2.1 y anexos O1–O7, `CURRENT.md`, `ABR_SSJY_STAGE_N82_20261029/LEDGER.json`, `ABR_SSJY_STAGE_N82_20261029/CT2_TRAJECTORY.json`, informe Tawkify, inventario de 85 SOURCES, 30 PRIORS y 113 UPDATES preexistentes. No se duplican SRC056–057 Arias-Sarah, SRC081 Mixmosa, SRC083 Graz, SRC084 UKDS ni SRC085 Tawkify. Las dos fichas SRC086 y SRC087 corresponden a muestras y publicaciones nuevas respecto al inventario, **no a dos datasets nuevos procesados ni a dos replicaciones**.

### SRC086 — Pronk & Denissen (2020), depósito original DataverseNL

- Archivo original [DOI 10.34894/8WQ1UC](https://doi.org/10.34894/8WQ1UC), [ficha institucional Tilburg](https://research.tilburguniversity.edu/en/datasets/replication-data-for-a-rejection-mind-set-choice-overload-in-onli/), [metadatos B2FIND](https://b2find.eudat.eu/dataset/f986f50d-309b-5eb7-996f-70de9916ceb7), [artículo original DOI 10.1177/1948550619866189](https://doi.org/10.1177/1948550619866189).
- Tres estudios publicados; **Estudio 2: 158 participantes (82 hombres, 76 mujeres)**, perfiles de personas realmente disponibles, decisión explícita de aceptar/rechazar por oportunidad, reciprocidad `match`, orden de presentación. Los autores reportan media de 2,15 matches por participante; **cifra publicada, NO calculada aquí**.
- Puerta: B2FIND etiqueta `info:eu-repo/semantics/restrictedAccess`, `OpenAccess=false`. No se ha accedido a archivos originales, no hay SHA256, codebook efectivamente inspeccionado, términos de reutilización aceptados ni auditoría de unión de registros. La publicación abierta no determina derechos de los microdatos. No confundir perfiles `available` con una plataforma que asigna oportunidades aleatoriamente; el estudio no mide duración de uniones.
- Antecedente adversarial **fuerte**: la caída de aceptación por orden de alternativas/choice overload no es una predicción nueva que ESBM pueda reclamar sin distinguirse de esta investigación. Su archivo constituye **una ruta institucional nueva** distinta de las vías previamente agotadas, pero **no desbloquea N83 mientras esté restringido**.

### SRC087 — Ogushi et al. (23/09/2026), decisiones bilaterales observadas en Japón

- [Artículo original](https://doi.org/10.3389/fcomp.2026.1893669), [texto editorial y disponibilidad](https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2026.1893669/full).
- Datos descritos por autores: 625 encuentros cara a cara; **619 con ambos sí/no de intercambio de contactos disponibles**. La tabla 2 publicada contiene 214 dos no, 105 sí únicamente mujer, 220 sí únicamente hombre, 80 sí mutuos. Estas cantidades son agregados **publicados por los autores**, no microfilas propias. `80/619` no describe supervivencia de pareja.
- El artículo ya propone predicción temporal multimodal con Random Forest: F1 ponderado publicado 0,6248 para decisiones de mujeres y 0,5379 para decisiones de hombres en las mejores especificaciones; autores indican incertidumbre frente al baseline aleatorio incluyendo cero. Posibles baselines adversariales también incluyen SRM actor/partner, preferencias ex ante, atributos del evento y comportamiento temporal, no solo mayoría.
- La declaración de disponibilidad afirma aportaciones presentes en el artículo/suplemento y posible consulta al autor, **no licencia ni descarga verificada de filas**. El artículo es CC BY, pero esa licencia editorial no acredita permiso de reutilización de registros personales. No se contacta a autores conforme a instrucciones.
- Cohorte japonesa original independiente de Columbia/Mixmosa/Tawkify, con desenlace más directamente bilateral que ratings de atracción; antecedente nuevo, pero **sin datos reutilizables obtenidos** y sin seguimiento de duración.

## R1–R5 y umbral para N83 (diseño prospectivo NO congelado)

**R1 — estimando:** prioridad a `P(aceptación_i=1, aceptación_j=1 | ambos tuvieron oportunidad real observada, elegibilidad, asignación/evento, tiempo)`. Distinguir reciprocidad mutua del sí de una sola persona; y distinguir intercambiar contacto, deseo subjetivo, relación formada, duración y bienestar. Las diferencias por sexo y orden son heterogeneidad, no causalidad automática.

**R2 — controles competentes:** modelos actor/partner (Social Relations Model, regresión mixta), propensión por elegibilidad y evento, popularidad objetivo observada *ex ante*, preferencias/pretratamiento, atributos socioeconómicos disponibles, posición de oferta, efectos del evento, interacción y secuencia; ML calibrado (regularización, RF/boosting) en paridad de columnas, exposición, presupuesto y splits; comparación explícita con Pronk, Joel 2017, Eastwick 2025, Ogushi 2026, Bruch 2018 y Leesch 2024. No usar random global pobre como único adversario.

**R3 — selección/multiplicidad:** ninguna hipótesis seleccionada de estos resúmenes podrá presentarse como prereg original. Antes de observar outcomes de un archivo nuevo, fijar una predicción específica que difiera del prior art, familia de hipótesis, estimando, tratamiento de dependencia de participantes, métrica principal, varianza por clúster y splits; **holdout externo de personas Y eventos/plataforma** si se reivindica generalización. Sin una cohorte independiente, no alegar validación externa.

**R4 — identificabilidad/ablaciones:** comprobar presencia realmente vista frente a simplemente disponible, decisiones explícitas vs silencio, selección de asistentes, randomización o no de orden/algoritmo, dependencia actor-target y sesgo de supervivencia; desactivar secuencia, percepción temporal y mecanismos definidos en simulación para verificar si los efectos eran impuestos. Sin diseño identificador no inferir efectos causales.

**R5 — valor marginal:** STOP_R5 se mantiene. N83 solo puede abrirse tras **derechos y consentimiento para investigación/reutilización verificados, microdatos originales efectivamente accesibles con SHA256, QA de claves, exposición bilateral y desenlaces, pregunta científicamente nueva con rivales y control fuerte, contrato A–J y script con SHA congelado ANTES de acceder a outcomes**. Estas condiciones NO se cumplieron. No fabricar código congelado ni fijar ahora un estimando que depende de columnas desconocidas.

## Dictamen y contabilidad

Se registran **SRC086/SRC087** y **U114/U115** (ambos `NO_CHANGE_WITH_REASON`); estados y número de priors se conservan: **87 SOURCES / 30 PRIORS / 115 UPDATES**. `P-BOUNDED` integra el antecedente real de choice-overload; `P-DYADIC_ACCESS` documenta el nuevo dataset bilateral publicado no descargable. Cambios documentales materiales **no equivalen** a incremento científico, ni a un ciclo N83.

**CT2** 7/100 ordinal constante; no hay nuevo punto porque esta revisión no es experimento. Ver [CT2 0–100 + vista ampliada N77–N82](../ABR_SSJY_STAGE_N82_20261029/CT2.svg) y [trayectoria JSON sin interpolación](../ABR_SSJY_STAGE_N82_20261029/CT2_TRAJECTORY.json). N1 nuevos=0; N2=0; N3=0. `CLEAN_CLONE_NOT_VERIFIED`; ningún dato personal difundido; `main` intacto.

**Siguiente puerta realmente accionable:** acceso por el titular a un archivo DataverseNL legalmente autorizado, o a otro dataset original con licencia verificada que aporte decisiones de ambos y conjunto de oportunidades, inspeccionado primero **sin outcomes**; si no existe, esperar evidencia nueva y mantener saldo. No repetir OSF web/API, Essex, Stanford, Gist ni revisión de los mismos catálogos.
