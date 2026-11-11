# V15 â€” BÃºsqueda de polÃ­ticas neuronales individuales que superen al azar para k variable

**Fecha de ejecuciÃ³n:** 11/11/2026. **Estado:** experimentaciÃ³n exploratoria reproducible, con evaluaciÃ³n congelada por condiciones y un holdout posterior de profesiones. La garantÃ­a universal (Â«en toda sociedadÂ») no estÃ¡ demostrada.

## Pregunta y criterio

Una aldea con N=120 individuos debe elegir k profesiones entre M opciones intercambiables y procurar un tamaÃ±o por profesiÃ³n N/k. El beneficio individual es min(n_j/(N/k),(N/k)/n_j). La hipÃ³tesis operativa que se analiza es **alimentaciÃ³n media mayor que la reasignaciÃ³n aleatoria en cada k ensayado**, no aÃºn formaciÃ³n perfecta de k grupos.

Se consideran **canÃ³nicos** los k que dividen N; para otros k, la recompensa antigua no garantiza que exactamente k grupos con poblaciones enteras cercanas a N/k sean el Ã³ptimo de bienestar. No usar k no divisor como confirmaciÃ³n de reparto exacto.

**La victoria estricta frente al azar en cada sociedad es matemÃ¡ticamente imposible de garantizar**: para cualquier k vÃ¡lido existe una probabilidad positiva de que una asignaciÃ³n aleatoria produzca ya exactamente k grupos equilibrados, con alimento 1. Una polÃ­tica alternativa no puede superar 1. Por ello, Â«superar siempre al azarÂ» se operacionaliza como superar la MEDIA del control en cada condiciÃ³n k/M especificada.

La esperanza teÃ³rica de la polÃ­tica aleatoria se calcula con S=1+Binomial(Nâˆ’1,1/M), y E[r]=sum_s P(S=s) min(s/(N/k),(N/k)/s). Se comprueba ademÃ¡s por simulaciÃ³n de mundos nuevos; la primera comprobaciÃ³n no requiere entrenar ninguna red.

## Nueva arquitectura

Las redes de cada habitante tienen parÃ¡metros **privados y diferentes**; los gradientes de recompensa de otros individuos no modifican directamente sus parÃ¡metros. No se usan censos mundiales, Dk como observaciÃ³n, recompensas colectivas ni orÃ¡culo que asigne colores. SÃ­ se conoce el encargo k y el nÃºmero M de profesiones posibles, se observa la ocupaciÃ³n entre ocho vecinos y la recompensa individual observada.

V15 reemplaza una clasificaciÃ³n directa entre M colores por nueve **operaciones invariantes al renombrado de profesiones**: permanecer; seguir la profesiÃ³n modal, minoritaria o aleatoria de los vecinos; explorar profesiones aleatorias o ausentes localmente; regresar a la profesiÃ³n previa o a la mejor recordada; y tomar una opciÃ³n local ponderada por frecuencia.

| Variante | ParÃ¡metros por agente | Horizonte entrenamiento | Actualizaciones | Semilla |
|---|---:|---:|---:|---:|
| RNN recurrente | 1.473 | 28 | 2.400 | 3111 |
| MLP sin recurrencia | 857 | 20 | 1.300 | 4111 |

Entrenamiento con REINFORCE y recompensa exclusivamente personal, sin comunicaciÃ³n. Pares (M,k) de entrenamiento predeterminados, con M=24 u 80. La RNN y el MLP difieren en arquitectura, nÃºmero de actualizaciones, horizonte y semilla: NO son repeticiones controladas de un Ãºnico diseÃ±o.

## PolÃ­tica de inferencia y salvaguarda local

El controlador de operaciones aprendido se ejecuta de modo **estocÃ¡stico cuando k/M<0,50** y con **argmax cuando k/Mâ‰¥0,50**. Este umbral se eligiÃ³ a partir de un piloto exploratorio y NO constituye un hiperparÃ¡metro confirmado externamente.

En el estudio posterior se aÃ±adiÃ³ una salvaguarda de movilidad para k/Mâ‰¥0,70: **si el agente obtiene al menos 0,75 de comida individual, se queda en su ocupaciÃ³n actual en lugar de ejecutar un traslado propuesto por la red**. El umbral 0,75 se eligiÃ³ entre siete variantes comparadas en once condiciones de DESARROLLO. Como el veto se hace despuÃ©s de la decisiÃ³n neuronal, esta polÃ­tica es neuroheurÃ­stica y NO una regla de movilidad aprendida de forma puramente end-to-end.

La salvaguarda evita ciertos traslados perjudiciales cuando casi todas las profesiones deben mantenerse activas. Se evaluÃ³ posteriormente en cuatro nÃºmeros de profesiones que nunca figuraron en los entrenamientos neuronales ni en la selecciÃ³n del umbral (M=16,32,48,72).

## BaterÃ­a principal congelada (M=24 y 80)

