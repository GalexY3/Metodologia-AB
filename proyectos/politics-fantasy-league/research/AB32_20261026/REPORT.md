# AB32 · Informe final de 32 ciclos adaptativos (26 de octubre de 2026)

## Resultado ejecutivo

**32/32 ciclos autorizados cerrados:** primeros **12/12 BRANCHING** y posteriores **20/20 adaptativos**. **26 conclusiones técnicas o documentales de alcance acotado** y **seis STOP_R5** (C16 y C19–C23). Los STOP_R5 no se transforman en «éxitos» para llenar cuota. Los 32 ciclos no son 32 experimentos sociológicos independientes.

**Fuente y QA final:** [GitHub Actions 40350939895](https://github.com/GalexY3/Metodologia-AB/actions/runs/40350939895), **4/4 trabajos correctos**, **111 tests Python** y **Chromium real** con navegación y panel de dos eventos fuente originales, sin puntuación de políticos. [Ledger secuencial completo](SEQUENTIAL_LEDGER.json) · [Resultados estructurados](RESULTS.json) · [Priors del bloque](PRIORS_DELTA.md) · [Traza C19–C23](C19_C23_ACTUAL.json) · [Traza C26–C32](C26_C32_ACTUAL.json).

## Hallazgo

Se han obtenido y examinado **13 JSON nominales originales del Congreso**, fechados en **11 días distintos** de 2024–2026, con URLs y SHA-256 de cada captura en el ledger y sus trazas; son muestras seleccionadas adaptativamente, no el archivo completo de la legislatura. Los JSON recientes de julio/septiembre 2026 presentan 350 candidatos a enlace de nombre exacto, concordancia de grupo y fechas válidas en las muestras contrastadas.

La comprobación de **9 de abril de 2024** cambió las creencias: dos votaciones distintas de la misma sesión ofrecen **349 registros cada una**, con **un nombre sin enlace exacto** con la instantánea de 2026 y **dos conflictos entre código/grupo histórico y último grupo del registro de 2026**. No adjudicamos quién es ni imputamos cambios de afiliación.

### Deriva temporal observada en una votación nominal fuente por fecha

| Fecha | Ciclo | Filas de voto | Cadenas de nombre sin enlace | Conflictos de grupo vs. registro 2026 |
|---|---:|---:|---:|---:|
| 2024-04-09 | C24 | 349 | 1 | 2 |
| 2024-04-09, segundo JSON | C25 | 349 | 1 | 2 |
| 2024-12-10 | C26 | 350 | 1 | 2 |
| 2025-03-25 | C27 | 350 | 1 | 2 |
| 2025-05-06 | C28 | 350 | 1 | 2 |
| 2025-06-12 | C29 | 350 | 1 | 2 |
| 2025-09-10 | C30 | 350 | 1 | 1 |
| 2025-11-27 | C31 | 350 | 1 | 1 |
| 2026-09-22 | C32 | 350 | 0 | 0 |

La secuencia muestra que **la concordancia con un registro contemporáneo no es uniforme retrospectivamente**. No establece causalidad, dirección de cambio de partido ni identidad de la cadena discordante. Cada SHA, URL y fecha proceden de una solicitud real a la fuente oficial, verificada dentro de CI.

### Población de diputados y cautela institucional

El catálogo oficial del Congreso devuelve instantáneas JSON de **137 «activos»** y **275 «de baja»**, con campos de nombre, circunscripción, grupo, formación electoral y fechas, pero **sin identificador personal inmutable explícito** en los campos analizados. Una fuente legal independiente [BOE-A-2026-20742](https://www.boe.es/buscar/doc.php?id=BOE-A-2026-20742) confirma la disolución de Congreso y Senado con fecha **06/10/2026**; por tanto, «activo» en el JSON de 26/10/2026 no se interpreta automáticamente como escaño ordinario vigente. El BOE no suministra retroactivamente el momento `first_public_at` de las votaciones.

Se integra al producto **solo un manifiesto de DOS votos históricos agregados**, totalmente cotejados con originales, en `GET /api/verified-rollcalls`; la interfaz los distingue del antiguo piloto manual. Contiene `first_public_at: null` y `real_person_scoring: false`, no personas ni atribución individual de puntos. La auditoría visible impide manipular fuente, puntuación o fecha pública en la API.

## Secuencia AB: decisión genuinamente posterior al dato

C01–C18 avanzaron mediante hipótesis por ciclo, prueba en GitHub Actions, evidencia y nueva hipótesis elegida tras el resultado previo. Tras C18, la primera política de muestreo prospectiva eligió fechas no documentadas desde 2024, con **C19–C23 cinco STOP_R5 consecutivos**. El ejecutor cortó la secuencia y actualizó heurísticos Beta (prior 1,1 → 1,6 para disponibilidad de fuente); **no aseguró que no existieran votaciones históricas**, sino que las fechas elegidas no tenían ficheros nominales enlazados en el calendario consultado.

El resultado obligó al **pivot C24** hacia la fecha que sí aparecía en el índice original de la institución. Hallado el desacuerdo de 2024, **C25** eligió replicarlo en una segunda votación de la misma sesión; se reprodujo. Los registros C26–C32 demuestran que **antes de cada petición se escribió la pregunta, fecha, alternativa y estado previo de creencia**, y solo tras recibir el original, computar la discrepancia y actualizar priors se eligió la siguiente fecha. Los priors Beta aquí son heurísticos de muestreo exploratorio, **no probabilidades calibradas de validez universal** ni resultados inferenciales con muestreo aleatorio.

## Separación epistemológica

- **Documental corroborado:** 13 ficheros originales recuperados, sus digestos, fechas, totales, intervalos de mandato observables y discrepancias fuente-a-fuente, más BOE institucional.
- **Ingeniería comprobada:** manifiesto fuente verificado, API local de solo lectura, pantalla separada, pruebas negativas de fecha/host/tampering, GitHub Actions y Chromium.
- **Pendiente:** fuente individual de identidad inmutable; historia de cambios de grupo; régimen exacto de derechos para cada tipo de uso; hora certificable de primera publicación `first_public_at`; medición válida de acciones y peso político real; atribución de puntos y seguridad multiusuario.
- **No demostrado:** que un diputado «merezca» más puntos por votar, influencia causal de persona en el resultado o emparejamiento jurídico global a partir de nombres.

La madurez contractual **PFL-V1 rev. 3 continúa 36,350 %**, seis gates sin liberar, **VSDS 1/3**, **CT2 20/100 y 24/100**, nuevos N1/N2/N3: **cero**. No se ha fusionado la rama en `main`.

## Siguiente cuestión de alto valor (sin autorizar nuevos ciclos)

Conseguir un **historial oficial de identificadores, nombramientos, sustituciones y cambios de grupo por individuo y fecha**, para discriminar errores ortográficos de variación organizativa. Si esa historia no existe en fichero estructurado, plantear adjudicación de casos mediante fichas personales del Congreso con procedencia verificable, manteniendo el STOP_R5 para toda identidad dudosa. No hay motivos para seguir puntuando automáticamente políticos reales con el esquema actual.
