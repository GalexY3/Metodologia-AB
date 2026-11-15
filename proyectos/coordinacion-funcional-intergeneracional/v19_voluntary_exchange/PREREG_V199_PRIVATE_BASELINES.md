# V199 — Rivales privados, formación y adaptación después de invertir señales

Fecha de diseño15/11/2026. V198 ya terminó: su deriva media oráculo conserva bienestar en6/6casos, mientras V196 muestral pierde el criterio75%en6/6. V197 corrigió los evaluadores de empates. No se ha entrenado ningún caso V199. Las fixtures técnicas no usan padres reales para seleccionar métodos, tasas o cortes. El turno anterior constituye progreso verificable, no una espera ni un plan pendiente.

## A–C. Cuello de botella y antecedentes que pueden refutar nuestra interpretación

Antes de atribuir necesidad de soporte coordinador a una institución, hay que ejecutar aprendices privados conocidos que toleren retornos ruidosos. Se comparan la regla hysteretic de Matignon, Laurent y Le Fort-Piat2007, ecuación3, y el algoritmo lenient LMRL2 de Wei y Luke2016, sección4. Los parámetros principales se toman de sus textos: hysteretic alpha.1/beta.01; LMRL2 alpha.1, temperatura50, decaimiento.995, umbral de selección codiciosa2, theta=omega=1. Las ecuaciones de ambos se inspeccionaron visualmente en sus PDF originales. Son implementaciones propias de reglas publicadas; no se ejecuta código original de autores ni se reproduce su benchmark completo.

La tarea es una secuencia de decisiones terminales con contexto privado binario; gamma0, sin retorno futuro ni difusión de temperaturas entre episodios. Es una adaptación contextual explícita de LMRL2, no su reproducción exacta con gamma.9en juegos multiestado. Los pagos aquí pueden diferir entre personas por L_i, mientras esos trabajos se centran en juegos cooperativos de pago común. La transferencia de sus garantías no se asume.

## D. Poblaciones, fases y presupuestos

Seis escenarios: k4/8/12 por unanimidad/mayoría, m=k−1votantes.32mundos por escenario,20grupos por mundo. Cada persona tiene pérdida fija privada1o7. Pr(GOOD)=.6. Ratificar da+1si GOOD y−L_i si BAD; rechazar da0. Cada persona observa únicamente su señal y aprende de su pago realizado; no recibe verdad, señales o Q ajenas, pagos contrafactuales, pulso común, crítico central ni transferencia de recursos.

Dos cohortes. MAINTENANCE reutiliza exactamente las Q JOINT_SIGNAL_PULSE_10 de V195 y sus pérdidas, fijadas por hash. Son padres con historia asistida y NO nuevas raíces científicas. FORMATION empieza sin pulsos y sin Q aprendidas, con32mundos nuevos independientes por cada uno de los seis escenarios:192raíces nuevas, apareadas entre métodos dentro de cada mundo. Los escenarios nuevos tienen semillas de pérdidas, estados y acciones separadas por cohorte, k, regla, mundo y stream. Los20grupos no se cuentan como20réplicas independientes de cada mundo.

Ambas cohortes ejecutan8000oportunidades en el entorno original y4000adicionales tras invertir la codificación de la señal: precisión.8→.2, sin cambiar información mutua disponible, prior, pérdidas ni física. Los agentes no reciben aviso de cambio. Una política con sus dos etiquetas de señal intercambiadas conserva exactamente el valor anterior; el problema sigue siendo resoluble. Los métodos no necesitan saber que existe el corte. No comparar formación y mantenimiento como si tuvieran el mismo presupuesto histórico: los padres de mantenimiento ya tuvieron8000sesiones asistidas.

Los métodos comparten las mismas cintas ambientales y de monedas por mundo. Los dados de cada persona siguen siendo privados e independientes. El bloque de100pasos se genera por anticipado sin depender de políticas y se consume completo antes de guardar RNG; esto no equivale a observación anticipada para los aprendices. No hay selección de los mejores mundos ni rescate por test.

## E–F. Métodos congelados y auditoría

1. IQL_JITTER: actualización simétrica alpha.1, epsilon-greedy; conserva el ruido uniforme1e−12de V196 en la selección codiciosa. Evaluarlo con su CDF triangular, no con probabilidad.5en todo el intervalo.
2. IQL_EXACT: mismo algoritmo, selección máxima estricta y desempate aleatorio solo en igualdad exacta. Es el control principal que elimina el posible artefacto de redondear márgenes pequeños.
3. IQL_SLOW: máximo estricto, tasa simétrica.01; control de aprendizaje lento/menor varianza, no mecanismo nuevo.
4. HYSTERETIC: máximo estricto, alpha.1cuando el error TD>=0y beta.01cuando<0. Usa su propio pago. Q inicial0en formación, parámetros publicados. No confundir estimaciones optimistas con utilidad esperada individual mejorada.
5. RUNNING_MEAN: máximo estricto, tasa1/(9+n_visitas)por estado/acción propio. Prior explícito de9pseudobservaciones; la primera actualización usa.1. El prior conserva la Q parental en mantenimiento y Q0en formación. No representa el verdadero número de visitas de los padres, que no se guardó.
6. LMRL2: temperatura propia por estado/acción, selección Boltzmann usando la media de temperaturas de las dos acciones; cuando esa media<2, máximo estricto. Actualiza un error negativo con probabilidad `1−exp(−1/T_sa)`, los no negativos siempre; T_sa se multiplica por.995después de elegir esa acción, incluso si no se acepta el error. Alpha.1. En formación inicializar Q_i=−L_i, el mínimo retorno propio conocido, como recomienda el artículo. En mantenimiento conservar la Q parental y reiniciar T=50declaradamente. El método usa su exploración nativa, sin añadir un epsilon persistente no publicado.
7. FROZEN solo en MAINTENANCE: Q parental sin actualizar y sin epsilon; control que distingue retención de adaptación. No se cuenta como aprendiz exitoso.
8. IQL_MIN solo en FORMATION: IQL_EXACT con Q_i=−L_i para controlar la diferencia de inicialización de LMRL2. No es una nueva familia de algoritmo.

