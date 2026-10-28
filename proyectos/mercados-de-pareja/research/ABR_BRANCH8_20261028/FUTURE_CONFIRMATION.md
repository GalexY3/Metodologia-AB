# N08 · Contraste externo futuro, PRERREGISTRO DE PLANIFICACIÓN, NO EJECUTADO

**Fecha de formulación:** 28/10/2026, después de leer N01–N07. **Estado:** `PLANNING_AB_ONLY`, `NOT_EXECUTED_CONFIRMATORY`, sin datos humanos, código externo ni intervención. Las observaciones que motivaron estas hipótesis no pueden contar como verificación de ellas.

## Estimando propuesto
En mercados digitales de búsqueda de pareja con consentimiento documentado, estimar la diferencia en probabilidad de aceptación recíproca dentro de un horizonte fijado, por estrato de valor inicial estimado desde atributos anteriores a la intervención, bajo exposición de la historia de rechazos a terceros frente a no exposición, manteniendo equivalentes los perfiles mostrados y presupuesto de oportunidades.

Si el acceso a datos aleatorizados resultara imposible, reformular en términos descriptivos observables y registrar la pérdida de identificación causal. No utilizar simulación de reputación como sustituto de observación.

## Rivales
- `H_DYN`: la difusión de información de rechazo tiene un efecto adicional verificable sobre reciprocidad o exclusión a exposición y preferencias comparables.
- `H_STATIC`: las correlaciones observadas están explicadas por preferencias, composición, redes y disponibilidad temporal sin efecto adicional de información reputacional.
- `H_OTHER`: confusión por visibilidad algorítmica, edad, autoselección de usuario, comportamiento no medido, definición de status, heterogeneidad de gustos.

## Endpoints y controles obligatorios antes de ejecutar
1. Especificar población elegible, consentimiento, unidad de aleatorización e interferencia de tratamientos. Tratamientos reputacionales que afecten a personas reales requieren supervisión ética y no deben producir perjuicio.
2. Registrarse en protocolo prospectivo sellado antes de acceso al outcome. Datos previos de MATE10 y BRANCH8 son exposición exploratoria.
3. Principal: cambio en tasa de reciprocidad por candidato expuesto, no solo la correlación de calidad entre quienes forman pareja. Secundarios: cobertura, daño/exclusión por estratos, tiempo, intervalos de incertidumbre y variación de preferencias.
4. Un comparador de matching estático competente, paridad de perfiles vistos, algoritmos de recomendación y duración. Baselines: permutación condicionada a oportunidades y controles de red.
5. Preespecificar intervalo de equivalencia y tamaño mínimo relevante según datos reales; no elegir umbral retrospectivamente. Debe existir un resultado nulo capaz de detener la línea.
6. Pruebas de privacidad y no puntuación individual pública, dada la naturaleza sensible de reputación y apareamiento.
7. Auditoría de código por actor distinto y reproducción limpia; registro AB-R A–J.

## Puertas pendientes
`DATA_ACCESS_BLOCKED`, `ETHICS_REVIEW_REQUIRED`, `REALISTIC_EXPOSURE_GRAPH_UNKNOWN`, `PROPER_BASELINE_NOT_YET_INFORMATION_MATCHED`, `EXTERNAL_REPLICATION_NOT_VERIFIED`. **Ninguna autorización actual incluye la ejecución de este experimento con personas.**
