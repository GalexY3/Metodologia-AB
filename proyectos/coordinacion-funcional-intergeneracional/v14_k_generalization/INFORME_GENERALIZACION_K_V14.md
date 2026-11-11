# V14 — Generalización neuronal a un número solicitado de profesiones

**Estado:** resultados exploratorios. Cada métrica cuantitativa procede de un JSON de evaluación con un checkpoint neuronal congelado. Los experimentos de seguimiento y el currículo se decidieron tras consultar resultados de desarrollo; los valores nuevos de k no formaron parte del gradiente, pero NO constituyen un holdout confirmatorio sellado.

## 1. Objetivo

La pregunta es si redes neuronales de agentes diferentes aprenden una regla adaptable al encargo explícito de formar exactamente **k** profesiones cualesquiera, con tamaño N/k cada una, en vez de limitarse a una tendencia fija a concentrar a sus vecinos. N=120, M variable, grafo circular de ocho vecinos por agente. No se estudia MHU ni se afirma cooperación causal en esta fase.

La recompensa de un individuo en profesión j de n_j trabajadores es r_i=min(n_j/(N/k),(N/k)/n_j), sin función auxiliar de recompensa colectiva, sin global Dk como input, sin conteo global de profesiones y sin supervisor central. Los 120 agentes tienen **225 parámetros privados cada uno**, en total 27000. Una red neuronal puntuadora de 12 características y 16 unidades ocultas evalúa todas las profesiones con los mismos pesos DENTRO del agente; los pesos son independientes ENTRE agentes. Se conserva memoria EMA de las ocupaciones entre los vecinos. La profesión propia y la recompensa son visibles. No hay mensajes en V14.

## 2. Configuración y tratamientos

| Brazo | Objetivo k visible | k en las actualizaciones | M de entrenamiento | Actualizaciones |
|---|---|---|---|---:|
| k visible, 1400 | sí | 2, 3, 4, 6 | 12, 24 | 1400 |
| k oculto, 1400 | no | 2, 3, 4, 6 | 12, 24 | 1400 |
| currículo hasta 15, 3000 | sí | 2, 3, 4, 6, 10, 15 | 12, 24 | 3000 |
| rango ampliado, 3500 | sí | 2, 3, 4, 6, 10, 15, 24, 30 | 12, 40 | 3500 |

Entrenamiento con REINFORCE y baseline por agente a través de 16 sociedades paralelas; horizonte de 24 turnos, lr=0,009, γ=0,97 y entropía=0,003. Una sola semilla de inicialización por brazo. La variante currículo empieza desde el checkpoint de 1400 actualizaciones de k visible, con su estado de optimizador; **no es una segunda semilla independiente**. La condición «rango ampliado» empieza desde cero, si está presente.

La arquitectura ve el valor de k solo en los canales habilitados de la política, incluyendo proporción 1/k y frecuencia de vecinos multiplicada por k. El control «k oculto» conserva EXACTAMENTE los 225 parámetros y recibe ceros en dichos canales; conoce el resultado de sus propias acciones porque su recompensa personal depende de la cuota.

## 3. Evaluación congelada con objetivos conocidos y nuevos, según el brazo

Las evaluaciones principales usan 3 nuevas semillas de mundo, 48 sociedades paralelas por semilla y 80 turnos, **144 sociedades por condición**. No se entrena en estos mundos. Las políticas se prueban también frente a elección aleatoria e imitación local. Un k puede estar excluido del entrenamiento en unos brazos e incluido en otros; consultar las listas de k del apartado 2. M=80 nunca se utilizó en el entrenamiento.

| k solicitado (M=80) | Visible inicial | Control sin k | Currículo hasta 15 | Rango amplio | Azar |
|---:|---:|---:|---:|---:|---:|
| 5 | 0.737 | 0.731 | 0.733 | 0.755 | 0.104 |
| 8 | 0.671 | 0.730 | 0.709 | 0.732 | 0.167 |
| 10 | 0.624 | 0.704 | 0.678 | 0.714 | 0.209 |
| 12 | 0.580 | 0.669 | 0.642 | 0.699 | 0.250 |
| 15 | 0.505 | 0.588 | 0.599 | 0.663 | 0.313 |
| 20 | 0.377 | 0.468 | 0.530 | 0.621 | 0.415 |
| 24 | 0.303 | 0.422 | 0.493 | 0.600 | 0.491 |
| 30 | 0.239 | 0.391 | 0.441 | 0.566 | 0.586 |

En estas evaluaciones la cuota perfecta no se alcanzó sistemáticamente; consultar el campo exact de cada JSON. Un valor de alimento alto NO significa que la población se dividiera en exactamente k profesiones ni que cada una contuviera la cuota requerida.

## 4. Alcance de la generalización

