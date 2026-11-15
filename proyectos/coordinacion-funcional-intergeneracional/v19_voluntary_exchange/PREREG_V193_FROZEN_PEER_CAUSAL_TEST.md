# V193 — ¿Necesita coadaptación continua la generalización tardía de V192?

15/11/2026. V192 terminó antes de registrar esta campaña. PRIVATE_FULL produjo cuatro candidatos descriptivos; ambas redes terminaron con precisión conjunta de test1.0. Sus cortes de memorización fueron1200,1100,1100,1200 y sus t_gen10200,12000,11700,10600. Los cuatro controles oráculo también generalizaron tarde; las cuatro historias PRIVATE_BANDIT_IS quedaron alrededor1/31. Son resultados exploratorios de cuatro bloques, no confirmación independiente ni acreditación2/3. V193 conoce esos resultados y no se presenta como predicción virgen de su existencia.

## A–C. Pregunta, rival y falsador

La hipótesis fuerte diría que los dos aprendices deben seguir adaptándose conjuntamente durante la fase posterior a memorizar para que aparezca generalización. El rival es una convención ya formada que proporciona feedback suficiente para que cada red experimente grokking individual. La existencia de dos redes no distingue esas explicaciones.

Congelar un compañero que todavía falla en entradas locales de test puede limitar trivialmente el test conjunto. El estimando principal es la precisión local del aprendiz activo, medida bajo el desfase elegido con entrenamiento, sin escogerlo por test. El resultado conjunto y su techo informacional se reportan aparte. El juego, intereses comunes y oráculo de feedback contrafactual continúan diseñados; esta campaña no estudia invención de instituciones materiales.

## D–F. Intervenciones y presupuesto

Usar los cuatro checkpoints `PRIVATE_FULL/first_memorization_s192115..192118.pt` de V192. Se guardaron tras cinco evaluaciones con precisión conjunta de entrenamiento>=.99, sin seleccionar por test. No se eligen otros cortes después de ver la nueva intervención.

Dos brazos por cada historia parental: FREEZE_A, que mantiene fija la redA y continúaB; FREEZE_B, que hace lo contrario. La red congelada conserva su función completa y la misma exploración epsilon-greedy=.1. No se sustituye su conducta estocástica por argmax. El aprendiz activo conserva arquitectura, datos, optimizador, momentos y su estado aleatorio. Ambos siguen recibiendo únicamente sus pagos propios completos; no se suministra la etiqueta local verdadera.

Continuar hasta el paso total60000de V192. Las actualizaciones restantes son60000−t_memde cada historia. En las dos historias cuyo corte es1100se ejecutan100pasos de intervención antes de agruparlas con las otras dos en1200. Solo alinea los contadores de Adam activos; cada compañero permanece congelado desde su corte original. Los historiales tienen el mismo presupuesto que su continuación conjunta original. Las copias técnicas para conservar la forma de kernels GPU no se cuentan como nuevas semillas.

Se usarán como comparación las continuaciones conjuntas originales V192, no nuevos historiales supuestamente independientes. Hay cuatro raíces de entrenamiento y ocho continuaciones contrafactuales; no ocho réplicas independientes. Se conservarán las curvas, estados y semillas emparejadas. Evaluar cada100actualizaciones y guardar estados cada5000. No detener por test ni prolongar el horizonte.

## G. Criterio prospectivo causal

El criterio para refutar robustamente la necesidad de coadaptación continua después de memorizar requiere, en cada brazo por separado, al menos3/4historias activas con precisión LOCAL de test>=.95 en el punto final y una mediana del déficit frente a la red correspondiente de la continuación conjunta <=.02. V192 termina con precisión local1.0 para ambas redes. Reportar todos los casos y ambos brazos, aunque el criterio global falle.

Registrar el primer tiempo de cinco evaluaciones consecutivas de precisión local activa>=.95 y comparar su curva con la original. Si un brazo no generaliza, no declarar automáticamente probada la necesidad de coadaptación: comprobar la información del feedback, ruido y sensibilidad numérica. Un resultado positivo de congelación no dice que la interacción anterior a memorizar fuera innecesaria.

Para un compañero congelado con distribución de error modular h_Fsobre sus entradas retenidas, el test conjunto no puede superar max_g h_F(g), porque los inputs locales son independientes y no hay comunicación de sus estados. Esta cota se documenta como identidad conocida, no descubrimiento. El feedback de entrenamiento puede seguir siendo informativo aunque ese techo de test sea bajo: se conserva la distribución de errores del compañero sobre entrenamiento y su separación entre los modos principales.

Contraste secundario descriptivo: comparar bit a bit pesos y momentos de la red activa con la continuación conjunta en cada checkpoint posterior y comparar RNG. Si coinciden, documentarlo; no elevarlo a confirmación científica independiente ni a necesidad teórica universal. El criterio primario usa precisión local, no exige igualdad de parámetros.

## H–J. Auditoría e interpretación

Antes del registro se reconstruyó la continuación conjunta histórica desde los primeros checkpoints hasta5000. Las24comparaciones tensoriales de pesos y estados, junto con RNG, fueron idénticas bit a bit, error máximo0. Esa prueba valida la reanudación; no es nueva trayectoria científica. Se conserva un error previo de mezclado de dispositivos CPU/GPU al combinar momentos, corregido antes del registro. No se ejecutó congelación científica antes de registrar este protocolo.

Congelar las fuentes, datos de contexto, hashes de estados parentales y auditoría antes de continuar. Los estados binarios parentales se identifican por SHA256en el manifiesto previo y se entregarán completos con la evidencia final; no hace falta duplicarlos como texto en GitHub para fijar su identidad. Se preservan los archivos V192sin cambios.

Un procesoGPU, máximo35%memoria, dos hilosCPU, BelowNormal,seisCPU y descansos por bloque. CT2 histórico61, rama nueva sin puntuación; N2=N3=0. Un resultado que atribuya la transición a grokking individual tras formar una convención será un negativo relevante de la hipótesis fuerte y no se ocultará.
