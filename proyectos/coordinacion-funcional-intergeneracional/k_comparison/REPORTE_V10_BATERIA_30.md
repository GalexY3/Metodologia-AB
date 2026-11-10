# V10. Batería de microagentes de 41, 57 y 73 parámetros

Fecha 10/11/2026. Estudio exploratorio de aprendizaje descentralizado en aldea con diez profesiones. Todos los agentes tienen políticas independientes, y la misma política de cada agente puntúa simétricamente las diez opciones. Nadie recibe el óptimo de ocupación N/k, el censo global, Dk ni recompensas contrafácticas.

## La economía se conserva

El entorno es la versión de aldea anterior, con k=2 o k=4 profesiones óptimas entre diez alternativas, recompensa individual r_i=min(n_j/(N/k), (N/k)/n_j), donde n_j es el número de habitantes de la profesión de i. Todas las profesiones son equivalentes y cualquiera puede resultar elegida.

Las entradas de la red de 41 parámetros son la frecuencia de una profesión entre los vecinos, su frecuencia suavizada y si es la profesión propia. La red de 57 parámetros añade la alimentación propia y su variación; la de 73 también añade la alimentación media de la sociedad y su variación tras las acciones reales anteriores. En los tres casos **la recompensa sigue siendo 100 % individual**, sin shaping, sin bonificación por colaborar y sin señal contrafáctica marginal de Argon. No se utiliza comunicación aprendida: solo observación local, diferenciada de los mensajes aprendidos que queremos investigar.

## Batería realizada

Se realizaron en GalexY_travel 18 entrenamientos de N=36, con tres semillas independientes 1411/2522/3533 por cada k y arquitectura; 350 actualizaciones, 32 sociedades por actualización, 24 turnos cada sociedad y evaluación estocástica con 48 sociedades de desarrollo.

Se realizaron en DESKTOP-I4SULKD, usando su GPU RTX 4070 SUPER, 12 entrenamientos de N=324, con dos semillas 1411/2522 por k y arquitectura; 350 actualizaciones, 24 sociedades por actualización, 20 turnos y evaluación estocástica con 48 sociedades de desarrollo.

Los treinta entrenamientos completaron sin errores de ejecución y se guardaron con estados de entrenamiento, pesos, configuraciones, semillas, series temporales y replays de sociedades.

## Resultados finales, comida media por persona

| N | k | 41 parámetros, 3/2 semillas | 57 parámetros, 3/2 semillas | 73 parámetros, 3/2 semillas | Repartos exactos |
|---:|---:|---:|---:|---:|---|
| 36 | 2 | 0,2490 | 0,2498 | 0,2488 | 0 en todas |
| 36 | 4 | 0,4971 | 0,4987 | 0,4976 | 0 en todas |
| 324 | 2 | 0,2049 | 0,2049 | 0,2049 | 0 en todas |
| 324 | 4 | 0,4100 | 0,4099 | 0,4099 | 0 en todas |

Todas las sociedades de N=324 mantuvieron las diez profesiones ocupadas. En N=36 la media fue aproximadamente 9,75-9,79. Por tanto, esta batería no confirma aprendizaje de la solución ni una ventaja sistemática de añadir las estadísticas públicas de la aldea a las entradas neuronales, a 350 actualizaciones.

## Cuestión metodológica central

La implementación de este directorio conserva el entrenador REINFORCE individual de V9, incluido el suelo 0,5 en la normalización de retorno y la observación de frecuencias únicamente entre vecinos. No es idéntica a una segunda implementación experimental de microagentes realizada por separado, que usa un suelo 0,2 en las ventajas e incluye al propio individuo en el histograma local. En aquella segunda implementación, con N=36, k=2 y 600 actualizaciones, una de las redes de 57 parámetros obtuvo 0,695 de alimentación en desarrollo, 6/64 sociedades exactas y 19/384 sociedades exactas en tres lotes adicionales. Otra semilla de entrenamiento no produjo el mismo resultado. **No combinar estos resultados en una sola estimación**, pues cambian presupuesto y algoritmo de aprendizaje.

La divergencia muestra por qué no puede atribuirse automáticamente al tamaño de red una mejora debida al proceso de optimización o la representación de las observaciones. Es un hallazgo experimental útil, pero sin prueba causal concluyente.

Se añadieron por separado scripts para comparar 90 % recompensa individual + 10 % alimento global, así como un control de normalización de gradientes más permisiva. Esas variantes se deben reportar como tratamientos distintos, no confundirlas con la batería de treinta experimentos.

## Cómo reproducir y encontrar los datos

Motor y política neuronal: village.py y micro_agent.py. Pruebas test_micro_agent.py (cinco verificaciones aprobadas). Scripts complementarios: micro_social.py y micro_optimized.py.

Los 30 directorios de ejecución se encuentran bajo runs/v10_n36_* y runs/v10_n324_*. Cada directorio contiene config.json, DESIGN.json, history.jsonl, latest.pt, replay.json, control.json y status.json. Para cada paso registrado de evaluación pueden inspeccionarse medias, distancia distributiva, profesiones ocupadas, personas con hambre y diferencias entre políticas deterministas y estocásticas.

Este reporte no constituye una prueba de cooperación genuina. No se han aprendido mensajes, acuerdos o coaliciones; no se han demostrado generalizaciones sociales. Una ventaja de rendimiento requeriría contrastes con y sin acceso a observaciones sociales, topologías nuevas y perturbaciones de mensajes y compañeros.

## Continuidad

Repositorio privado GalexY3/Metodologia-AB. Rama research/aldea-micro-v10-20261110. Los pesos de ambas máquinas se reunieron mediante fusión explícita de las ramas experimentales. No modificar ni borrar las ejecuciones anteriores V6-V9.
