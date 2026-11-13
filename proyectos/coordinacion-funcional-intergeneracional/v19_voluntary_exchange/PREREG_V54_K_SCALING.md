# V54 — Generalización de la especialización endógena al número de oficios k

Preregistro 13/11/2026, antes de entrenamientos V54. Motivación: V51/V52 enseñaron que cuatro roles se coordinan en equipos K4 cuando existe una estrategia de dones previamente aprendida; k2 también se había probado con un entorno diferente. No hay evidencia previa de una función de escalado k manteniendo tamaño poblacional y algoritmo fijos. Esta campaña constituye una prueba nueva, no una confirmación automática.

## Hipótesis causal y preguntas

**RQ54a:** Si se mantienen constantes los 120 agentes, el entrenamiento y la función de utilidad individual, ¿hasta qué número de oficios k aprenden una asignación perfectamente complementaria sin cuotas ni planificador?

**RQ54b:** ¿Cómo cambia el éxito en función de la disponibilidad de una estrategia privada de reciprocidad preaprendida y de la capacidad de producción de regalos?

**RQ54c:** ¿Qué dificultades de aprendizaje (tiempo de convergencia, selección individual de profesión, fracaso de coordinación) aparecen al aumentar k, distinguiéndolas de imposibilidades físicas?

## Entorno factorial principal

- **N=120 en todas las celdas**; k∈{2,3,4,5,6,8,10,12}, todos divisores de N. Se constituyen N/k equipos de tamaño k con conexiones de clique K_k. La composición de cada equipo y los enlaces son **externos**. Cada persona elige de forma independiente una de k profesiones, sin que el sistema exija cuotas de ocupación. La sociedad se considera profesionalmente completa en un equipo cuando aparecen exactamente los k oficios.
- Dos estrategias de donar congeladas, transferidas de V47 a N120 mediante una permutación predefinida y posterior repetición de las48 políticas individuales: **LOLA20** (reciprocidad preaprendida) y **NL** (control con donaciones casi extinguidas). El origen de las políticas privadas es el checkpoint V47 con semilla3111 para la primera semilla de entrenamiento y4111 para la segunda. A los120 agentes se asignan pesos privados iniciales de donación, sin actualizarlos durante V54. Ninguna política profesional es preentrenada; todos los120 actores de rol comienzan aleatorios e independientes.
- Dos semillas de actor ocupacional y distribución aleatoria,7111 y8111, cruzadas con los dos tipos de donante, para **32 entrenamientos principales** (8 valores k ×2 condiciones de donación ×2 semillas). El donante inicial y la semilla de actor se mantienen emparejados a través de k. No se elegirá el mejor checkpoint intermedio.
- Todas las ocupaciones se pueden cambiar cada8 rondas pagando0,015; entrenamiento REINFORCE privado con baseline de mundos, política MLP individual y no compartida (24 unidades ocultas, características de profesión propia, distribución de roles vecinos, alimento anterior, reloj y último cambio), Adam0,003, entropía0,01, 1.400 actualizaciones, lote12 mundos, horizonte48, descuento temporal0,995. Entrenamiento con mitad de mundos inicializados en una ocupación monolítica0 y mitad con roles aleatorios. Pesos de rol inicializados del mismo procedimiento para todas las condiciones; los tamaños de entrada y salida varían inevitablemente con k.
- Se registran u1,200,400,600,800,1000,1200,1400 y checkpoint final con optimizador. Las recompensas tienen exclusivamente alimento personal y no se premia directamente la diversidad, cobertura grupal o número de roles.

## Economía comparada y capacidad productiva

**Condición de entrenamiento ELASTIC.** Cada agente dispone de un enlace de regalo privado con cada uno de sus k−1 vecinos. El actor de regalo Bernoulli V47 se aplica independientemente a cada vínculo y conserva memoria de una ronda para ese vínculo; el regalo puede omitirse. La producción total potencial aumenta con k, pero el coste total de donar a todos los vecinos se mantiene igual a0,12, por lo que cada regalo cuesta0,12/(k−1). Se acepta que esta tecnología de escalado de capacidad es una hipótesis fuerte de laboratorio y **no** una descripción realista del trabajo productivo. Recompensa:
`food_i=0,20+0,55 × (# tipos complementarios distintos recibidos)/(k−1) +0,25×I(recibe los k−1 tipos) −[0,12/(k−1)]×(# regalos enviados)−0,015×I(cambia de oficio)`.
Con todos los roles distintos y donaciones universales, comida=0,88 para cualquier k. La equivalencia de pago con V51/V25 es exacta cuando k=4, excepto que el grupo k y N difieren.

