# AB — Observatorio acumulativo de mejoras, fricciones y prácticas útiles

**Creado:** 2026-10-21. **Estado:** registro **propositivo**, no modificación automática de AB 3.2.1, ni nueva versión metodológica, ni priors metodológicos validados. **Actualización:** anexar entradas y cambios de estado en nuevos commits, sin borrar observaciones desacreditadas. Este documento será el punto de entrada para las observaciones procedentes de todos los proyectos; cada entrada conserva fuente, alcance, contraevidencia y posible decisión.

## Política de clasificación y mantenimiento

- Prefijos: `AB-M` (mejora/debilidad), `AB-B` (beneficio observado en la práctica). IDs estables e independientes de `A01–A21` y de los priors de LARP.
- Estados: `PROPUESTA`, `EN_EVALUACION`, `ADOPTADA_NORMATIVAMENTE`, `VALIDADA_EXTERNAMENTE`, `RECHAZADA`, `REPARAR`. **Todas las entradas iniciales son propuestas**; la observación de un problema no demuestra que una reparación concreta mejore AB globalmente.
- Registrar fecha, proyecto originario, síntoma, hipótesis/beneficio, intervención candidata, falsador o coste, fuentes, decisión humana si procede y fecha de revisión. Anexar versiones; evitar reescritura silenciosa.
- Distinción: `A` = prior metodológico vigente; `AB-M/B` = observación sobre el proceso. No elevar a prior A sin evaluación y justificación explícitas. El repositorio de investigación sustantiva conserva sus propios priors y pruebas.

## Fricciones y propuestas de mejora

### AB-M001 — Inflación del número de «ciclos»
- **Fecha / fuente:** 2026-10-21, LARP BR30: `GalexY3/proyecto-LARP`, `docs/01_LEDGER_30_CICLOS.md` y `src/run_br30.py`.
- **Observación:** 30 entradas se distribuyeron en seis familias; muchas entradas varían sólo el k, cuantil, frecuencia, dropout o bandwidth. Aunque se registró honestamente que no eran 30 estudios independientes, la etiqueta «30 ciclos» confunde **condiciones de una misma prueba** con decisiones abductivas genuinamente diferenciadas.
- **Mejora propuesta:** la unidad `CICLO_AB` requiere nueva pregunta discriminante, hipótesis rivales explícitas, elección/ejecución de prueba y actualización/AB-DECIDE con información nueva. Barridos de parámetros, seeds y contrastes que comparten pregunta son `CONDICION`/`RUN`, asociados a un mismo ciclo padre. Mantener los 30 IDs históricos sin renumerarlos; en informes próximos usar el recuento `ciclos sustantivos / familias / condiciones / réplicas`.
- **Falsador/coste:** puede generar más burocracia y ciclos con varias pruebas complejas; medir tiempo de auditoría y errores de clasificación frente a contar condiciones. **Estado: PROPUESTA**. **No demuestra eficacia causal.**

### AB-M002 — Prerregistro de código suficientemente auditable
- **Fuente:** LARP BR30, commits de diseño y huella previa; publicación del código íntegro junto con resultados.
- **Observación:** bloquear una cadena SHA-256 antes del piloto aporta trazabilidad criptográfica sobre bytes entregados después, pero dificulta auditar el código real, dependencias y las reglas de selección **antes** del ensayo.
- **Mejora:** commit privado del código íntegro, dependencias, entorno y tests antes del primer run que vaya a presentarse como confirmatorio; hash de árboles/datasets y semilla, y acta de *freeze*. Distinguir explícitamente preregistro de protocolo, bloqueo de fuente y ejecución. Permitir reparación versionada con invalidación explícita del holdout comprometido.
- **Falsador/coste:** preregistrar cada cambio reduce agilidad exploratoria; aplicarlo con umbrales diferenciados a exploración y confirmación. **Estado: PROPUESTA**.

### AB-M003 — Independencia jerárquica y pseudorreplicación de geometrías
- **Fuente:** BR30, 20 mundos Fourier confirmados con **una única geometría por algoritmo**; 8192 puntos de consulta en una misma nube.
- **Observación:** IC por mundo no responde a la incertidumbre entre realizaciones geométricas; consultas, vecinos y seeds pueden ser niveles dependientes. La evidencia es condicional a las posiciones concretas.
- **Mejora:** adjuntar a cada estimando el DAG/árbol `generador→geometría→mundo→consulta→medición`, especificar qué nivel se aleatoriza y cuál condiciona los IC. Exigir por defecto múltiples geometrías independientes al generalizar propiedades del algoritmo generador, sin sacrificar de forma ritual análisis finitos correctamente condicionados.
- **Falsador/coste:** pérdida de precisión/potencia por n geométrico pequeño; usar inferencia jerárquica si procede, reportar ambos estimandos. **Estado: PROPUESTA**.

### AB-M004 — Comparador experto antes de optimización exploratoria
- **Fuente:** BR30: RANDOM y rejilla estratificada no sustituyen al artículo SIGGRAPH 2010 `Multi-Class Blue Noise Sampling`; código del autor localizado en https://github.com/1iyiwei/noise (directorio RainbowNoise), MIT (licencia verificada en el índice del repositorio).
- **Observación:** superar baselines débiles puede crear un programa de cientos de ciclos que sólo redescubre técnicas conocidas.
- **Mejora:** `BASELINE_GATE`: revisar teoría, implementación abierta, coste y equivalencias matemáticas antes de derivar 20 variantes propias. Registrar si un baseline auténtico es inaccesible, incompatibilidades de dimensión o restricciones de recurso y una alternativa justificada, **sin** llamarla equivalente.
- **Falsador/coste:** portabilidad de software antiguo y tiempo de integración pueden consumir más que el experimento; comparar valor informativo/coste. **Estado: PROPUESTA**.

