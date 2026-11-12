# V21b — Reputación y variación de topología: preinscripción

Fecha: 12-11-2026. El tratamiento experimental se define antes de lanzar los nuevos entrenamientos, con checkpoints V20 congelados como control.

**H4.** Entrenar las mismas redes privadas sobre una secuencia mixta de grafos circulares y reconectados producirá mayor retorno causal de donaciones en las pruebas con red reconectada que entrenarlas exclusivamente en la red circular, conservando costes, recompensa individual, inicializaciones y 600 actualizaciones.

Se ejecuta `v20_curriculum.py` (código de V20, sin rediseño) con `--schedule smooth --topology mixed`, cuatro semillas 3111, 4111, 5111 y 6111. Cada proceso recibe el mismo número de mundos, épocas y evaluaciones que su control V20 circular. La intervención cambia solo el grafo social de entrenamiento: ninguna política colectiva ni recompensa central.

Se contrasta alimentación con coste alto final 0,12, donaciones y efecto causal individual sobre las redes circular y reconectada. El criterio relevante es el censo de todos los agentes y la mejora sobre cada pareja de semillas. La ventaja media de alimentación no prueba reciprocidad, y una mejora en grafos reconectados puede reducir rendimiento en los circulares. Se reportarán ambas propiedades y los efectos negativos.

No se reoptimizarán tratamientos para los casos de evaluación reservados. Los experimentos longitudinales V21 previos siguen una campaña separada.
