# AB-E2E-01 — Prerregistro del contraste AB frente a investigación competente

**Fecha de congelación:** 2026-10-21. **Estado:** DISEÑADO, NO EJECUTADO CON AGENTES. **Versión:** 1.0. **Método bajo prueba:** AB 3.2.1 + anexo operativo de gobernanza O1. **Unidad de inferencia:** cápsula/estudio independiente, no pregunta individual ni réplica del mismo estudio.

## 1. Pregunta y límites

¿La aplicación explícita de AB aumenta la exactitud de conclusiones científicas sobre datos reales frente a un procedimiento de investigación convencional competente, con el mismo modelo, acceso, tiempo, cómputo y presupuesto de tokens? El estimando primario es la **diferencia media de puntuación oficial entre AB y baseline** para una tarea seleccionada determinísticamente por cápsula de BixBench, agregando dos ejecuciones por brazo y cápsula. Se estudia un **efecto de instrucciones/procedimiento sobre un agente de IA** en ese benchmark; NO la validez de AB como teoría epistemológica general, ni efectos causales sobre científicos humanos.

Hipótesis nula: Δ=0. Alternativa bilateral: Δ≠0; dirección de interés Δ>0. Un resultado negativo también debe publicarse.

## 2. Fuente externa y población

**Primaria:** BixBench, repositorio público `Future-House/BixBench` (código consultado en revisión `49311180bdacb324c596f2e07596c126f2004008`), que describe 205 preguntas de 60 cápsulas/cuadernos publicados. La revisión del código **no fija por sí sola la revisión del dataset**; al obtener los datos se registrarán revisión y hashes, antes de las trayectorias. Se elegirá **una pregunta por cápsula**, mediante SHA256 y semilla pública congelada `AB-E2E-20261021-LOCKED-01`. Objetivo: 60 cápsulas distintas, dos réplicas por brazo = 240 trayectorias. Si hay menos de 60 cápsulas elegibles o los datos no están accesibles, **STOP / BARRERA_DE_ACCESO**; no completar la cuota con tareas duplicadas ni inventar resultados.

**Transferencia secundaria, no agrupada:** DiscoveryBench real/test (`allenai/discoverybench`, revisión de código `c31fcf011e070f021a5f5b906896d0821f6880e8`), seis familias de estudios: arqueología, plantas invasoras, metarregresión, NLS, ingeniería de requisitos y World Bank. Agrupar variantes raw/derivadas de la misma fuente. La cifra de 264 tareas del artículo NO implica 264 estudios independientes. No usar tareas de prueba para diseñar prompts.

**Calibración técnica:** tareas de entrenamiento de DiscoveryBench (sin reportar como efecto confirmatorio). Si exige cambiar instrucciones tras calibración, congelar una nueva versión ANTES de abrir tareas de prueba y documentar enmienda; no alterar el resultado primario retroactivamente.

## 3. Intervenciones comparables

- **AB:** prompt `PROMPT_AB.txt`, AB 3.2.1 operacional, registro de hipótesis rivales, pruebas discriminantes, auditoría adversarial, actualización y AB-DECIDE.
- **Baseline competente:** prompt `PROMPT_BASELINE.txt`, investigador estadístico riguroso con acceso explícito a hipótesis, incertidumbre, controles, código y validación, pero libre de elegir su flujo de trabajo. **No** es un control ingenuo.
- Ambas condiciones: mismo modelo y versión, mismo contexto inicial por tarea, mismas herramientas, ficheros, bibliotecas, CPU/RAM, tiempo máximo, límite de tokens y de llamadas. Sin navegación al artículo que revela el resultado. El evaluador desconoce el brazo.
- Presupuesto inicial propuesto, a verificar por la plataforma: **60 minutos, 30 llamadas de herramienta, 20.000 tokens de salida y mismo límite de tokens de entrada por trayectoria**. El costo consumido se mide; no se compensa una condición dándole más recursos.
- Orden de ejecución se pseudoaleatoriza por hash. Las réplicas y condiciones requieren **contextos nuevos**, sin compartir historial, resultados, memoria ni artefactos del otro brazo. Temperatura y semilla iguales cuando la API lo permita; registrar cuando no lo permita.
- La selección de tareas y el orden no deben exponerse al agente junto con las respuestas correctas. Los prompts, presupuestos y configuración se congelan antes de puntuar.

## 4. Variables y puntuación

**Primaria:** puntuación oficial BixBench [0,1] por respuesta (0 si incorrecta, rechazo, límite de recursos o fallo atribuible al agente). El evaluador oficial puede utilizar juicio semántico de LLM; fijar versión, temperatura y prompts del evaluador, ocultar el brazo y auditar manualmente una muestra aleatoria ≥20% de respuestas mediante dos revisores independientes. Discrepancias: adjudicación ciega; registrar concordancia y tasas de corrección. Si el evaluador no es reproducible o tiene sesgo por estilo, la conclusión se degrada a **INCONCLUSA**.

