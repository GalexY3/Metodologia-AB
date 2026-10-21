# AB 3.2.1-O1 — Anexo operativo de gobernanza GitHub + Drive

**Fecha:** 21-10-2026. **Naturaleza:** regla de organización y auditabilidad adoptada por decisión del investigador; **no** una eficacia causal demostrada de AB. No altera el núcleo epistémico de AB 3.2.1 ni supone una versión 3.3.

## Principio A16: fuente de verdad, documentación y procedencia

1. **GitHub = fuente primaria versionada de investigación.** Cada proyecto tiene su repositorio independiente. Allí se guardan código, instrucciones de ejecución, prerregistros, hipótesis rivales, ledgers de priors, ciclos, resultados legibles por máquina, erratas y decisiones AB-DECIDE. Un commit documenta qué se sabía y qué se modificó; por sí solo no acredita validez científica.
2. **Google Drive = archivo documental complementario.** Informes extensos, revisiones, presentaciones, datos voluminosos con derechos de conservación y material gráfico. Todo informe final incluye URL del repositorio, commit o tag exacto, identificador de ciclo, fuentes y límites de reproducibilidad. Si el informe de Drive contradice el registro GitHub, no se corrige en silencio: se abre una errata y se reconcilian versiones.
3. **Separación epistemológica:** `GalexY3/Metodologia-AB` contiene priors *metodológicos* A; `GalexY3/goodhart-research` contiene priors *sustantivos* G. LARP y otras investigaciones conservan sus propios ledgers; un hallazgo en Goodhart o LARP no es una validación automática de AB.
4. **Commit con valor informativo:** tras cambios relevantes en protocolo, prior, diseño, resultado o decisión, registrar commit con mensaje descriptivo y referencia a evidencia. No hacer commits decorativos por cumplir cuotas. En investigaciones extensas pueden agruparse resultados coherentes en un commit trazable. Mantener historia de reparaciones, no sobrescribir para aparentar prerregistro perfecto.
5. **Priors acumulativos:** nunca eliminar silenciosamente un prior. Preservar ID, procedencia, fecha, ámbito, estado, incertidumbre, evidencia favorable/contraria, falsador y motivo de revisión. Marcar `NORMATIVO`, `MATEMÁTICO`, `SINTÉTICO`, `EMPÍRICO_OBSERVACIONAL`, `CAUSAL_IDENTIFICADO` o `NO_VALIDADO`, sin convertir etiquetas en credenciales científicas.
6. **Privacidad y publicación:** repositorios privados permanecen privados hasta decisión humana de publicación. Antes de hacer público un repo, revisar secretos, datos personales, derechos de datasets, autorías, afirmaciones y reproducibilidad. No copiar información confidencial a repositorios públicos. El repositorio `avian-patterns-lab` es público y solo debe usarse para material compatible con su alcance y visibilidad.
7. **Acceso y permisos:** verificar las capacidades reales de conectores en cada sesión. No inferir que acceso de lectura equivale a escritura; comprobar un commit con lectura posterior. No prometer ejecución autónoma entre chats o en segundo plano sin una automatización explícita.
8. **Metadatos mínimos de cada ciclo:** ID, fecha, proyecto, pregunta, estimando, rivales, predicción discriminante, prereg hash/commit, fuente y licencia, seeds, versión de código, auditoría, hallazgo negativo, resultado, incertidumbre, status del holdout, decisión y enlace al informe documental.

## Procedimiento de cierre

- Crear/actualizar código y pruebas en GitHub, ejecutar y auditar, registrar ledger y commit.
- Generar informe extenso en Drive; incluir referencias a commits verificables, datos, métodos, incertidumbre y hallazgos negativos.
- Añadir en GitHub un índice con el enlace a Drive. El índice es un puntero, no una segunda fuente de verdad para números experimentales.
- Al descubrir un error: errata visible + nuevo commit + versión corregida del informe, sin borrar la historia.

## Relación con el método

A16 mejora la **capacidad de auditoría y transferencia entre conversaciones** por diseño, pero el contraste de que esta organización mejore descubrimiento, replicación o coste frente a una alternativa competente sigue **pendiente**. No usar la ausencia de errores de hash como evidencia de veracidad del contenido.