Los otros aprendices usan epsilon.08en mantenimiento y después del cambio. En formación, epsilon decae.30→.08durante6000pasos y luego permanece.08. LMRL2 mantiene su regla nativa en todas las fases; no se ajusta para rescatarlo. Los conteos propios se registran, pero solo RUNNING_MEAN los usa para la tasa. FROZEN no actualiza ningún contador o parámetro.

Guardar métricas analíticas cada1000pasos y Q, conteos, temperaturas y todos los RNG cada4000, incluido0,8000y12000. Conservar precisión de ratificación GOOD/BAD, bienestar codicioso, bienestar nativo mientras exploran y retornos realizados acumulados, distinguiendo personas de pérdidas altas/bajas. La evaluación no entrega información al aprendizaje. Las probabilidades se integran bajo señales privadas condicionalmente independientes y la regla real de elección. La ley continua del pequeño jitter ignora los redondeos finitos del generador; se declara ese límite.

Antes de registrar, exigir paridad con reglas escalares de acciones y actualizaciones; retornos explícitos de la física a través del kernel real; escrituras solo del estado/acción elegido; aislamiento bit a bit entre grupos e invariancia de FROZEN; comprobación Monte Carlo de probabilidades nativas y restauración bit a bit del RNG desde JSON. Las fixtures no entrenan poblaciones reales. Después, congelar código, protocolo, informe técnico, dependencias y hashes de padres, publicar y comprobar bytes HTTP antes de entrenar.

## G–I. Criterios, falsadores e interpretación

H1 principal de mantenimiento: HYSTERETIC conserva al paso8000>=75%del valor codicioso parental en al menos4/6escenarios y deja retorno esperado medio>=0en ambos tipos de pérdidas. Además, frente a IQL_EXACT debe ganar al menos.02de bienestar y tener un intervalo pareado simultáneo positivo en al menos4/6. Usar bootstrap por32mundos,20000remuestreos, intervalos Bonferroni con cobertura individual99.1667%para las seis comparaciones de esta familia. Si falla cualquiera, H1 falla; no cambiar el rival a posteriori para rescatarla.

H2 de formación sin apoyo: al paso8000HYSTERETIC produce bienestar>=.05y supera IQL_EXACT en>=.02, con esos mismos intervalos simultáneos positivos y retornos medios no negativos para ambos tipos, en al menos4/6. Rechazar todo no cumple. Es otra familia declarada por separado; no se infiere una familia conjunta95%entre H1/H2. El resto de métodos se informa íntegro como rivales o controles secundarios; sus intervalos95%son descriptivos y no se presentan como nuevas confirmaciones principales.

H3 de adaptación, secundario fijado: un método pasa un escenario si antes del cambio produce bienestar>=.05y al paso12000recupera>=75%de su propio valor anterior con pagos esperados no negativos para ambos tipos. Si no existe precursor útil no se cuenta como adaptación. Rechazar todo no satisface el criterio. Informar también el daño acumulado durante transición, aunque finalmente se recupere. Los seis casos se muestran; un método solo se considera robusto en ese corte si pasa al menos4/6.

El comparador numérico IQL_JITTER frente a IQL_EXACT puede mostrar que una parte del fallo previo depende del tratamiento de márgenes pequeños. No se atribuirá esa diferencia a una nueva institución. Un éxito de HYSTERETIC o LMRL2 refutaría la supuesta necesidad del soporte externo para esas trayectorias y condiciones, pero sería una solución conocida. Un éxito de tasa lenta o media creciente puede deberse a retener historia; el cambio de señales está diseñado para detectar ese coste de plasticidad. Un fracaso no demuestra imposibilidad del aprendizaje privado ni desacredita el algoritmo original fuera de esta adaptación sin tuning.

## J. Decisión y evaluación

Tras los resultados, auditar los cálculos con otro motor de convolución y comprobar al menos una repetición histórica desde un checkpoint guardado si hay discrepancias. El siguiente mecanismo se elegirá por el rival que sobreviva, no por mantener una hipótesis preferida. Para afirmar emergencia de institución habrá que estudiar después su adopción y mantenimiento voluntarios, costes y rechazo real, con rivales de contratos/MATE; los métodos y la institución de voto aquí son asignados externamente.

Un proceso CPU de investigación, dos hilos NumBa, BelowNormal y afinidad existente, sin GPU. Registrar versiones, negativas y desviaciones; no modificar artefactos ya archivados ni el índice del usuario. DRIFT D1: contraste de rivales privados en la línea de votación existente. CT2 histórico61sin cambio, rama nueva sin puntuación, N2=N3=0. No conceder puntos por192semillas ni por que un algoritmo conocido funcione.