Los modelos con entrenamiento hasta k=6 generalizan parcialmente su capacidad de obtener alimento a valores superiores de k, pero en k=20,24,30 pueden empeorar respecto al azar. El currículo con k=10,15 ofrece una mejora en objetivos altos y sigue sin lograr repartos exactos en objetivos novedosos. La inferencia central de la batería es que las políticas aprenden una heurística distributiva, **sin acreditación todavía de una política universal condicionada por k**.

El control que nunca observa k alcanza o supera a la política informada en numerosas condiciones del entrenamiento inicial. El actor entrenado desde cero sobre más valores de k supera al control en más casos, pero tuvo más actualizaciones y otros objetivos de entrenamiento; no se identifica por separado el efecto causal de conocer k.

## 5. Ablación de la instrucción k con pesos congelados

| k (M=80) | Señal k presente | Señal k anulada | Delta |
|---:|---:|---:|---:|
| 5 | 0.734 | 0.756 | -0.022 |
| 8 | 0.713 | 0.760 | -0.046 |
| 10 | 0.686 | 0.752 | -0.067 |
| 12 | 0.649 | 0.721 | -0.072 |
| 15 | 0.599 | 0.687 | -0.088 |
| 20 | 0.533 | 0.640 | -0.107 |
| 24 | 0.502 | 0.609 | -0.108 |
| 30 | 0.439 | 0.569 | -0.131 |

La ablación mantiene pesos idénticos pero pone los canales k a cero durante el test. Es una **intervención fuera de distribución** y puede incluir efectos de desplazamiento de la distribución de entradas; por sí sola no identifica causalidad del beneficio de conocer k. Se incluye por separado el control con los mismos canales enmascarados DESDE EL ENTRENAMIENTO. En el modelo del currículo ampliado, eliminar los canales k del actor congelado mejoró frecuentemente la comida, señal de que todavía no se aprovecha de forma funcional esa instrucción.

## 6. Los casos k que no dividen N

El motor de entrenamiento original exige N divisible por k para que cada grupo tenga exactamente N/k trabajadores. Para explorar k=7,9,11,13,14,16,17,19,21,22,23,25,27,29 se relajó únicamente la validación de divisibilidad EN EVALUACIÓN, conservando la función individual original. El reparto viable de referencia usa tamaños piso(N/k) y techo(N/k); la distancia D no puede ser cero en todos esos escenarios.

| k (M=80) | Modelo currículo | Azar | Alimento de reparto entero equilibrado |
|---:|---:|---:|---:|
| 7 | 0.710 | 0.145 | 0.986 |
| 9 | 0.699 | 0.186 | 0.967 |
| 11 | 0.660 | 0.227 | 0.985 |
| 13 | 0.633 | 0.269 | 0.962 |
| 17 | 0.571 | 0.351 | 0.984 |
| 19 | 0.547 | 0.392 | 0.933 |
| 23 | 0.501 | 0.469 | 0.936 |
| 29 | 0.444 | 0.568 | 0.943 |

Es un test de extensibilidad del mecanismo de recompensa, no una afirmación de que la red resuelva perfectamente cualquier k.

## 7. Qué exigiría considerar resuelto el problema

La métrica principal futura debería ser la fracción de mundos con exactamente k grupos ocupados y cuotas factibles; criterio secundario, comida normalizada por el óptimo entero, estabilidad temporal y rapidez para adaptarse a un k nuevo. Es esencial demostrar que variar únicamente k en un mismo estado induce decisiones útiles y distintas. Un aprendizaje que maximiza comida promedio sin respetar el número solicitado no satisface el encargo.

Para el siguiente prototipo se recomienda mejorar el condicionamiento de objetivo (escala logarítmica/multiplicativa, redes con más memoria, separación entre cambio de profesión y elección de destino), ampliar el currículo, y comparar con una regla individual heurística de igual información y presupuesto, sin añadir global counts a escondidas.

No hay todavía demostración de cooperación fuerte ni de grokking; no se han efectuado múltiples semillas independientes del mismo brazo. Una buena simulación aislada del visor no valida generalización estadística.

## 8. Archivos de reproducción

- train_k.py: política neuronal y entrenamiento con señal k opcional.
- test_v14.py: cuatro tests de independencia de pesos, variación de acción ante k, cuotas y entrenamiento.
- evaluate_k.py y nondivisible_k.py: pruebas con pesos congelados y cuotas fraccionarias.
- ablate_k.py: intervención intra-checkpoint de visibilidad de k.
- runs/: checkpoints, estados de optimizador y configuración de los experimentos.
- evaluations/: métricas granulares por semilla, incluida la condición objetivo oculta.
- compare_k.py, COMPARACION_K.csv y este informe: tablas derivadas de esos registros.
- make_k_panel.py y PANEL_K_UNIVERSAL.html: reproducción autónoma de sociedades reales para varios k y tres o más políticas.

**Ningún resultado que falte de un archivo JSON se debe afirmar como ejecutado.**