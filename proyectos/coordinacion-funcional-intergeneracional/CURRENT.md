# CURRENT — Coordinación funcional distribuida

**Fecha inicial:** 9/11/2026. **Máquina principal:** DESKTOP-I4SULKD. **Rama:** research/intergenerational-k-coordination-20261109. **Worktree local:** C:\Programación\AB-coordinacion-intergeneracional-20261109. **Repositorio:** GalexY3/Metodologia-AB. El laboratorio de grokking y lesiones V10–V15 está cerrado en la rama research/grokking-lesion-v12-travel-20261109, commit base ac897748f0fdfb9630f967ebf08a41f5858bcee8.

## Contrato del usuario y prioridades

Proyecto posterior a V15 de regeneración neuronal, planteado por el usuario en texto adjunto: N agentes deben distribuirse de manera estable entre k funciones en proporción 1/k; comunicación con un vecino por turno; entrenamiento k=1..4 y evaluación k>4; investigar aprendizaje/generación y después sustitución intergeneracional. El texto mencionaba DOCX/PDF que no se han inspeccionado como archivos binarios. No asumir su contenido; QUEUE.md recoge el texto fuente disponible y cautelas.

## P0 realizado

Modelo `model.py`, parámetros en PROTOCOL_V0.md: N120, anillo grado4, matching sobre aristas (cada agente ≤1 conversación/tick), memoria local descontada, θ_i con tres pesos privados sobre rareza local, persistencia, imitación; REINFORCE con recompensa de complementariedad calculada solo con información local. División conocida k2..4 y evaluación inédita k5..8. Se probaron 10 invariantes. La heurística manual de función menos observada resuelve 12/12 en cuatro semillas por k2..4; el agente REINFORCE P0 k4 0/4 y test k5..8 0/10 en cada k. La recompensa de escasez y las features son ingeniería previa, no solución autónoma no guiada.

## P1 realizado

PROTOCOL_P1_SCALE.md fijado después de observar P0 y antes de nueva cohorte/test. Cambia UNA característica: `−freq_local(c)` → `−k×freq_local(c)`. Entrenamiento de P0 y P1 desde cero en la MISMA cohorte seed20261110, 8 episodios por k2..4, 120 pasos cada; validación conocida nueva semillas 7000+100k+s (s0..3); test nuevo 10000+100k+s (s0..9) k5..8, parámetros congelados, 140 ticks. Resultados test P0 vs P1: k5 0/10 vs10/10; k6 0 vs6; k7 0 vs3; k8 0 vs1. La heurística manual k5 9, k6 5, k7 0, k8 0 para esas semillas. Informes REPORT_P0_P1.md, código model_p1.py y experiment_p1.py, JSON results_p1/P1_RESULTS.json y archivo results_p1/TEST_LOCK.json. **Una cohorte independiente por tratamiento**: no hablar de prueba universal.

## G0 realizado

PROTOCOL_TURNOVER_V0.md: regla de minoría manual, comunidades estables en k4 o k5 (intentos 20 por k, elegibles k4=20 y k5=17). Reemplazar 25,50,75% de agentes, con idéntico vector posshock y nodos sustituidos entre tres intervenciones: herencia de regla, no enseñar, enseñanza por contacto con p=.25/turno (contacto limitado y efecto desde tick siguiente). Horizonte 150. Con k4 y 50/75%: heredada20/20, sin enseñar0/20, contacto20/20. Con k5 y50%: heredada17/17, sin enseñar0/17, contacto11/17; con 75%: heredada17, sin0, contacto5. Reporte REPORT_G0.md, auditoría RESULTS_G0_AUDIT.json PASS para333 ramas. Esta etapa no representa política aprendida por REINFORCE ni emergencia de grokking social.

## Resultado de conjunto

La coordinación local es técnicamente factible; un agente puede usar conocimiento parcial para promover equilibrio global. La extrapolación de la política aprendida es sensible a la escala de rasgos, y el éxito se reduce al aumentar k. La pérdida y transmisión de una regla ya programada afectan fuertemente la reconstrucción intergeneracional bajo shocks emparejados. NO se ha demostrado un mecanismo de grokking colectivo, originalidad científica, ni un fenómeno causal en sociedades reales.

## Próximos pasos concretos

1. Replicar P1 vs P0 **entre varias semillas de entrenamiento independientes**, no solo episodios test de la misma cohorte. Reservar nuevas semillas de evaluación y quizá k9..12 para no reutilizar k5..8 ya inspeccionados. Mantener escala/recompensas fijas y controlar mensajes/tasa de actualización. Usar ambos PCs si conviene.
2. G1: comparar desde idéntico vector posshock la recuperación de agentes que han aprendido θ_i, frente a recién llegados con θ inicial y controles con θ heredados. Antes garantizar que el sistema aprendido establece estabilidad. Cuidado con distinguir reset de θ, reset de memoria y reemplazo de colores.
3. Un diseño para analogía grokking requiere series temporales de rendimiento conocido y desconocido sin entrenar con test, transición tardía real y comparación con aprendizaje gradual a competencia equivalente. Actualmente no se ha observado.
4. Gráficos y memoria reproducible en informes/JSON, no reciclar test vistos como virgen.

## Rectificación fundamental del usuario, 10/11/2026

