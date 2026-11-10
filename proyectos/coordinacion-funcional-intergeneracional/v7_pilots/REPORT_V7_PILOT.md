# V7. Informe de la primera batería exploratoria

Fecha: 10 de noviembre de 2026. Datos de `diagnose.py` con semilla de desarrollo 700301, 96 sociedades por brazo (32 por k), horizonte 32. Los datos son EXPLORATORIOS y no constituyen una evaluación sellada.

## Estado de V6 anterior

Se comprobó que V6, sobre N=324, figuraba detenida con 518.400 episodios y `checkpoint_exists=true`. Se conservó su checkpoint y no se abrió su holdout, reservado en el protocolo original a completar el millón. El estado `stopped` ya se observaba al consultarlo; no se ejecutó una terminación forzada.

## Qué se ha ensayado

Cinco brazos: V6 legacy, V7 gated sin memoria, V7 GRU sin mensajes, V7 GRU con mensajes y V7 GRU con entrenamiento evolutivo sin mensajes. Cada uno recibió 40 actualizaciones, 12 sociedades por actualización y doce turnos por episodio, con N=36, k=2,3,4 y M=10. La comparación de coste no es igual: ES hace cuatro pares de evaluaciones con perturbaciones en cada actualización, de modo que procesa más sociedades que REINFORCE.

Las evaluaciones iniciales con política greedy revelaron una degeneración: los cuatro actores V7 con puerta de conservación escogían siempre quedarse en el color actual. Su distancia D permanecía idéntica durante las 40 actualizaciones; esto diagnostica un sesgo de decisión determinista, no ausencia comprobada de actualización de pesos. En entrenamiento estocástico V7 sí cambiaba cerca del 24–25% de las veces. El legado V6 cambiaba cerca del 90%.

## Evaluación retrospectiva del piloto con selección estocástica

Distancia final D_4. Menor es mejor. Cada fila se refiere a una única inicialización entrenada, sobre 32 mundos de desarrollo con k=4.

| Condición | Red sin entrenar (estocástica) | Tras 40 actualizaciones (estocástica) | Estados ocupados | Churn | Exactos | Estables |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| V6 legacy | 0,4158 | 0,4149 | 9,69 | 90,3 % | 0/32 | 0/32 |
| V7 gated C1 | 0,4123 | 0,4089 | 9,84 | 25,0 % | 0/32 | 0/32 |
| V7 GRU C1 | 0,4106 | 0,4063 | 9,84 | 25,0 % | 0/32 | 0/32 |
| V7 GRU C2 | 0,4063 | 0,4054 | 9,78 | 24,3 % | 0/32 | 0/32 |
| V7 GRU ES C1 | 0,4106 | 0,4123 | 9,78 | 25,2 % | 0/32 | 0/32 |
| Uniforme continua, control | — | 0,3993 | 9,81 | ~90 % | 0/32 | 0/32 |
| Uniforme al inicio y congelada | — | 0,4036 | 9,88 | 0 % | 0/32 | 0/32 |

Las pequeñas diferencias entre modelos no demuestran superioridad. En este lote, el control uniforme continuo obtuvo menor distancia que cualquiera de los cinco modelos entrenados. Los cuatro brazos V7 continúan usando casi los diez colores. El descenso del churn respecto a V6 se explica al menos parcialmente por la puerta inicial de conservar estado, presente antes del aprendizaje.

Para k=2 y k=3 tampoco se detectaron exactos o estabilidad, y los errores se mantuvieron cercanos al azar (véase el JSON de resultados completo). Ninguna de estas pruebas muestra todavía coordinación colectiva aprendida.

## Diagnóstico metodológico

1. La evaluación greedy por sí sola es insuficiente: con gate_bias=-1, el actor puede escoger quedarse siempre, ocultando variaciones en las probabilidades de cambio. En futuras baterías se deberán preregistrar ambas evaluaciones y registrar P(cambiar).
2. La política con GRU en esta fase usa memoria por estado y actualización explícita, pero carece de planificación simbólica. Los resultados no muestran por sí solos si la memoria contribuye.
3. Comparar C1/C2 con una sola inicialización y 32 mundos por k no proporciona evidencia robusta sobre la ventaja de mensajes. Se necesitan replicaciones independientes de entrenamiento.
4. ES usa el mismo retorno colectivo sin atribuir mérito individual, pero consume más evaluaciones por actualización, por lo que los resultados no equiparan presupuesto ambiental.
5. Los episodios de 12 turnos y N=36 son pilotos de viabilidad. No está justificado todavía escalar exactamente estos procedimientos a 324 agentes o a un millón de episodios.

## Siguiente decisión

No extender esta configuración sin cambios. Antes de una batería confirmatoria, comparar modelos estocásticos con mayor duración, un tratamiento explícito de la exploración y, como condición estructural separada, activaciones menos simultáneas para examinar si la señal colectiva se diluye. Mantener además la tarea original sin cambiar como referencia. Fijar las semillas, el criterio de selección y el presupuesto por interacciones (no solo por actualizaciones) antes de repetir. La evaluación confirmatoria reservada permanece cerrada.

Los ensayos anteriores no invalidan la hipótesis de que la coordinación pueda emerger; tampoco aportan evidencia afirmativa.

Código: `experiment.py`. Revisión de checkpoints: `diagnose.py`. Salidas completas: `RESULTS_V7_PILOT_DEVELOPMENT.json`. Panel comparativo local: `http://127.0.0.1:8766` en DESKTOP-I4SULKD.