**Secundarias, no confirmatorias:** completitud del flujo, afirmaciones injustificadas, trazabilidad, abstenciones apropiadas, errores graves, uso de recursos (tokens, tiempo, llamadas), consistencia entre réplicas y puntuación oficial DiscoveryBench. No construir un índice total ad hoc ni optimizarlo retrospectivamente.

**Intención de tratar:** incluir todas las trayectorias asignadas; fallo, timeout y negativa explícita se califican 0. Una caída verificable de infraestructura común a ambos brazos permite repetir una vez con idéntica configuración, registrando el evento; nunca reintentar selectivamente según la respuesta. **Una ausencia de calificación no se interpreta silenciosamente como cero:** debe resolverse y registrarse el estado explícito antes del análisis.

## 5. Análisis congelado

Para cada cápsula i, calcular `d_i = mean(score_AB_i) - mean(score_BASELINE_i)` con dos réplicas por brazo. Estimador primario: `mean_i(d_i)` sobre 60 cápsulas, ponderación igual por cápsula. IC 95% percentil bootstrap de **cápsulas completas** (20.000 remuestreos, semilla 20261021). Prueba bilateral de cambio de signo pareado (100.000 permutaciones Monte Carlo, semilla 20261021); interpretación condicionada a intercambiabilidad bajo nula y ausencia de contaminación. Informar ambas medias, diferencia, intervalo y valor p. No contar 240 trayectorias como 240 estudios independientes.

**Criterio preregistrado para una ventaja en este benchmark:** Δ>0, límite inferior del IC 95% >0 y p bilateral <0,05, sin problemas graves de aislamiento, grader o paridad de presupuesto. Si no se cumple, **no declarar superioridad**. Si el intervalo es negativo, informar evidencia contra AB. Ningún resultado en un único benchmark valida universalmente AB.

Se aplicará análisis de sensibilidad por cápsula, adjudicación humana, exclusión de fallos de infraestructura verificables y rendimiento por tipo de tarea; estos análisis son secundarios. Si la tasa de faltantes técnicos es alta o se incumple la paridad, invalidar la afirmación principal.

## 6. Potencia y riesgo de falsos positivos

Sesenta cápsulas pueden resultar insuficientes para detectar mejoras pequeñas. Con discordancia hipotética del 40% entre resultados binarios y diferencia real de 20 puntos porcentuales, una aproximación por pares independientes da potencia de orden **70–75%** (estimación orientativa; dos réplicas por cápsula modifican la varianza). No interpretar un nulo como equivalencia ni ausencia de utilidad. Una réplica externa en otros dominios y modelos será necesaria incluso si el resultado es positivo.

## 7. Auditoría adversarial y falsadores

Comprobar: respuestas de referencia memorizadas en preentrenamiento; consulta prohibida a la respuesta pública; fuga de etiquetas; puntuación influida por la extensión de la respuesta; diferencia de tiempo/llamadas; modelos cambiados; independencia falsa de tareas del mismo estudio; grader no ciego; modificaciones de prompts tras ver resultados; coste de ejecución; sesgo por selección de cápsulas. Documentar tanto los errores de AB como los del baseline. No usar un resultado sintético anterior como validación independiente.

## 8. Parada y decisión AB

`DESIGNED` ahora. `RUN` solo después de disponer de las tareas, agentes aislados y puntuador; `SUPPORTED_IN_BENCHMARK` únicamente si supera el criterio primario y auditoría; `INCONCLUSIVE` si potencia/graders/paridad no bastan; `REFUTED_IN_BENCHMARK` si la evidencia apoya inferioridad; `STOP/ACCESS_BLOCKED` si faltan recursos. **No actualizar A01 a «AB validada» por escribir el protocolo, ejecutar el harness o probarlo con datos simulados.**

## 9. Publicación y privacidad

GitHub conserva este prerregistro, prompts, código y commits; Drive almacena informes extensos, anexos y trazas autorizadas. No publicar credenciales, tokens de acceso, identificadores privados de Drive, datos personales ni respuestas gold no licenciadas. El repositorio puede hacerse público más adelante tras una revisión de privacidad y licencias. Los resultados negativos se registrarán igualmente.

## 10. Fuentes

- BixBench: https://github.com/Future-House/BixBench ; artículo https://arxiv.org/abs/2503.00096
- DiscoveryBench: https://github.com/allenai/discoverybench ; artículo https://arxiv.org/abs/2407.01725
- AB 3.2.1: protocolo interno, revisión de 19-10-2026. Este prerregistro es una **propuesta ejecutable**, no una inscripción en un registro institucional independiente.
