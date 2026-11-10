# V8 — Rediseñar el problema de coordinación antes de entrenar más

**Fecha:** 10/11/2026. Diagnóstico postexperimental exploratorio. No es un protocolo preregistrado anterior a los experimentos que aquí se describen. La hipótesis de aprendizaje colectivo sigue abierta y no existe un resultado confirmatorio.

## 1. Problema formal que debemos conservar

Sea una sociedad de N agentes sobre una red local de grado cinco. Cada uno selecciona una etiqueta c_i en {0,...,9}; k está en {2,3,4} para el entrenamiento principal. La condición objetiva es que *exactamente k etiquetas cualesquiera* estén ocupadas y cada una reúna N/k individuos. No se imponen las etiquetas vencedoras. El agente puede decidir individualmente; su recompensa de resultado es igual a la de todos sus compañeros.

Sea p_(j) la frecuencia del j-ésimo color más ocupado. Entonces

D_k = 1 - Σ_{j=1}^k min(p_(j), 1/k).

Para k divisor de N, D_k=0 equivale al éxito exacto. La métrica no se sustituirá por la mera cercanía de cada una de las diez etiquetas a 10%, porque eso legitimaría el azar uniforme.

### 1.1. El objetivo contiene DOS regímenes distintos

Identidad algebraica:

D_k = [1 - Σ_{j=1}^k p_(j)] + Σ_{j=1}^k max(p_(j)-1/k,0).

Llamaremos **fuga** a la masa de población fuera de los k estados más frecuentes y **sobrecarga** a la masa que supera la cuota de 1/k dentro de esos k estados.

La fuga exige que se reduzcan los estados sobrantes; la sobrecarga exige que la concentración no se transforme en monocultura. Cerca de la distribución inicial uniforme entre diez colores, generalmente domina la fuga: ninguno de los colores predominantes ha superado todavía la cuota. El algoritmo necesita descubrir una dinámica de concentración y, más adelante, una dinámica de compensación de cuotas. Un único signo escalar D no revela cuál de esos problemas afronta cada individuo. Esta descomposición es SOLO una métrica de auditoría, no una entrada censal a la política ni una recompensa individual.

## 2. Problema de información: dos mundos indistinguibles

Considérese N=36, k=2, un agente en estado 0 y sus cinco vecinos también en 0. Las sociedades siguientes pueden tener ese mismo entorno local:

* Mundo A: n_0=17, n_1=19, n_2...n_9=0.
* Mundo B: n_0=19, n_1=17, n_2...n_9=0.

En ambas D_2=1/36. Si el agente pasa de 0 a 1, en A empeora (D_2=2/36) y en B mejora (D_2=0). Mismo estado, vecindario y observación global escalar D; acción óptima local opuesta. La ambigüedad de observación instantánea es matemática, aunque memoria, comunicación o experimentación secuencial pueden reducirla. No constituye una prueba de imposibilidad de la cooperación.

## 3. Diagnóstico de la simultaneidad

