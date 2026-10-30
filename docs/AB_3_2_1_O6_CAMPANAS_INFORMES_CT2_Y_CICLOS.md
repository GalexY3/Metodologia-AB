# AB 3.2.1-O6 — Protocolo portable de campañas, informes y autorización de ciclos

> **Excepción prospectiva de PFL · solicitud del investigador 30/10/2026:** [política de progreso y continuidad](https://github.com/GalexY3/politics-fantasy-league/blob/main/docs/WORKING_AGREEMENT.md). Para Politics Fantasy se sustituye la petición obligatoria al cierre por una decisión motivada hacia un hito de producto o evidencia discriminante. No pedir más ciclos por fórmula, no convertir QA/traspasos en ciclos, preservar los cinco ABH10 y dos históricos pendientes y aplicar R5. Esta excepción prevalece en PFL sobre las cláusulas de solicitud normal y último párrafo de este documento. No modifica otros proyectos ni demuestra eficacia metodológica; el resto del texto conserva las directivas y su historia.

**Fecha:** 24 de octubre de 2026. **Estado:** norma operativa de presentación y gobernanza adoptada por solicitud del investigador. **No** declara una mejora de eficacia científica de AB; sigue siendo metodología provisional. Complementa AB 3.2.1 y los anexos O1–O5 sin sustituir R1–R5 ni A–J.

## Directiva posterior del investigador — 29 de octubre de 2026

Para nuevas solicitudes de ciclos AB, el intervalo vigente pasa de 5–15 a **5–30 ciclos por petición**, siempre con autorización expresa del usuario y sin obligación de agotar cuotas bajo R5. Se autorizó específicamente en PFL un bloque de **20 ciclos libres de investigación/desarrollo + 10 ciclos de investigación de autonomía técnica frente a Codex**, conservando separadas las 2 plazas residuales antiguas. La orden posterior del usuario pide ejecutar el bloque completo sin consultas intermedias: si un ciclo falla, registrar INVALID/INCOMPLETE y buscar una nueva vía antes de terminar; no inventar ejecuciones ni eludir R5. **Esta actualización prevalece sobre los límites de 28/10 de 5–15 recogidos abajo, conservados como historia.** ChatRelay sigue en pausa.

## Nota histórica del investigador — 28 de octubre de 2026

La directiva anterior de solicitudes de 20–45 ciclos queda **sustituida** para futuros bloques por **5–15 ciclos**, sin límite acumulado implícito de bloques y siempre con autorización independiente. **ChatRelay se suspende por defecto**: no asignarle ciclos ni ejecutar intermediaciones automáticas; solo reconsiderarlo ante evidencia excepcional y nueva decisión expresa. El saldo histórico de ChatRelay no migra a campañas nuevas. Esta instrucción es de gobernanza, no prueba empírica de mayor rendimiento de otros canales.

## 0. Para otra instancia de ChatGPT: cómo comenzar

1. Leer, por este orden, el [README principal](../README.md), [AB 3.2.1](METODO_AB_3_2_1.md), [O3](AB_3_2_1_O3_BUCLES_DRIFT.md), [O4](AB_3_2_1_O4_CONFIANZA_Y_NIVELES.md), [O5](AB_3_2_1_O5_DISTANCIA_DRIFT.md) y **este O6**. Si se opera con asistentes de programación, leer también [AGENTS.md](../AGENTS.md).
2. Localizar en el repositorio del proyecto concreto su contrato de campaña, últimos resultados verificados, rama/PR y ledger de hallazgos; **no** deducir archivos o puntuaciones a partir de memorias o respuestas previas sin comprobar procedencia.
3. Si el usuario autoriza nuevos ciclos, preservar total autorizado, condiciones de DRIFT/BRANCHING/PIVOT, número de ciclos de planificación, fuente de evidencia y saldo disponible. Una autorización **no** equivale a ejecución, ni a permiso para declarar un descubrimiento.
4. Al terminar un informe de campaña, respetar la presentación y la petición de siguiente autorización descritas abajo. **La solicitud no es ejecución automática**.

## 1. Gramática de ciclos y autorizaciones

- Un ciclo AB sustantivo = contrato completo **A–J** (pregunta, hipótesis rivales, diseño discriminante, instrumentación, ejecución o verificación documental legítima, auditoría adversarial, contrastes independientes cuando existan, actualización de priors, dictamen y decisión).
- Distinguir `EXPERIMENTAL_AB`, `PLANNING_AB_ONLY`, `INVALID`, `NOT_EXECUTED` y `POST_HOC_AUDIT`. Un plan o auditoría añadida no es un experimento ejecutado. Una repetición por reparación conserva ambas versiones, no multiplica el número de ciclos válidos.
- **Solicitud normal al cierre de cada informe final de campaña (directiva vigente desde el 29/10/2026):** solicitar entre **5 y 30 ciclos** adicionales inclusive (un entero), eligiendo cantidad y tipo por el cuello de botella de evidencia. Ejemplos: `SOLICITO BRANCHING 5 CICLOS` o `SOLICITO PIVOT 10 CICLOS`. Las nuevas solicitudes fuera del intervalo 5–30 no están autorizadas por defecto. Se permite encadenar bloques posteriores previa autorización separada; esta regla no modifica presupuestos históricos.
- **No volver a solicitar autorización ya concedida durante la ejecución de la campaña**; si el investigador autorizó un bloque condicional (p. ej. 20 + 5 planificación + 30), consumir primero esa autorización sin confundir fases.
- La aceptación del usuario se aplica solo al bloque pedido/concedido; no presuponer nuevos bloques ilimitados.
- La regla metodológica R5 permite `STOP` cuando no hay evidencia nueva; si el investigador **ordena expresamente cumplir un mínimo o prohíbe STOP para un bloque particular**, dentro de ese bloque optar por DRIFT/BRANCH/PIVOT, pero no inventar ejecución, resultados ni grado científico para cubrirlo. Explicar si los instrumentos impiden honestamente ejecutar los ciclos.
- Si el usuario dispone una fase de `PLANNING_AB_ONLY`, cumplir A–J documental por ciclo y etiquetarla; no fingir datos empíricos.

## 2. Escala de confianza CT2, 1–100 (O4)

CT2 pregunta: «¿Cuánta confianza fundada existe en que **seguir esta línea científica identificada** permita llegar a **2/3**?». **No es una probabilidad calibrada**.

En inicio y después de **cada ciclo/decisión** conservar:
`cycle_id, timestamp, branch_id, CT2_before, CT2_after, rationale, evidence_for, evidence_against, strongest_baseline, evidence_bottleneck, grade_0_3, selection_exposure`.

Exigir justificación para cada subida/bajada; NO subir CT2 por número de ciclos, semillas, pivotes, créditos, test débil, supuestos impuestos o simple optimismo. Se permite subir provisionalmente si aparece un mecanismo discriminante con nuevo experimento verificable; debe bajar si el control adversarial derrota la propuesta.

**CT2 por rama, jamás un solo marcador sin identidad.** Tras PIVOT/DRIFT D3–D5, cerrar trayectoria anterior y comenzar la nueva CT2 con estimando y horizonte nuevo. Los saltos entre ramas no son aumentos en probabilidad de la hipótesis antigua.

## 3. DRIFT D0–D5 (O5)

Anotar **D0,0 a D5,0**, admitiendo decimales justificados, con los anclajes normativos de O5. Mínimo:
`parent_branch, new_branch, D_score, mechanism_changed, population_changed, estimand_changed, data_source_changed, what_is_inherited, prior_art_gate, decision`.
D0 = mismo tema; D5 = campo sustantivo prácticamente diferente. El valor D no mide novedad ni éxito.

Cuando se autorizan ciclos especiales D3–D5, escribir su análisis extenso A–J y dejar el estado `PLANNING_AB_ONLY` (no experimental), salvo que el usuario autorice explícitamente pruebas reales separadas.

## 4. Hallazgos 0–3 y ledger permanente

Seguir O4: 0/3 insuficiente o inválido; 1/3 aporte exploratorio local y reproducible; 2/3 novedad discriminante respaldada por controles fuertes, literatura y **confirmación externa independiente**; 3/3 alcance mayor aún. La decisión de 2/3 **no se deduce** de CT2 alta ni de múltiples 1/3 sumados.

Mantener `N1_campaign`, `N1_portfolio_audited`, `N2`, `N3`, `historical_unreviewed` separados. **Contar una idea una sola vez**, no por conjunto de datos, semilla, condición o bloque. Conservar también resultados refutados y candidatos rechazados.

En LARP, el ledger canónico es [proyecto-LARP/research/FINDINGS_1_3/LEDGER.json](https://github.com/GalexY3/proyecto-LARP/blob/main/research/FINDINGS_1_3/LEDGER.json). En otros proyectos, crear otro ledger trazable con el mismo esquema; el repositorio metodológico AB define reglas, no absorbe automáticamente todos los resultados sustantivos.

Por hallazgo guardar: `id, grade, novelty_status, exact_claim, reproducibility_status, source_commit_or_archive, experimental_support, prior_art, falsifier, adverse_evidence, limits, external_replication, duplicate_of, relates_to, potential_combinations, updated_at`. En un DRIFT lejano, conservar referencias y límites de los hallazgos previos; no transferir su validez causal a otro campo.

## 5. Qué debe incluir cada **informe final** de campaña

**A. Marcadores al inicio:** ciclos autorizados/ejecutados/válidos/inválidos/planning, línea actual y D, CT2 inicial/final, N1 nuevos/no duplicados, N1 acumulados auditados, N2/N3; *no inventar 2/3*.

**B. Narrativa de evidencia:** pregunta, datos y naturaleza (reales observados, sintéticos, retrospectivos, prospectivos), metodología, competidores fuertes, resultados cuantitativos, refutaciones, efectos condicionados al generador, decisiones DRIFT/BRANCH/PIVOT con motivos. Separar exámenes E/G internos de **replicación externa**. Indicar reparaciones y prereg previo si los hubo.

**C. Gráfica CT2 obligatoria** en cada informe final (si hay al menos dos puntos): una visualización por código, preferentemente Python/Matplotlib o vector programático, nunca una imagen inventada para aparentar datos. Ofrecer:
1. **Serie completa 1–100** (eje 0–100).
2. **Vista ampliada** para movimientos pequeños, claramente rotulada como escala ampliada.
3. Eje temporal/ciclo verídico, rupturas y reinicios CT2 cuando cambia la línea D3–D5; distinguir con líneas o notas el estado antes/después de la auditoría `POST_HOC`. Mostrar solo puntos de CT2 registrados, no puntos interpolados interpretados como medidas reales. Explicar que CT2 **no es probabilidad**.
4. Adjuntar si es factible `CT2_TRAJECTORY.csv/json` para que otra instancia regenere el gráfico.

**D. Evidencia inspeccionable:** enlazar código, dataset/procedencia, hash de fuente, prereg commits, ledger A–J, JSON por semilla, resumen, auditoría de validez, priors acumulativos, ZIP y estado de PR/merge. **Solo enlaces realmente verificados**; no afirmar reproducibilidad en clon limpio ni archivo remoto si no se ejecutó/verificó.

**E. Diagnóstico explícito del umbral 2/3:** qué es nuevo, antecedente más próximo, predicción discriminante, control competente, evidencia externa necesaria, bloqueos y CT2 razonada. Decir “NO ACREDITADO” si faltan pruebas.

**F. Último párrafo — siguiente autorización:** recomendar una dirección y **pedir 5–30 ciclos AB** con tipo `CONTINUE`, `PIVOT`, `BRANCHING` o `DRIFT`, cantidad motivada y frase terminal inequívoca. No asumir aprobación ni programar trabajo futuro sin acción explícita del usuario. Excepción: si se está reportando una *fase intermedia* y ya existe autorización de fases posteriores, indicar saldo concedido y no volver a pedir.

## 6. Contratos de datos mínimos para portabilidad

```json
{
  "campaign_id": "AB_CAMPAIGN_ID",
  "authorized": [{"kind": "EXPERIMENTAL_AB", "count": 20}, {"kind": "PLANNING_AB_ONLY", "count": 5}],
  "executed_valid": 0,
  "executed_invalid": 0,
  "source_repo_branch": "owner/repo:research/branch",
  "cycles": [{"id":"C01", "type":"EXPERIMENTAL_AB", "AB_A_J_file": "...", "pre_commit": "...", "result_commit": "...", "status":"NOT_EXECUTED", "D":0.0, "CT2_before":10, "CT2_after":10, "grade_0_3":0}],
  "ct2_trajectories": [{"branch_id":"B0", "points":[{"cycle_id":"BEGIN","ct2":10,"reason":"baseline"}]}],
  "N1_new": [], "N1_ledger_url": "...",
  "N2": 0, "N3": 0,
  "external_replication_status": "NOT_VERIFIED",
  "preregs_and_repair_log": [],
  "remaining_authorized": 25
}
```

Este esquema es una plantilla, no resultados. Guardar `campaign.json` y `CT2_TRAJECTORY.json` versionados para retomar entre chats. Cuando no haya acceso a un repositorio o archivos, reconocer el límite y pedir acceso; no reconstruir estados privados a partir de cifras recordadas.

## 7. Reglas de honestidad y evaluación de O6

O6 **estandariza una experiencia de colaboración**, no una teoría del descubrimiento ni una promesa de que llegar a 2/3 sea inevitable. Nunca optimizar la curva CT2 como objetivo; que caiga es perfectamente legítimo. Nunca atribuir a otros GPT acceso automático garantizado a memorias/herramientas/repositorios: para reproducir esta dinámica, deben poder **leer estas instrucciones y los artefactos del proyecto**.

El cumplimiento de este protocolo de presentación no eleva la validez científica de un resultado ni modifica los requisitos de confirmación independiente de O3/O4.
