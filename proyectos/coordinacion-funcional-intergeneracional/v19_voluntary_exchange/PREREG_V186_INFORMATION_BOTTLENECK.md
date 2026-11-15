# V186 — Separar información perdida, tiempo y generalización del receptor

15/11/2026. Auditoría causal D1 del pilotoV185, cuyos resultados completos son conocidos: receptor con diccionario fijo memoriza en600actualizaciones y generaliza en13600/11600; testfinal97.91%/99.30%. Aprendizaje privado de comunicación no alcanza train99% y termina test27.35%/62.02%,con24/28símbolos. No se ejecutaron las congelaciones condicionales deV185 porque faltaba su condición previa. No son resultados perdidos.

## A–C. Hipótesis y antecedente

Un protocolo que confunde dos valores dea destruye información necesaria para sumar conb en todos los casos. Se calcularán techos Bayes exactos bajo cada soporte (train,test,completo), sin usar ese decodificador oráculo en el entrenamiento. El principio de información y los equilibrios de agrupación en juegos de señales son antecedentes clásicos, no teoremas nuevos propios. Pregunta causal: ¿basta reparar las colisiones del diccionario para que un receptor ya entrenado generalice, o basta dar más tiempo al aprendizaje conjunto?

## D–F. Intervenciones y criterio

Usar exactamente los dos checkpoints INDEPENDENT_COMM deV185 en30000, incluidos optimizadores, baseline y RNG. Tres continuaciones de30000actualizaciones adicionales por historia, todas hasta60000totales:

- CONTINUE_JOINT: mismo algoritmo privado deV185; controla tiempo y presupuesto.
- FROZEN_ORIGINAL: fijar el diccionario codicioso final del emisor; solo aprende receptor.
- BIJECTIVE_REPAIR: mantener al primer valor dea de cada símbolo original y reasignar los valores restantes, por orden creciente, a símbolos no utilizados, también por orden creciente. Solo aprende receptor. No usar etiquetas, test ni selección de una reparación favorable. Ambas condiciones con diccionario fijo son deterministas para igualar esa decisión.

La reparación es una intervención oráculo impuesta desde fuera, no un algoritmo de emergencia privada ni una institución aprendida. Los tres brazos comparten receptor y su estado deAdamW original al inicio; copiar estados para evitar contaminación entre brazos. Datos, arquitectura, objetivos y tasas permanecen congelados.

Primario prospectivo de suficiencia específica: BIJECTIVE_REPAIR testfinal>=.95 y ventaja>=.10 frente a CADA rival en AMBAS historias. Si CONTINUE_JOINT generaliza, duración sigue siendo una explicación suficiente en esa historia y falla este gate de ventaja específica. Si la reparación falla, no atribuir la limitación exclusivamente a colisiones. No cambiar a un checkpoint intermedio favorable. Mostrar las seis curvas y todos los techos, incluso si el gate falla. Son dos historias reutilizadas, no seis estudios independientes.

Antes de continuar, contrastar el núcleo de actualización conV185 mediante replay desde sus checkpoints25000 hasta30000. Verificar pesos, baseline, política codiciosa y precisiones contra archivos ya conocidos. Es auditoría técnica, no nueva confirmación científica. Registrar cualquier diferencia numérica y no ocultarla.

Diagnósticos posthoc del piloto: computar el mejor cambio unilateral de símbolo ante el receptor fijo y el techo de clasificación de entrenamiento para el diccionario actual. Un óptimo de clasificación restringido no es Nash en todo el espacio de políticas neuronales ni excluye intervenciones coordinadas. No reivindicar como novedosos el techo de capacidad, un juego de señales o la generalización con diccionario predefinido.

## G–J. Decisión y alcance

Registrar código y hashes en remoto antes de las continuaciones nuevas. ConservarV185intacto y todos los resultados del nuevo control de presupuesto. No declarar grokking colectivo si lo observado se explica por un receptor que generaliza con un código fijado; tampoco declarar imposibilidad a partir de dos semillas y un algoritmo. Una afirmación positiva colectiva requerirá más semillas independientes, congelaciones realmente informativas y comparación con antecedentes más cercanos.

Un workerGPU,doshilosCPU,BelowNormal,seisCPU. CT2histórico61 sin incremento, nueva rama sin puntuación, N2=N3=0. Objetivo global activo.
