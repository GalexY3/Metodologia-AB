# V2-RL — Evaluación reservada de transferencia y necesidad de colaboración

Fijado el 10/11/2026 **después del desarrollo** y **antes del primer test reservado**.

**Checkpoints fijos:** V2-B crédito=0 y crédito=2, ambos seed221, actualización180. La elección NO depende del test. Se usaron 2160 sociedades de entrenamiento por tratamiento (12×180), horizonte de entrenamiento 24 pasos. El test se ejecutará con parámetros congelados.

**N36:** k2,k3,k4, semillas de entornos independientes de desarrollo e inicializaciones de entrenamiento, 96 sociedades paralelas por k/condición, horizonte 90 turnos. Comparar política crédito2 probabilística, política crédito0 probabilística, versión determinista de crédito2, aleatoria sin aprendizaje, y quedarse inmóvil. Intervenciones adversariales sobre la misma política crédito2: desactivar los mensajes de todos salvo un único emisor, eliminar el snapshot del emisor dejando solo el color pedido, y ocultar el feedback global anterior al actor en tiempo de ejecución (el entrenador ya no está activo). Mismos estados iniciales por k y condición.

**N120:** misma política entrenada exclusivamente en N36, sin actualización de parámetros, en cuadrícula 10×12, k2,k3,k4, 60 sociedades por condición, horizonte 90, condiciones: crédito2 probabilística, crédito0 probabilística, aleatoria e inmóvil. Es una prueba de cambio del tamaño y topología, NO de extrapolación a k>4.

**Métricas:** D global (variación total respecto a cuotas), D al último paso, promedio de diez últimas rondas, mejor D alcanzada, porcentaje que llegó alguna vez a D≤.06, porcentaje que terminó en D≤.06, proporción con diez rondas seguidas de D≤.06 y churn≤.05, proporción de sociedades en D=0 exacto al final, churn, mensajes y solicitudes recibidas. Ninguna de esas métricas es idéntica a la precisión de clasificación de un modelo neuronal.

**Cautelas:** un solo entrenamiento por tratamiento. 96 o 60 entornos test no son réplicas de entrenamiento independiente. Los tests de ablation cambian los canales de información o emisores sin reentrenar: un fracaso puede deberse a cambio de distribución de observaciones, no a necesidad causal universal del mensaje. Un emisor con ≤5 vecinos no puede corregir un exceso inicial de ~16 de color mayoritario en N36,k4 bajo el protocolo de peticiones, demostrando necesidad estructural de múltiples emisores para el reparto perfecto en ese entorno.

Los resultados de desarrollo ya inspeccionados no se usarán para modificar checkpoints, recompensas, horizonte ni umbral de estabilidad. Los tests se sellan con SHA256 de modelos y pesos antes de ejecutarse, y sus archivos de resultados no se sobrescribirán si ya existen.
