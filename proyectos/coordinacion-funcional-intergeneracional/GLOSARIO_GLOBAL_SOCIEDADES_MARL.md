# Glosario global de conceptos operativos de las simulaciones MARL

Versión 12/11/2026. Documento único de definiciones de trabajo para el proyecto «coordinación funcional intergeneracional». Vinculado a la línea de investigación V19–V23. Las definiciones establecen distinciones analíticas reproducibles; no presuponen universalidad empírica ni equivalencias automáticas con instituciones humanas. Se ampliará en futuras rondas sin cambiar silenciosamente los significados ya empleados.

## Agente con parámetros privados

Agente cuyo vector de parámetros de política neuronal no está compartido con ningún otro individuo del mismo modelo. En V23 cada persona tiene un actor privado de donación y otro de movilidad ocupacional. La optimización se ejecuta en el mismo programa y utiliza la recompensa propia de cada agente, lo que permite entrenamiento computacional centralizado sin convertir la función objetivo en recompensa grupal.

## Cooperación contributiva

Conducta por la que un agente asume un coste material propio para proporcionar un bien a otro agente identificado. Se mide directamente mediante la decisión de donación dirigida y su coste: en evaluación V23 el coste nominal es 0,12 por donación. Que existan donaciones no establece que sean sostenibles, recíprocas o evolutivamente estables.

## Cooperación efectiva

Combinación de contribuciones y recepción de bienes que mejora una medida de funcionamiento de la población, como el alimento medio, frente a controles especificados. No debe confundirse con la mera regularidad espacial, con el interés común normativo ni con una reciprocidad demostrada causalmente. En el experimento V23 se contrasta con políticas de donación y movilidad observadas en mundos congelados, con coste de contribución alto.

## Complementariedad ocupacional estructural

Proporción de enlaces entre personas de profesiones distintas, calculada como media de la relación 1(rol_i ≠ rol_j) sobre los vecinos de cada individuo. En k=2 esa medida captura la fracción de contactos con bienes potencialmente diferentes. No significa necesariamente recepción efectiva, porque es posible tener compañeros complementarios que nunca donan. En k>2 debe complementarse con diversidad de las profesiones distintas presentes entre vecinos, dado que la simple desigualdad no mide cobertura de k-1 bienes.

## Complementariedad material realizada

Recepción efectiva, en una ronda, de bienes de profesiones diferentes a la propia. En la función de recompensa V19–V23 interviene la cobertura de k−1 categorías y una bonificación por completar todos los bienes complementarios. Es distinta de la estructura potencial de la red.

## División del trabajo aprendida

Distribución ocupacional que surge de decisiones privadas de movilidad de los agentes, actualizadas por refuerzo de sus retornos individuales, partiendo de distribuciones iniciales en las que el reparto final no está impuesto por un planificador. Su existencia necesita documentación de los cambios observados y controles de movilidad aleatoria o de inmovilidad; los resultados de una sociedad de referencia no bastan para extrapolar a cualquier topología.

## Coaprendizaje simultáneo

Entrenamiento en el que las dos políticas neuronales que gobiernan distintas categorías de acción cambian de pesos durante las mismas trayectorias y épocas, sin congelar una política previamente adquirida. En V23 se aplica a donar y cambiar de profesión. Se diferencia de V22, donde la política de donación fue preentrenada en V21 y permaneció inmóvil durante el aprendizaje ocupacional.

## Aprendizaje escalonado

Esquema de adquisición de capacidades que entrena primero un subsistema de acción y después otro. Puede descubrir coordinación compleja, pero no acredita espontaneidad de todas las capacidades desde cero. V21→V22 representa esta estrategia.

## Convención posicional

Regularidad de conducta adquirida que depende de la identidad y/o posición de cada individuo dentro de una red social estable. Una política puede mantener una organización espacialmente alternada y perder eficiencia cuando se permutan los pesos privados entre puestos. Es una interpretación que requiere una intervención de reasignación para distinguirse de la inferencia contextual de roles vecinos.

## Reciprocidad individual causal

Efecto sobre el retorno propio descontado de obligar a un individuo a dar un bien en una ronda, comparado con impedirle darlo, manteniendo emparejados el mundo inicial y los generadores aleatorios y dejando que los demás comportamientos sigan sus políticas neuronales aprendidas. Se estima de manera individual; puede ser positivo sin demostrar que todas las contribuciones espontáneas sean racionales o que el mecanismo sea exclusivamente reciprocar favores directos.

## Reciprocidad directa e indirecta

La reciprocidad directa depende del comportamiento futuro del receptor de un favor hacia su donante, mientras que la indirecta puede operar mediante observaciones de terceros sobre contribuciones previas. Las políticas V21 observan tanto ayuda recibida directamente como señales públicas de generosidad; eliminar ambos canales permite probar la dependencia informacional, pero no identifica automáticamente un mecanismo social universalmente diferenciado.

