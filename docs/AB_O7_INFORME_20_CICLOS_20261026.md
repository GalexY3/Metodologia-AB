# AB O7 / AB-P — campaña exploratoria de 20 ciclos instrumentales (26/10/2026)

**Decisión:** 20/20 comprobaciones focales C01–C20 PASS, **28/28 pruebas locales totales PASS**: 20 checks de ingeniería, 3 regresiones antiguas (tras adaptación de contrato), 5 smoke tests en Chromium. **No** son 20 estudios independientes, no hubo preregistro externo, ni comparación causal AB vs baseline. A–J y datos por ciclo: [LEDGER.json](../research/AB_O7_ATLAS20_20261026/LEDGER.json). Prototipo AB Atlas v0.2 disponible como archivo local descargable de esta conversación; GitHub conserva aquí la especificación y resultados, no el prototipo completo.

| Ciclo | Contraste | Observación resumida |
|:--|:--|:--|
| C01 | Scaffold para proyecto universal | Root + fases propuestas |
| C02 | Separar investigación/producto | Contrato de entrega no contaminó AB-R |
| C03 | Outcome y audiencia | Persisten explícitos |
| C04 | Alcance versionado | Dos scopes sin borrar historia |
| C05 | Falta de gates | Ready false por defecto |
| C06 | Gate sin evidencia | Rechazado |
| C07 | Exención de gate crítico | No cuenta como pasado |
| C08 | Entregable validado sin aceptación | Rechazado en modo estricto |
| C09 | Criterio, prueba y revisor | Aceptación estructural registrada |
| C10 | No mezclar métricas científicas | CT2 no se deriva de entrega |
| C11 | Ciclo de dependencias | Rechazado |
| C12 | Priorizar prerequisito bloqueante | Prioridad heurística lo antepone |
| C13 | Formato previo 1.0 | Lectura compatible |
| C14 | Scan de repositorio | Archivos unreviewed, sin conclusiones |
| C15 | Mutación inválida | Disco inalterado |
| C16 | Run + complaint con integridad | Relación consistente |
| C17 | Complaint con run inexistente | Rechazado |
| C18 | Causa sospechada vs probada | Campos separados |
| C19 | Guardar/leer JSON | Nodos y eventos conservados |
| C20 | AB revisable sin superioridad autoatribuida | No se declara mejora por cambiar reglas |

**Incidencias reales:** 3 pruebas antiguas fallaron porque el scaffold ahora añade nodos por defecto; al especificar `--no-scaffold` las 3 pasaron de nuevo. Chromium restringió la navegación file:// y localhost en este entorno; se probó HTML/JS real mediante `page.set_content`, una limitación respecto a abrir la página en cualquier dispositivo.

**Valor real de esta campaña:** los invariantes de contrato y una herramienta de seguimiento más coherente; diseño de UI sobrio sin gamificación; separación AB-P/AB-R; gates independientes del porcentaje; vinculación de quejas a ejecuciones; fuente JSON machine-readable. **No demostrado:** mejora del conocimiento fiable, del tiempo de reanudación, de los productos entregados o de la productividad frente a gestión profesional convencional. Puede persistir sesgo común porque los tests comparten implementación y fixtures. Las referencias de evidencia pueden ser falsas hasta que se auditen.

**R5:** STOP a más baterías iguales de checks sintéticos; no repetir ciclos solo por llenar cuota. Para evaluar eficacia real hacen falta nuevas evidencias: proyecto real GitHub con cambios concurrentes, validación con usuarios, auditoría de accesibilidad, escala, y **AB-P+grafo versus gestor profesional competente** con igual información, tiempo, herramientas y tareas. No subir CT2 ni adjudicar 2/3 por estos 20 ciclos. AB-O7 v0.2 sigue **PILOTO NO VALIDADO COMPARATIVAMENTE**.
