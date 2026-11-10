# V5 — Memoria temporal y capacidad de cálculo individual

Estudio registrado antes del entrenamiento completo en [PREREG_V5.md](PREREG_V5.md). Ampliación de V4: diez estados disponibles y objetivo de seleccionar exactamente k=2,3,4 a cuotas iguales.

## Diseño

Se cruzan memoria de un turno (W1) y memoria de ocho turnos (W8), con redes H64 y H128, dos capas ocultas. Cada individuo conserva pesos y gradientes propios. Las etiquetas de estado son equivarientes dentro de cada actor. Los mensajes y observaciones de vecinos solo se incorporan si fueron visibles para el actor. No se revela el censo de colores.

El modelo W8 es un MLP con ventana temporal explícita, no una GRU/LSTM ni un mecanismo de planificación simbólica. «Capacidad de razonamiento» significa aquí procesamiento no lineal más amplio; requiere prueba para saber si representa alguna estrategia.

Archivos: agents_memory.py, train_v5.py, evaluate_v5.py, test_memory.py. Se conserva la recompensa global original de V4 r=−D−0,03·churn para aislar arquitectura. Solo comunicación C2 en el piloto.

Cuatro experimentos de 150 actualizaciones, batch12, episodio32 turnos, seed521. Evaluación reservada de los cuatro modelos más modelos sin entrenar y azar, con 100 mundos nuevos por k y horizonte100. No seleccionar checkpoints ni ajustar con datos test.

Los checkpoints se guardan en runs/W{memory}_H{width}_C2_seed521_u150/. El éxito inicial exigiría replicación sobre semillas diferentes; la ejecución de tests no es evidencia de cooperación.