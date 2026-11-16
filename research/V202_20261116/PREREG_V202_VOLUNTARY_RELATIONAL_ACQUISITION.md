# V202 — adquirir pagos relacionales sin cumplimiento automático

Diseño prospectivo, 16/11/2026. Se registrará en GitHub antes del primer entrenamiento científico. Los ensayos de compilación, paridad y ejecución corta usan semillas 90000–90001 y no seleccionan resultados científicos. Esta es una puerta de viabilidad del aprendizaje, no una reivindicación de originalidad ni formación completa de organización.

## A–C. Pregunta, rivales y discriminante

¿Aprenden agentes privados un patrón funcional de producción y pagos voluntarios, y cambia su adquisición cuando todos observan el recuento de pagos? V201-R proporciona un control viable a capital fijo, pero no acredita adquisición. V172 ya aprendió adopción de una gramática con sanciones ejecutadas por el simulador; V202 elimina ese cumplimiento automático. Ningún pago, multa, castigo, deber de producción o transición a una norma se impone durante el aprendizaje.

Rivales: (a) el retorno futuro y la memoria pública permiten adquisición desde políticas indiferentes; (b) existe un acuerdo estable pero el aprendizaje privado no alcanza su cuenca; (c) la información pública tampoco basta para estos aprendices; (d) el resultado depende de un prior cooperativo suministrado o de otra propiedad del algoritmo. Un fracaso no prueba imposibilidad de toda institución con observación privada.

La unidad de incertidumbre es el mundo de entrenamiento independiente: **32 raíces**, ocho grupos separados por raíz. Los seis brazos emparejan los mismos sorteos físicos y de exploración, sin compartir parámetros ni experiencias. Los grupos son subunidades; los brazos y los controles inicializados no son nuevas raíces. No hay datos humanos nuevos, holdout externo ni selección de hiperparámetros sobre resultados.

## Física, acciones e información

Cuatro agentes, roles fijos 0–3, capital fijado en S=0,8903152454708944 como fixture, no como equilibrio de inversión. Tres ordinarios tienen pérdidas [1,1,7] permutadas por grupo; el crítico tiene L=7. Estados IID G con probabilidad 0,65 y señales privadas condicionalmente independientes de fiabilidad 0,8. Producción autárquica y prima conjunta son las auditadas en V201-R: y=0,25(1−exp(−S)), prima 0,8(1−exp(−S)), coste de trabajo 0,05. El crítico paga preparación 0,30 cuando elige JOINT, aunque no se complete. Si todos eligen JOINT, en G cada uno recibe y+prima; en B recibe −L_i. En caso incompleto se recibe autarquía. Se comparan AUTO y JOINT: descansar está estrictamente dominado por AUTO a este stock y no se elimina una alternativa que pudiera mejorar la utilidad.

Solo después de una producción conjunta GOOD cada ordinario decide pagar 0 o 0,25 al crítico. Los pagos son transferencias abstractas de utilidad de suma cero, sin saldos, crédito o restricción financiera. El simulador ejecuta únicamente los pagos elegidos. El calendario de decisiones, la gramática de transferencia, roles, pertenencia y tecnología son suministrados; no se dirá que los agentes inventaron esas posibilidades.

Se conserva el vector de los tres últimos pagos de una oportunidad GOOD, inicialmente sin historia. Cada agente observa su señal y el último resultado físico (incompleto, BAD o GOOD), inferible de su propio retorno. En PUBLIC todos observan el recuento de pagos de la última oportunidad exitosa. En PRIVATE los ordinarios solo recuerdan si ellos pagaron y el receptor crítico observa el recuento. Las rondas sin éxito conservan la última información de pagos. Nadie recibe pérdidas, Q, logits o retornos ajenos. Hay 30 entradas posibles por tabla, con algunas no utilizadas por observadores privados.

## Algoritmos y presupuesto congelados

Seis brazos: IQL_PUBLIC_COLD, PG_PUBLIC_COLD, IQL_PRIVATE_COLD, PG_PRIVATE_COLD, IQL_PUBLIC_WARM y PG_PUBLIC_WARM. Cada individuo tiene sus propias tablas para modo y pago.

- IQL: Q-learning contextual con continuación temporal, tasa 0,05; la decisión de pago recibe su propio pago neto y valor futuro, y la de modo recibe recompensa total y valor futuro. Empates exactamente uniformes.
- PG: REINFORCE privado por relación completa, logits de Bernoulli independientes por entrada, baseline privado de Monte Carlo; tasa de política 0,02/20 y baseline 0,05 por entrada visitada. El gradiente corresponde a la política mixta que realmente explora, verificado por diferencias finitas. No hay recompensa TEAM, metagradiente sobre otros agentes, bonificación prosocial ni actor compartido. Logits limitados a [−12,12].
- Exploración en ambos: mezcla uniforme epsilon desde 0,20 hasta 0,02 linealmente en las primeras 48.000 rondas; después 0,02. PG conserva sus logits durante cada relación y actualiza al terminarla; IQL actualiza en cada ronda. La comparación no identifica exclusivamente un efecto de una sola pieza del optimizador.
- Una relación termina con probabilidad exógena 0,05 por ronda; las tablas persisten y comienza otra con historia vacía. Esto implementa valoración efectiva beta=0,95. **No se aplica un segundo descuento 0,95** a los retornos dentro de la relación: IQL usa continuación 1 si sobrevive y 0 si termina; PG usa retorno sin descuento hasta terminar. El buffer de 512 rondas produce un error visible si se agota, no truncado silencioso. Relaciones PG aún abiertas al final se guardan y no se usan como episodios completos.
- COLD: Q empatadas en valor autárquico; logits cero. WARM: prior explícito de la política conocida (L=1 dona y paga en estado cooperativo, L=7 sigue señal; respuesta a impago por recuento). Q favorecida con diferencia uno; logits ±ln(19). WARM mide dependencia del prior y mantenimiento bajo el aprendizaje; **no es emergencia** ni una segunda cohorte independiente.
- 60.000 rondas por grupo y brazo, 10.000 por bloque, con checkpoints 0 (inicialización reproducible), 10.000, 30.000 y 60.000. CPU BelowNormal, afinidad de seis procesadores lógicos, un proceso de campaña; dos hilos Numba permitidos. No GPU necesaria para estas tablas. Sin barrido de tasas o arquitecturas después de observar resultados.

