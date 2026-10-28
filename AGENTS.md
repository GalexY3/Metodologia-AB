# Instrucciones portables para agentes de investigación AB

Este repositorio es la autoridad metodológica del protocolo AB del investigador. Antes de crear o revisar campañas, leer **en este orden**:
1. [README](README.md)
2. [AB 3.2.1, base](docs/METODO_AB_3_2_1.md)
3. [O3, DRIFT/BRANCHING](docs/AB_3_2_1_O3_BUCLES_DRIFT.md)
4. [O4, CT2 1–100 y hallazgos 0–3](docs/AB_3_2_1_O4_CONFIANZA_Y_NIVELES.md)
5. [O5, escala DRIFT D0–D5](docs/AB_3_2_1_O5_DISTANCIA_DRIFT.md)
6. **[O6, campañas, gráficos CT2 y solicitudes de 20–45 ciclos](docs/AB_3_2_1_O6_CAMPANAS_INFORMES_CT2_Y_CICLOS.md)**.

## Contrato de experiencia con el usuario

- Los experimentos y planificaciones autorizados son **ciclos AB completos A–J**. Ejecutar solo lo efectivamente instrumentado; registrar incompletos, invalidaciones, auditorías post hoc y negativos.
- Mantener CT2 1–100 por **rama concreta**; nunca hacerla subir por obligación. **Mostrar gráfico CT2** de escala 0–100 y vista ampliada al cerrar informes, con puntos respaldados por ledger.
- En cada DRIFT asignar distancia **D0–D5** justificada; ciclos especiales D3–D5 se etiquetan `PLANNING_AB_ONLY`.
- Conservar cada 1/3 **único** en ledger persistente del proyecto, con evidencia, límites, falsador, parentescos y posibles combinaciones; no duplicar por semillas o fuentes. No conceder 2/3 sin contribución novedosa, control fuerte y replicación independiente.
- En el **último párrafo** de cada informe final de campaña, solicitar **20–45** nuevos ciclos AB con propósito, cantidad y modo; líneas terminales como `SOLICITO BRANCHING 30 CICLOS` o `SOLICITO PIVOT 20 CICLOS`. **No** solicitar de nuevo ciclos ya autorizados y todavía pendientes de ejecutar.
- Registrar contratos, hash, prereg antes de ejecutar y guardar JSON por semilla, ledger A–J, prior ledger, auditoría y estado verdadero GitHub.
- La investigación científica es prioritaria al formato: nunca inventar resultados para cubrir cuotas ni afirmar CT2/2/3 favorables sin evidencia.

La metodología **no garantiza** que un modelo de ChatGPT tenga acceso automático al repositorio, los archivos ni las herramientas. Requerir conexión o material aportado por el usuario cuando falte acceso.

**Procedencia y detalle completo:** [O6](docs/AB_3_2_1_O6_CAMPANAS_INFORMES_CT2_Y_CICLOS.md). Su adopción normaliza informes y colaboración, **no demuestra** la eficacia científica de AB.

## Regla de cierre interactivo AB (decisión del investigador, 28/10/2026)

**En todas las respuestas de cierre o continuidad de proyectos AB, incluir al final un botón funcional** (o la acción equivalente ofrecida por la interfaz) con una petición ya redactada para el siguiente turno; no limitarse a escribir `SOLICITO ...` como texto inerte.
- **Si hay ciclos autorizados pendientes:** botón «Continuar con X ciclos ya autorizados», con proyecto, rama, número de plazas, R5, observaciones, controles y condición explícita de no gastar plazas sin evidencia; **no pedir autorización duplicada**. Una pulsación reabre la conversación, no demuestra que se haya ejecutado trabajo ni lo realiza en segundo plano.
- **Si el saldo es cero:** botón «Autorizar [20–45] ciclos AB» con cantidad, modo, objetivo y requisitos A–J redactados. La nueva autorización existe **solo si el usuario pulsa y confirma el mensaje**; una sugerencia no concede créditos.
- **Si AB-DECIDE está en STOP_R5 y quedan plazas:** el botón de continuación reevalúa acceso a evidencia y posibles pruebas discriminantes; sin nueva clase de evidencia, conserva STOP y saldo.
- Conservar siempre el cierre escrito y el resumen de evidencia y límites incluso cuando la interfaz muestre el control. Si el cliente no admite botones, ofrecer un enlace de continuación propio de la plataforma o un mensaje exacto para copiar.
- Esta regla es de experiencia de usuario, **no una modificación de R1–R5 ni evidencia de eficacia científica**. No contabilizar la corrección documental como ciclo AB.

## Norma transversal: descubrimientos documentales, fuentes y priors (28/10/2026)

- **Obligatorio en todos los proyectos AB:** cada hallazgo documental nuevo, antecedente relevante, resultado de otra investigación, limitación de fuente o contradicción verificable debe tener **registro de la fuente original y de lo que aporta**, y **actualización explícita de al menos un prior**, o un evento `NO_CHANGE_WITH_REASON` justificado cuando no corresponda cambiarlo.
- Guardar bajo cada proyecto un **registro versionado de SOURCES, PRIORS y UPDATES**, con IDs estables y referencias cruzadas, enlazado desde los ledgers A–J. La fuente incluye DOI/URL, sección/página o dato exacto, procedencia, fecha y tipo de acceso (artículo, resumen, catálogo, microdatos efectivamente leídos), derechos/licencia de texto y datos separadas, contribución a hipótesis, limitaciones y falsador.
- `UPDATES` es append-only lógico, nunca se borra un resultado desfavorable; la retractación se registra como nueva corrección. Evitar tratar como independientes dos publicaciones que reutilicen una misma muestra.
- **No inventar priors numéricos bayesianos:** si no hay distribución y likelihood definidos, usar actualización cualitativa. CT2 (trayectoria ordinal 2/3) no es probabilidad ni sustituye el prior de la hipótesis.
- Al recuperar hallazgos documentales antiguos, etiquetar `retrospective_backfill` y `before=NOT_RECORDED_AT_TIME` donde proceda, sin fingir prerregistro. Añadir el registro retrospectivamente **no consume un nuevo ciclo AB**.
- Implementación de referencia y plantilla ya creada: [Mercados de pareja · SOURCES / PRIORS / UPDATES](proyectos/mercados-de-pareja/research/PRIORS/README.md) y [SOURCE_TEMPLATE.json](proyectos/mercados-de-pareja/research/PRIORS/SOURCE_TEMPLATE.json). Para otras líneas, inicializar un registro equivalente en el directorio del proyecto cuando aparezca su siguiente hallazgo documental.
