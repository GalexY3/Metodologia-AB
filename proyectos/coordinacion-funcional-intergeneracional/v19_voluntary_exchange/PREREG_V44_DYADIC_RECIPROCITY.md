# V44 — Aprendizaje neuronal de reciprocidad condicional en un juego diádico sin contratos

**Preregistro exploratorio 13/11/2026**, antes de los entrenamientos de V44. El experimento surge de la factibilidad matemática V42 y de las extinciones de donación en V41, para distinguir la incapacidad de aprender una respuesta individual contingente de la dificultad adicional de cuatro profesiones, tres ofertas dirigidas, red circular y movilidad ocupacional.

## Pregunta

¿Pueden 48 agentes con políticas neuronales privadas e independientes descubrir estrategias de donación recíproca sin acuerdos de liquidación, sin política preentrenada ni recompensa grupal, cuando la otra persona puede responder a la donación pasada?

## Entorno

24 parejas disjuntas permanentes, 48 agentes, oficios inicialmente complementarios y fijos dentro de cada pareja. Los individuos eligen simultáneamente donar una unidad a su pareja o no donarla. La entrega es unilateral; nadie puede condicionar materialmente su transferencia a que el otro la haga en el mismo turno. La recompensa propia en cada turno vivo es **b + v·(regalo recibido) − c·(regalo emitido)**, con b=0,20, v=0,55/3=0,18333 (mismo valor de una especialidad complementaria en V25), y c=0,04. No se introduce un bonus por reciprocidad ni un castigo por negarse a ayudar. El mecanismo de reciprocidad *grim trigger* estudiado en V42 **no** está programado en el actor.

Cada actor dispone de una política privada de Bernoulli, red MLP de 16 unidades, sin parámetros compartidos. La observación contiene regalo propio anterior, regalo observado de la contraparte anterior, recompensa propia anterior, indicador de la primera ronda y un sesgo constante. Los actores no conocen el momento exacto de terminación en la condición de horizonte incierto. En el control «sin información del otro» se suprime únicamente la variable de regalo observado de su contraparte; se mantiene la misma arquitectura y número de parámetros.

## Diseño inicial de aprendizaje

Dos probabilidades de continuación entre rondas, **q=0,20** (por debajo del umbral V42 qcrit≈0,2193) y **q=0,95** (por encima), truncamiento máximo 48 rondas; los mundos de 24 parejas terminan juntos. Dos condiciones de observación, regalo previo del compañero visible o invisible, y dos semillas neuronales 3111 y4111, total ocho redes poblacionales nuevas entrenadas desde pesos aleatorios. Entrenamiento con REINFORCE por retorno propio descontado, gamma0,995, lotes de16 mundos independientes, 1000 actualizaciones, entropía controlada 0,005, gradientes privados por persona y sin comunicación entre optimizadores. Se requiere que la política no incluya un guion externo de reciprocidad.

Evaluación congelada en seis semillas ambientales no vistas, 32 mundos por semilla, observación propia o parcialmente suprimida según tratamiento. Auditar cooperación mutua, desigualdad, retorno privado total de forzar a un individuo a donar en t0 frente a prohibirlo, con todas las demás acciones libres durante el episodio y supervivencia emparejada. Adicionalmente medir **sensibilidad conductual aprendida**: diferencia de probabilidad `p(donar|compañero donó antes)-p(donar|compañero no donó)` con las demás observaciones fijas; útil como detector de reciprocidad, no prueba causal temporal por sí solo.

## Hipótesis falsables

H44a: en al menos una población q0,95 con señal del otro, el efecto causal medio de donar es positivo, con ≥24/48 individuos positivos, y tasa de donaciones mutuas >0,25 durante ronda vivas.

H44b: para q0,95, los dos modelos con información de la contraparte mantienen más donaciones mutuamente beneficiosas y mayor retorno privado de donar que sus controles sin dicha información.

H44c: en q0,20 ninguna condición obtiene ≥24 individuos con retorno positivo por donar. Se trata de una predicción basada en el umbral de una norma idealizada, **no un teorema universal para cualquier aprendizaje**.

Si H44a falla, el resultado demuestra insuficiencia de esta arquitectura y entrenamiento, no que la cooperación sea imposible; V42 ya ofrece una estrategia contrafactual individualmente sostenible. Si H44a tiene éxito, replicar con 8–12 semillas adicionales y transferir a redes con múltiples potenciales compañeros antes de hablar de cooperación social robusta.

## Limitaciones

Las relaciones emparejadas y oficios complementarios son impuestos exógenamente; esta es una **simplificación de identificación de un único mecanismo**. La cooperación diádica no equivale a organización ocupacional endógena ni invención normativa. No se usarán ayudas reputacionales diseñadas retrospectivamente ni selección del mejor checkpoint para «rescatar» el resultado. Las conclusiones finales deben diferenciar el desempeño de aprendizaje, controles y oráculos analíticos.
