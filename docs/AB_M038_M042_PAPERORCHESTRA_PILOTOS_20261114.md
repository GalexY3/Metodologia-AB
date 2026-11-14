# AB-M038–M042 · PaperOrchestra, pilotos técnicos y pruebas pendientes

Fecha de propuesta e implementación técnica: 14 de noviembre de 2026.
Estado general: PROPUESTA / PILOTO, NO_VALIDADO. El protocolo normativo continúa siendo AB 3.2.1 con anexos vigentes. O7 y AB-META autorizan estudiar modificaciones con posibilidad de rechazo y reversión, pero no convertir software operativo en evidencia de superioridad científica.

## Antecedente y límites de atribución

Y. Song, Y. Song, T. Pfister y J. Yoon (2026), PaperOrchestra: A Multi-Agent Framework for Automated AI Research Paper Writing. Código oficial: https://github.com/google-research/paper-orchestra . El artículo estudia la transformación de materiales de investigación preexistentes en manuscritos LaTeX, mediante agentes de organización, búsqueda bibliográfica, figuras, escritura y revisión. Sus resultados de escritura no prueban por sí mismos una mejor capacidad de generar descubrimientos científicos. La adaptación de sus ideas a AB constituye una hipótesis de ingeniería, todavía sin evaluación empírica comparativa. No se incorpora código de terceros; este piloto es implementación nueva.

Fuentes AB examinadas: docs/METODO_AB_3_2_1.md, docs/AB_3_2_1_O2_OPERACIONES_REPRODUCIBLES.md, docs/AB_3_2_1_O3_BUCLES_DRIFT.md, docs/AB_3_2_1_O4_CONFIANZA_Y_NIVELES.md, docs/AB_3_2_1_O6_CAMPANAS_INFORMES_CT2_Y_CICLOS.md, docs/AB_3_2_1_O7_GRAFO_UNIVERSAL_MODOS_Y_AUTOCRITICA.md, ab_atlas/atlas_delta.py y benchmarks/AB_E2E_01/PREREGISTRO_AB_VS_BASELINE_v1.md.

## AB-M038 · Recuperación y revisión bibliográfica adversarial

Situación anterior: AB prevé un revisor de literatura y exige contrastar novedad y contraevidencia, pero no ofrece en este repositorio un pipeline automático de catálogo verificado y anotación de afirmaciones.

Intervención: ab_tools/literature.py y CLI. Se crean búsquedas por función (prior art, rivales, metodología), recuperación de metadatos OpenAlex y Semantic Scholar, normalización de DOI, deduplicación, filtro temporal por año con ambigüedad explícita en el año límite, estados de error por consulta, estado inicial UNCLASSIFIED y clasificación manual posterior P0/P1/PX/PM/PN, anotaciones con pasaje-localizador-revisor y un reporte de lagunas. Las categorías PX (contraevidencia), PM (instrumentación) y PN (novedad) son propuestas propias; no se atribuyen al esquema de Google.

Control y riesgo: encontrar un título o abstract no significa haber leído ni validado la publicación. Las categorías y anotaciones no son clasificaciones independientes verificadas. Búsqueda heurística, posible sesgo de idioma, omisión de libros, problemas de desambiguación y rate limits. No se copia la obligación de citar el 90 % de los artículos recuperados: AB debe medir pertinencia y falsación, no el volumen de citas.

Prueba pendiente: banco con publicaciones canónicas y falsas, reivindicaciones conocidas y literatura adversarial relevante. Medir recall@k de antecedentes, precisión de afirmaciones respaldadas, tasa de referencias inexistentes, falsas atribuciones y tiempo/coste, contra una revisión bibliográfica competente a recursos comparables.

## AB-M039 · Contratos ejecutables y orquestación

Situación anterior: el núcleo 3.2.1 define roles científicos y A–J; Atlas 0.3 conserva nodos y deltas, pero el conjunto no implementa un coordinador autónomo general de agentes LLM.

Intervención: ab_tools/orchestration.py. Un DAG de tareas con contratos por rol, entrega JSON, hash del payload, orden por dependencias y revisión por un identificador distinto. Se bloquean contratos vacíos, entregas sin rivales, dependencias cíclicas y autoaprobación por el mismo identificador. El módulo no invoca modelos ni crea hallazgos.

Control y riesgo: roles distintos no implican modelos ni errores independientes. La revisión registrada no garantiza que el evaluador sea fiable. Para independencia epistémica hace falta auditoría externa de modelos, fuentes y aislamiento. La validación de esquema tampoco comprueba que un estimando sea correcto.

Prueba pendiente: replicar los mismos problemas científicos usando flujo monolítico, flujo por roles y flujo por roles con auditor ciego, manteniendo modelo, herramientas, presupuesto y acceso a datos. Medir tasa de errores, omisiones y coste.

## AB-M040 · Trazabilidad afirmación–evidencia

