# Aldea con diez profesiones. Comparación del objetivo k=2 frente a k=4

Fecha: 10/11/2026. Estudio exploratorio, no preregistrado, sin test confirmatorio.

## Objetivo del usuario

El problema debe requerir una organización genuinamente colectiva; no basta un reparto correcto producido por una estrategia que cada individuo pueda ejecutar independientemente. Recompensa exclusivamente individual de alimento. Diez profesiones equivalentes e intercambiables. Individuos con políticas recurrentes y pesos separados, observaciones locales, sin censo global, ni cuota revelada, ni información de la recompensa que obtendrían tras un cambio de profesión.

## Economía

Para N personas y k profesiones óptimas, la cuota productiva es q=N/k. Si hay n_j trabajadores en la profesión j, cada integrante recibe

r_i = min(n_j/q, q/n_j).

El máximo individual 1 solo se alcanza en n_j=q. El reparto global óptimo tiene exactamente k profesiones cualesquiera de q trabajadores y el resto vacías. Las etiquetas posibles siguen siendo diez. Se han probado k=2 (q=162 si N=324) y k=4 (q=81). El valor de k no es observable por los agentes.

## Entrenamientos efectivamente ejecutados

Se copió y generalizó el motor original V9 sin sobrescribir los pilotos anteriores, preservando RNN con 700 parámetros individuales y memoria de 12 unidades, decisión simultánea, cinco vecinos, ninguna recompensa global, REINFORCE personal y ninguna comunicación. Las 7 pruebas automáticas pasaron. La identidad de la recompensa k4 respecto al código original se verificó explícitamente.

N=36: 3 semillas independientes (1411, 2522 y 3533); 120 actualizaciones con 24 sociedades de entrenamiento y episodios de 24 turnos. Evaluación estocástica en 48 sociedades por checkpoint y 40 turnos. Se compararon los checkpoints previos de k4 contra los nuevos k2.

N=324: una semilla de entrenamiento 1411; 120 actualizaciones iniciales con 12 sociedades y episodios de 20 turnos. Ambas políticas se reanudaron con sus pesos y estados de optimizador originales y se entrenaron desde la actualización 121 hasta la 240, conservando los checkpoints previos. Evaluación en 24 sociedades por actualización. Nuevas evaluaciones post hoc: semillas 660003 y 760007, 96 sociedades por semilla, 48 turnos.

Importante: cambiar k también cambia la función de alimento y la distancia inicial al óptimo; no equivale a cambiar únicamente el número de etiquetas deseadas.

## Resultados en 36 habitantes, tras 120 actualizaciones

| Semilla | k2 alimento medio estocástico | k4 alimento medio estocástico |
| --- | ---: | ---: |
| 1411 | 0,267554 | 0,552984 |
| 2522 | 0,255916 | 0,514596 |
| 3533 | 0,262796 | 0,521798 |
| Media | 0,262089 | 0,529793 |

En esas seis condiciones, 0/48 repartos exactos por brazo. La población seguía ocupando aproximadamente 9 a 10 profesiones.

Excepción relevante: con la semilla 3533, la elección determinista de la política entrenada para k2 alcanza alrededor de 0,90 de alimento medio, mientras que su política estocástica queda cerca de 0,26. Sobre 192 sociedades adicionales post hoc, la política determinista alcanzó aproximadamente 0,8905 de alimento, D2 alrededor de 0,0602 y 1/192 repartos exactos. No es una solución robusta ni evidencia de cooperación comunicativa.

## Resultados en 324 habitantes

| Actualización | Alimento k2 | Alimento k4 |
| --- | ---: | ---: |
| 1 | 0,2059 | 0,4119 |
| 100 | 0,2757 | 0,5866 |
| 110 | 0,3888 | 0,6306 |
| 120 | 0,5635 | 0,5789 |
| 130 | 0,6033 | 0,5325 |
| 150 | 0,5131 | 0,5057 |
| 200 | 0,5006 | 0,5006 |
| 240 | 0,5002 | 0,5003 |

0/24 sociedades exactas en las evaluaciones de desarrollo finales de ambas condiciones. Evaluación post hoc sobre otras 192 sociedades por brazo: alimento aproximadamente 0,5, sin reparto exacto.

Una auditoría que reconstruyó las decisiones deterministas del checkpoint tras 240 actualizaciones identificó:

- k2: UNA profesión con 324 trabajadores y las otras nueve vacías; alimento medio exactamente 0,5 y número medio de profesiones ocupadas 1.
- k4: DOS profesiones, con ocupaciones 169 y 155 en una sociedad representativa, las otras ocho vacías; alimento medio exactamente 0,5 y profesiones ocupadas 2.

Las políticas estocásticas conservan algunos trabajadores residuales en profesiones distintas. Este fenómeno describe dos fracasos productivos diferentes que generan la misma recompensa agregada. No es prueba de convergencia general con otras semillas o redes.

