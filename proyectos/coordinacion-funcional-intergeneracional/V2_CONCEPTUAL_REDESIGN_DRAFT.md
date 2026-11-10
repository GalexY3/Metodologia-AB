# V2 — Rediseño conceptual pendiente de confirmación

**Fecha:** 10/11/2026. **Estado:** propuesta conceptual, **NO IMPLEMENTADA**, **NO EVALUADA**. Este documento recoge la rectificación explícita del usuario a la arquitectura P0–G1. Los experimentos anteriores no contestan directamente la nueva pregunta: usaban anillo grado4, emparejamientos con máximo una comunicación recibida por turno, cambio de color propio, recompensa de rareza local. **Conservar P0–G1 como pilotos diferentes; no trasladar sus estimaciones como resultados de V2.**

## 1. Especificación literal de la interacción deseada

Cada agente tiene exactamente un color/rol en 1..k. Su percepción directa en el inicio de cada turno incluye **su propio color** y **los colores de todos sus vecinos**. Cada agente puede elegir **un vecino como destinatario de un mensaje saliente** con una copia de toda esa información local, y solicitarle que adopte cierto color. Cada agente puede recibir cero, una o varias peticiones de vecinos en el mismo turno, independientemente de si envió su propio mensaje. Puede obedecer o rechazar. Después de las decisiones simultáneas se observa una señal de **progreso colectivo respecto al turno anterior** (no un premio exclusivamente por alcanzar el objetivo exacto), susceptible de guiar el aprendizaje de sus estrategias.

No sustituir la estructura anterior por un matching uno-a-uno. Cada agente debe tener **máximo un mensaje saliente, pero cualquier número de entrantes** hasta su grado. Permitir silencio o mensaje sin petición como acciones de control, sujeto a decisión del usuario. Por defecto NO se cambian colores unilateralmente, solo cuando se acepta una solicitud; si se permite cambio voluntario, introducirlo como condición experimental separada.

## 2. Topología recomendada para "5 vecinos salvo bordes"

Red geométrica rectangular **10×12**, N=120, adyacencia von Neumann de hasta cuatro contactos más **una arista diagonal disjunta por nodo**: cada bloque no solapado 2×2 aporta dos diagonales emparejadas (esquinas opuestas). Con ello todos los agentes estrictamente interiores tienen 5 vecinos, los bordes menos, y el grafo es no dirigido. No usar torus, que elimina el contraste de borde que el usuario imaginó. Registrar coordenadas, aristas, distancias, centralidad y sesgo de frontera. Baselines de otra topología solo más adelante. La agrupación principal significa cobertura numérica 1/k de los roles, NO formación de cúmulos espaciales contiguos; la segunda propiedad sería otro objetivo a definir.

## 3. Secuencia síncrona del turno (sin fuga de información)

A. Snapshot de colores y grafo al inicio t. Ningún agente conoce los contajes globales, salvo un **escálar de feedback colectivo** recibido de la ronda anterior durante entrenamiento.

B. Observación local o_i(t): propio color, colores de sus 3–5 vecinos, peticiones recibidas anteriormente, memoria acotada, número k y feedback de resultado anterior. Si mensajes incluyen el vector de colores de vecinos del remitente, permiten acceso a observaciones **de segundo salto** después de llegar; no atribuir a los agentes conocimiento directo de segundo salto antes del mensaje.

C. Emisión: cada agente escoge **0 o 1** vecino destinatario, color solicitado c∈1..k y adjunta su snapshot local (colores/ids de vecinos directos) más petición. El mensaje de t se construye con información de t y se entrega antes de la decisión receptora.

D. Recepción: los mensajes entrantes se reciben TODOS, 0..grado(i), con sus peticiones y snapshots. Receptor puede **mantener su color o aceptar exactamente una petición** y adoptar el color solicitado. En caso de varias peticiones diferentes escoge la que acepta; nunca cambia a dos colores. Un agente también puede recibir peticiones aunque haya enviado una. El conjunto de destinatarios de mensajes no se restringe mediante matching.

E. Actualización simultánea de TODOS los colores. Ningún agente decide con los nuevos colores de vecinos del mismo turno; evita cascadas instantáneas artificiales.

F. El simulador (evaluador) calcula n_c(t+1), distancia global D(t+1), cambio respecto a t y disemina solo el feedback escalar acordado durante entrenamiento. Nunca entrega n_c al actor.

G. Cada agente registra sus acciones, mensajes recibidos, decisión, feedback y memoria; se actualizan parámetros de aprendizaje según método fijado. La señal de la ronda t+1 guía la evaluación de acciones de t, con crédito ambiguo entre agentes.

## 4. Objetivo y recompensa densa

Para N agentes y k funciones, n_c(t)=cantidad de agentes de color c. Definir
  D(t)=1/2 Σ_c |n_c(t)/N − 1/k|.
D∈[D_min,1−1/k] (si N múltiplo de k, D_min=0); si N no es múltiplo de k, mínimo discreto con floor(N/k)/ceil(N/k), no exigir proporciones fraccionarias imposibles.

Feedback incremental base sugerido:
  r_progress(t)=N·[D(t)−D(t+1)].
