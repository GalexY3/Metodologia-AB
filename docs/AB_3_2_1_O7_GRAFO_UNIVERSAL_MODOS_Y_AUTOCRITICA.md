# AB 3.2.1-O7 — Mapa vivo, modos de proyecto y autocrítica

**Fecha:** 26-10-2026. **Estado:** anexo operativo piloto prospectivo solicitado por el investigador; eficacia comparativa NO_VALIDADA. Complementa 3.2.1/O1–O6, sin sobrescribir preregistros ni resultados históricos. La documentación integral y prototipo local AB Atlas v0.1 se elaboraron separadamente; su existencia no acredita despliegue sincronizado.

## 1. AB es explícitamente mutable y sustituible

AB es un medio para alcanzar resultados científicos y proyectos útiles, no un fin. Puede modificarse, simplificarse, revertirse e incluso reemplazarse por un procedimiento mejor. Identificar y documentar un error es una contribución a su mejora, nunca una razón para ocultarlo. Registrar las limitaciones reales y la contraevidencia. No dar por bueno un cambio solo porque lo proponga o pruebe el propio agente.

Las modificaciones profundas del método son objeto de investigación **AB-META**: hipótesis rivales, comparador competente, métrica de utilidad y coste definida antes de la evaluación, sesgos e incertidumbre, auditoría independiente cuando sea posible, decisión humana, versión prospectiva, revisión tras adopción y posibilidad de rollback. Si no hay evaluación suficiente, estado UNVALIDATED.

## 2. Grafo universal obligatorio en nuevas iniciativas, bajo piloto

Toda iniciativa bajo AB, sea investigación, desarrollo de producto o combinación, arranca con al menos un nodo raíz y un objetivo. Generar y mantener un **grafo dirigido, tipado, versionado**, representado por defecto como árbol pero con convergencia y vínculos múltiples. Cada nodo conserva ID estable, tipo, modo, estado, justificación, fuente y dependencias. Las ramas cerradas, refutadas, respondidas, sustituidas o bloqueadas permanecen navegables; no borrar evidencia contraria.

Estados mínimos: open, active, answered, validated, blocked, closed, refuted, superseded, proposed, unreviewed. Relaciones mínimas: branches_from, depends_on, tests, supports, refutes, answers, blocks, replaces, merges, related_to. La conclusión epistémica no se deduce del estado procesal: **cierre ≠ confirmación**.

**Dos proyecciones del mismo registro:** (1) una representación interactiva para usuario: navegación, búsqueda, filtros, edición, árbol, dependencias, anomalías, decisiones e historia; (2) grafo/ledger en JSON para agentes: recorrer raíz→subgrafo relevante→rivales/bloqueos→evidencias y cargar solo documentos necesarios. El HTML no es fuente de verdad y el JSON no puede inferir que un hallazgo fue validado porque encontró un archivo. Ingesta no examinada: artifact/unreviewed.

Actualizar al abrir o cerrar ramas, resolver preguntas, cambiar hipótesis, ejecutar pruebas relevantes, modificar proyectos y detectar errores. En cierres de campaña auditar preguntas huérfanas, dependencias bloqueadas, duplicados, evidencias antiguas y contradicciones. Proporcionalidad para evitar burocracia excesiva.

## 3. Modos diferentes bajo un núcleo común

**AB-R (investigación):** conservar A–J con estimando, rivales, controles competentes, preregistro cuando corresponda, exposición adaptativa, auditoría y confirmación independiente. Un experimento de simulación no valida un efecto externo.

**AB-P (proyecto):** objetivos/usuarios, alcance versionado, dependencias, especificación, implementación, aceptación, seguridad, entrega y mantenimiento. El cierre se acredita mediante criterios funcionales o de producto, no mediante grados de descubrimiento 2/3. El porcentaje de madurez es contra un scope, nunca probabilidad de éxito ni sustituto de garantías críticas.

**AB-H (híbrido):** enlazar AB-P y AB-R por transferencia de evidencias sin mezclar inferencias: un test de código no demuestra una teoría, y una inferencia científica no constituye una funcionalidad terminada. Politics Fantasy separa juego, fuentes e identidad política, predicción científica y compromisos de seguridad.

**AB-META:** AB aplicado a evaluar la utilidad, costes y fallos de AB frente a prácticas competentes.

## 4. Complaints por ejecución, con coste mínimo

Toda ejecución sustantiva crea recibo compacto `run_id`, fecha, versión AB, objetivo, resultado/estado, artefactos y costes disponibles, con `complaint_ids` posiblemente vacío. Una lista vacía significa «sin incidentes registrados», no «sin errores».

Una complaint voluntaria de humano/agente/auditor/test conserva descripción, clasificación, severidad, evidencia, causa sospechada vs verificada, propuesta y estado: open/triaged/repaired/verified/rejected. Puede referirse a errores factuales, inferencias, metodología, código, eficiencia, UX, fuentes, ética o gobernanza. No confundir denuncia con defecto demostrado. La reparación no borra el fallo; ejecución invalidada y nueva corrida quedan vinculadas.