## Redundancia informacional funcional

Situación experimental en la que la eliminación aislada de uno de varios canales de observación no destruye un efecto, pero la eliminación conjunta sí. En V21 la disponibilidad alternativa de memoria directa y generosidad pública resultó compatible con este patrón. Es una definición del patrón de dependencia, no una demostración de que dos mecanismos cognitivos o instituciones sean intercambiables en otros entornos.

## Captura de coordinación vs. captura de cooperación

Distinguir medidas de estructura, como enlaces ocupacionales complementarios, de medidas de acción, como donaciones dirigidas, y de medidas de consecuencia, como alimento y retorno causal. Una población puede alcanzar un patrón estructural ordenado sin sostener contribuciones efectivas; el control V23 sin historial de donaciones permitió observar esa diferencia.

## Currículo de coste

Programa experimental de variación temporal del coste de donar durante entrenamiento. En V23 la condición principal comienza con 0,01 y aumenta hasta 0,12 en 800 actualizaciones; después permanece constante. La evaluación final impone el mismo coste de 0,12 a todas las condiciones. No es una política de cooperación preprogramada, pero sí una intervención experimental exógena que modifica el problema de aprendizaje.

## Coste privado de movilidad

Penalización asumida exclusivamente por el agente que decide cambiar de profesión, incorporada a su recompensa de la ronda en que cambia. En V22–V23 su valor es 0,015. La existencia de este coste permite distinguir cierta estabilidad ocupacional de movilidad incesante sin consecuencias.

## Retorno individual descontado

Suma de las recompensas propias a lo largo de una trayectoria, ponderadas por la potencia temporal de gamma. En V23 gamma=0,995. Es la función utilizada para estimar ventajas de la propia acción y no debe confundirse con alimento final de la última ronda.

## Baseline de otros mundos para el mismo individuo

Estimador de valor de referencia calculado excluyendo el mundo concreto de cada agente y promediando el retorno del mismo índice personal en otros mundos del mismo lote. No agrega el bienestar de los miembros de un mundo ni hace común su recompensa: reduce la varianza de la estimación del gradiente por agente.

## Auditoría contrafactual emparejada

Intervención que replica el mundo inicial y su secuencia de aleatoriedad en dos tratamientos, imponiendo un acto inicial diferente a un individuo para medir el efecto causal sobre su trayectoria futura. V20 y V23 realizan intervenciones sobre todos los agentes, evitando la selección exclusiva de una profesión a través de índices pares en k=2. Las parejas condicionadas por un mismo mundo o semilla no deben contarse como entrenamientos independientes.

## Robustez topológica

Mantenimiento de propiedades medibles cuando se alteran enlaces de la red conservando otras condiciones. Se distingue de la generalización por tamaño poblacional, por número de profesiones o por cambio de identidades y parámetros individuales. Rendimiento inferior en una red reconectada indica límite de transferencia, incluso si el efecto sigue siendo positivo.

## Validez fuera de muestra

Evaluación de políticas congeladas, sin actualizaciones del optimizador, sobre semillas ambientales no utilizadas durante entrenamiento. Las sociedades de evaluación representan muestras de contextos estocásticos; varias sociedades generadas desde la misma semilla no equivalen a nuevas semillas de entrenamiento ni a nuevas arquitecturas independientes.

## Reorganización tras choque

Capacidad de cambiar la asignación de profesiones y el comportamiento contributivo después de perder individuos, alterar enlaces o modificar la disponibilidad de bienes, recuperando niveles funcionales medidos. Esta capacidad está pendiente de ser demostrada de forma robusta en la línea V23 y debe medirse longitudinalmente tras el choque.

## Condición suficiente operacional (pendiente)

Criterio empírico explícito que combina cooperación individual causal sostenida, división del trabajo aprendida conjuntamente desde cero, diferencia respecto a controles de azar, mantenimiento fuera de muestra y transferencia de escala. El umbral numérico y los escenarios de N y k deben preinscribirse antes de declarar completado el objetivo científico general; todavía no se considera satisfecho.


## Restricción de capacidad material por ronda

Límite de bienes que cada persona puede producir o enviar durante una ronda. En V19–V24 el máximo es una donación dirigida por persona y ronda; si cada receptor necesita k−1 categorías distintas, el número de entregas necesarias para abastecer plenamente a toda la población es N(k−1), mientras que el número máximo de entregas disponibles es N. El cociente de capacidad disponible sobre demanda es 1/(k−1). Definición formal y prueba en V24_TEOREMA_FACTIBILIDAD.md.

