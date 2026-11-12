# V28 — Una restricción estratégica adicional: el horizonte finito y la inducción hacia atrás

Nota teórica del 12/11/2026. Se refiere a las variantes V19–V26, donde una donación voluntaria genera un beneficio material inmediato para el receptor y un coste exclusivo para el donante, y no existe consecuencia o activo transferible después del último turno de cada trayectoria.

## Formulación del juego de etapa

En cada ronda, para cada actor i, la recompensa propia contiene los beneficios derivados de los bienes de distintas profesiones que el individuo **recibe** desde otros y menos el coste positivo c>0 por cada unidad que **envía**. Las decisiones de donación de todos los agentes se realizan en una misma fase de juego, sin posibilidad de observar el resultado de una donación ajena tomada contemporáneamente antes de escoger la propia. Por tanto, fijadas las acciones simultáneas de los demás, emitir una unidad adicional de regalo reduce la recompensa **inmediata** propia exactamente en c. Los receptores sí obtienen bienes nuevos cuando la unidad es útil, pero su beneficio no se retribuye al donante dentro de la misma decisión de la etapa. La función `step` y la función `step_multi` comparten este hecho; está verificado con intervención inicial emparejada por individuo.

Una acción de movilidad ocupacional también cuesta 0,015 por cambio y, si nadie ofrece bienes, no incrementa inmediatamente la comida propia. La utilidad de un cambio reside en permitir que otros le entreguen distintos bienes más adelante. Esto hace que las ventajas ocupacionales estén subordinadas a la posibilidad de intercambio.

## Proposición

**Supuestos:** horizonte fijo y finito T conocido por todos; maximización estricta de suma de recompensas individuales descontadas, sin preferencias altruistas; las contribuciones se deciden simultáneamente; cualquier regalo emitido cuesta c>0 sin generar bienes para su remitente en esa misma ronda; no existen transferencias, sanciones, reputación vendible ni valor terminal después de T; los agentes son suficientemente racionales y comparten conocimiento del juego para aplicar inducción hacia atrás. Los actores no pueden comprometer acciones futuras fuera de la secuencia de decisiones del simulador.

**Resultado:** el juego contiene una trayectoria de equilibrio perfecto en subjuegos con cero contribuciones en todas las rondas. Si además todo cambio de profesión es costoso y no produce utilidad propia sin transferencias, el estado de no donación ni movilidad es la única trayectoria de equilibrio de etapa que se prolonga por inducción hacia atrás.

**Demostración:** en la última ronda T, una donación propia reduce la recompensa propia en c, con independencia de las contribuciones que los demás elijan en esa misma etapa. No existe futuro donde recibir reciprocidad. Por tanto, no donar es una respuesta estrictamente dominante respecto a donar, y no cambiar de oficio domina a cambiarlo si nadie dona. Conociendo esa conducta terminal, el turno T−1 tampoco permite modificar mediante una donación los bienes que recibirá el remitente en T−1, y tampoco permite conseguir favores en T: ningún agente donará en T. El razonamiento se repite inductivamente hasta el primer turno. Se obtiene una trayectoria de no intercambio a pesar de que existan asignaciones de donaciones que aumentarían el bienestar medio.

Esta proposición es una manifestación del problema de cooperación en juegos repetidos finitos y su resultado de inducción hacia atrás. No contradice que el aprendizaje por refuerzo incompleto, las heurísticas de reciprocidad, los límites cognitivos y las convenciones estables produzcan cooperación observable durante episodios finitos. En particular, los modelos V23 aprendieron contribuciones individualmente rentables respecto a contrafactuales propios dentro de la población de políticas congeladas, pero eso no equivale a probar que sus políticas conjuntas constituyan un equilibrio perfecto en subjuegos.

## Condición temporal de sostenibilidad

Si una acción de donación cuesta c>0 ahora y aumenta la probabilidad de obtener en el futuro recompensas materiales Δ_s positivas, la desigualdad necesaria para que sea individualmente conveniente mantenerla bajo la reacción esperada de sus compañeros es

c ≤ Σ_{s=1}^{T−t−1} γ^s Δ_s.

La derecha se reduce cuando se aproxima el final de la simulación. En el último turno es cero. El marco V23 utiliza γ=0,995 y T=48; las políticas observan una característica normalizada de tiempo, por lo que pueden aprender la proximidad del horizonte. La existencia de reciprocidad causal positiva en los primeros turnos no verifica por sí sola estabilidad hasta el final.

## Falsadores empíricos

Extraer de las políticas congeladas V23 y V25 los perfiles de tasa de donación por ronda, alimentación y recepción para las 48 rondas, evaluando seis semillas ambientales reservadas. Contrastar tasa media de los primeros ocho turnos con los últimos ocho, condicionando al mismo modelo y población. También evaluar la intervención forzada en el penúltimo o último turno para confirmar que su retorno privado no puede ser positivo en el horizonte cerrado: en el último turno debe ser exactamente −c por unidad.

No utilizar como falsador de la proposición la observación de contribuciones de un agente neuronal acotado. La proposición depende de racionalidad secuencial y expectativas comunes, no de que una política aproximada pueda alcanzar el equilibrio racional perfecto.

## Intervenciones futuras para quitar la barrera de finitud

Introducir una vida social de duración indefinida con terminación probabilística inesperada, de forma que el horizonte residual no sea completamente predecible, manteniendo el retorno propio como objetivo. Otra alternativa es introducir producción durable, reservas, reputación reutilizable entre generaciones o instituciones que aporten valor terminal. Cada cambio debe compararse frente al juego finito sin ocultar que modifica la estructura de incentivos; no es equivalente a subir el tamaño de red neuronal o la memoria.

El experimento V28 de perfil temporal es una auditoría diagnóstica de los modelos ya entrenados, no un nuevo entrenamiento y no puede por sí solo declarar OBJETIVO COMPLETADO.
