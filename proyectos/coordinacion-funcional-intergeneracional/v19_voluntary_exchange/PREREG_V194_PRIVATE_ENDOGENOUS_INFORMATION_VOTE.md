# PREREG V194 — Aprendizaje PRIVADO de votos y adopción del régimen informativo

2026-11-15. Registrado antes de entrenar V194. Línea adicional tras V193/V193B (información correlacionada afecta al consenso pero sus votantes eran programados). Prioridad científica: falsar si una población con **políticas individualmente aprendidas y heterogeneidad de pérdidas** alcanza el régimen de información conveniente sin recibir una instrucción para seguir la señal. Se hacen afirmaciones expresamente **exploratorias**: los juegos de jurado con información correlacionada, adquisición endógena y feedback privado tienen antecedentes principales. Revisados Basak, Deb & Kuvalekar (AER 2026, doi:10.1257/aer.20241056), Condorcet con votos correlacionados (JEBO 1995, doi:10.1016/0167-2681(94)00068-P) y Voting with endogenous information acquisition (Games and Economic Behavior 2017, https://www.sciencedirect.com/science/article/pii/S0899825617300064). No reivindicar la relación pública/privada ni Q-learning como descubrimientos.

## Entorno y decisiones
32 mundos ×20 grupos de votación por mundo, dos cohortes independientes de 16 mundos cada una, m=k−1 votantes con k∈{4,8,12}; equipos de votantes fijos (NO endógenos), cada votante i con pérdida privada Li∈{1,7} sorteada al crear mundo, conocida solo por su propio Q. Estado bueno/malo independiente por reunión Pr(GOOD)=.6; en GOOD acuerdo aprobado produce +1 por persona; en BAD produce −Li por persona. NO acuerdo produce cero. Un canal público tiene coste privado .02 por persona por reunión (se pague o no acuerdo). Un informe independiente gratis. Calidad marginal de toda señal .8 en ambos estados. El entorno muestrea una señal distinta por elector; si se elige público, todos ven el informe del primero, mismo estado y exactitud. Todas las decisiones de cada elector tienen acceso solo a propia señal y a canal adoptado, **jamás al estado GOOD/BAD**, informes ajenos, pérdidas ajenas o gradientes colectivos.

La adopción de PUBLIC se decide mediante mayoría simple de votos individuales previos al informe (m impar). Esas papeletas provienen de Q privada sobre {INDEPENDENT,PUBLIC}, sin observaciones del estado actual. Tras recibir señal, cada elector elige YES/NO mediante su Q privada dependiente del canal y señal. Regla de ratificación del proyecto UNANIMITY o MAJORITY fijada por el experimentador. Por tanto la adopción del canal es aprendida en el protocolo, **pero no son creados el sistema de voto, el mecanismo de sanción ni la estructura de grupos**. Una sola ronda por estado, 8000 períodos de aprendizaje; sin persistencia material intertemporal ni especialización de oficios.

## Algoritmo
Q privada por agente sobre 2 acciones de canal y 2 acciones de voto en cada {canal, señal}. No parámetros compartidos ni central critic. Recompensa de update es exclusivamente utilidad material realizada por ese elector, sin contrafactuales. Actualización de bandido q(a) <- q(a)+alpha*(r−q(a)); alpha=.10. Selección epsilon-greedy inicial .30 que decae lineal a .08 a 6000 períodos; evaluación congelada epsilon=0 (con aleatorización minúscula de empates). Q inicial igual al valor 0 para ambos actos, empate aleatorio. Cada agente tiene Q independientes; algoritmos de selección y de actualización son definidos y no se adaptarán después de examinar el resultado.

## Familias
A. ADAPTIVE_PRIVATE: Q privada aprende canal (voto adopción) y voto para aprobar el acuerdo. Canal adopta por mayoría.
B. FIXED_INDEPENDENT_PRIVATE: señal independiente siempre; Q privada aprende votos.
C. FIXED_PUBLIC_PRIVATE: señal pública siempre; Q privada aprende votos.
D. RANDOM_CHANNEL_PRIVATE: adopción del canal uniforme independiente del estado, Q privada solo aprende votos (control sin aprendizaje de institución).
E. SIGNAL_FOLLOW_INDEPENDENT y SIGNAL_FOLLOW_PUBLIC: conducta diseñada votar según señal; NO aprendizaje (referencias clásicas).
F. PERFECT_STATE_ORACLE: votantes coordinados con estado verdadero y pérdidas totales; cota tecnológica externa (NO modelo de agentes).

Cada familia compite con mismas semillas ambientales por (k,regla); la señal pública del primer votante comparte su uniforme con primera señal individual. Ningún brazo recibe verdad durante política, excepto oráculo externo. No entrenar oráculo.

## Factorial / hipótesis
Tres k × dos reglas {UNANIMITY, MAJORITY}, 32 mundos ×20 grupos ×8000 entrenamientos y 2000 evaluaciones NUEVAS de estado por mundo. En cada grupo Li∈{1,7} de manera independiente e irrevocable; reportar distribución de composición y efectos. Un estimando primario exploratorio es diferencia de utilidad media de evaluador privado ADAPTIVE versus el mejor brazo FIXED_PUB/FIXED_IND elegido por welfare medio de cohorte (selección ex post es un benchmark superior y se indicará, no un p pre-registrado). Comparar también contra señal-follow fija y oracle. Evaluación también tasa de canal público, tasa de voto, aprobación correcta/errónea, desigualdad entre tipos Li, subgrupos adaptados, bienestar final, cambios durante entrenamiento.

Predicciones falsables:
1. ADAPTIVE a diferencia de las familias fijas debe mostrar adopción PUBLIC no trivial (en al menos un caso entre 10 y 90%; de lo contrario posible colapso de representación).
2. Bajo mayoría k=12, SIGNAL_FOLLOW_INDEPENDENT supera SIGNAL_FOLLOW_PUBLIC en valor material por la agregación independiente; verificar contra valor binomial exacto con L promedio, no declarar novedad.
3. Bajo unanimidad k=12 y L medio esperado≈4, SIGNAL_FOLLOW_PUBLIC supera SIGNAL_FOLLOW_INDEPENDENT en media, pero bajo k=4 es inferior; verificar fórmulas conocidas.
4. Aprendizaje privado ADAPTIVE puede fallar frente a FIXED: registrar ambos signos, intervalos y composición; no optimizar desde evaluación.
5. Si PRIVATE aprende estrategias triviales de aprobación/rechazo por no pivotalidad y abandona la información, reportarlo como problema de crédito individual, sin atribuir que “no quieren cooperar”.

## Integridad
Dos generadores RNG separados por arm para acciones y para entorno, con reinicio exacto de semilla ambiental entre brazos y de semilla nueva de evaluación. Unidad de remuestreo: mundo, n=32; 20 equipos y 2000 episodios por mundo NO cuentan independientes. Bootstrap pareado10k mundos para diferencias; diferencias de tipos por individuos son descriptivas salvo estimando correctamente agrupado. Motor vectorizado más referencia escalar enumerada para 500 perfiles aleatorios de resultado, incentivo y protocolo de canal; proteger de dependencia entre resultados. Ninguna afirmación de generalización a k no entrenado ni a humanos.

Condiciones de cierre: guardar código, hashes, datos de los mundos, predicciones comparadas, Q, verificaciones, errores, teoría, límites y todos los resultados negativos. **N2=0,N3=0 y CT2=61** hasta evidencia nueva de originalidad externa. Evitar usar el resultado como sustitución del problema principal de cooperación material, grupos endógenos y profesiones aprendidas. Si fracasa, escoger siguiente hipótesis por causalidad novedosa, no más Q semillas de este juguete.
