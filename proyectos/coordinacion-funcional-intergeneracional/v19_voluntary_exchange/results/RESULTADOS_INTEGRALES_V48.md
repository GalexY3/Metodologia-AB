# V48 — Límites de reciprocidad al cambiar de compañero durante el episodio

Doce checkpoints congelados V47 (NL, LOLA5, LOLA20 × cuatro semillas), cinco probabilidades de cambiar todo el emparejamiento bipartito entre rondas (0,0,05,0,25,0,60,1), dos regímenes de memoria (señal de antigua contraparte retenida o anulada cuando cambia). Se mantienen48 personas, 24 parejas profesionales complementarias en cada ronda, v0,55/3, c0,04, q0,95, máximo48 rondas, sin recompensas sociales, contratos, enseñanza, reentrenamiento ni selección posterior de políticas. La política da una donación unilateral al compañero actual, no al anterior.

## Resultado central por tasa de cambio y método

| Método | Reemparejar/ronda | Memoria | Comida | Mutualidad | Retorno privado t0 | Positivos por semilla | Contactos distintos |
| --- | --- | --- | --- | --- | --- | --- | --- |
| NL | 0.0 | carry | 0.2003 | 0.0000 | -0.0301 | 0,0,0,0 | 1.0000 |
| NL | 0.0 | reset | 0.2003 | 0.0000 | -0.0301 | 0,0,0,0 | 1.0000 |
| NL | 0.05 | carry | 0.2003 | 0.0000 | -0.0302 | 0,0,0,0 | 1.8454 |
| NL | 0.05 | reset | 0.2003 | 0.0000 | -0.0301 | 0,0,0,0 | 1.8454 |
| NL | 0.25 | carry | 0.2003 | 0.0000 | -0.0322 | 0,0,0,0 | 4.5745 |
| NL | 0.25 | reset | 0.2003 | 0.0000 | -0.0322 | 0,0,0,0 | 4.5745 |
| NL | 0.6 | carry | 0.2003 | 0.0000 | -0.0371 | 0,0,0,0 | 8.2332 |
| NL | 0.6 | reset | 0.2002 | 0.0000 | -0.0369 | 0,0,0,0 | 8.2332 |
| NL | 1.0 | carry | 0.2003 | 0.0000 | -0.0419 | 0,0,0,0 | 11.0877 |
| NL | 1.0 | reset | 0.2002 | 0.0000 | -0.0419 | 0,0,0,0 | 11.0877 |
| LOLA5 | 0.0 | carry | 0.3427 | 0.9913 | 0.0196 | 46,47,47,47 | 1.0000 |
| LOLA5 | 0.0 | reset | 0.3427 | 0.9913 | 0.0196 | 46,47,47,47 | 1.0000 |
| LOLA5 | 0.05 | carry | 0.3427 | 0.9914 | 0.0189 | 46,47,47,47 | 1.8454 |
| LOLA5 | 0.05 | reset | 0.3392 | 0.9514 | 0.0190 | 46,47,47,47 | 1.8454 |
| LOLA5 | 0.25 | carry | 0.3427 | 0.9914 | 0.0108 | 41,44,42,38 | 4.5745 |
| LOLA5 | 0.25 | reset | 0.3256 | 0.8032 | 0.0143 | 44,44,45,42 | 4.5745 |
| LOLA5 | 0.6 | carry | 0.3427 | 0.9913 | -0.0147 | 2,5,5,2 | 8.2332 |
| LOLA5 | 0.6 | reset | 0.3003 | 0.5404 | -0.0127 | 8,6,10,7 | 8.2332 |
| LOLA5 | 1.0 | carry | 0.3427 | 0.9913 | -0.0381 | 0,0,0,0 | 11.0877 |
| LOLA5 | 1.0 | reset | 0.2733 | 0.2839 | -0.0695 | 0,0,0,0 | 11.0877 |
| LOLA20 | 0.0 | carry | 0.3428 | 0.9932 | 0.3522 | 48,48,48,48 | 1.0000 |
| LOLA20 | 0.0 | reset | 0.3428 | 0.9932 | 0.3522 | 48,48,48,48 | 1.0000 |
| LOLA20 | 0.05 | carry | 0.3428 | 0.9933 | 0.3041 | 48,48,48,48 | 1.8454 |
| LOLA20 | 0.05 | reset | 0.3123 | 0.7196 | 0.2886 | 48,48,48,48 | 1.8454 |
| LOLA20 | 0.25 | carry | 0.3428 | 0.9933 | 0.1960 | 48,48,48,48 | 4.5745 |
| LOLA20 | 0.25 | reset | 0.2624 | 0.3204 | 0.1659 | 48,48,48,48 | 4.5745 |
| LOLA20 | 0.6 | carry | 0.3429 | 0.9934 | 0.0517 | 48,48,48,48 | 8.2332 |
| LOLA20 | 0.6 | reset | 0.2326 | 0.1242 | 0.0375 | 48,48,48,48 | 8.2332 |
| LOLA20 | 1.0 | carry | 0.3428 | 0.9928 | -0.0243 | 0,0,1,0 | 11.0877 |
| LOLA20 | 1.0 | reset | 0.2211 | 0.0658 | -0.0354 | 0,0,0,0 | 11.0877 |