## Endpoints y auditoría causal

Se evalúa la política terminal congelada exactamente mediante una cadena de 27 estados (últimos pagos y resultado físico), beta=0,95, desde historia vacía. IQL usa su política codiciosa con empates uniformes; PG usa sus probabilidades nativas sin añadir la mezcla exploratoria. No se confunde el cambio de estas evaluaciones con una comparación pura de algoritmos. Se conserva la información observada por cada política; el evaluador puede enumerar el estado oculto sin suministrárselo al agente.

Un grupo es funcional si simultáneamente: (1) cada agente gana al menos 0,02 de utilidad normalizada por ronda frente a AUTO; (2) la tasa descontada normalizada de producción conjunta GOOD es al menos 0,20; (3) deshabilitar todos los pagos manteniendo las políticas reduce esa tasa en al menos 0,10. El tercer requisito identifica dependencia causal de la interacción aprendida; no basta que aparezcan pagos con cooperación independiente de ellos. Se informa también la respuesta futura a una omisión única de un pago en la primera oportunidad GOOD.

**Única hipótesis confirmatoria H1:** PG_PUBLIC_COLD alcanza al menos 50% de grupos funcionales y supera PG_PRIVATE_COLD en al menos 20 puntos porcentuales. Dos requisitos del mismo compuesto: bootstrap emparejado por las 32 raíces, 20.000 remuestras, intervalos 97,5% para cada requisito (Bonferroni dos). Se exige cota inferior ≥0,50 y cota inferior de la diferencia ≥0,20. El resultado se declara fallido si no cumple ambos, sin rescatarlo con brazos o subgrupos seleccionados.

Los otros brazos, WARM, tasas de pago por tipo y diferencias PG−IQL son diagnósticos descriptivos, con la selección explícita. No acreditan una nueva confirmación por cambiar el criterio después.

Además se calcula mejor respuesta exacta a los demás congelados en PUBLIC, incluida decisión de pago posterior al éxito; se verifica que usar la máscara completa no dé valor adicional frente al recuento realmente público. Se informa explotabilidad desde el inicio y residual. Para PRIVATE solo se prueban desviaciones factibles con información propia (AUTO siempre, JOINT siempre, seguir señal y no pagar). Son cotas inferiores de desviación, **no** una mejor respuesta POMDP óptima ni un certificado de equilibrio. Estas auditorías se separan del criterio funcional común para no favorecer una modalidad con un examen más débil.

## D–J. Integridad, interpretación y decisión

Antes de registrar: comparación del operador exacto con enumeración literal, privacidad de entradas, gradiente de la política mixta, control programado de V201-R con explotabilidad nula y pruebas de checkpoints/RNG. Se preservó un fallo de expectativa del auditor: la primera oportunidad GOOD llega geométricamente, no necesariamente en t=0. Se corrigió la expectativa de la ablación antes de entrenar; no se alteró el motor para superar ese test. La serialización de Philox se comprobó por separado.

Se congelan protocolo, motor, evaluación, runner y análisis en commit GitHub y se verifican sus bytes antes de ejecutar. Se guardan JSON por raíz y brazo, tablas, estados, RNG, versiones, exposición de selección y todos los resultados. No sobrescribir fallos ni otros proyectos. Una reparación tras el inicio requerirá INVALID/errata y un nuevo registro.

H1 positiva solo demuestra adquisición en este banco diseñado. Novedad, formación de roles/membresía/capital y transporte a humanos quedan pendientes. H1 negativa con control WARM útil sugiere barrera de adquisición; WARM también negativo obliga a revisar competencia del aprendiz antes de culpar a la información. R5: no iniciar una cadena de ajustes de tasas para salvar H1. Prioridad posterior para una nueva clase de evidencia, mecanismo o comparador fuerte.

Antecedentes: [Haupt et al. 2024](https://doi.org/10.1007/s10458-024-09682-5), contratos con transferencias vinculantes; [MATE 2024](https://doi.org/10.1007/s10458-024-09666-5), reciprocidad mediante protocolo de tokens; [Halac 2015](https://doi.org/10.1111/1756-2171.12080), incentivos relacionales e inversión específica. Ninguno se ejecuta aquí como implementación original. El control de equilibrio tampoco es un descubrimiento del teorema folk. CT2 histórica 61; nueva línea sin puntuar; N2=N3=0. La autorización autónoma del investigador sigue vigente.
