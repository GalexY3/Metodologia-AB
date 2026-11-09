# Erratum de elegibilidad, 2026-11-09

Este documento **no** reescribe retroactivamente el prerregistro original. Tras las corridas exploratorias se detectó un falso positivo de estabilidad local: con fracción de entrenamiento 0.37, WD=1, seed=0, la red permanece alrededor de 60% durante una ventana, pero termina en 75.08% en el paso 45.000.

**Modificación para experimentos NUEVOS:** una ventana de 5 observaciones entre 55-65% y amplitud <=4 pp se denomina ahora **meseta transitoria candidata**. El término **meseta persistente hasta horizonte observado** requiere además que las últimas 10 observaciones estén íntegramente entre 55-65%, con amplitud <=4 pp, y que la media de sus últimas 5 observaciones difiera de la media de las primeras 5 en <=2 pp. Esto tampoco prueba estabilidad infinita; un ensayo de durabilidad extendido independiente seguirá siendo necesario.

Un control *gradual* debe alcanzar la misma meseta persistente en la misma tarea, arquitectura, conjunto de test y rango de train accuracy, sin la fase de latencia post-fit y sin una transición concentrada. Para reducir causalidad espuria por selección posterior, los futuros parámetros y las semillas confirmatorias deben congelarse antes del entrenamiento de esas réplicas.

No equiparar la observación actual de 60% en checkpoints **durante** grokking (wd=1,4500; wd=0.4,11000) con semigrokking de final estable.