## 5. AB aprende sin inflarse

Circuito: CAPTURAR → DEDUPLICAR → PRIORIZAR → PROPONER → COMPARAR → DECIDIR → REVISAR/REVERTIR. Reparación local reversible: REPAIR con pruebas y errata. Modificación metodológica: RFC y AB-META, con decisión humana explícita antes de alteraciones duraderas. Si un requisito consume más de lo que aporta, retirarlo. El principio R5 continúa vigente: cupos son techos, no cuotas de descubrimientos. La métrica es evidencia fiable y utilidad neta por coste total, no número de ciclos, nodos, commits o porcentajes.

## 6. Evaluación pendiente

**NO_VALIDADO:** no hay ensayo que pruebe que exigir este mapa o complaints mejora la investigación o productividad de cualquier proyecto. Un CLI/HTML local no constituye sincronización GitHub/Drive, recuperación semántica exhaustiva ni sistema multiagente de producción. Antes de extender O7 comprobar en tareas diversas tiempo de reanudación, errores no detectados, preguntas perdidas, sobrecarga, calidad de decisiones y resultados de campo; comparar también con un gestor de proyectos competente. Permitir retroceder, reducir o retirar O7 si no aporta ganancia neta.


## Revisión prospectiva 0.2 del piloto O7 (26-10-2026)

**AB-P es modo nativo y no un cambio de etiqueta de AB-R.** Su contrato mínimo diferencia destinatarios/outcome, alcance versionado, fases discover/specify/build/verify/release/operate, criterios de aceptación de entregables, dependencias, gates críticos (sin gate definido NO implica readiness), coste, operaciones y quejas por corrida. Un `waived` crítico no se equipara a `passed`. La investigación AB-R conserva grados de evidencia y sus exigencias de hipótesis rivales; AB-H enlaza evidencias sin confundirlas.

Prototipo local AB Atlas v0.2 probado con 20 comprobaciones de ingeniería C01–C20, además de 3 tests legados tras adaptación y 5 smoke tests Chromium; 28/28 PASS, **sin evaluación causal de superioridad metodológica**, y sin sincronización remota de código. Se identifica una regresión de expectativas en tres pruebas antiguas y su reparación. A–J e informe disponibles en:
- [Modo AB-P v0.2](AB_O7_ABP_V02_20261026.md)
- [Informe de los 20 contrastes](AB_O7_INFORME_20_CICLOS_20261026.md)
- [Ledger de C01–C20](../research/AB_O7_ATLAS20_20261026/LEDGER.json)

La norma continúa **PILOTO**, mutable/reversible. No inducir CT2, 2/3–3/3 o probabilidades de éxito de los 20 tests. Aplicar R5: detener nuevas comprobaciones locales repetitivas hasta probarlo con un proyecto real, usuarios y baseline competente.


## Implementación Atlas 0.3 — actualización por lotes y economía de contexto (26-10-2026)

**Nueva infraestructura versionada:** [motor de grafo](../ab_atlas/abmap.py), [aplicador de deltas](../ab_atlas/atlas_delta.py), [visor](../ab_atlas/viewer/template.html), [protocolo ChatGPT](../ab_atlas/docs/AB_ATLAS_V03_CHATGPT_SYNC.md) y [suite de pruebas](../ab_atlas/tests). El caso real de aplicación inicial es [Politics Fantasy](../proyectos/politics-fantasy-league/ab_atlas/README.md), con `seed.json` + `updates/*.json` + `CURRENT.md`. El HTML es una vista navegable regenerable, no la fuente de verdad.

Cada bloque autorizado de X ciclos AB debe producir **un lote mínimo de cambios** (altas, estados, pruebas, puertas de entrega, ejecuciones y complaints), preservando IDs e historia. Los agentes recuperan primero un resumen compacto, no la totalidad del grafo. `parent_batch` permite rechazar secuencias obsoletas; el aplicador exige integridad referencial, aceptación documentada de entregables y pruebas para gates superados. No confundir una referencia de evidencia con su autenticación, ni aplicar cambios metodológicos nuevos como mejora ya demostrada.

**Certificación limitada:** se verificaron en ejecución local 37 pruebas (20 contrastes instrumentales originales, 3 legadas, 9 pruebas de deltas y 5 interacciones de navegador). Las 20 fichas A–J originales se conservan; las nueve comprobaciones nuevas son tests de ingeniería, no nuevos ciclos científicos ni prueba de superioridad de AB. Faltan benchmarking de costes/contexto real, conflictos simultáneos multiagente, seguridad de un servicio web, auditoría de fuentes y evaluación con usuarios. No aumentar CT2 ni VSDS por haber añadido código.
