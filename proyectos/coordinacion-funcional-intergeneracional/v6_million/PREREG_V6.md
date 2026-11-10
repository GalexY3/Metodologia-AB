# V6 — Protocolo previo al entrenamiento científico de un millón de episodios

Fecha: 10/11/2026. Las nueve sociedades usadas en el test técnico smoke1 no forman parte del entrenamiento científico. Los parámetros principales se fijan antes de la primera ejecución principal.

## Problema

144 agentes con políticas distintas, conectados a una malla toroidal 12×12 de grado exactamente cinco, compuesta por cuatro enlaces ortogonales y un emparejamiento diagonal perfecto. Es una topología cinco-regular, pero no se presenta como un verdadero teselado geométrico snub-square. Cada agente puede seleccionar cualquiera de 10 colores, con objetivo público k=2,3,4. El éxito requiere exactamente k colores ocupados, cada uno con N/k agentes. No se fijan los colores vencedores.

Cada agente tiene pesos propios, 64 neuronas ocultas por red, y libertad de cambiar voluntariamente de estado. Puede enviar silencio o una solicitud a uno de cinco vecinos, eligiendo el color solicitado entre diez. El mensaje transmite además la distribución de colores observada por el emisor entre sus vecinos. Solo el receptor seleccionado puede conocer ese contenido. Un agente puede recibir muchas solicitudes en un turno y no está obligado a aceptarlas.

Las observaciones son estado propio, colores vecinos, memoria local EMA de experiencias anteriores, sus propias decisiones pasadas, mensajes recibidos y feedback GLOBAL idéntico a todos. No se proporciona censo total, contribución contrafactual individual, pesos de otros agentes ni heurísticas programadas de consenso. La memoria exponencial no constituye planificación interna ni razonamiento simbólico.

## Métrica y señal de aprendizaje

D_k=1−Σ_{j=1}^{k}min(p_(j),1/k), donde p_(j) son las frecuencias de los k estados más frecuentes entre diez. D=0 exige cuotas exactas cuando N es divisible por k.

Recompensa por turno para la SOCIEDAD completa, idéntica para TODOS sus agentes:
r_t=N·[D_k(t)−D_k(t+1)]+0,25·[1−D_k(t+1)].

Al último turno se añade 2·[1−D_k(T)]. No se penaliza el cambio individual ni se premian directamente obediencia o imitación. La recompensa combina progreso y proximidad global, con término terminal también colectivo.

Entrenamiento mediante REINFORCE con retornos gamma=.99, baseline leave-one-world-out calculado entre SOCIEDADES con el mismo k, normalización estadística entre sociedades, grad clip por agente=5 y AdamW lr=.0007. Entropía inicial .0015 con reducción progresiva hasta el 20% al finalizar el presupuesto. Los gradientes de cada individuo actualizan exclusivamente sus pesos. No se emplea crítico con acceso al mundo ni pesos compartidos.

## Presupuesto y evaluación

144 agentes, batch=48 sociedades, horizonte16, hidden64, semilla6123, dispositivo CUDA cuando exista. Objetivo mínimo 1.000.000 episodios, redondeado a 20.834 actualizaciones y 1.000.032 episodios de sociedad. Equivale a 16.000.512 turnos de sociedad, y a aproximadamente 2.304 millones de interacciones individuales por acción; son tres acciones por individuo y turno (destinatario, solicitud, color propio).

Cada actualización tiene seed derivada del índice, para reanudar sin recomenzar. Se guarda latest.pt con pesos y estado AdamW cada 100 actualizaciones; métricas de entrenamiento cada20 y desarrollo independiente cada200. El desarrollo usa seed82000 y 64 turnos, pesos congelados. Estos resultados se pueden consultar durante entrenamiento y no justifican selección de checkpoints por mejor rendimiento.

HOLDOUT SELLADO: solo tras alcanzar el presupuesto, seed847202611+100k, 100 sociedades nuevas por k, 96 turnos. Brazos predefinidos: política entrenada estocástica, política entrenada greedy, política entrenada sin mensajes, red sin entrenar, aleatorio continuo y aleatorio con parada al turno24. Informar D final y temporal, estados ocupados, exactos, churn, estabilidad durante los últimos diez turnos con D≤.02 y churn≤.05, exactos y estables. Congelar hashes de modelo y código antes de abrir test, sin reutilizarlo para escoger checkpoints. Un único seed de entrenamiento implica que las 100 sociedades por tratamiento NO son replicaciones independientes de aprendizaje.

Un millón de episodios es un presupuesto solicitado, NO una promesa de lograr equilibrio. La duración real depende de GPU y coste de simulación. Cualquier modificación de arquitectura, recompensa o acceso a información debe registrarse como una versión distinta y contrastarse con controles.


## Enmienda preexperimental final: elección N=324 (10/11/2026)

**Esta enmienda prevalece sobre las referencias iniciales a N=144 de este protocolo.** Las dos pruebas piloto smoke1 y bench_gpu con 144/324 agentes y pocos episodios se usaron exclusivamente para verificar código y rendimiento. No se consultaron resultados científicos para seleccionar la población. El usuario solicitó ampliar significativamente la red, y 324 supera la mayor muestra de 240 agentes ensayada antes. Se fija la corrida principal de un millón con **malla toroidal de 18×18=324 agentes**; diez estados; k2,3,4; batch48; horizonte16; hidden64; seed6123; recompensa, entrenamiento y validación exactamente como se describen arriba. Cada individuo mantiene pesos propios; NO se compartirán políticas.

La meta de un millón se redondea a 20.834 actualizaciones, 1.000.032 episodios completos y 16.000.512 turnos de sociedad, multiplicados por 324 agentes. El código permite otras poblaciones de lado múltiplo de seis, siempre como NUEVOS experimentos en otro directorio. La población 324 y los hiperparámetros elegidos quedan fijados antes de entrenar el modelo principal. Los tests reservados siguen teniendo 100 sociedades nuevas por condición y k y 96 turnos, evaluados solo después de cumplir el presupuesto.
