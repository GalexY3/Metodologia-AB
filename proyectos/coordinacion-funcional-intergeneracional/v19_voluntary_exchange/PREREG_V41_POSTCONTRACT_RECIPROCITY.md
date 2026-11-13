# V41 — Persistencia privada de reciprocidad después de retirar los contratos

**Preregistro exploratorio 13/11/2026, antes de iniciar entrenamientos V41.** Se formula después de los hallazgos V39–V40: al ejecutar unilateralmente las propuestas aprendidas bajo contratos hay ganancias sociales elevadas a coste0,04, pero una propuesta unilateral marginal perjudica de manera inmediata a quien la emite. **La pregunta** es si la experiencia pasada con contratos deja estrategias sociales capaces de reorganizarse mediante reciprocidad diferida cuando desaparece por completo la garantía contractual.

## Pregunta y estimando

RQ41: ¿Tras retirar permanentemente la ejecución condicionada por consentimiento bilateral, las políticas privadas originalmente socializadas en contratos mantienen voluntariamente contribuciones individualmente rentables a lo largo de nuevos aprendizajes bajo un juego unilateral? El retorno privado causal del primer regalo en episodios nuevos, descontando todas las reacciones futuras, es el criterio principal; la alimentación social y número de regalos son secundarios y no sustituyen el incentivo individual.

## Diseño factorial 2 × 2 × 2

**Fuentes de aprendizaje anterior**, con dos semillas neuronales originales3111 y4111 cada una:

- **Contrato previo**: checkpoints V30 `v30_MUTUAL_C04_s3111` y `v30_MUTUAL_C04_s4111`, tras 700 actualizaciones y precio final0,04.
- **Donación previa**: checkpoints V29 `v29_L_D6_C04_s3111` y `v29_L_D6_C04_s4111`, tras850 actualizaciones y precio final0,04. Utilizan la misma memoria 'legacy' de destinatarios que el actor V30. Este comparador tiene150 actualizaciones históricas adicionales y una programación de precios distinta; **no representa un experimento perfectamente igualado en experiencia pasada**.

Cada checkpoint se bifurca experimentalmente en dos continuaciones desde el mismo estado neuronal y de Adam, una con historial social disponible y otra con señales sociales suprimidas tanto al elegir propuestas como ocupaciones. **Ocho tratamientos** 2 fuentes × 2 memorias × 2 semillas. En todos, N48/k4, anillo grado6, 12 mundos por actualización, horizonte48, coste final fijo0,04 desde la primera hasta la última actualización, 1000 actualizaciones adicionales, gamma0,995, tres regalos dirigidos posibles por persona y ronda, coste personal por cada regalo emitido, coste profesional0,015 y elección ocupacional cada ocho turnos. Los premios provienen exclusivamente del alimento individual, sin recompensa agregada. Sin transmisión ni mentor.

Los agentes de todas las condiciones entrenan **desde el comienzo de la continuación bajo la regla unilateral original**, sin contratos disponibles durante esos 1000 pasos de aprendizaje. Se conservan los parámetros y estados de Adam de cada checkpoint. El uso de información social se manipula exclusivamente en el vector de observaciones; no se modifica la producción material ni la recompensa. Las ocho ramas utilizan semillas deterministas de desarrollo pero la bifurcación comparte pesos al inicio.

## Predicciones falsables

H41a: alguna de las cuatro condiciones con historia contractual previa obtiene retorno causal medio descontado del regalo inicial >0 para al menos24 de 48 agentes al final de la continuación, tras1000 actualizaciones, sobre semillas ambientales nuevas.

H41b: al menos uno de los dos pares de ramas contractuales con señales sociales obtiene mayor retorno causal privado que su propia rama sin historial social en el escenario primario anillo/monolito, por al menos+0,025.

H41c: los modelos con experiencia contractual previa presentan mayor retorno causal privado medio en ≥2 comparaciones por semilla y nivel de historial social que los que fueron entrenados unilateralmente antes de la continuación. Es exploratorio por la diferencia de150 actualizaciones anteriores y currículo de precios.

H41d: si alguna condición supera H41a, se requiere que el retorno permanezca positivo en ≥24 individuos también tras reconectar la red, y que la ventaja alimentaria sobre el mejor de tres controles de movilidad ocupacional aleatoria sea >+0,025. La condición evita atribuir un éxito general a convenciones específicas de posiciones.

**Resultado primario**: efecto causal propio descontado de forzar vs prohibir el primer regalo en t0 (48 rondas) para todas las48 personas individualmente, controlando seis semillas ambientales reservadas970001,970007,970009,970021,970031,970037. Evaluaciones congeladas a u1000; ningún checkpoint intermedio puede sustituir el final. Controles adicionales de profesión fija, tasas de movilidad aleatoria0,15/0,35/0,60, regalos prohibidos, historial social suprimido, personas trasladadas y red reconectada. Se documenta el historial de entrenamiento (1,200,400,600,800,1000) para mecanismos dinámicos y posible extinción de contribuciones.

## Interpretación crítica

Una mejora tras transferencia de un checkpoint contractual al juego unilateral no demuestra que los agentes hayan inventado una institución; la experiencia contractual fue exógena. Un modelo con alto alimento y bajo retorno causal privado sigue sin acreditar cooperación individualmente estable. Un retorno positivo en el laboratorio debe distinguirse de equilibrio evolutivo estable, que requeriría más semillas, redes, tamaños, agentes nuevos y análisis longitudinal.

No se autoriza declarar el OBJETIVO COMPLETADO salvo que se demuestre cooperación y organización endógenas robustas mucho más allá de esta prueba.