Situación anterior: AB guarda hashes, commits y ledgers, y AB Atlas tiene relaciones tipadas, pero el repositorio no demostraba trazabilidad de cada afirmación concreta hasta los datos y cálculos que la respaldan.

Intervención: ab_tools/traceability.py y ab_tools/atlas_bridge.py. Ledger de afirmaciones, fuentes locales o externas, localizadores, sentido del vínculo, revisor, integridad SHA-256 de archivos locales, detección de contradicción y exportación a operaciones del esquema existente ab.atlas.delta.v1. Los nodos se crean como proposed/unreviewed, nunca como validated.

Antecedente complementario: data-to-paper, https://github.com/Technion-Kishony-lab/data-to-paper , plantea la trazabilidad retrospectiva desde afirmaciones a código y datos. Este piloto implementa un subconjunto documental, no trazabilidad dinámica de cada celda o resultado computado.

Control y riesgo: hash correcto significa identidad de bytes, no veracidad. Un enlace atestiguado significa que alguien lo registró, no que sea exacto. El contenido de URL no se descarga ni valida. Las rutas locales se restringen al directorio raíz declarado al auditarlas; se detectan archivos modificados. No se inserta automáticamente el lote Atlas ni se modifica historial canónico.

Prueba pendiente: inyectar errores de atribución, cifras, archivos obsoletos y omisiones de fuentes en estudios con respuesta conocida. Comparar tasa de errores encontrados y coste con revisión convencional competente.

## AB-M041 · Separación de auditoría científica y revisión editorial

Situación anterior: AB F–I exige auditoría adversarial y dictamen multidimensional, pero no un gate programático para separar versiones científicas congeladas de mejoras textuales. PaperOrchestra utiliza revisiones iterativas que aceptan mejoras de puntuación de evaluadores y conservan versiones anteriores cuando empeoran.

Intervención: ab_tools/review.py. Cinco gates científicos con estados PASS/FAIL/UNKNOWN y evidencia, auditor distinto del autor, comparación entre versiones con afirmaciones estructuradas congeladas, tokens numéricos y citas; la salida final es EDITORIAL_REVIEW_POSSIBLE, no PUBLICATION_APPROVED.

Control y riesgo: una comparación de tokens no verifica que el significado sea idéntico. Una cifra puede cambiar de sujeto sin variar su token. Los gates son atestados y requieren auditoría real. El objetivo no es maximizar una nota de LLM susceptible de Goodhart.

Prueba pendiente: versiones con alteraciones semánticas, numéricas, estadísticas y bibliográficas; medir tasa de falsas aceptaciones y falsas alarmas; incluir revisores externos ciegos.

## AB-M042 · AB-META comparativo y ablaciones

Situación anterior: AB-E2E-01 ya define un benchmark preregistrado, pero está preparado y NO EJECUTADO CON AGENTES; su infraestructura sintética no acredita eficacia.

Intervención: ab_tools/meta_eval.py. Analiza resultados aportados desde agentes o evaluadores externos, contrastando condiciones por unidad independiente, agrupando réplicas, diferencias pareadas, bootstrap percentil y aleatorización de signos, costes medios y advertencias sobre modelo, presupuesto, ids de cegamiento y n pequeño. Permite comparar varias ablaciones de modo exploratorio. No consume respuestas humanas ni ejecuta modelos.

Control y riesgo: bootstrap y p calculados no sustituyen la validez de la unidad inferencial ni la calibración del grader. El test de signos requiere intercambiabilidad bajo la nula; la comparación causal requiere asignación y aislamiento adecuados. Pese a la comparación pareada, los p de varias condiciones NO pueden usarse sin un plan de multiplicidad. Los datos sintéticos de tests no son hallazgos.

Prueba pendiente: ejecutar AB-E2E-01 con sus 60 cápsulas si están legítimamente disponibles, dos brazos aislados y evaluador ciego; posteriormente un diseño factorial/ablación de estos módulos en dominios distintos, incluido un dominio de ciencias sociales si existen tareas de referencia y permisos. Preregistrar estimando y evaluación antes de observar resultados.

## Auditoría de integración y estado

- Conservados el núcleo AB 3.2.1, O1–O7 y los priors A01–A21, sin actualización normativa.
- AB Atlas se reutiliza mediante un exportador compatible; su fuente de verdad y validador siguen intactos.
- Los módulos nuevos son locales, opcionales, sin dependencias adicionales ni credenciales embebidas.
- Las pruebas de software cubren contratos, errores de red, hashes, contradicciones, independencia de identificadores, deltas Atlas, revisión y análisis pareado. Consultar los resultados de ejecución y commit asociado, que deben verificarse por separado.
- No hay evidencia de mejoras científicas end-to-end ni resultados positivos de AB-E2E-01 a raíz de esta implementación.

Decisión preliminar AB-META: MANTENER COMO PILOTO y someterlo a comparadores competentes; REVERTIR o simplificar módulos que no aporten utilidad neta.
