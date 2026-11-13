# Enmienda técnica V43 — Independencia de la aleatoriedad de supervivencia

Fecha 13/11/2026. Introducida durante entrenamiento y **antes de las evaluaciones congeladas finales**. Preregistro original y commit fuente del entrenamiento: `5594763d83da6be7d46783e4b7e785fa8b1b390b`. No se modifican las hipótesis, costes, probabilidades, muestras ni modelos.

La primera implementación del rollout V43 sortea la continuación de un mundo HAZARD con `torch.rand(c.batch)` utilizando el generador aleatorio global. Si la política de donación o el control de profesión consumen cantidades diferentes de números aleatorios, se desplaza la secuencia de sorteos de supervivencia de turnos posteriores. Eso **no sesga necesariamente las ganancias marginales esperadas**, pero dificulta el emparejamiento experimental perfecto de condiciones.

Antes de las evaluaciones congeladas se agregó un argumento **opcional** `survival_generator=None` a `v43_random_horizon.roll`. La ruta por defecto mantiene el generador global y, por tanto, la semántica y distribución usadas por los ocho procesos de entrenamiento ya iniciados. Los evaluadores nuevos proporcionarán un generador de supervivencia con semilla ambiental específica y separada, compartido entre condiciones y controles, para que la duración no dependa de cuánto azar consume la política.

Los ocho entrenamientos V43 continúan con el código Python ya cargado al iniciarse y con sus checkpoints originales; **no se han detenido ni reiniciado**. En el análisis se identificarán por separado el código original de entrenamiento del commit anterior y la versión ampliada de evaluación. La enmienda no modifica los pagos físicos ni añade recompensa, contrato o profesor. Se conservarán los tests de paridad determinista V25/V41 y la comprobación de que los mundos terminados no generan recompensa ni gradiente.

Los resultados deben distinguir evaluación condicional a semillas ambientales y políticas neuronales congeladas, sin tratar los mundos como nuevas inicializaciones independientes.
