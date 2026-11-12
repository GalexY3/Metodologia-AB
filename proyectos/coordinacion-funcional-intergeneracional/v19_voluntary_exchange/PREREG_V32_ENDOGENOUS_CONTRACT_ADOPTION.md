# V32 — Adopción institucional endógena: donar unilateralmente o proponer contratos

Preregistro exploratorio del 12/11/2026. Redactado después de observar los resultados causales positivos de V30 en el régimen contractual y antes de entrenamientos V32. No es una réplica ciega de V30 y no debe clasificarse como tal.

## Pregunta

¿Pueden agentes con objetivos exclusivamente privados aprender simultáneamente a especializarse, elegir destinatarios, decidir si contribuyen y adoptar voluntariamente un mecanismo de reciprocidad contractual que está disponible pero que no se impone como única opción de intercambio?

## Economía

N48, k4, anillo de grado6, horizonte48, tres oportunidades de transferencias por individuo y ronda. Cada actor dispone de tres políticas neuronales independientes por persona, cada una inicializada aleatoriamente y sin pesos compartidos: 1) una política categórica para elegir ocupación cada ocho rondas, 2) una política Bernoulli y categórica para decidir la emisión de hasta tres regalos y los vecinos destinatarios, 3) una nueva política Bernoulli individual que selecciona en cada ronda entre el régimen de donación unilateral y el régimen contractual. La elección institucional se aplica a las tres oportunidades de ese actor durante esa ronda.

Si el individuo elige **unilateral**, todos los regalos emitidos llegan a los receptores y cada unidad cuesta c. Si elige **contrato**, las propuestas son gratuitas salvo que otro individuo también haya elegido contrato y haya emitido una propuesta de retorno; cada pareja mutuamente comprometida liquida exactamente una unidad en cada dirección, pagando el coste c por unidad realmente intercambiada. Un receptor puede aceptar una donación unilateral mientras elige contractual para sus propias propuestas. Las propuestas repetidas de contrato a una pareja no generan unidades adicionales. Ninguna regla central indica a los individuos qué modo elegir ni cuál genera mayor bienestar.

La institución contractual **es una opción estructural exógena del entorno**. Únicamente la adopción de esa opción y la coordinación de sus usos puede emerger de las decisiones privadas. No confundir adopción institucional con invención de normas, ni una mejora respecto a donaciones unilaterales con mayor altruismo.

## Factores y semillas anteriores al entrenamiento

Dos semillas neuronales fijadas, 3111 y 4111. Dos inicializaciones de la política institucional por semilla: sesgo logit inicial 0, que implica 50% de preferencia contractual esperada, y sesgo logit -2, que implica alrededor de 12% de adopción inicial. Cuatro modelos en total. Todos los pesos restantes se inicializan con las mismas distribuciones V25. El entrenamiento optimiza **únicamente el retorno propio descontado** mediante REINFORCE con baseline de mundos del mismo individuo; el modo institucional no tiene recompensa adicional ni instrucción de imitación.

Hiperparámetros: 1000 actualizaciones, lote12 mundos, horizonte48, coste de movilidad0,015, gamma0,995; precio de regalo inicial0,002 hasta u400, subida a0,04 entre u400–650 y precio constante0,04 hasta u1000. Learning rate gift0,002, role0,003, institution0,003; entropías .015, .01 y .01; hidden20 por red. Evaluaciones en u1,200,400,600,800,1000. Los mundos iniciales alternan monolíticos y roles aleatorios.

## Criterios

H32a: desde prevalencia inicial contractual baja, algunos actores aprenden a elegir contratos para la mayoría de sus propuestas y obtienen alimentación mayor que el baseline0,20 a coste final, sin premio colectivo.

H32b: la elección institucional, al ser causalmente intervenida en modelos congelados, mejora el retorno propio de un número apreciable de actores frente a forzar el modo unilateral, y los resultados superan el control de modo aleatorio fijo. El aumento de adopción sin retorno privado positivo no se considera resultado de aprendizaje institucional funcional.

H32c: la movilidad ocupacional se reorganiza desde poblaciones monolíticas y aporta mejora sobre controles de movilidad al azar. Transferencia a grafos reconectados y sustitución de posiciones se audita separadamente.

## Controles negativos y validez

Evaluar políticas congeladas con modo institucional forzado siempre unilateral, siempre contractual y aleatorio equiprobable, manteniendo idénticos actores donantes y ocupacionales, así como con no regalos, rol fijo y movilidad aleatoria. Comparar la trayectoria del régimen adoptado espontáneamente contra controles de modo externo sin reentrenar; estos son contrastes contrafactuales de política y no equivalen a cambiar la institución de la economía.

Seis semillas ambientales reservadas y todas las personas en contrafactual de elección del modo institucional inicial, con emparejamiento de estados y generadores pseudoaleatorios. Indicar además la proporción de individuos con retorno neto positivo por preferir contratos.

Aunque V32 funcione, aún se necesitará escalar a N120, analizar redes diferentes y comprobar robustez ante nuevas inicializaciones. **No declarar OBJETIVO COMPLETADO solo por una selección institucional funcional en una de las semillas**.
