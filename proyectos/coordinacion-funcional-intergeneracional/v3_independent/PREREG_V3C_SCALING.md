# V3C — Tamaño de sociedad, capacidad individual y entrenamiento prolongado

**Registrado el 10/11/2026, DESPUÉS de los resultados negativos de V3B-120 y V3B-600, ANTES de entrenar V3C.** Esto es exploración metodológica prospectiva, no confirmación retrospectiva. Ninguna condición utiliza crédito individual, crítico global, pesos compartidos entre agentes ni reglas codificadas de reparto.

## Objetivo experimental
Verificar si el fracaso de REINFORCE independiente con recompensa compartida proviene de una sociedad demasiado pequeña, de una red neuronal poco expresiva o de insuficientes generaciones de entrenamiento. Mantener el mismo mecanismo de red geométrica con interiores grado5, emisión de ≤1 mensaje por agente/tick, recepción múltiple, elección voluntaria de color incluso sin mensajes, feedback escalar común `r_t=N(D_t−D_{t+1})`, memoria W1, cambio síncrono y scorer equivariante por color dentro de cada política individual θ_i.

## Matriz fijada

Seed de entrenamiento **411** en todos los brazos de la primera cohorte, pesos iniciales apareados entre C1/C2 de igual N,hidden. Los mundos independientes usan generador distinto por update. El conjunto de k incluye k2,3,4 en partes iguales por minibatch (4 mundos cada uno), con 70% de un color mayoritario elegido aleatoriamente en cada mundo.

| Condición | N | Rejilla | Hidden | Actualizaciones | Episodios por brazo | Rondas de interacción en entrenamiento |
|---|---:|---|---:|---:|---:|---:|
| Tamaño pequeño-capacidad alta | 36 | 6×6 | 64 | 2000 | 24000 | 576000 |
| Tamaño medio-capacidad original | 120 | 10×12 | 24 | 1500 | 18000 | 432000 |
| Tamaño medio-capacidad alta | 120 | 10×12 | 64 | 2000 | 24000 | 576000 |
| Tamaño grande-capacidad alta | 240 | 12×20 | 64 | 1000 | 12000 | 288000 |

Cada fila comprende dos brazos C1 sin mensajes y C2 con mensajes, ocho entrenamientos. No elegir la mejor por resultados de desarrollo. Presupuesto elevado sujeto a límites computacionales reales: **reportar por separado cualquier corrida incompleta**, con la actualización alcanzada, y NO comparar su checkpoint parcial como si fuera el final de la matriz.

Todos: batch12 mundos, steps24 por episodio, Adam lr .002, gamma .99, entropy .003, advantage_scale10, norma grad L2 clip10 por individuo y leave-one-out dentro del mismo k. Mayor hidden significa mayor capacidad funcional de cada θ_i, no cambio de información. N mayor significa más políticas individuales, no copiar 36 cerebros para simular 240. El número de agentes aumenta el coste y la dificultad de atribución del crédito.

## Evaluación prefijada
Los checkpoints finales solo se evaluarán DESPUÉS de su entrenamiento y bloqueo SHA256 de código/modelo. Semillas de mundos nuevas que no coincidan con entrenamiento/desarrollo, mínimo 40 sociedades por k y brazo, horizonte120 turnos. Medir D final, media últimos10, D/E[D_IID(N,k)] exacta, equilibrio sostenido diez turnos con D≤0,06 y churn≤0,05, churn, D=0 exacto, ratio de peticiones y coincidencias, AUC y curvas desde 0. El umbral fijo D≤0,06 NO es comparable entre tamaños; D/E[D_IID] y distancias absolutas son métricas primarias para esa comparación.

Se deberán comparar C1 vs C2, también C2 en test sin mensajes C3, aleatorio permanente y aleatorio T24→parar, además de inmóvil. Usar mismas condiciones físicas de inicio por fila y k. Los tres tamaños no equivalen a replicaciones independientes de política: primero comparar condicionalmente a seed411; si hay señal favorable, repetir semillas diferentes y evaluar robustez. Una política con D menor pero churn alto NO se considera estabilidad colectiva aprendida.

## Hipótesis y riesgos
No asumir que N mayor mejora. El global r tiene crédito más difuso cuando N aumenta. No presuponer que hidden64 es mejor que hidden24 ni que 2000 updates suficientes. Si las redes mantienen acciones cercanas a uniformes, documentar explícitamente posible fracaso de credit assignment. Información de más turnos/memoria W4 es una intervención posterior y no forma parte de esta matriz. No reinterpretar resultados como aprendizaje de jerarquías o consenso social humano.
