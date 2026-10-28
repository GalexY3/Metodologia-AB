# Registro obligatorio de fuentes y priors · Mercados de pareja

Norma solicitada por el investigador el 28/10/2026. **Todo descubrimiento documental** (antecedente científico, dato externo, contradictorio, limitación de acceso material, novedad y resultados de otras investigaciones) queda vinculado a una SOURCE y una PRIOR_UPDATE o una revisión sin cambio explícito.

## Dos asientos obligatorios

1. **SOURCES.json:** identificador persistente de fuente, título/autores, DOI o URL verificable, fecha de publicación y de consulta, sección/página/tipo de afirmación, población/método, qué aporta exactamente al proyecto, limitaciones, estado de acceso al documento y a los datos (DISTINTOS), derechos de reutilización de texto frente a derechos de datos. Nunca confundir un abstract o metadatos con microdatos procesados.
2. **UPDATES.json:** entrada nueva por prior afectado con id, source_ids, cycle_id, prior_id, before, direction, after, why, what_the_source_contributes, limits, falsifier_or_followup, timestamp, evidence_type y si es retrospective_backfill. Si no hay cambio justificable, usar direction=NO_CHANGE_WITH_REASON y explicar por qué.
3. **PRIORS.json:** resumen cualitativo vigente de las hipótesis rivales, fuentes a favor/en contra, incertidumbre pendiente, evidencias de identificación, siguiente discriminante. No borrar antiguas entradas de UPDATES al revisar PRIORS.

## Semántica

Un prior es la **posición cualitativa trazable de investigación antes del próximo contraste**, NO una probabilidad bayesiana calculada: emplear OPEN, CHALLENGED, STRONG_PRIOR_ART, SUPPORTED_DESCRIPTIVELY, DATA_BLOCKED, NOT_IDENTIFIED u otra etiqueta definida con explicación. No inventar probabilidades numéricas. Una CT2 es una puntuación ordinal de perspectivas de novedad 2/3, no la probabilidad de la hipótesis ni una puntuación de verdad.

Separar: preferencias sin homofilia explícita; filtrado por falta de reciprocidad; pérdida de prestigio público tras rechazo; popularidad recibida durante el mismo período; popularidad medida **antes** de mostrar perfiles; intentos frente a reciprocidad, pareja estable, convivencia o matrimonio.

## Flujo obligatorio para futuros ciclos AB documentales

A. Leer SOURCES/PRIORS/UPDATES y verificar si DOI u otro identificador ya está registrado; evitar falsa independencia por citar el mismo estudio dos veces.
B. Al concluir investigación A–J, guardar o actualizar SOURCE con acceso real y límites y registrar UPDATE o NO_CHANGE_WITH_REASON para cada prior relevante.
C. Vincular source_ids, prior_ids y prior_update_ids en ledger A–J. Mantener las entradas anteriores: append-only lógico, revisiones mediante nuevo evento SUPERSEDES y commits versionados. Registrar quién verificó qué, con prueba y fecha.
D. En CURRENT.md enlazar los priors cambiados y no elevar niveles o CT2 por el mero volumen documental. No copiar artículos enteros ni datasets cuando copyright/licencia es incierto.
E. Cuando las fuentes se hayan localizado en campañas anteriores, crear un **backfill retrospectivo** y marcar before=NOT_RECORDED cuando el estado anterior no se registró entonces. No fingir que existía un prerregistro previo.
F. R5: la actualización documental de mantenimiento **no es un nuevo ciclo** por sí sola. Solo contabilizar ciclos AB A–J efectivamente ejecutados.

## Estructura persistente

- SOURCES.json — referencia original, evidencia y aportación concreta, estado de derechos y acceso.
- PRIORS.json — hipótesis, juicios cualitativos actuales y pruebas pendientes.
- UPDATES.json — historial de actualizaciones con evidencia enlazada por source_ids y cycle_id.
- SOURCE_TEMPLATE.json — contrato reutilizable para futuras adiciones.

La documentación de cada campaña conserva el informe y el ledger propios. El registro global enlaza estos expedientes. El backfill inicial recoge lo rastreable en expedientes previos; **no constituye una revisión bibliográfica exhaustiva**.
