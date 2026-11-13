# V42 — Sombra del futuro: factibilidad material de reciprocidad sin contratos

**Preregistro teórico-experimental 13/11/2026, previo a las simulaciones V42.** Se formula tras el fallo V41 (ocho entrenamientos, 1000 actualizaciones, donaciones cercanas a cero y retorno causal privado ≈−0,04 para todos los agentes). No presupone que los actores de V41 aprendan un mecanismo que no aprendieron.

## Pregunta

**RQ42. ¿La desaparición de cooperación unilateral refleja una imposibilidad estratégica del juego material o una dificultad para aprender estrategias contingentes de reciprocidad?** La versión mínima se estudia en una pareja aislada de participantes con oficios complementarios dentro de una población de48 personas, bajo las mismas recompensas V25, sin contratos ni transferencias garantizadas.

## Juego y contraste mecánico

El juego contiene b=0,20 de subsistencia, una contribución por persona hacia su compañero y valor v=0,55/3 de recibir exactamente una categoría profesional complementaria, sin premio adicional por cobertura completa. Cada donante paga c∈{0,04,0,12}. Dos participantes del mismo par actúan simultáneamente y pueden dar o no dar; no existe liquidación condicional que ejecute o rechace sus actos.

Se construyen 24 parejas disjuntas (i, i XOR 1) en N48; el reparto ocupacional balanceado 0,1,2,3 garantiza especialidades distintas dentro de cada pareja. El motor original `v25_multi_capacity.step_multi` verificará comida cooperativa por ronda (b+v-c), comida del desertor inmediata (b+v), pérdida del receptor (v), y ausencia de efectos a terceros. No se cambia ninguna fórmula alimentaria.

## Repetición y horizonte incierto

Se prueba como **oráculo explícito, no como conducta aprendida**, una estrategia de cooperación condicional *grim trigger*: ambos participantes dan en todas las rondas mientras ninguno haya incumplido antes; después de una deserción ambos dejan de dar en períodos posteriores. La respuesta al incumplimiento no está programada en el entorno V41; se introduce únicamente como estrategia contrafactual para estudiar posibilidad de un equilibrio.

Con probabilidad de continuación exógena q∈{0,15; 0,20; 0,25; 0,40; 0,50; 0,60; 0,75; 0,80; 0,95; 0,98} y descuento `gamma=0,995`, el factor efectivo es `beta=gamma*q`. La diferencia del retorno descontado de seguir cooperando frente a desertar una sola vez, dado que la otra persona sigue la norma, es:

`Delta = (beta*v - c)/(1 - beta)`.

Por tanto, la cooperación es individualmente sostenible para cada persona en la pareja cuando `beta*v >= c`; para los dos costes calcularemos `q_crit = c/(gamma*v)`. El juego no presupone recompensa grupal, pero presupone que **ambas personas saben y aplican el desencadenante de sanción**, condición aún no aprendida espontáneamente por nuestras redes.

## Simulación y pruebas

Monte Carlo determinista por semilla con al menos 200.000 duraciones geométricas independientes por cada par (c,q). Se cuantifica media, desviación estándar y error estándar de la diferencia del retorno, y se comprueba que la expresión analítica cae dentro del intervalo descriptivo 4×SE respecto a la simulación. Pruebas de ambos lados del umbral; en particular q=0,20/0,25 al coste0,04 y q=0,60/0,75 al coste0,12 deben cambiar de signo.

Se registra también el caso q=0 con vida de una sola ronda y preferencia privada estricta por desertar, como control negativo. **No confundir** el modelo geométrico de duración desconocida con nuestro simulador actual de 48 rondas cuyo momento final es observable por las redes (`t/horizon`). La inducción regresiva de un juego repetido *finito y conocido con único equilibrio no cooperativo de etapa* se aplicaría al subsistema diádico racional, no queda demostrada para la compleja economía de cuatro oficios y redes neuronales.

## Hipótesis

H42a: el motor material coincide con los pagos analíticos por unidad y el beneficio marginal de desertar exactamente c en la primera ronda.

H42b: la condición de sostenibilidad de la norma diádica responde al umbral `q_crit` en ambos costes, con los cambios de signo preregistrados.

H42c: la media Monte Carlo coincide con el valor de la derivación dentro de cuatro errores estándar en todos los puntos del diseño.

H42d: existe un conjunto de duraciones inciertas que hace rentable privadamente cooperar **en la pareja y bajo la norma dada** a cada coste, incluso cuando no existe contrato de ejecución simultánea.

## Interpretación y límites

Una norma contrafactual que es un equilibrio bajo supervisión perfecta y sanción coordinada **no es una institución emergente aprendida**. V42 únicamente prueba factibilidad estructural. En caso favorable, justifica un V43 que entrene redes privadas bajo duración incierta, tiempo oculto y memoria de contrapartes, manteniendo como control las mismas redes con horizonte conocido. Ese entrenamiento será el falsador relevante del origen endógeno de reciprocidad.