## La identidad matemática detrás del plató de 0,5

La producción total de cada profesión j equivale a min(n_j*n_j/q,q), ya que cada trabajador recibe min(n_j/q,q/n_j).

La alimentación media de la aldea es

mean(r) = (1/N) SUM_j min(n_j*n_j/q, q).

Si m profesiones están ocupadas y TODAS tienen como mínimo q integrantes, cada profesión produce q y la alimentación media se simplifica a m/k. Por tanto, si m=k/2, la alimentación es exactamente 0,5.

En k2, el modelo determinista final concentra la aldea en m=1 profesión. En k4 concentra la aldea en m=2 profesiones. El parecido numérico de los resultados no significa que las estructuras sean iguales.

Las distribuciones con m<k profesiones igualmente pobladas constituyen equilibrios de Nash de cambios unilaterales bajo los parámetros de población de este experimento: abandonar el grupo para fundar uno vacío produce muy poco, y cambiar a un grupo ya sobrecargado empeora la recompensa. La política k4 observada de 169/155 todavía admite ajustes individuales entre las dos profesiones y no debe presentarse como equilibrio exacto, aunque sea próxima a la estructura estable 162/162.

## Barreras mínimas a la migración coordinada

Desde k2 con una sola profesión de 324 trabajadores, cada uno obtiene 0,5 raciones. Una coalición que se mude a otra profesión vacía obtiene m/162 por integrante mientras m<=162. Para que a los propios migrantes les convenga, m debe ser como mínimo 82. Los 242 que se quedan elevan su recompensa a 162/242, aproximadamente 0,669.

Desde k4 con dos grupos de 162 trabajadores, cada integrante obtiene 0,5. Si 41 emigran conjuntamente desde una de las profesiones a una tercera vacía, los emigrantes pasan a 41/81, aproximadamente 0,506; los que se quedan en la profesión de origen pasan a 81/121, aproximadamente 0,669. El segundo grupo mantiene 0,5. Es una mejora débil de Pareto con beneficios estrictos para los participantes del grupo origen.

Así se define un problema de acción colectiva operacional: una emigración unilateral empeora, pero una coalición suficientemente numerosa mejora la situación de sus miembros. El aprendizaje de una coordinación semejante no ha sido demostrado.

## Ideas de reformulación, todavía sin implementar

**A. Iniciar la sociedad en una trampa de Nash.** No solo desde diez profesiones aleatorias, sino también en k2 desde 324 habitantes en un único grupo y en k4 desde 162/162 entre dos grupos. Aleatorizar las etiquetas activas de cada episodio. El objetivo científico pasa a ser escapar de una organización subóptima mediante interacciones entre individuos. No programar una regla que obligue a migrar conjuntamente.

**B. Dar tiempo para negociar.** Separar una fase breve de mensajes locales antes de la actualización simultánea de profesión. Los anuncios no comprometen ni mueven automáticamente a nadie. Comparar silencio, símbolos sin significado fijado y mensajes sobre intención de cambiar a una profesión. Recompensa estrictamente alimentaria individual.

**C. Reservas de alimento.** Un individuo puede soportar temporalmente una recompensa mala mientras funda un nuevo grupo con otros. Requiere estudiar vulnerabilidad al agotamiento y distinguir la capacidad de tolerar pérdidas de la aparición de cooperación.

**D. Complementariedad funcional real.** Mantener diez profesiones intercambiables como candidatas, pero que cada una produzca un bien distinto. Para sobrevivir, un individuo necesita dos bienes diferentes cualesquiera, obtenidos mediante intercambios voluntarios. Cualquier pareja de profesiones puede ser válida. Sin intercambio, una monocultura no satisface las necesidades del individuo. Esta es una nueva tarea, no una continuación inalterada del modelo actual.

**E. Evaluación causal.** Intervenir mensajes y redes, intercambiar compañeros, introducir fallos profesionales y medir recuperación. Exigir una ventaja frente a políticas sin observación social y frente a estrategias individuales simples antes de denominar al resultado cooperación colectiva.

## Conclusión

La hipótesis de que dos profesiones son automáticamente más fáciles no se confirmó en los pilotos estocásticos de N=36. En N=324 ambos objetivos dieron mejoras transitorias pero terminaron en estructuras distintas con recompensa media de 0,5: monocultura para k2 y dos profesiones sobredimensionadas para k4. Existe un antecedente pequeño de solución casi óptima mediante elección determinista en una de tres semillas k2 de N=36, pero no constituye resultado general ni cooperación aprendida.

La explicación algebraica de las trampas permite orientar la próxima investigación hacia la formación voluntaria de coaliciones, intenciones comunicadas y supervivencia de grupos fundadores, sin añadir recompensas colectivas. Los resultados son exploratorios y no establecen una ley general sobre el número óptimo de profesiones.
