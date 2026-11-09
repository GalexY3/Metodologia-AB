# Exploración V4 — factibilidad de dos historias con competencia igualada

2026-11-09. Diseño posterior al protocolo V3; **exploratorio y separado del experimento confirmatorio**.

Se construyó una tarea mixta de suma modular (p=31) y una segunda rama con etiquetas aleatorias fijas. Entradas: dos operandos y una etiqueta explícita de contexto. Misma arquitectura (embedding + capa oculta ReLU de 300 unidades + clasificación de 31 salidas), misma partición de entrenamiento, validación y test, para todas las condiciones.

Existen 961 pares de suma modular y 640 pares de la segunda rama, con 55% train y 20% valid en cada rama. La fracción limpiamente generalizable es 961/1601≈60%; la rama aleatoria aporta una precisión casual de 1/31 en validación. Por tanto, el techo **esperado**, no matemáticamente exacto en el test finito, es ≈61%. La fracción no es el objetivo original del investigador, que dejó libre el umbral: es una prueba de factibilidad de mesetas parciales causada por una tarea con información irrecuperable.

**Advertencia crítica:** este escenario NO equivale por sí mismo al semigrokking intrínseco de Varma et al., donde una sola operación modular presenta coexistencia de circuitos memorísticos y generalizadores. Un 61% causado por el techo de Bayes de una mezcla de dos tareas no demuestra semigrokking clásico. Puede ser un control instrumental para analizar historia de generalización, pero un resultado sobre ese montaje no debe generalizarse a semigrokking intrínseco sin un segundo experimento.

Se varía weight decay manteniendo semillas y datos, después se probarían historias de entrenamiento con cambios de regularización/schedules. La hipótesis A requiere memorizar primero y mejorar tarde hasta la meseta parcial; B debe adquirir la misma capacidad progresivamente en paralelo al entrenamiento y mantener la meseta. Si ambas siguen retraso postmemorización, el par se **rechaza**. Registro completo de train/valid/test durante esta exploración significa que **el conjunto test aquí no es un test sellado confirmatorio**. En una réplica confirmatoria, se bloqueará la lectura del test final antes de congelar criterios.

Hay una hipótesis rival fuerte: la regularización y el estado del optimizador pueden causar directamente las diferencias de resistencia o recuperación, independientemente de la historia grokking. Se requiere diseño factorial y controles, y separar resiente vs recuperación.