**Controles físicos de capacidad:**
- **FIXED3**: el individuo solo puede emitir tres unidades por ronda; si tiene >3 candidatos que su política quiere regalar, una selección aleatoria exógena de hasta tres enlaces determina los efectivamente entregados; cada regalo cuesta0,04. Con k−1>3, **no todos los miembros pueden recibir simultáneamente todos los k−1 bienes**; sin embargo, un destinatario aislado sí podría recibirlos si cada productor lo prioriza. Por conservación de dones, la fracción de personas con cesta completa queda acotada superiormente por 3/(k−1), incluso antes de considerar profesiones duplicadas. Se evaluará el efecto material *sin reentrenamiento*, separando limitación tecnológica de fracaso de aprendizaje.
- **PER_LINK04**: donación a cada vecino con coste0,04 sin reducirlo al aumentar k; potencia de k−1 regalos, pero coste máximo0,04(k−1). Se evalúa como contrafactual con pesos congelados para identificar sensibilidad del supuesto de coste.

Ambos controles usan las mismas funciones de cobertura, recompensa y voluntariedad, modificando exclusivamente capacidad y coste de producción. No son experimentos de reaprendizaje para estas tecnologías; así se reportará.

## Evaluación fuera de muestra y controles

Seis semillas ambientales reservadas `999201,999207,999209,999221,999231,999237` para cada checkpoint final. Veinticuatro mundos por semilla para condición inicial MONOLITH y RANDOM, en tres tecnologías ELASTIC/FIXED3/PER_LINK04. Los mismos mundos evalúan cada actor profesional congelado frente a los baselines ocupacionales FIXED, RANDOM_SWITCH_0.15, RANDOM_SWITCH_0.35, RANDOM_SWITCH_0.60, y al ORACLE_ROLES que fija los k oficios distintos según posiciones, manteniendo el donante entrenado correspondiente.

Indicadores: tasa de equipos con k profesiones al final, cobertura media de profesiones recibidas, cobertura total de k−1 bienes, alimentación media, tasa de regalos realizados, cambios de profesión, pérdida relativa frente a benchmark oracular y ventaja de alimentación respecto al mejor de los tres controles de movilidad aleatoria. Se guardan resultados por semilla ambiental y tecnología y por inicio; se calculan intervalos descriptivos de variación entre las dos semillas de entrenamiento sin tratarlas como muestra representativa.

## Resultados preregistrados

H54a: en condición ELASTIC/LOLA20, desde MONOLITH, ≥6/8 valores de k alcanzarán fracción media de equipos completos≥0,80 en las dos semillas ocupacionales, con comida≥0,65.

H54b: al menos para uno de k≥8, en ELASTIC/LOLA20 desde MONOLITH, la fracción de equipos completos será <0,80 en al menos una semilla, señalando una frontera de aprendizaje bajo presupuesto constante.

H54c: en ELASTIC/LOLA20, la ventaja alimentaria frente al mejor cambio de roles aleatorio será≥+0,10 para al menos 6/8 k en ambas semillas.

H54d: en ELASTIC/NL la comida no superará0,30 para todos los valores k y semillas, aun si se diferencian ocupaciones.

H54e: en FIXED3, cuando k≥5, la fracción de personas que recibe los k−1 tipos distintos no puede superar 3/(k−1); cualquier violación de esa cota de conservación sería un **bug de contabilidad**. No se supone que todos los individuos pierdan la cobertura: algunos sí pueden conseguir la cesta completa, a expensas de otros.

No ajustar estos umbrales después de observar resultados. Una prueba positiva demostraría escalabilidad **condicionada a la forma externa de equipos cliques, tecnología de capacidad creciente y reciprocidad preentrenada**; no probaría nacimiento desde cero de las donaciones ni elección endógena de k.

## Próximo problema si se observa generalización

Permitir que k mismo sea una variable elegida por los agentes, introduciendo coste de mantener una profesión, límites productivos reales y libre elección de vínculos. La frontera empírica observada orientará ese diseño, en vez de fijar un valor de k porque tenga buen resultado a posteriori.
