# Enmienda de reserva de semillas V44

Fecha 13/11/2026. Detectado mientras los entrenamientos V44 estaban ya iniciados y antes de cualquier evaluación congelada final.

El entrenador `v44_private_dyads.py` utilizó internamente para **desarrollo** tres semillas ambientales `970001,970007,970009` que el preregistro V44 citaba entre las seis reservadas para evaluación fuera de muestra. No influyen en los gradientes (se reponen los estados RNG y las redes no se actualizan durante desarrollo), pero comprometen su condición de evaluación completamente no observada. Por tanto, no se presentarán como semillas de **holdout ciego**.

La evaluación final V44 se realizará con seis semillas nuevas **`980101,980107,980109,980121,980131,980137`**, que no se utilizaron en desarrollos, entrenamientos ni pruebas de humo. La selección de estas semillas es anterior a los resultados de cualquiera de los ocho checkpoints finales y se fija aquí. Permanecen los mismos ocho entrenamientos, precios, cantidades de mundos y criterios, sin seleccionar puntos intermedios ni cambiar parámetros.

Asimismo se amplió la API de `simulation` con `survival_worlds=None`: si se pasa `worlds`, se sortea una vida por sociedad-mundo y se replica en las48 ramas contrafactuales, emparejando el calendario de supervivencia de todos los sujetos. La ruta predeterminada `None` mantiene el comportamiento de los entrenamientos originales, que no fueron reiniciados ni modificados durante su ejecución. Esta mejora afecta únicamente a la fidelidad causal de la evaluación, no a la política aprendida.

**Limitación**: el enfoque diádico sigue contando con parejas complementarias asignadas por el diseñador, una infraestructura de relación externa cuya emergencia no se estudia aquí.
