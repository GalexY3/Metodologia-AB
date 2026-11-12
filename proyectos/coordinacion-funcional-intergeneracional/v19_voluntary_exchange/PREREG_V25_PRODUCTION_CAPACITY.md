# V25 — Factibilidad material de sociedades con cuatro especialidades

Preinscripción exploratoria del 12/11/2026, posterior a las pruebas negativas V24 y al teorema de factibilidad de donaciones unitarias. La formulación y alternativas de coste preceden a cualquier entrenamiento V25.

## Pregunta

¿El colapso cooperativo de V24 bajo k=4 se relaciona causalmente con la producción de una única unidad por trabajador y por ronda? Para distinguirse de la simple memoria de roles, mantener la movilidad ocupacional aprendida desde cero y la donación voluntaria dirigida, modificando solo la cantidad de acciones materiales por individuo. V25 convierte el máximo de una donación en tres decisiones independientes de donación por ronda, una por cada necesidad complementaria posible con k=4. Los agentes pueden ofrecer 0, 1, 2 o 3 unidades, asumir cada coste voluntariamente y dirigir cada una a cualquier vecino. Se permiten receptores duplicados y entregas redundantes; no se programa una estrategia para aprovechar las tres oportunidades.

## Intervenciones factoriales

V24 control histórico: capacidad 1, coste por unidad 0,12, comida máxima 0,347 para k=4. V25A: capacidad 3, coste por unidad 0,12. V25B: capacidad 3, coste por unidad 0,04, lo que deja el gasto total máximo por agente igual al coste de una donación de V23/V24 (0,12). V25A mantiene el precio unitario; V25B mantiene el presupuesto contributivo máximo. No se compararán sin nombrar explícitamente las dos diferencias.

Para las tres acciones se reutiliza un actor privado de donación con los mismos parámetros internos y tres muestras estocásticas dentro de la misma ronda. Esta política todavía no observa qué vecinos recibieron los otros regalos de esa ronda, lo que constituye una restricción cognitiva independiente. No se prohíbe desperdiciar regalos por duplicación. El actor de ocupación V24 selecciona una profesión entre cuatro mediante una política categórica privada. Todas las redes comienzan aleatoriamente y aprenden por retorno de alimento propio descontado.

## Diseño

N=48, k=4, grado6, anillo en entrenamiento. Dos semillas 3111 y 4111. 1000 actualizaciones por corrida; lote 12, horizonte 48, movimiento ocupacional cada ocho rondas con coste 0,015. Programa de coste: precio unitario muy reducido durante las primeras 500 actualizaciones y subida proporcional hasta el precio de evaluación durante otras 300; últimas 200 actualizaciones con precio final. En V25A el precio final es 0,12, en V25B 0,04. Durante evaluación, siempre se impone el precio final de cada tratamiento.

Controles congelados de roles fijos y repartos de profesiones equilibrados/aleatorios, coste y cantidad de regalos por persona, receptores redundantes, cobertura de categorías distintas, población plena, alimento medio y comparación con límite económico teórico.

## Benchmark constructivo (no aprendido)

En una red circular con ocupaciones distribuidas periódicamente 0,1,2,3 y grado seis, una regla de asignación programada podría enviar desde cada agente un bien a cada uno de sus tres vecinos siguientes. Todos recibirían los bienes de tres ocupaciones ajenas, con gasto contributivo de tres unidades. La alimentación resultante sería 0,64 por persona a coste por regalo 0,12 y 0,88 a coste por regalo 0,04, antes de cambios ocupacionales. Esta regla solo es prueba de factibilidad, nunca se utilizará como política durante entrenamiento ni como evidencia de emergencia.

## Hipótesis y criterios

H1: ampliar capacidad de producción manteniendo precio unitario posibilita una ventaja positiva sobre 0,20 en algunas semillas, aunque la política debe aprender a distribuir donaciones y evitar redundancias.

H2: permitir hasta tres contribuciones a coste total comparable al caso k=2 mejora la estabilidad de las donaciones y la cobertura material respecto al coste unitario 0,12.

Ambas hipótesis pueden fracasar si la reciprocidad social o la selección de receptores no escalan. Las propias ocupaciones deberán seguir siendo endógenas; un benchmark prefijado no satisface el objetivo. Se informará la distancia al oráculo, el gasto real y las diferencias entre semillas.
