# Herramientas experimentales AB · M038–M042

**Estado: PILOTO TÉCNICO / NO VALIDADO CIENTÍFICAMENTE.** Estos módulos son extensiones optativas y reversibles a AB 3.2.1/O7. No constituyen AB 3.3 ni modifican retrospectivamente campañas, CT2, niveles 0–3, priors o criterios de publicación. Sus pruebas de software no son pruebas de eficacia científica.

Referencia de diseño: [Google Research, PaperOrchestra](https://github.com/google-research/paper-orchestra), Yiwen Song et al. (2026). No se ha copiado código del proyecto. Se tomaron como antecedentes la búsqueda bibliográfica dirigida, los roles con salidas estructuradas, el refinamiento con reversión y los benchmarks con evaluadores humanos. Se rechazaron como objetivos la cita obligatoria de un porcentaje de referencias y la optimización exclusiva de puntuaciones de revisores.

## Qué puede ejecutarse ya

| Código | Función | Instrumentación real | Límite |
|---|---|---|---|
| M038 | literature.py | Búsquedas planificadas, OpenAlex / Semantic Scholar, deduplicación, registro de tareas, clasificación y citas evaluadas | Metadatos sin verificación de contenido, sin garantía de cobertura |
| M039 | orchestration.py | Roles tipados, DAG, selección de tareas listas, entregas y revisión por identificador separado | No invoca LLM ni garantiza independencia epistémica |
| M040 | traceability.py + atlas_bridge.py | Ledger afirmación-evidencia, SHA de ficheros locales, contradicciones, exportación candidata a Atlas delta | Una relación atestiguada no demuestra verdad |
| M041 | review.py | Puerta científica independiente de edición, chequeo de campos congelados, números y citas, decisión conservadora | No puede demostrar equivalencia semántica del texto |
| M042 | meta_eval.py | Comparación pareada por caso, bootstrap, signos, coste y advertencias de paridad | No ejecuta agentes ni valida por sí solo el grader |

Todos los módulos utilizan la biblioteca estándar de Python 3.10+; no requieren instalar dependencias para las pruebas.

## Prueba en un clon limpio

En la raíz del repositorio:

    python -m compileall -q ab_tools
    python -m unittest discover -s tests -p test_ab_tools.py -v
    python -m unittest discover -s ab_atlas/tests -p test_*.py -v
    python -m ab_tools --help

Para obtener un plan bibliográfico que explícitamente busque contraevidencia:

    python -m ab_tools literature-plan --question "emergencia de cooperación entre agentes" --rival "agrupación aleatoria" --out plan_literatura.json

El parámetro opcional --cutoff-year 2024 excluye registros posteriores a 2024; los publicados dentro de 2024 quedan etiquetados como SAME_YEAR_ORDER_UNVERIFIED porque el año por sí solo no establece el orden cronológico. Los registros recuperados empiezan como UNCLASSIFIED, y no como referencias pertinentes automáticamente.

La recuperación online es opcional y requiere conexión real a las API públicas:

    python -m ab_tools literature-search --plan plan_literatura.json --provider openalex --out catalogo.json
    python -m ab_tools literature-coverage --plan catalogo.json

Semantic Scholar se puede añadir con --provider semanticscholar. Si existe SEMANTIC_SCHOLAR_API_KEY, se envía a esa API únicamente como cabecera; jamás se almacena en el ledger. Los fallos de red o cuota se conservan como errores y el resultado pasa a PARTIAL. La búsqueda NO lee necesariamente los artículos completos y nunca atribuye apoyo a una hipótesis por metadatos.

Las evaluaciones sustantivas de un artículo son manuales o hechas por un agente sujeto a auditoría. Ejemplo de registrar una contradicción:

    python -m ab_tools literature-assess --plan catalogo.json --ref-id doi:10.ejemplo/uno --claim H1 --relationship contradicts --passage "Texto comprobado" --locator "página 4" --reviewer auditor-1 --role PX --out catalogo_anotado.json

El identificador debe ser uno que exista efectivamente en el catálogo. Registrar el pasaje NO equivale a verificar su exactitud ni autoriza elevar CT2.

## Contratos y grafo

El archivo de ejemplo de tareas se encuentra en examples/ab_tools_demo/tasks.json. No contiene agentes en ejecución. Define las responsabilidades y dependencias que debe satisfacer cualquier ejecutor externo.

    python -m ab_tools workflow-init --tasks examples/ab_tools_demo/tasks.json --out flujo.json
    python -m ab_tools workflow-ready --file flujo.json

Al entregar un artefacto, hay que proporcionar JSON con los campos obligatorios del rol. La tarea queda en estado submitted; una revisión por otro identificador puede aprobar o rechazarla. Esta revisión constata el contrato, no la independencia estadística o la verdad científica.

Un ledger nuevo se genera así:

    python -m ab_tools claims-init --out claims.json
    python -m ab_tools claims-add --file claims.json --id H1 --text "Afirmación condicionada" --out claims.json
    python -m ab_tools evidence-file --file claims.json --id E1 --path resultados/ensayo.json --root . --out claims.json
    python -m ab_tools claims-link --file claims.json --claim H1 --evidence E1 --relationship supports --locator "resultado.primary" --reviewer auditor-1 --out claims.json
    python -m ab_tools claims-audit --file claims.json --root .

Los SHA registran integridad local, no contenido verdadero. Las fuentes externas se añaden con evidence-url y mantienen estado EXTERNAL_CONTENT_NOT_FETCHED. Las relaciones support/refute requieren localizador y revisor identificados.

Para exportar nodos **propuestos y sin validar** al Atlas ya existente:

    python -m ab_tools atlas-export --claims claims.json --batch AB-LIT-0001 --parent-batch "" --parent-node root --out atlas_batch.json

La salida es un lote CANDIDATO en el esquema ab.atlas.delta.v1. Antes de aplicarlo hay que situarlo en un directorio de deltas del proyecto y utilizar el validador existente ab_atlas/atlas_delta.py check con su baseline real y cadena parent_batch vigente. No se ha alterado automáticamente ningún mapa existente.

## Revisión editorial y benchmark

Un informe de revisión científica aporta cinco checks con estado PASS, FAIL o UNKNOWN y una referencia de evidencia para cada PASS. Los checks obligatorios son source_integrity, design_fidelity, statistical_reproduction, citation_support y leakage_and_selection. La firma del auditor es una declaración atribuida, no una certificación independiente.

    python -m ab_tools review-compare --before borrador_v1.json --after borrador_v2.json --scientific-audit auditoria.json --reviewer editor-1 --out dictamen.json

La edición solo pasa a EDITORIAL_REVIEW_POSSIBLE si el gate científico es PASS atestiguado, las afirmaciones congeladas son idénticas y no cambian los tokens numéricos o de citas. Esa salida requiere todavía inspección humana o revisión externa semántica.

Para evaluar condiciones experimentales con datos de una ejecución real:

    python -m ab_tools meta-compare --rows evaluaciones.json --baseline baseline --candidate ab --out comparacion.json
    python -m ab_tools meta-ablations --rows evaluaciones.json --baseline baseline --out ablaciones.json

Cada fila de evaluaciones.json necesita case_id, arm, replicate, score en [0,1], cost_seconds, status, blind_id, model_version y budget_id. Un fallo o timeout recibe score=0. El estimando es la diferencia media de puntuación por caso independiente, agregando las réplicas de cada brazo. Un mismo caso o cuaderno NO debe contarse tantas veces como semillas. El análisis advierte sobre diferencias de modelo y presupuesto y sobre muestras pequeñas. Para afirmaciones confirmatorias se necesitan controles de aleatorización, grader ciego calibrado, preregistro, holdout y corrección por selección/multiplicidad pertinentes.

## Integración y siguiente paso científico

La fuente de verdad de la investigación sigue siendo el repositorio y ledger canónico de cada proyecto. Los módulos anteriores generan artefactos portables; cualquier intervención en AB 3.2.1 requiere evaluación separada bajo AB-META y autorización explícita conforme a O7. El preregistro AB-E2E-01 permanece sin ejecutar con agentes reales: estos tests no lo sustituyen.

Plan de validación propuesto: pruebas sintéticas de detección de fallos, tareas reales comparadas con un procedimiento competente, ablaciones por módulo, evaluación humana ciega y reporte de coste total. El registro detallado se conserva en docs/AB_M038_M042_PAPERORCHESTRA_PILOTOS_20261114.md.
