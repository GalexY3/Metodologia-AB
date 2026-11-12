# V27 — Réplicas entre inicializaciones neuronales independientes en el segundo ordenador

Preregistro 12/11/2026 previo a los entrenamientos V27. La campaña V23 documentó resultados positivos de coaprendizaje simultáneo de donación y movilidad en cuatro semillas principales, y fracasos en modelos con historial social retirado. Sin embargo, cuatro semillas neuronales son insuficientes para estimar la prevalencia de las soluciones cooperativas. V27 amplía esta muestra sin cambiar la arquitectura, los parámetros ni la función de recompensa.

## Pregunta

¿Aparecen regímenes de cooperación individualmente rentable y especialización ocupacional por coaprendizaje desde pesos aleatorios en inicializaciones nuevas, ejecutadas en un hardware distinto con PyTorch CPU, en condiciones idénticas a V23?

## Especificación congelada

Seis nuevas semillas neuronales fijadas ANTES de entrenar: 7311, 8311, 9311, 10311, 11311 y 12311. Arquitectura V23, dos redes privadas por individuo sin parámetros compartidos, 24 agentes, dos profesiones, anillo de grado2, lote20, horizonte48, 1400 actualizaciones, coste de movilidad 0,015, gamma .995, arquitecturas ocultas de dimensión20. Coste de donación progresivo 0,01→0,12 en primeras 800 actualizaciones y constante 0,12 hasta 1400; mismas pérdidas y tasas de aprendizaje V23. El entrenamiento se ejecuta con el Python y PyTorch CPU existentes en GALEXY_TRAVEL, sin importar checkpoints V23.

Todos los modelos se guardarán como `runs/v27_CPU_REP_s<semilla>` y se evaluarán con los mismos mundos ambientales y auditorías originales V23. El código del entrenador y del auditor permanece sin cambios; las diferencias de hardware y semilla quedarán documentadas.

## Criterios descriptivos

Se define **éxito doble estricto** si la alimentación media congelada de cada modelo en mundos monolíticos circulares supera al mejor control de cambios ocupacionales aleatorios por al menos +0,05, y su efecto causal de una donación inicial es positivo en promedio sobre todos los 24 individuos. La dependencia social se considera confirmada solo si el retorno se vuelve negativo al retirar el historial de donaciones durante evaluación.

Registrar separadamente la proporción de agentes con retorno individual positivo, la fracción de enlaces interprofesionales, los repartos exactos 12/12 y la sensibilidad a red reconectada. No seleccionar checkpoints mediante test; emplear la actualización 1400 sin excepción.

Los seis entrenamientos adicionales, combinados con cuatro semillas originales V23, permiten describir 10 inicializaciones distintas de la misma condición. Un intervalo binomial con diez muestras sigue siendo amplio y no constituye una prueba de universalidad, ni de generalización k=4.

No reclamar que V27 complete el objetivo científico general; se usa para estimar robustez y replicación de la condición ya demostrada en N24/k2.