### AB-M005 — Reivindicaciones desagregadas y congruencia de instrumentos
- **Fuente:** BR30 y ensayo previo LARP vs Transformer.
- **Observación:** un interpolador RBF por tipos con fórmula composicional conocida mide utilidad de geometría para un problema sintético; no valida automáticamente un mecanismo neuronal, semántica de expertos ni el coste de entrenar un LLM.
- **Mejora:** tabla `observación→estimando→mecanismo→dominio de validez→reivindicación permitida`; exigir nueva medición independiente al saltar de muestreo geométrico a arquitectura de aprendizaje o lenguaje. Registrar *baseline analítico* para detectar tareas diseñadas a favor de la propuesta.
- **Falsador/coste:** formalismo extra si el alcance ya está inequívoco; evaluar reducción efectiva de sobreafirmaciones. **Estado: PROPUESTA**.

### AB-M006 — Parada escalonada por valor de información, no por cupos consumidos
- **Fuente:** AB 3.2.1 R5 y LARP BR30; la nueva línea necesita nuevas geometrías y baseline multiclase, no nuevas semillas Fourier.
- **Mejora:** presupuesto máximo expresado en `ciclos sustantivos` con gates `STOP/REPAIR/PIVOT/CONTINUE`; contingencias por acceso, FLOPs y errores. El número concedido es **techo**, no obligación. Una ampliación deberá identificar evidencia realmente nueva y presupuesto antes de pedirla.
- **Riesgo:** reglas de parada pueden introducir sesgo si se miran repetidamente resultados confirmatorios; contabilizar `alpha spending`/protocolos secuenciales cuando corresponda, y conservar costes de confirmación. **Estado: PROPUESTA**.

### AB-M007 — El branching necesita un árbol de decisiones y control de fuga
- **Fuente:** AB priors A03, A06, A17, A20; LARP 30 condiciones + una única selección confirmatoria.
- **Mejora:** cada rama tiene parent_id, hipótesis rivales, artefactos compartidos, presupuesto, información que autorizó su apertura y ledger de todas las afirmaciones visibles. Separar exploración del holdout sellado y documentar cuándo un test ha sido contaminado; adaptar control de error al número real de afirmaciones, no aplicar Bonferroni mecánico.
- **Riesgo:** sobrecorregir reduce potencia; no afirmar que una sola selección confirmatoria siempre invalida toda corrección por otros usos de datos. **Estado: PROPUESTA**.

### AB-M008 — Gobernanza en múltiples repositorios: procedencia bidireccional
- **Fuente:** anexo 3.2.1-O1; BR30 se archivó en GitHub privado y Drive con commit SHA y enlaces.
- **Mejora:** añadir a todo informe documental `repo/ref/commit/código/dataset/fecha`, más una comprobación automática de enlaces, integridad y divergencias. Distinguir *reproducibilidad computacional* de *veracidad científica*. Una discrepancia abre errata; no se reescribe silenciosamente.
- **Riesgo:** enlaces privados pueden no ser portables y la comprobación criptográfica no detecta errores de modelo. **Estado: PROPUESTA**.

## Prácticas que conviene conservar (no implican prueba de superioridad de AB)

### AB-B001 — Contraste pareado y selección de una afirmación antes de confirmación
- **Fuente:** LARP BR30, piloto seeds 11–20; selección explícita C11 antes de nuevas seeds 901–920.
- **Beneficio observado:** comparaciones bajo el mismo conjunto de mundos y queries reducen confusión por entradas distintas; declarar *una* reivindicación antes de abrir un nuevo conjunto evita presentar treinta hallazgos como igualmente confirmados.
- **Límite:** mismo generador y misma geometría, sin replicación externa. **Estado: PROPUESTA para conservar**.

### AB-B002 — Controles de invariancia que deben dar nulo
- **Fuente:** BR30, tests de permutación de filas y condiciones F27/F30; `avian-patterns-lab` comprueba gradientes por diferencias finitas, traslaciones y conservación de cuotas.
- **Beneficio observado:** un efecto no nulo tras renombrar índices habría detectado un bug; el control nulo valida aspectos de implementación.
- **Límite:** aprobar invariantes no valida el estimando ni la novedad. **Estado: PROPUESTA para conservar**.

### AB-B003 — Evidencia contraria y fronteras de aplicabilidad
- **Fuente:** BR30 f6, dropout .60, empate LOCAL/MHU y RBF clásico.
- **Beneficio observado:** documentar condiciones donde la mejora se reduce o invierte hace falsable la afirmación y limita extrapolaciones.
- **Límite:** falsabilidad escrita no prueba que el proceso AB sea superior; medir si cambia decisiones de investigación. **Estado: PROPUESTA para conservar**.

### AB-B004 — Commit canónico + documentación complementaria
- **Fuente:** AB 3.2.1-O1 y commits LARP BR30, archivo Drive.
- **Beneficio operacional:** archivos y fuente verificables, separación AB/LARP, posibilidad de transferir investigación entre chats.
- **Límite:** beneficios de organización inferidos por inspección, no medidos contra alternativas de gestión. **Estado: PROPUESTA para conservar**.

## Próximas revisiones / principios de auditoría
- En el siguiente estudio LARP, al menos una revisión de `AB-M001`, `AB-M003`, `AB-M004` y `AB-M006` debe acompañar AB-DECIDE, con resultados nuevos **si los hay**.
- No llamar descubrimientos a estas observaciones de gobernanza: son mejoras candidatas, pruebas negativas o beneficios de trazabilidad.
- Si la hipótesis de método no produce evidencia propia, registrar `NO_VALIDADO` y no añadir priors A numéricos.
- Incorporar otras entradas en nuevos commits; no borrar este bloque histórico.
