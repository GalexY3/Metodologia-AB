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
