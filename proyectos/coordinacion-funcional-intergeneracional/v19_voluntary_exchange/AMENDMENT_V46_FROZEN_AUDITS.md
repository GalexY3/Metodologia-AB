# V46: enmienda de auditoría prospectiva y pruebas de transferencia

Fecha 13/11/2026. Fijada tras comenzar los entrenamientos V46, **antes de ejecutar las evaluaciones ambientales y transferencias de pareja**. No modifica los 1000 pasos, cuatro semillas neuronales3111/4111/5111/6111, alfa0/1/5/20, objetivos privados ni criterios principales.

Las seis semillas nuevas de simulación fuera de muestra serán **990101, 990107, 990109, 990121, 990131 y 990137**, cada una con128 mundos independientes y hasta48 rondas con supervivencia q, para cada política congelada. Se contrastarán alimentación, donación y mutualidad simuladas con la solución Markov exacta, con tolerancia absoluta preregistrada0,015 en cada métrica agregada. Las estimaciones causales principales se obtienen **por enumeración exacta de la cadena Markov**, no por estimar retornos con episodios de entrenamiento.

Para transferencia de identidad, en cada política congelada se formarán12 emparejamientos aleatorios completos de las48 políticas individuales (12 semillas fijas `991101, 991107, 991109, 991121, 991131, 991137, 991141, 991149, 991153, 991159, 991163, 991171`). Se calcularán los48 incentivos privados de donar en t0, alimentación y mutualidad exactos tras cada permutación, sin reentrenar. El resultado mide robustez de convenciones diádicas a sustitución de compañero y no equivale a sociedades con vecinos variables dentro del episodio.

Controles adicionales, declarados antes de evaluarlos:
- Una condición `LOOK`, que calcula el mismo paso anticipado del compañero pero impide que el gradiente de i atraviese la actualización modelada del otro. Se ejecutarán los tres alfa1/5/20 en las cuatro semillas q0,95; permite atribuir resultados al término diferencial de *opponent shaping*, y no solo anticipar que el compañero cambiará.
- En q0,20 se entrenarán NL y los tres alfa LOLA en dos semillas3111 y4111, 1000 actualizaciones. Esta extensión es un control negativo de horizonte, no forma parte del criterio principal basado en q0,95.
- Se verificará la identidad matemática de la solución descontada con iteración de Bellman independiente, gradiente privado con diferencias finitas y reproducción empírica con simulaciones nuevas. Se preservará como métrica el porcentaje de individuos con retorno privado positivo, no solo la media.

**Límites:** la solución exacta, la capacidad de anticipar el gradiente de otro agente y las parejas profesionales fijas son recursos de laboratorio. Incluso una victoria preregistrada no acredita que redes neuronales con aprendizaje puramente experiencial logren el objetivo general.