## Hipótesis preregistradas

| Hipótesis | Resultado |
| --- | --- |
| h48a | cumple |
| h48b | falsada |
| h48c | falsada |
| h48d | cumple |

H48b, que exigía reciprocidad individualmente rentable bajo reemparejamiento total y memoria carry, queda falsada aunque los mismos actores sostengan un nivel alto de cooperación observada. H48c exigía diferencia≥0,025 por la señal carry frente a reset en r0,60, y no se cumple: la retención de señales anteriores no basta por sí sola para restaurar incentivos individuales.

## Diseño causal

En cada condición se simularon seis semillas ambientales reservadas con128 mundos para alimento/mutualidad y8 mundos para intervención individual. En cada mundo se crearon48 ramas por separado (una por individuo), con propuestas originales o forzadas en el primer turno. Para cada par de ramas se mantuvieron **exactamente iguales** el calendario de supervivencia, los emparejamientos de todos los turnos y las mismas muestras de uniformes para todas las decisiones libres posteriores. La primera donación tiene coste material−0,04 para el actor intervenido, y el retorno descontado propio evalúa el efecto sobre conductas futuras ajenas. La interpretación del promedio entre individuos se condiciona a las cuatro inicializaciones neuronales.

## Interpretación

[Inferencia] Las reglas conductuales de reciprocidad condicional pueden mantener bienes circulando incluso cuando los beneficios de una contribución ya no revierten hacia su autor. Esto distingue cooperación material colectiva de cooperación que constituye una mejor respuesta privada. Bajo relaciones nuevas en cada turno, contribuir puede ayudar a un compañero que a su vez donará a otro: la reciprocidad se convierte en externalidad difusa y el incentivo individual se debilita.

El experimento no prueba que nuevas políticas, entrenadas directamente bajo cambio intraperíodo, hubieran aprendido lo mismo; solo mide transferencia congelada. Tampoco incluye más de una contraparte simultánea ni elección endógena de profesión. La condición de memoria carry arrastra la última conducta observada desde la relación anterior, por lo que no identifica públicamente al autor original de esa donación.

## Reproducción

El preregistro fijó exactamente las tasas, las semillas ambientales994101/107/109/121/131/137, las políticas y los criterios. Código v48_within_episode_rewire.py, tests test_v48_dynamic_rewire.py, todos los datos originales results/v48_dynamic_v47_Q95_*.json, CSV y JSON de métricas y este informe. Hashes:
PREREG_V48_WITHIN_EPISODE_REMATCHING.md: ed79b265f4992dd3cdb8e17714d014cc64a496dd3dcaa15583ce1f852721e991
v48_within_episode_rewire.py: 2640a2df264425628e913d2be28559456c5339ccca80f47f80415e9698d13b62
test_v48_dynamic_rewire.py: 5ac520e3ee74739645c433e69557c6e2d6db865c57552b7efa8dcc406fca9c50
v48_summarize.py: e69020b831419a915ed2b9e8bab83dd16bacbbfc9517a19c020d67c1bbc5bc65