**V2 conceptual pendiente, todavía NO programado:** el usuario precisa agentes sobre una red geométrica donde cada nodo interior tiene cinco vecinos y los del borde menos; observa su color y todos los colores vecinos directamente; puede enviar su snapshot local y una solicitud de cambio a un único vecino saliente por turno; al mismo tiempo puede recibir múltiples solicitudes entrantes y elegir obedecer o rechazarlas. Tras actualizar colores simultáneamente se les ofrece feedback continuo de progreso colectivo respecto a la ronda anterior, no premio binario por éxito perfecto. Hay que explorar memoria temporal de varias rondas y entrenamiento inicial hasta k4, con k5 reservado para extrapolación. El protocolo de discusión está en V2_CONCEPTUAL_REDESIGN_DRAFT.md. NO presentar los resultados P0/P1/P2/G0/G1, que utilizaron anillo grado4 y emparejamientos bilaterales limitados, como estimaciones de esta nueva interacción. Conservarlos como pilotos de modelos distintos sin borrar. No empezar V2 sin concretar las ambigüedades pendientes (contigüidad de grupos y quién recibe el indicador global).


## Actualización V3B tras crítica de Argon — 10/11/2026

**ESTADO ACTUAL MÁS RECIENTE EN ESTA RAMA:** La investigación principal sobre cooperación se encuentra en `v3_independent/`. Consultar `v3_independent/README.md`, `PROTOCOL.md` y `ARGON_RESPONSE.md` antes de continuar. Las notas previas sobre V2 «pendiente» se conservan como registro histórico: V2 fue ejecutado, pero sus resultados corresponden a una arquitectura con parámetros compartidos y/o crédito individual centralizado y NO satisfacen el requisito final del usuario.

El usuario exige N **agentes separados**, cada uno con parámetros θ_i propios y sin compartir estrategias ni gradientes. Cada agente ve directamente su propio color y los colores de vecinos inmediatos; puede enviar un mensaje con snapshot local y petición a **un solo vecino**, y recibir mensajes de múltiples vecinos. **Puede cambiar su propio color libremente sin mensajes**. Su única decisión física sobre el estado es elegir uno de k colores, incluido mantenerse; no hay botón adicional «aceptar mensaje». El contenido de los mensajes puede afectar la decisión, pero la coincidencia de color no prueba obediencia. Feedback r=N(D_t−D_{t+1}) **único para todos**, sin recompensas contrafactuales individuales; no hay crítico con histograma global.

Para evitar preferencias permanentes por etiquetas arbitrarias, cada agente tiene una red de puntuación **equivariante entre colores**, distinta de las demás personas; renombrar colores permuta outputs y no altera la política. Entrenamiento REINFORCE con baseline leave-one-out de **otros mundos del mismo k** (no del agente), clipping por θ_i. Comparaciones C1 sin mensajes, C2 con mensajes, C3 ablación posterior de C2. Métricas D/E[D_IID] («desequilibrio relativo al azar», NO hiperuniformidad), TV, churn, estabilidad, reparto exacto, aleatorio siempre activo y aleatorio con parada.

**Completado y verificado:** 10 pruebas automáticas pasadas, incluida independencia de gradientes y equivariancia; 2 actualizaciones de ejecución de prueba C1 y C2 con seed341, batch6, steps5. Esas microejecuciones solo demuestran que la nueva arquitectura se ejecuta, **no que aprende a cooperar**. No hay test científico V3B todavía. Queda pendiente entrenamiento suficiente con varias cohortes y evaluación reservada, contrastes de comunicación y perturbaciones. Los pilotos previos se conservaron íntegros en sus propias ramas.


## V3C — Resultado de escalado y entrenamiento largo, 10/11/2026

**LEER PRIMERO** `v3_independent/REPORT_V3C_SCALING.md`, `PREREG_V3C_SCALING.md`, `v3_independent/holdout_v3c/`. Las simulaciones en los dos ordenadores **se han ejecutado realmente**: N36 hidden64 2000 actualizaciones, N120 hidden24 1500, N120 hidden64 2000, N240 hidden64 1000, con C1 y C2 por diseño (8 entrenamientos y 8 checkpoint finales). Se añadieron dos entrenamientos N36 hidden64 de episodios de 96 turnos con 500 actualizaciones cada uno; sus checkpoints existen, pero en este informe no figura evaluación independiente de esta variante.

**Resultado vigente:** en las cuatro configuraciones y en k2,3,4, NO hubo ninguna sociedad estable durante los últimos diez turnos en C1 ni C2. La distancia D permanece próxima al azar IID, con diferencias C1-C2 variables. En cambio, el control aleatorio programado para detener cambios en turno 24 alcanza estabilidad parcial o frecuente, especialmente con N elevado. Los agentes neuronales no han aprendido todavía a reducir suficientemente el churn a pesar del entrenamiento extenso. Esto no demuestra imposibilidad, solo fracaso de estos algoritmos y presupuesto. Los tests de tamaño/capacidad se hicieron con una sola cohorte seed411 por condición, y no representan replicación independiente por semilla.

**Repositorio y continuidad:** rama `research/cooperacion-individual-v3-20261110`; proyecto `proyectos/coordinacion-funcional-intergeneracional/v3_independent`, y experimentos anteriores conservados. Los modelos N120/H64 y N240/H64 se entrenaron en DESKTOP-I4SULKD y se integraron desde rama `research/v3c-scaling-desktop-20261110`; N36 y N120/H24 están en GalexY_travel. Los pesos, logs, SHA-locks y resultados del escalado se consolidaron en la rama común.
