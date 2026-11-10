# V3 — Cooperación entre agentes con aprendizajes estrictamente individuales

**Fecha:** 2026-11-10. **Estado:** protocolo de piloto, anterior a nuevos resultados de V3. Reemplaza V2 para la hipótesis principal según la corrección explícita del usuario. V2 se conserva como un **control distinto** de entrenamiento centralizado y pesos compartidos, no como demostración de cooperación entre aprendices individuales.

## Restricción de individualidad

En V3 hay N redes neuronales distintas, cada una con parámetros θ_i y momentos de Adam independientes. Cada red i se actualiza SOLO con log-probabilidades de las decisiones que tomó i, multiplicadas por la MISMA recompensa de equipo recibida por TODOS. No se copian pesos ni gradientes, no se entrena un crítico central con censo mundial, no hay conocimiento de las acciones de todos los agentes y no existe política compartida. Para ejecutar las N redes eficientemente sus matrices se apilan en un tensor, pero **NO se mezclan ni promedian parámetros entre i**; probar con gradientes que la salida de un agente depende solo de su bloque θ_i y no de otros bloques.

La única información exógena de coordinación es un único escalar de recompensa pública r_t=N[D(t)−D(t+1)], idéntico para todos. Para actualizar gradientes en el entrenador se puede restar una media de retornos por instante calculada sobre episodios paralelos y escalar por su desviación, pero NO se distribuye mérito ni diferencia contrafactual por individuo. La propia experiencia local y la recompensa común guían el aprendizaje.

**Observación permitida:** color propio, colores actuales de los vecinos directos (permitido explícitamente en especificación del usuario), parámetro público k y último feedback global. La información de segundo salto solo llega a través del mensaje dirigido permitido. No hay acceso a memoria interna ajena ni a θ_j. Para una variante más restrictiva en la que tampoco se ven colores vecinos sin mensaje, habría que diseñar una condición específica; no reinterpretar esta capacidad originalmente concedida.

## Protocolo del turno

Red geométrica cuadrada, cardinales + una diagonal por nodo en cada bloque 2×2; nodos interiores grado5 y fronterizos grado3/4.

Cada i puede emitir ≤1 mensaje hacia vecino j: copia del snapshot local de i y petición de color c. El receptor puede recibir de 0 a grado(j) mensajes, aunque ya haya enviado el suyo. Cada individuo toma una decisión sobre su estado: **mantenerse, adoptar voluntariamente cualquier color legal, o aceptar exactamente una petición entrante**. El mensaje saliente es una decisión independiente de la decisión sobre el propio color; puede enviarse incluso si se elige cambiar de color voluntariamente. Las nuevas etiquetas se aplican simultáneamente. Ningún actor accede al censo global. La opción voluntaria de cambiar se añadió el 10/11/2026 por rectificación expresa del usuario, antes de cualquier entrenamiento V3.

Al final solo el **evaluador** calcula la distancia TV global y comunica una recompensa común de progreso a todos. No hay recompensa terminal binaria ni feedback de cuánto aportó i. En test se congelan θ_i, pero cada agente puede actualizar la observación temporal del último feedback común.

## Piloto escalable y métricas

N=36, cuadrícula6×6, k2,3,4, prioridad primero comprobar k4, porque su equilibrio requiere asignaciones no triviales de nueve agentes por color. 70% inicia en un mismo color aleatorio según mundo. Pesos por agente persistentes entre episodios de entrenamiento; colores y turnos se reinician. Todas las decisiones de agentes están condicionadas por sus observaciones individuales y sus propios parámetros.

Algoritmo inicial: REINFORCE independiente de cada agente (gradiente de política basado en recompensa global), Adam, con baseline dependiente de la *posición temporal* y estimado mediante lotes de episodios, no de la identidad del actor. No introducir la recompensa marginal de V2. Gamma=.99, 24 pasos por episodio, batch de mundos paralelos. Probar cientos de actualizaciones, monitoreando D final, D mínimo, estabilidad en diez turnos, porcentaje de peticiones y de cambios. No prometer éxito: el aprendizaje cooperativo con señal común puede fallar por asignación difícil de crédito, y la prueba debe conservar el resultado negativo si lo hay.

Durante la evaluación no se permitirá ni una sola actualización de los pesos; k2..4 con semillas nuevas. Comprobar baseline uniforme aleatorio continuo (incluida elección voluntaria de color), aleatorio 24 rondas y luego detenerse, permanecer, y políticas sin canal de mensajes pero **con capacidad unilateral de cambio**. Estos dos aleatorios son controles DIFERENTES; el 0% de estabilidad del continuo depende de que siga actuando y no demuestra indispensabilidad del aprendizaje.

Un aumento de N requiere nuevos agentes θ_i o reglas declaradas de nacimiento/aprendizaje. NO se puede copiar una política única entrenada en N36 a N120 como hizo V2, pues eso traicionaría la independencia original. La prueba de traspaso intergeneracional debe preservar o reiniciar memorias/pesos individuales según condición experimental, con comunicación de conocimientos limitada a los mensajes permitidos.

## Límites e hipótesis

Un conjunto de individuos puede aprender estrategias complementarias o similares; no forzar heterogeneidad por diseño. Los mensajes **no son necesarios físicamente** para cambiar de color, pues hay cambio voluntario. Por ello, quitar los mensajes **sí permite una ablación relevante de cooperación**, sin quitar la capacidad de modificar el propio estado. Se compararán agentes independientes con peticiones y aceptación, con la misma política pero sin mensajes, y agentes que solo realizan cambios autónomos desde el comienzo de su entrenamiento. Conservar poder de cambio, presupuesto temporal, feedback global y semillas equivalentes para estas condiciones. El que todos reciban el mismo escalar global tampoco prueba que no puedan inferir quién contribuyó: pueden hacerlo estadísticamente a partir de experiencias repetidas, sin oráculo.

El estudio tiene validez en un sistema sintético. Aun si emerge coordinación, no demostraría automáticamente consenso cultural humano, grokking colectivo o ley matemática de convergencia universal. La función objetivo solo exige cuotas globales, no contigüidad espacial de los grupos.
