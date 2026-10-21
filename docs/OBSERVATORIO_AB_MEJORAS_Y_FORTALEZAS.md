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


---
## Anexo acumulativo — 21-10-2026, LARP BR12 dinámico
**Procedencia:** `GalexY3/proyecto-LARP`, commits `aff298281e3b9efab361964cf068a95c8c0b1163` (prerregistro dinámico), `56b38d13ae6b9e3c02b03021961a922772128b50` (primer código congelado) y `4d4d2179c2c9913150d9cb7088fe645fb2603037` (código y 12 decisiones posteriores). Documento `docs/07_BR12_LEDGER_12_CICLOS.md`.

### AB-M009 — Exigir convergencia y optimización justa de baselines
- **Observación/resultado:** comparación LARP LOCAL (MSE f1 k24 .1404) frente CVT inicial (.1542), aparentemente favorable a LOCAL. Después de mayor optimización CVT y bandwidth elegido solo en desarrollo, CVT refinado consiguió .0893–.0922 frente LOCAL .1074 en un holdout del mismo generador. Esto *cambia el signo* del ranking, aunque se modificaron tanto CVT como el estimador y el estudio es exploratorio.
- **Mejora candidata:** previo a cualquier reivindicación de superioridad, comprobar la curva de convergencia de todos los comparadores competentes y conceder un presupuesto documentado de ajuste por método; desagregar efecto del generador y del predictor mediante factorial si es posible. Reportar coste de entrenamiento, generación e inferencia por separado.
- **Falsador/coste:** la igualdad de presupuestos puede impedir optimizar alguno de los métodos; más tuning induce selección y exige holdout renovado. Diseñar pilotos realistas para escoger un buen balance.
- **Estado:** PROPUESTA. No acredita AB por sí misma. **Relacionado con AB-M004**.

### AB-M010 — Equivalencia de implementaciones y dimensión como condición de inferencia
- **Observación:** el nuevo LOCAL_derived de N512 alcanzó 69.2% cobertura k16, mientras el LOCAL original Scale3D N4096 alcanzaba ~96% bajo otra escala. Ni parametrización, ni optimizador, ni N eran idénticos, de modo que equipararlos habría producido una inferencia falsa.
- **Mejora candidata:** toda `REPLICACION` debe tener manifiesto de equivalencia: misma función de energía, gradientes, semillas, geometría/dimensión, tamaños, inicialización, criterio de convergencia y outputs; sin equivalencia usar `DERIVADO/PROXY`, permitir utilidad exploratoria pero prohibir declaración de réplica.
- **Falsador/coste:** equivalencia exacta no es siempre necesaria para transferencia; distinguir replicación bitwise, conceptual e independiente por objetivos antes de imponer prueba costosa.
- **Estado:** PROPUESTA. Relacionado con AB-M003.

### AB-M011 — Veracidad del estado confirmatorio después de tuning adaptativo
- **Observación:** LARP BR12 utilizó mundos de desarrollo 5101–5108 y evaluación 6101–6112; pero fue una rama elegida tras observar otras pruebas del mismo generador y la fuente completa de fases adicionales no estaba congelada en GitHub antes de cada test. Por tanto, el resultado se presenta como **exploratorio con holdout interno**, NO una confirmación preregistrada ni externa.
- **Mejora:** etiqueta de origen de la hipótesis (previa/emergente), grado de reutilización del generador, estado del holdout y fecha de freeze del código. Exigir tabla de cuántos tests fueron inspeccionados y un registro de los cambios de comparación para calibrar inferencia.
- **Falsador/coste:** no prohibir investigación exploratoria adaptativa; penalización ritual consume poder de descubrimiento. Estado PROPUESTA.

### AB-B005 — Decisión dinámica que abandona una hipótesis favorecida
- **Observación favorable:** el branching llevó desde esperar superioridad LOCAL frente CVT a STOP cuando un comparador refinado y mejor calibrado invirtió el orden; después se buscaron mecanismos rivales (acceso por tipo, MLP, dropout, espectro) sin promover hallazgos a nivel 2/3.
- **Beneficio práctico:** el registro de la secuencia y los siguientes falsadores reduce el riesgo de que el branching se transforme en búsqueda retrospectiva de la mejor semilla. No se ha probado que AB sea mejor que un equipo científico convencional.
- **Límite:** los 12 ciclos comparten varios DGP y geometrías; clasificar su valor informativo sigue siendo subjetivo.
- **Estado:** PROPUESTA para conservar.

### AB-B006 — Resultados positivos en la variable mecanismo, negativos en el outcome
- **Observación:** MHU suprime considerablemente S(k) en 80 modos pero un CVT por tipo de mayor S(k) predice mejor los campos suaves del piloto. Medir mecanismo y outcome separadamente evitó inferir utilidad por excelencia de un proxy.
- **Beneficio:** mecanismo deseado no es resultado final; mantener mecanismos, riesgos y resultados separados en el ledger. No equivale a novedad matemática sobre HU.
- **Estado:** PROPUESTA para conservar.

**No cambia automáticamente AB 3.2.1 ni A01–A21**. Tras una futura comparación metodológica podrá proponerse cambiar el núcleo con un commit y justificación, no por anotación autoaprobada.