La evaluaciÃ³n RNN original utilizÃ³ 4 semillas de mundo nuevas Ã— 64 mundos por semilla = **256 sociedades** por condiciÃ³n, con 90 turnos, sin modificaciÃ³n de pesos. Los valores de esta tabla comparan polÃ­tica de temperatura k/M frente a random puro; para altos cocientes se aÃ±adiÃ³ posteriormente el veto local, evaluado como tratamiento independiente.

| M | k | k entrenado en ese M | RNN adaptativa | Azar | Margen |
|---:|---:|:---:|---:|---:|---:|
| 24 | 2 | sÃ­ | 0.5645 | 0.0995 | +0.4651 |
| 24 | 3 | sÃ­ | 0.6645 | 0.1492 | +0.5153 |
| 24 | 4 | sÃ­ | 0.6704 | 0.1989 | +0.4715 |
| 24 | 5 | no | 0.6603 | 0.2486 | +0.4117 |
| 24 | 6 | sÃ­ | 0.6544 | 0.2984 | +0.3561 |
| 24 | 8 | no | 0.6582 | 0.3977 | +0.2605 |
| 24 | 10 | sÃ­ | 0.6600 | 0.4961 | +0.1638 |
| 24 | 12 | no | 0.7110 | 0.5890 | +0.1220 |
| 24 | 15 | sÃ­ | 0.7502 | 0.6944 | +0.0558 |
| 24 | 20 | sÃ­ | 0.7685 | 0.7608 | +0.0077 |
| 24 | 24 | no | 0.7573 | 0.7416 | +0.0157 |
| 80 | 2 | sÃ­ | 0.6093 | 0.0415 | +0.5678 |
| 80 | 3 | no | 0.6731 | 0.0622 | +0.6109 |
| 80 | 4 | sÃ­ | 0.6987 | 0.0829 | +0.6158 |
| 80 | 5 | no | 0.6954 | 0.1037 | +0.5917 |
| 80 | 6 | sÃ­ | 0.6853 | 0.1244 | +0.5609 |
| 80 | 8 | no | 0.6940 | 0.1659 | +0.5281 |
| 80 | 10 | sÃ­ | 0.6852 | 0.2073 | +0.4779 |
| 80 | 12 | no | 0.6564 | 0.2488 | +0.4076 |
| 80 | 15 | sÃ­ | 0.6363 | 0.3110 | +0.3253 |
| 80 | 20 | sÃ­ | 0.6388 | 0.4140 | +0.2248 |
| 80 | 24 | no | 0.6538 | 0.4907 | +0.1631 |
| 80 | 30 | sÃ­ | 0.6846 | 0.5855 | +0.0991 |
| 80 | 40 | sÃ­ | 0.7493 | 0.6818 | +0.0676 |
| 80 | 60 | sÃ­ | 0.7517 | 0.7024 | +0.0493 |

RNN adaptativa por k/M, **25/25** condiciones con ventaja media. Peor margen: +0.00771. No se alcanzÃ³ reparto exacto en las evaluaciones registradas de esta baterÃ­a.

## GeneralizaciÃ³n a M nunca entrenados, ANTES de la salvaguarda

Se probaron M=12,40,60 con la polÃ­tica de inferencia fijada y sin retrenamiento. Se encontraron fallos cerca de k/Mâ‰ˆ1, donde el reparto azaroso ya parte de una situaciÃ³n favorable.

| Variante | Condiciones superiores al azar | Condiciones comprobadas | Peor margen |
|---|---:|---:|---:|
| RNN | 33 | 35 | -0.0264 |
| MLP | 34 | 35 | -0.0081 |

## SelecciÃ³n de umbral de movilidad, solo desarrollo

Se comparÃ³ sin veto y con umbrales 0,75; 0,80; 0,85; 0,90; 0,95; 0,99 en once pares difÃ­ciles. **El mejor umbral por criterio maximin fue 0,75**. Esta selecciÃ³n pertenece al conjunto de desarrollo; no usar los mismos mundos como prueba de generalizaciÃ³n.

| Umbral | Condiciones positivas | Peor margen |
|---|---:|---:|
| sin veto | 10/11 | -0.0199 |
| 0.75 | 11/11 | +0.0147 |
| 0.8 | 10/11 | -0.0096 |
| 0.85 | 10/11 | -0.0200 |
| 0.9 | 10/11 | -0.0225 |
| 0.95 | 10/11 | -0.0195 |
| 0.99 | 10/11 | -0.0195 |

## Holdout posterior de profesiones nunca utilizadas

Una vez fijado el umbral 0,75, se evaluÃ³ el MISMO modelo congelado en M=16,32,48,72. Estos valores de M no se utilizaron para entrenamiento neuronal ni para seleccionar el veto. Cuatro semillas de mundo Ã— 64 sociedades = 256 por par; horizonte de 90 turnos.