Escalado por N para que una corrección de 1 individuo tenga efecto computacional visible. Premia mejoras, penaliza empeoramientos, vale 0 si no hay cambio. **No** convierte en binario «perfecto/imperfecto». Se reporta también D absoluta y la tasa de cambios, pero NO se revela necesariamente D ni n_c al agente como observación (opción experimental a comparar).

IMPORTANTE: recompensa común de equipo ≠ mérito causal individual. N cambios simultáneos pueden interferir y la señal global es ruidosa para el agente; un valor cero puede esconder avances compensados. Es un problema conocido de *credit assignment*. Baselines y potencial-based shaping, actor-critic con entrenamiento centralizado y ejecución descentralizada, o recompensas contrafactuales como variantes, no como propiedades gratuitas de la configuración.

No usar r_progress como si preservara automáticamente la política óptima bajo γ<1: reward shaping formal con potencial Φ=−D exige F=γΦ(s_{t+1})−Φ(s_t). Probar penalización pequeña por churn después de un piloto, pero evitar que la política de quedarse quieto se imponga desde el inicio. Medir éxito sostenido y no solo máximo momentáneo.

## 5. Aprendizaje y memoria

**Memoria principal inicial:** ventana explícita W=4 rondas (incluido último feedback, snapshots de vecinos, propuestas/solicitudes y decisiones). Es interpretable, usa pocos recursos y permite advertir cambios sin acumular información obsoleta. **Ablaciones predefinidas:** W=1, W=4, W=8 y resumen recurrente con estado de capacidad fija (GRU), sin asumir cuál aprende mejor. Conservar toda la historia sin límite no es opción principal: crece con t y se desactualiza tras cambios de función, relaciones y generaciones. Separar claramente memoria episódica de interacciones y memoria procedural/paramétrica θ aprendida.

Política compartida neuronal entrenable para todos los agentes, con estados de memoria personales separados; compartir pesos es una simplificación de ingeniería para aprender con más señales, **no** telepatía entre agentes. Los actores de ejecución solo acceden a o_i y mensajes. En una variante usar políticas por agente para contrastar. Dos decisiones por turno: (i) petición saliente (destinatario, color), (ii) aceptación de una petición entrante o rechazo. Para k variable se necesita puntuación compartida por candidato de color, no salida fija limitada a colores vistos; diseño permutación-equivariante para evitar privilegiar identidades de color. Evitar introducir la heurística exacta «elige color menos frecuente» dentro de la política. Baseline de esa heurística está permitido solo como control explícitamente diseñado.

Durante **entrenamiento** podemos distribuir el escalar global de progreso a todos o usar un crítico central que conoce D y produce gradientes para actores locales (CTDE), especificando la asimetría. Durante **test**, congelar θ y decidir si retirar feedback al actor; se debe evitar que el test continúe optimizando por gradientes si se pretende evaluar transferencia ya adquirida.

## 6. Orden de tareas

Comenzar con k=2 para verificar señales y convenciones; luego entrenar sobre k=2,3,4 con mismas reglas e hiperparámetros. k=1 es control trivial y no debe contar como aprendizaje. k=5 queda como **primer test realmente fuera de rango**; k=6..8 son estrés extrapolativo. Elegir en train/val semillas distintas de inicialización y emparejamientos. **No usar k=5 para ajustar hiperparámetros** si luego se reclama generalización virgen a k=5.

Entrenar desde desbalance severo (p.ej. 70% color0) y evaluar contra permanecer sin cambiar, solicitar aleatoriamente, aceptar siempre, aceptar nunca, políticas aleatorias coordinadas por misma señal de aprendizaje, y regla manual de rareza local como benchmark, **sin atribuir emergencia al benchmark**.

Una ronda puede mostrar mejora temporal por azar; exigir curva D(t), áreas de desequilibrio, estabilidad sostenida, cambios, diversidad de contacto, tasa de mensajes, rechazos y conflictos entre peticiones. Una vez que el agente realmente alcanza equilibrio en k≤4, recién entonces estudiar progresión k>4 y el relevo generacional. Evitar «100% acierto» como único indicador.

## 7. Dos preguntas que exigen definición del usuario

- **¿Agrupar correctamente** quiere decir únicamente reparto equilibrado por roles (aproximadamente N/k), o también que cada color forme regiones conectadas o grupos espaciales? Son objetivos distintos y pueden entrar en tensión.
- **¿Recibir la recompensa global cada ronda** significa un marcador público idéntico para todos o solamente feedback del entrenador que no es observable como dato de decisión? El marcador público cumple la petición, pero crea un canal de información global; ambas son comparables y deben declararse.

## 8. Consecuencia para el trabajo anterior

Archivar P0,P1,P2,G0,G1 como **modelos diferentes** sin borrarlos; hay resultados válidos *para sus propias reglas*, pero no representan esta nueva especificación de comunicación dirigida. No reetiquetar resultados previos como evidencia de V2. **No ejecutar un nuevo simulador hasta que el diseño de mensajes y la recompensa sean definidos.** V2_CONCEPTUAL_REDESIGN_DRAFT.md es documento de discusión y no preregistro irrevocable.
