# PF-SEQ32S · secuencia adaptativa autorizada (26-10-2026)

Autorización: **12 ciclos BRANCHING**, seguidos de **hasta 20 ciclos adicionales**, con decisión sobre el ciclo n+1 tomada **solamente tras revisar los resultados de n**. AB 3.2.1, contratos A–J, STOP_R5, priors acumulativos y separación de fuente/medición/puntuación. Este documento **no preregistra la lista futura de ciclos**.

Base: rama apilada sobre `research/pfl-final20-source-integrity-20261026` (PR #12, aún draft). PR #11 también draft e independiente. No fusionar ni afirmar seguridad pública. Progreso de referencia PFL-V1 rev3 = 36,350%; seis gates siguen bloqueados.

## C01 · prospectiva limitada / exposición previa (NO BLINDADO)
Hipótesis de trabajo: el cuello de botella de RPP puede resolverse antes que el de diputados si existe un conjunto abierto de identificadores legales reutilizables. Rival: un directorio web buscable sin bulk ni vigencias temporales será insuficiente; el Congreso podría proporcionar antes un universo de cargos públicos.

**Advertencia metodológica:** los portales del Registro y del Congreso ya estaban abiertos en esta conversación antes de escribir esta ficha; C01 es contraste documental exploratorio, no registro anterior a la exposición ni ensayo independiente.

Contrato antes de registrar la decisión n+1: evaluar accesibilidad de RPP, disponibilidad comprobable de datos originales de diputados, temporalidad y límites de reutilización. No asignar puntuaciones reales ni identidades registrales por coincidencias nominales.

## Resultado de C01 · observación y decisión
- Portal oficial RPP: https://servicio.mir.es/nfrontal/webpartido_politico.html (búsqueda por nombre/siglas/tipo/fecha, enlace desde datos.gob.es). Consultado vía web: error 502; no archivo bruto ni identificador legal verificado.
- Metadatos institucionales: https://datos.gob.es/es/aplicaciones/consulta-del-registro-de-partidos-politicos (actualización listada 2019, **no prueba** de actualidad de los datos).
- Congreso: https://www.congreso.es/gl/opendata/diputados ofrece CSV/JSON/XML; `https://www.congreso.es/webpublica/opendata/diputados/DiputadosActivos__20260725050010.json` sí devolvió contenido JSON oficial con campos de personas/circunscripción/formación/grupo/fechas. Es una instantánea de julio, **no el censo activo de octubre de 2026**.
- Senado: https://www.senado.es/web/relacionesciudadanos/datosabiertos/reutilizacion/index.html licencia general CC BY 4.0 salvo indicación contraria, con límites; no extrapolar al Congreso/RPP.
- **Dictamen J:** redirigir C02 a verificar un contrato de extracción del JSON del Congreso; mantener RPP sin reconciliación y sin datos inventados. No posterior numérico, puesto que no hay denominador ni ensayos independientes.

**C02, selección tras C01 (preregistro del siguiente contraste, no de C03–C32):** probar si los campos observados del JSON histórico permiten un registro de diputados estrictamente temporal y sin biografías ni ratings. Rival: nombre y fecha por sí solos no prueban identidad jurídica persistente ni vigencia actual. Criterio: parser fail-closed, títulos de fuente, schema mínimo, estado temporal, pruebas negativas. Si falla, volver a fuentes alternativas.

## C02 · resultado observado y actualización antes de elegir C03
- En [GitHub Actions 40341944931](https://github.com/GalexY3/Metodologia-AB/actions/runs/40341944931): Python local integration, JS source contracts, Chromium y descarga BOE pasaron; **la prueba de descarga propia del JSON Congreso falló con HTTP 404**. No se capturaron bytes originales ni se adjudicó identidad de personas; el proyector tiene tests de seguridad unitarios pero no una cohorte original importada.
- Actualización PF-S02: la existencia de un enlace oficial indexado no implica disponibilidad actual del archivo estático de julio, especialmente tras la disolución de las Cortes anunciada el 06/10/2026. Evidencia: HTTP 404 en runner; rival: acceso temporal o ruta histórica distinta. Sin probabilidad numérica por un único intento.
- **Dictamen J de C02: STOP_R5 para importación Congreso a partir de este URL**, conservar el código experimental NO conectado a producto; avanzar a C03 examinando documentación estable del BOE que vincule nombre de cargo y acto de nombramiento.

### C03 · preregistro decidido tras el 404 real de C02
Pregunta: ¿el nombramiento por Real Decreto 835/2023 (BOE-A-2023-23543) permite obtener una primera cohorte positiva de nombramientos con fecha y cargo, sin afiliaciones partidistas supuestas?
H1: sí, un PDF institucional de un acto único permite conciliación completa de todas las líneas de nombramiento. H0: extracción inconsistente, cambios en original, roles ambiguos o fallos de captura hacen imposible verificar la cohorte.
Instrumento: descarga HTTPS desde BOE, SHA-256, pdftotext -layout y cotejo automático de filas extraídas contra un snapshot explícito, con metadatos de fecha de publicación, no de fin de mandato. Éxito solo si los 22 actos se extraen y la comparación exacta da cero errores; de otro modo STOP_R5.
Efecto de alcance: **nombramiento de miembros del Gobierno en noviembre 2023 no equivale a legisladores ni cargo actual en octubre 2026**; no puntuación real.

## C03 · resultado observado, corrección adaptativa y decisión
- [GitHub Actions 40342767919](https://github.com/GalexY3/Metodologia-AB/actions/runs/40342767919) falló inicialmente porque el parser omitió **«Ministro del Interior»**. Se corrigió la gramática permitida (de/del/para), sin alterar nombres del documento.
- [GitHub Actions 40342982881](https://github.com/GalexY3/Metodologia-AB/actions/runs/40342982881): descarga oficial **193.759 bytes**, SHA256 `16f05bba24508af229870b68dbfb72ba258e62416713a8cfe5c49c70ba792efe`, **MATCH_BOE_CABINET_22**, cero divergencias; Python, Node y navegador separados pasaron / navegador completando en el momento de lectura.
- H1 sustentada **solo para 22 actos documentales de nombramiento de noviembre de 2023**. H0 sobre imposibilidad de transcripción se debilita para esta fuente tras reparar parser; H0 sobre ausencia de continuidad temporal sigue intacta. Sin estimación de eficacia predictor/fantasy.
- Priors PF-S03: una publicación jurídica única permite verificar nombramientos con cargo y fecha; **no** identidad RPP, permanencia en cargo o evaluación normativa. Falsador: edición del original SHA-pinned o errata/rectificación oficial posterior.

### C04 · preregistro decidido tras fuente original verificada
Pregunta: ¿puede exponerse la cohorte de 22 **nombramientos históricos** mediante API read-only con digest original fijado y sin permitir que filas alteradas asignen scoring/partido/mandato actual?
H1: lector fail-closed y negativos evitan promoción semántica; rival H0: UI/API filtran atributos arbitrarios, o metadatos de nominación se convierten en cargos presentes.
Contrato: snapshot digest igual a fuente observada; whitelist exacta de campos; 22 IDs locales únicos; sin inferir first_public_at ni fecha de cese; prueba HTTP de respuesta pública sin scores. Si API/test rechaza fuente auténtica o tolera mutaciones, detener.