## Cota superior de abastecimiento pleno

Proporción máxima de personas que pueden recibir todas sus categorías complementarias bajo las restricciones del flujo de bienes, incluso suponiendo asignación óptima y cooperación universal. Con capacidad de una unidad y k especialidades, el límite es 1/(k−1). Su valor debe diferenciarse de la proporción empíricamente alcanzada por agentes en entrenamiento.

## Cota económica superior condicionada por contribuciones

Máximo compatible con el número real de regalos producidos, el beneficio que puede generar cada tipo útil de bien y el coste de producción o donación. Para el modelo unitario V19–V24, con fracción de donantes g y coste unitario c, alimento medio ≤0,20+g[0,80/(k−1)−c], antes de costes ocupacionales. Se usa como control de coherencia de resultados y para evitar comparar escalas funcionalmente incompatibles.

## Frontera de productividad cooperativa

Conjunto de combinaciones de cantidad de bienes, diversidad de servicios recibidos y recompensa que pueden materializarse dadas las reglas de producción e intercambio de un simulador. Es una frontera exógena de factibilidad material, aunque las políticas que operan bajo ella sean aprendidas. Cambiar la frontera no equivale automáticamente a mejorar la inteligencia colectiva.

## Eficiencia de entrega de dones

Cociente entre el número de categorías de bienes realmente útiles, distintas y recibidas por destinatarios y el número total de unidades emitidas. Oscila entre 0 y 1 si una unidad puede crear como máximo una nueva categoría útil para una persona. Permite separar ausencia de contribuciones de desperdicio por repetición o destino equivocado.

## Oráculo constructivo de factibilidad

Política externa explícitamente programada como benchmark matemático, cuya existencia demuestra que cierta asignación de roles y flujos es posible en un entorno dado. En V25 una asignación de profesiones repetida 0,1,2,3 y tres regalos dirigidos a los tres vecinos siguientes permite abastecer plenamente a todas las personas del anillo de grado seis. Este benchmark no entrena a los agentes, no mide emergencia y no debe presentarse como resultado de cooperación aprendida.

## Escalado de capacidad vs. escalado de coste

Distinción entre aumentar el número máximo de acciones productivas por trabajador y ajustar el coste unitario para preservar un presupuesto total comparable entre economías con diferentes necesidades. V25A permite hasta tres regalos a 0,12 cada uno; V25B permite los mismos tres a 0,04, con máximo gasto 0,12. La comparación factorial identifica qué obstáculo limita el comportamiento, sin confundir capacidad y precio.


## Equilibrio perfecto en subjuegos

Solución de un juego dinámico por la que las acciones son respuestas óptimas en cada contingencia y continuación posible del historial. En juegos repetidos de contribución voluntaria con horizonte finito públicamente conocido, regalos costosos y ningún valor después del último período, la inducción hacia atrás favorece no contribuir desde el último turno hasta el primero. La cooperación neuronal observada no acredita equilibrio perfecto en subjuegos.

## Inducción hacia atrás

Razonamiento que resuelve decisiones estratégicas empezando por la última etapa y sustituyendo en cada etapa precedente las respuestas futuras óptimas conocidas. En V28 se demuestra que una contribución propia del último turno empeora exactamente c la recompensa propia, sin posibilidad de recibir reciprocidad posterior. La proposición requiere racionalidad secuencial y conocimiento común del horizonte; sus condiciones no equivalen al comportamiento efectivo de redes neuronales aproximadas.

## Cooperación de racionalidad limitada

Patrón contributivo aprendido por actores con memoria, parámetros y experiencia de entrenamiento finitos que puede mejorar su retorno contrafactual dentro de la población de políticas observadas, sin constituir necesariamente una estrategia óptima en todos los subjuegos. Las donaciones persistentes en la última ronda de V23 evidencian una conducta cooperativa a pesar del incentivo terminal a no regalar.

## Perfil temporal de contribuciones

Serie de donaciones emitidas por persona y ronda, obtenida con pesos neuronales congelados y sin entrenamiento adicional. Permite separar la caída de contribuciones cerca del final del episodio de un abandono general del intercambio desde el comienzo. En V23 la tasa es binaria de 0 a 1 regalo por agente, mientras que en V25 el número puede alcanzar 3, por lo que deben normalizarse antes de comparar ambas familias.

## Horizonte social indeterminado

Diseño en el que los actores no conocen con certeza cuándo terminarán sus interacciones, por ejemplo, con riesgo probabilístico de finalización en cada turno y sin contador terminal público. La condición modifica el incentivo a sostener reputación y cooperación futura frente a episodios de duración conocida. No debe darse por válida su capacidad de generar cooperación sin nuevas pruebas con controles de horizonte.