| M | k | RNN con veto | Azar | Î” RNN | MLP con veto | Î” MLP |
|---:|---:|---:|---:|---:|---:|---:|
| 16 | 8 | 0.7009 | 0.5617 | +0.1392 | 0.7212 | +0.1595 |
| 16 | 10 | 0.7395 | 0.6836 | +0.0559 | 0.7613 | +0.0778 |
| 16 | 12 | 0.7820 | 0.7621 | +0.0199 | 0.7949 | +0.0327 |
| 16 | 15 | 0.8195 | 0.7856 | +0.0339 | 0.8204 | +0.0348 |
| 16 | 16 | 0.7862 | 0.7711 | +0.0150 | 0.7866 | +0.0154 |
| 32 | 20 | 0.7437 | 0.6988 | +0.0449 | 0.7516 | +0.0528 |
| 32 | 24 | 0.7774 | 0.7348 | +0.0426 | 0.7878 | +0.0530 |
| 32 | 30 | 0.7752 | 0.7266 | +0.0486 | 0.7828 | +0.0563 |
| 48 | 30 | 0.7453 | 0.7071 | +0.0383 | 0.7533 | +0.0462 |
| 48 | 40 | 0.7348 | 0.7159 | +0.0190 | 0.7482 | +0.0324 |
| 72 | 40 | 0.7504 | 0.6954 | +0.0550 | 0.7523 | +0.0569 |
| 72 | 60 | 0.7560 | 0.6965 | +0.0595 | 0.7597 | +0.0633 |

**v15_ops_rnn24_s3111**: 12/12 mÃ¡rgenes positivos; 12/12 lÃ­mites inferiores descriptivos al 95 % superiores a cero por mundos. Peor margen observado +0.0150.

**v15_ops_mlp16_s4111**: 12/12 mÃ¡rgenes positivos; 12/12 lÃ­mites inferiores descriptivos al 95 % superiores a cero por mundos. Peor margen observado +0.0154.

## Limitaciones y siguientes pasos

1. **No prueba cumplimiento exacto de k**: el Ã©xito de bienestar estÃ¡ lejos del objetivo de k grupos exactamente equilibrados. La variable de cantidad de ocupaciones y las cuotas deben conservarse como resultados, no sustituirse por raciÃ³n media.
2. **No prueba colaboraciÃ³n colectiva**: la ventaja puede proceder de aprendizaje individual y de operaciones locales predefinidas. Esta fase es Ãºnicamente una base neuronal funcional para una futura prueba de coordinaciÃ³n.
3. **No garantiza superioridad en cada mundo**: las cifras 25/25 y 12/12 son comparaciones de MEDIAS sobre conjuntos de mundos. Los intervalos descriptivos tratan la variaciÃ³n entre mundos pero no la incertidumbre entre muchas inicializaciones independientes de redes del mismo tipo.
4. **HiperparÃ¡metros exploratorios**: la arquitectura, el umbral de argmax por k/M y el veto de 0,75 se eligieron tras observar pilotos. Para una afirmaciÃ³n publicable hay que congelar la especificaciÃ³n y repetir en mÃºltiples semillas de entrenamiento con un holdout nuevo completamente reservado.
5. **Validez del incentivo**: para N/k no entero, es preciso rediseÃ±ar el incentivo o restringir k al conjunto de divisores si se quiere que exactamente k profesiones sean Ã³ptimas.
6. **Baselines mÃ¡s fuertes**: ademÃ¡s del azar, se guardan modos de imitaciÃ³n local y renovaciÃ³n aleatoria; debe compararse contra reglas autoorganizadas individuales sencillas, no solo un adversario aleatorio.

## ReproducciÃ³n

- v15.py y test_v15.py: arquitectura, entrenamiento y pruebas de gradientes independientes.
- evaluate_v15.py y evaluations/*_FROZEN.json: 25 condiciones originales con 256 sociedades por condiciÃ³n.
- unseen_M_v15.py y evaluations/*_UNSEEN_M.json: 35 condiciones adicionales fuera de M entrenados.
- stay_gate_v15.py y evaluations/*_GATE_DEV.json: bÃºsqueda de umbral en desarrollo; *_GATE_HOLDOUT.json: 12 pruebas nuevas con selecciÃ³n congelada.
- runs/*/latest.pt: parÃ¡metros aprendidos, optimizador y semillas.
- report_v15.py, INFORME_V15.md y comparaciones_v15.csv: sÃ­ntesis derivada Ãºnicamente de registros ejecutados.

**ConclusiÃ³n:** V15 constituye una mejora empÃ­rica importante sobre V14 para la mÃ©trica especÃ­fica de *superar la alimentaciÃ³n del azar por cada condiciÃ³n*. Queda por aprender una polÃ­tica que alcance exactamente k grupos, demostrar robustez entre muchas inicializaciones y estudiar cooperaciÃ³n propiamente dicha.