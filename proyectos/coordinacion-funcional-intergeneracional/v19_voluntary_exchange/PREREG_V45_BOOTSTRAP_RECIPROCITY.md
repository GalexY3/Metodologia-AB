# V45 — ¿Una convención inicial de generosidad permite aprender reciprocidad estable sin contratos?

Preregistro exploratorio fechado 13/11/2026, **posterior a la evaluación negativa V44 y anterior a V45**. La contribución novedosa consiste en manipular exclusivamente la condición inicial de la estrategia privada, no las recompensas o la estructura del juego.

## Pregunta y hipótesis

RQ45: ¿La dificultad de V44 se debe en parte a la trampa de coordinación producida por políticas inicialmente indiferentes (p(donar)≈0,5)? En una relación donde ambas partes reciben repetidamente los beneficios de ayudar, un primer período con contribuciones frecuentes puede proporcionar experiencia suficiente para desarrollar una respuesta contingente aprendida cuando alguien incumple.

No se impone una norma programada de castigo ni reciprocidad. Una condición inicial generosa **sí es una intervención exógena sobre las preferencias de partida** y no cuenta como surgimiento autónomo de altruismo; el resultado de interés es si permanece estable después de optimizar individualmente durante un juego con posibilidad de deserción.

## Diseño factorial y controles históricos

Utilizar exactamente el motor de parejas V44, q=0,95, costes c=0,04, valor al receptor v=0,55/3, 48 agentes con 24 parejas complementarias fijas, 48 turnos máximos, 16 mundos por actualización, actor privado MLP de 16 unidades y REINFORCE con recompensa exclusivamente individual, 1000 actualizaciones, entropía0,005, Adam tasa0,003. Las **únicas nuevas condiciones** son sesgos iniciales de donar `+1,5` y `+3,0` en los 48 logitos Bernoulli, que implican donación inicial aproximada de81,8% y95,3% respectivamente, antes de observaciones. Dos semillas neuronales3111 y4111 y dos posibilidades de observar la última donación del compañero (sí/no) producen **ocho nuevas redes**.

Comparadores históricos directamente emparejados por semilla y observación: los cuatro V44 `LONG_SOC` y `LONG_NOSOC` con logit inicial0 (50%). Los demás pesos iniciales de la red, reglas materiales, secuencias y optimizadores son los mismos, salvo la intervención de sesgo declarada. Las experiencias iniciales no son una demostración de cooperación aprendida.

## Resultados y criterios

Evaluación congelada tras u1000, seis semillas ambientales que no aparecieron en desarrollo: 980101, 980107, 980109, 980121, 980131, 980137. 32 mundos/semilla para alimento y8 mundos/semilla para intervención causal sobre cada persona. Además, sensibilidad de política al regalo anterior del compañero.

H45a: al menos dos de los cuatro modelos inicializados con logit+3,0 (considerando ambas semillas y observación social) obtienen retorno privado causal positivo de dar y≥24/48 personas positivas, con fracción de intercambios mutuos >0,25.

H45b: en ambas semillas, el sesgo+3 con información social produce mayor retorno causal de donar que el sesgo+0 de V44 con información social por al menos +0,025.

H45c: si algún modelo pasa H45a, se exige sensibilidad conductual positiva al regalo del compañero en al menos24/48 personas y una mejora de alimento final frente al control sin información social de la misma semilla y sesgo. Si no hay modelos que superen H45a, H45c no es aplicable.

H45d: comprobar si la primera actualización muestra donaciones cercanas al sesgo inicial, y si las redes abandonan esa generosidad en 1000 actualizaciones. Informar explícitamente la extinción si ocurre.

Interpretación: un éxito mostraría estabilidad de cooperación aprendida **condicional a un sesgo prosocial inicial proporcionado por el investigador** y no creación espontánea de normas ni división laboral. Un fracaso demostraría que incluso una historia inicial de contribuciones abundantes resulta insuficiente bajo esta arquitectura de aprendizaje privado. No extrapolar de dos semillas a leyes generales. V45 no permite declarar objetivo general completado.
