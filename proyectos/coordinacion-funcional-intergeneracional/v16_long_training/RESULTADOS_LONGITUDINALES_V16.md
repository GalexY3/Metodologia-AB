# V16 — Entrenamientos prolongados y búsqueda exploratoria de transiciones tardías

**11 de noviembre de 2026.** Los tres entrenamientos concluyeron y se conservaron los historiales de evaluaciones sucesivas, checkpoints y estados del optimizador. Se mantuvieron recompensas estrictamente individuales y redes privadas por agente. Los valores muestran media de comida de un conjunto de DESARROLLO repetido con 2 semillas de mundo y 24 mundos por semilla, no de un holdout confirmatorio final. No se produjeron visualizadores nuevos.

## Arquitecturas y presupuestos

| Experimento | Arquitectura | Rango actualizaciones | M/k de entrenamiento | Evaluaciones cronológicas |
|---|---|---|---|---:|
| v16_RNN24_L12000 | RNN 1.473 parámetros privados/agente | 2.400 a **12.000** | M24 y 80, dieciséis tareas | 25 |
| v16_MLP16_L8000 | MLP 857 parámetros privados/agente | 1.300 a **8.000** | M24 y 80, dieciséis tareas | 18 |
| v16_RNN16_BROAD_5000 | RNN 857 parámetros privados/agente | 0 a **5.000** | M12,24,40,80; 34 tareas, k=5/8/12 reservado | 14 |

RNN24 y MLP16 son CONTINUACIONES de checkpoints V15, con estado de Adam conservado y una tasa de aprendizaje modificada. La red BROAD es un entrenamiento nuevo. No son tres semillas equivalentes de un mismo tratamiento, y el uso de desarrollos mirados periódicamente introduce selección potencial.

## Generalización a k=12 con M=80 (valor k no entrenado en las tres variantes)

| Experimento | Primer checkpoint | Mejor checkpoint examinado | Último checkpoint |
|---|---|---|---|
| RNN24 hasta 12000 | 2.400: **0,6577** | 7.600: **0,7037** | 12.000: **0,6870** |
| MLP16 hasta 8000 | 1.300: **0,6761** | 5.600: **0,7173** | 8.000: **0,7036** |
| RNN16 currículo amplio | 0: **0,5124** | 4.400: **0,6772** | 5.000: **0,6738** |

La evolución es irregular. Los mejores valores de desarrollo no coinciden con el checkpoint final, por lo que prolongar el entrenamiento no garantiza un mejor estado. Esto hace necesario evaluar cada checkpoint en mundos no vistos y conservar los resultados, no seleccionar la última actualización a ciegas.

## Métricas finales

| Experimento | Comida conocida M24/k4 | Comida OOD M80/k12 | Comida OOD M40/k12 |
|---|---:|---:|---:|
| RNN24, 12000 | 0,6974 | 0,6870 | 0,6650 |
| MLP16, 8000 | 0,6840 | 0,7036 | 0,6703 |
| RNN16 amplio, 5000 | 0,6985 | 0,6738 | 0,6668 |

**Repartos exactos:** 0 en TODAS las 57 evaluaciones cronológicas consideradas, cada una con seis tareas de desarrollo y 48 sociedades por tarea. Los mundos evaluados se repiten entre checkpoints; no interpretar 57×6×48 como 16.416 observaciones estadísticamente independientes.

## ¿Ha aparecido grokking?

**No hay evidencia suficiente de grokking hasta 12.000 actualizaciones.** La definición original de Power et al. (2022) trata del desfase entre sobreajuste a entrenamiento y generalización tardía; aquí no se observó éxito exacto temprano ni transición posterior al éxito en k retenidos. Pequeñas ganancias con recaídas en alimentación OOD podrían ser aprendizaje gradual, oscilaciones estocásticas o una combinación, no prueba de grokking.

Un análisis serio debería fijar antes umbrales de éxito exacto en entrenamiento y test, introducir 5+ semillas independientes de inicialización para cada arquitectura y medir la contingencia causal de las decisiones respecto a k. Un rango efectivo decreciente de pesos no es condición matemática suficiente ni necesaria para declarar grokking.

## Diagnóstico adicional de Argon

Paralelamente se ha verificado el potencial exacto del juego, se han construido siete pruebas matemáticas y se han ejecutado 100 condiciones congeladas con cinco tratamientos de movilidad y sin modificar pesos del modelo V15. El dictamen correspondiente y los JSON están en DICTAMEN_ARGON_VALIDACION.md, argon_b1_b2.py y diagnostics/.

## Decisión metodológica

La prioridad siguiente no debería ser añadir decenas de miles de actualizaciones a ciegas al mismo agente. Primero hace falta una nueva arquitectura que permita aprender a **crear profesiones nuevas mediante movimientos complementarios** y que estime con incertidumbre la congestión a partir de datos auténticamente locales. Hay que evaluar por separado el efecto de cambiar observaciones, acción y recompensa, con métricas de reparto exacto y escapar de trampas desde 2×60 habitantes, y reservar un holdout sin inspección hasta el cierre.
