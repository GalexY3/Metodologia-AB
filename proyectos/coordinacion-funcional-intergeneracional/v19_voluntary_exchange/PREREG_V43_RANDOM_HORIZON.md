# V43 — El efecto de la duración incierta y la observación del final sobre la cooperación sin contratos

**Preregistro 13/11/2026, antes de los entrenamientos V43.** Motivación: V41 mostró que ocho continuaciones de agentes interesados únicamente en su alimentación propia abandonaron la donación unilateral a N48/k4 y coste0,04, incluso cuando habían aprendido previamente a contratar. V42 demostró la factibilidad matemática de un mecanismo oracular de reciprocidad cuando existe suficiente probabilidad de continuidad futura, sin demostrar aprendizaje de dicho mecanismo.

## Pregunta central

**RQ43.** ¿Puede la incertidumbre sobre la terminación de las relaciones y/o el ocultamiento del reloj del episodio permitir que agentes individuales descubran reciprocidad condicional rentable sin contratos, profesor, moralidad programada ni recompensas grupales?

## Factorial preregistrado

Se duplican dos checkpoints V30 previamente entrenados bajo contrato c0,04, N48 y cuatro profesiones (semillas neuronales3111 y4111, actualización original700 y estados Adam restaurados), y se crean cuatro ramas por checkpoint:

- **FIX_CLOCK:** horizonte material fijo de 48 rondas, y vector de observación original que revela la fracción t/48.
- **FIX_HIDDEN:** mismo horizonte fijo de 48 rondas, pero t/48 se sustituye por cero exclusivamente en las observaciones de las redes de donante y profesión; el reloj físico y las recompensas no cambian.
- **HAZARD_CLOCK:** probabilidad exógena de continuar de una ronda a la siguiente q=0,98, con truncamiento máximo en48 rondas, tiempo t/48 visible.
- **HAZARD_HIDDEN:** igual distribución de duración q=0,98 y truncamiento48, pero t/48 se oculta a las políticas privadas.

En ambas variantes HAZARD la terminación se sortea separadamente por sociedad-mundo, no por agente, para evitar confundir muerte individual con desintegración grupal. Después de terminar, las recompensas y los log-probs/entropías para ese mundo se enmascaran a cero en las actualizaciones; los pasos computacionales sobrantes no cuentan como experiencias. En FIX no se sortea supervivencia, y en CLOCK el código debe coincidir con el rollout original de V41 cuando se usan pesos, fuentes RNG y parámetros iguales.

Todas las ramas parten de los mismos pesos y estados del optimizador; 1000 nuevas actualizaciones, lote12, 48 rondas máximas, c=0,04 fijo desde el primer paso, gamma0,995, actor de destino-regalo privado y actor profesional privado por persona; entrega unilateral material original, sin liquidación automática, tres ofertas posibles, cambio de profesión cada8 rondas y coste de cambio0,015. Las redes no comparten parámetros ni recompensas.

El objetivo de una sociedad HAZARD se mide por alimento medio **por agente-ronda vivo**, y regalos por agente-ronda vivo, evitando confundir la duración de episodios con bienestar material. Las recompensas para la optimización son alimento propio descontado durante los turnos supervivientes de cada mundo; en particular NO se usa castigo adicional por terminar.

## Criterios y falsación

H43a: al menos una de las dos ramas HAZARD_HIDDEN presenta retorno causal medio privado positivo de forzar un regalo en t0 y ≥24/48 agentes positivos al terminar1000 actualizaciones, sobre seis semillas ambientales nuevas.

H43b: en ambos pares de semilla, HAZARD_HIDDEN supera HAZARD_CLOCK en retorno causal privado descontado por ≥+0,025.

H43c: en al menos una semilla FIX_HIDDEN supera FIX_CLOCK en retorno causal privado por ≥+0,015.

H43d: si una rama de HAZARD_HIDDEN supera H43a, el efecto debe mantenerse positivo para al menos24/48 personas en red reconectada y su alimentación por agente-ronda vivo debe superar al mejor de tres controles de movilidad profesional aleatoria (0,15;0,35;0,60) por ≥+0,025.

La evaluación final congela todas las redes a u1000, sin elegir retrospectivamente mejores checkpoints. Seis semillas ambientales970001,970007,970009,970021,970031,970037; 12 mundos por seed/condición para alimento y seis mundos para intervención causal de cada individuo. Informar retorno inmediato -c, beneficios posteriores, tasa de regalos, cobertura, supervivencia efectiva, inclusión de agentes y transferibilidad a red reconectada. El historial de aprendizaje se registra a actualizaciones1,200,400,600,800,1000 y no sustituye la prueba final.

## Auditoría técnica

Antes de entrenar, un test fijo de paridad debe verificar que el rollout FIX_CLOCK (q=1) produce exactamente los mismos alimentos, log-probs y observaciones que el motor V25/V41 para pesos, semillas y RNG idénticos. Otro test confirma que todos los mundos muertos dejan de aportar rewards y gradientes, mientras su terminación no altera la de los mundos vivos. Un tercer test verifica que ocultar el reloj no cambia los pagos físicos cuando las ofertas realizadas son idénticas.

## Validez

El límite físico de48 rondas sigue existiendo incluso bajo HAZARD; una sociedad sin reloj no sabe exactamente en qué ronda ocurre el truncamiento, pero la distribución efectiva de duración está acotada. Diferentes duraciones implican distinta cantidad de experiencia por episodio, por lo que las comparaciones más interpretables de reloj son **dentro** de un mismo tipo de horizonte; la diferencia FIX vs HAZARD está afectada también por la longitud efectiva. Cualquier beneficio de la incertidumbre no prueba que los agentes hayan inventado la propia institución de compromiso. Solo hay dos semillas neuronales por brazo.