\`information_bottleneck.py\` genera 1.500 mundos aleatorios por cada (N,k), con N=36,144,324; k=2,3,4. En cada mundo escoge *exclusivamente para la auditoría* un individuo fuera de los k grupos predominantes y un estado predominante bajo cuota. Esa modificación individual tendría un beneficio medible si fuese la única alteración. A continuación hace que otros m-1 agentes efectúen reasignaciones aleatorias simultáneas y calcula:

* Perturbación pública: N(D_antes - D_después).
* Señal causal focal OFFLINE: N(D_sin_focal - D_con_focal).
* Ruido: N(D_antes - D_sin_focal).
* Cociente diagnóstico: media(señal causal focal)/desviación típica(ruido).

Este cociente NO es una estimación directa de la varianza del gradiente REINFORCE. Ni el agente ni su optimizador reciben el contrafactual, que existe SOLO para la auditoría. Valores cercanos a cero indican que el efecto promedio de esa modificación resulta pequeño respecto a la variabilidad de las demás reasignaciones aleatorias.

Para N=324 y k=4 el cociente cae aproximadamente de 1,404 (m=2) a 0,371 (m=16), 0,165 (m=64), 0,092 (m=128) y cerca de cero (m=324). Este dato hace razonable comparar activación serial y simultánea como intervenciones metodológicas distintas; no demuestra por sí mismo por qué fracasó V6.

## 4. Control de solubilidad con feedback público, NO aprendido

\`feedback_controller.py\` propone colores al azar. En cada microturno, un conjunto de m individuos puede probar una asignación. Tras observar la diferencia de D colectiva, se adopta la modificación entera si mejora D y se revierte en caso contrario. Todos conocen el mismo indicador; nadie necesita consultar un histograma completo. **La regla de aceptar mejoras está programada**. Constituye una política de referencia o un límite alcanzable, no una estrategia social aprendida por una neurona.

Con N=324, k=4, 40 sociedades y 25 propuestas por individuo:

| Propuestas concurrentes | D final medio | Exactos |
| --- | ---: | ---: |
| 1 | 0,0027 | 18/40 |
| 4 | 0,0788 | 0/40 |
| 324 | 0,5023 | 0/40 |

Los grupos concurren con el mismo número de propuestas por agente, pero NO con el mismo número de observaciones de feedback por propuesta. Este aspecto es precisamente parte de la diferencia de protocolo y es una limitación para atribuir la mejora solo a la simultaneidad.

Para un mundo no resuelto y N divisible por k existe alguna mutación individual que reduce estrictamente D: si alguna de las k cuotas está por debajo del tope, debe haber población en los colores sobrantes o por encima de otra cuota, y mover una unidad desde ese exceso a la cuota deficitaria incrementa la masa cubierta. Una búsqueda serial aleatoria con rechazo de empeoramientos puede, por tanto, mejorar por escalones sin un selector explícito de colores ganadores. Con tiempo finito la convergencia exacta no es segura.

## 5. Prueba neuronal mínima: aceptar o revertir después de un ensayo

\`learn_acceptance.py\` implementa N políticas logísticas independientes, cada una con parámetros (w_i,b_i). El *entorno* ofrece una propuesta de estado aleatoria y comunica públicamente el cambio PROVISIONAL de D antes de confirmar la decisión. El agente activo elige aceptar o revertir mediante una Bernoulli cuya probabilidad depende del feedback provisional. La recompensa real después de aceptar o no es exclusivamente la diferencia global N(D_antes - D_después), idéntica para todos. La actualización REINFORCE afecta solo a la política de quien ha podido actuar.

Hay una diferencia epistemológica crucial: cuando solo uno actúa, el feedback global le permite identificar su propia contribución. No estamos solucionando el problema del crédito individual sin información; lo estamos haciendo tratable al organizar temporalmente la acción social. La propuesta es aleatoria y **no se aprende**, de modo que esto es una microtarea sobre inferir qué decisiones conviene ratificar, NO una prueba de negociación aprendida, aprendizaje de selección de estados ni cooperación plenamente emergente.

### Sensibilidad exploratoria al parámetro de aprendizaje

Entrenamiento por semilla: 324 agentes, entrenamiento solo con k=4; 48 mundos por episodio, 60 episodios de dos ciclos de activación individual, learning rate 0,5; evaluación con políticas congeladas en 64 sociedades nuevas y 40 ciclos individuales. Tres semillas distintas. Este parámetro se escogió DESPUÉS de inspeccionar un ensayo inicial a learning rate 0,04, por lo que las comparaciones son exploratorias y no un test confirmatorio. El piloto con 0,04 redujo D_4 aproximadamente de 0,535 a 0,51; 0,5 lo redujo alrededor de 0,05. Con 0,5 las probabilidades medias de ratificar una mejora de una unidad fueron aproximadamente 0,944, frente a 0,031 para ratificar un empeoramiento de una unidad.

| Repetición | Sin entrenar D_4 | Entrenado D_4 | Exactos entrenados |
| --- | ---: | ---: | ---: |
| 0 | 0,5379 | 0,0534 | 0/64 |
| 1 | 0,5372 | 0,0510 | 0/64 |
| 2 | 0,5345 | 0,0541 | 0/64 |

No es correcto concluir que el problema original haya quedado resuelto. Se cambió su protocolo de decisión: experimentación reversible, feedback después de la propuesta y antes de aceptarla, activación serial. El conocimiento de la recompensa provisional puede simplificar mucho la tarea, de forma deliberada y transparente.

## 6. Propuesta científica para V9

**Objetivo principal conservado:** elegir k estados entre diez, cuotas iguales y estabilidad, sin etiquetas ganadoras impuestas; pesos individuales y recompensa de equipo idéntica. La métrica exacta D_ k sigue siendo la variable de éxito. No convertir una mejora de D en «cooperación aprendida» sin comparaciones con azar y control sin mensajes.

**Ablación de la formulación:** protocolo original irreversible (elección, acción, después feedback), protocolo con revisión de la propia acción solo en el turno siguiente y protocolo con prueba reversible (versión microtarea). Comparar estas condiciones como tareas **distintas**, sin presentarlas como la misma realización.

**Ablación de simultaneidad:** 1, 4, 16, todos los agentes actuando por fase. Informar tanto el número de propuestas como el número de actualizaciones y mensajes globales de feedback; evitar que las comparaciones a presupuesto idéntico en propuestas se describan como igualación exacta de información temporal.

**Ablación neuronal:** mantener pesos de cada agente realmente independientes. Arquitectura de tipo GRU con un estado interno por color y memoria explícita del estado propio previo, acción pasada, feedback anterior, localización de contactos y mensajes. Tres cabezas: elegir propuesta, elegir destinatario/contenido de mensaje y decidir ratificación o conservación. Comparar con memoria de un turno y con puerta no recurrente. Una representación equivariante respecto al renombrado de estados reduce el riesgo de memorizar preferencias arbitrarias por etiquetas.

**Ablación comunicativa:** C1 sin mensajes y C2 con mensajes cuyos destinatarios y contenidos son elegidos por los agentes. La información sobre colores de otros barrios no debe difundirse sin una comunicación efectiva. Congelar pesos y bloquear mensajes en evaluación solo mide dependencia; el contraste causal preferente requiere dos tratamientos entrenados con la misma capacidad de cambiar por sí mismos.

**Generalización:** para N divisible por k, entrenar con k=2,3,4 y evaluar sin ajustes con otros k. También cambiar semilla inicial, perturbaciones, orden de intervención, localización y topología. Evitar memorización de posiciones y colores mediante aleatorización apropiada. Medir capacidad de recuperación después de desestabilizar un reparto, no solo el estado final.

**Métricas:** D total; fuga fuera de los k grupos dominantes; exceso sobre cupos; número de colores ocupados; exactos; tiempo hasta alcanzar D=0; porcentaje de tiempo en equilibrio, churn y capacidad de reparación. La recompensa será siempre idéntica para toda la sociedad. Una modificación de potencial y un bonus terminal se deben justificar frente a las propiedades del objetivo: para potencial \u03a6(s), la forma descontada canónica es \u03b3\u03a6(s')-\u03a6(s), no automáticamente \u03a6(s')-\u03a6(s) cuando \u03b3 es distinto de 1.

**Secuencia empírica:** primero demostrar el funcionamiento en N=36 y varias semillas de aprendizaje; segundo comparar descripciones de información y capacidad con controles claros; tercero comprobar N=144/324. No lanzar 1.000.000 episodios por el mero hecho de que el código sea capaz de ejecutarlos. La escalada debe responder a un piloto con evidencia favorable.

## 7. Qué significaría grokking

No basta observar una mejora lenta tras muchos episodios. En el sentido clásico de Power et al., el grokking supone una separación medible entre ajuste inicial al entrenamiento y generalización tardía en datos no vistos. Si el proyecto mantiene esa hipótesis, habrá que separar explícitamente cohortes o situaciones de entrenamiento y pruebas de generalización, registrar su trayectoria y analizar si existe un salto temporal reproducible después de un periodo de sobreajuste. Ninguno de los resultados V8 hasta ahora satisface estos criterios.

## 8. Bibliografía utilizada para el rediseño

- Nguyen et al., *Multi-agent deep reinforcement learning: a survey*, Artificial Intelligence Review. https://link.springer.com/article/10.1007/s10462-021-09996-w
- Zhao y Xie (2025), *Multi-level Advantage Credit Assignment for Cooperative Multi-Agent Reinforcement Learning*, AISTATS. https://proceedings.mlr.press/v258/zhao25c.html
- Liang et al. (2025), *Asynchronous Credit Assignment for Multi-Agent Reinforcement Learning*, IJCAI. https://ijcai.org/proceedings/2025/20
- Xu et al. (2023), *Consensus Learning for Cooperative Multi-Agent Reinforcement Learning*, AAAI. https://ojs.aaai.org/index.php/AAAI/article/view/26385
- Ng, Harada y Russell, *Policy invariance under reward transformations*, ICML 1999. https://wordpress.andrewng.org/index.php/publication/policy-invariance-under-reward-transformations-theory-and-application-to-reward-shaping/
- Power et al., *Grokking: Generalization Beyond Overfitting on Small Algorithmic Datasets*. https://arxiv.org/abs/2201.02177
