# Contrato de investigación V9: coordinación genuinamente colectiva

**Decisión del investigador (10/11/2026).** La condición no negociable es que la solución dependa de la acción y la información de una pluralidad de agentes. Una «estrategia ganadora» de un solo individuo, o una misma regla individual replicada masivamente sin dependencia de otros, NO es el fenómeno cuya emergencia se pretende estudiar. La presente especificación prevalece sobre interpretaciones anteriores de V6–V8 que confundían buen reparto agregado con cooperación.

## 1. Distinción conceptual

Llamamos **éxito distributivo** a obtener exactamente k estados ocupados entre M=10, cada uno con N/k individuos, con estados vencedores no fijados por el experimentador. Su indicador es D_k=0.

Llamamos **coordinación colectiva en sentido fuerte** a que el éxito dependa causalmente de interacciones entre los agentes: selección de estrategias condicionada por mensajes o conductas ajenas, ajuste recíproco de roles, respuesta a las perturbaciones de otros, y transmisión de información que ningún actor posee por sí solo.

El éxito distributivo es **necesario pero insuficiente** para afirmar coordinación colectiva. Incluso un buen rendimiento en situaciones nuevas puede ser producto de atajos del entorno, una regla uniforme apropiada por todas las redes o un canal de feedback global que actúa como oráculo. Distintas matrices neuronales por individuo tampoco bastan para demostrar interdependencia funcional.

Para distinguir estos casos, cada afirmación de «emergencia de organización» debe acompañarse de experimentos de dependencia causal: ¿qué pasa si suprimimos mensajes?, ¿si intercambiamos el contenido de mensajes entre contactos?, ¿si alteramos el orden y los interlocutores?, ¿si cambiamos las capacidades y estados de otros agentes?, ¿si sustituimos la sociedad por copias de una única política?

## 2. El problema que debe seguir siendo colectivo

Conservar como núcleo de referencia el enunciado de la investigación:

- Hay N individuos y M=10 estados accesibles.
- El objetivo público de la sociedad es organizarse en exactamente k estados cualesquiera, ocupados en partes iguales (inicialmente k=2,3,4; probar luego valores inéditos).
- Nadie conoce por anticipado las etiquetas que acabarán siendo convenciones dominantes.
- Cada individuo decide por sí mismo su próximo estado y, cuando corresponde, a quién enviar información/propuestas.
- Las políticas y parámetros de aprendizaje de los individuos son independientes.
- El resultado del conjunto es el criterio de recompensa de entrenamiento, compartido íntegramente y por igual entre individuos.

**No basta con** hacer que cada agente aprenda a detectar el signo de un escalar global D y aceptar toda transición que lo mejore. Eso convierte la decisión en una operación local trivial guiada por información omnisciente que la investigación no buscaba explicar.

**Tampoco basta con** exigir por código una firma de dos vecinos para cambiar de color y concluir que la cooperación es necesaria. Sería una obligación mecánica, no una ventaja emergente de cooperar. Las restricciones adicionales deben estar motivadas por una tarea social o informacional y contar con controles.

## 3. El resultado V8 que no debe confundirse con el objetivo

Los experimentos de V8 son legítimos como **controles de solubilidad y aprendizaje microconductual**:

1. La simulación de perturbaciones mostró que la variación del indicador global puede ocultar la contribución de una acción individual cuando muchos agentes cambian al mismo tiempo.
2. El control programado con propuestas aleatorias, feedback de D provisional y aceptación/reversión pudo acercarse al equilibrio, especialmente si actuaba un individuo cada vez.
3. La microtarea neuronal de aceptación/reversión aprendió a preferir propuestas que mejoraban el D observado y transfirió esa regla a objetivos k diferentes.

**Límite decisivo:** V8 añade un canal privilegiado —el signo de la variación global que tendría lugar si se confirmase la acción— y permite revertir inmediatamente. La política de propuestas es aleatoria y se proporciona desde fuera. No necesita comunicación entre vecinos ni consenso sobre qué etiquetas conservar. Por consiguiente, la estrategia aprendida no cumple el criterio de colectividad fuerte y ningún número de episodios o porcentaje de aciertos la convertirá retrospectivamente en tal evidencia.

Conservar V8 completo, incluidos los controles favorables y desfavorables, como referencia y auditoría. No venderlo como el resultado principal ni como demostración de «grokking social».

## 4. Reformulación preferente de la V9: observabilidad distribuida y acción interdependiente

La siguiente versión principal debe plantear una tarea donde cada agente disponga de información parcial que otros agentes pueden complementar. El **censo total de la sociedad, D exacto y el signo contrafáctico de una propuesta no se presentan a las redes al tomar decisiones**.

La recompensa común puede seguir calculándose por el entorno para actualizar redes durante el aprendizaje. Que el evaluador compute una variable global no obliga a darla como observación inmediata al actor. Deben existir dos protocolos separados y etiquetados:

- **Legado, información global en tiempo real:** reproducir el acceso a feedback que estaba permitido en V6–V8, como control explicativo.
- **V9 estricta, información local:** decisión a partir del estado propio, vecinos, mensajes efectivamente recibidos, memoria local y, cuando corresponda, observaciones pasadas locales. La recompensa compartida se utiliza para el entrenamiento, pero no se retransmite como un diagnóstico global de qué acción concreta conviene confirmar. Si se incorpora algún feedback público se tratará como tratamiento experimental declarado, no como parte silenciosa del actor.

La comunicación es una **capacidad opcional aprendida**, no una orden exógena de copiar colores: quién se comunica, con quién y qué estado se propone lo decide cada agente. Comparar **C1 sin comunicación** y **C2 con comunicación**, ambas pudiendo cambiar de color por iniciativa propia.

Si la tarea básica no produce necesidad empírica de comunicación, explorar —como variantes separadas, no como sustitución encubierta— restricciones sociales con significado: capacidades funcionales o costes heterogéneos privados, necesidades locales cambiantes, emparejamientos o recursos complementarios y perturbaciones inesperadas. Verificar por construcción que existen soluciones realizables para todas las sociedades de evaluación y evitar que una asignación oculta fija revele gratuitamente qué k etiquetas «deben» ganar. El resultado agregado seguirá exigiendo k cuotas iguales.

## 5. Un criterio operacional exigente

Ningún experimento aislado prueba la irreducibilidad de lo colectivo. Se requerirá un **paquete convergente** de tests:

- **Ablación comunicativa causal:** la sociedad entrenada y evaluada con comunicación debe superar de modo reproducible un brazo entrenado desde cero sin comunicación, igualando presupuesto ambiental, arquitectura (salvo canal comunicativo), semillas emparejadas y capacidades de cambio. Un brazo C2 evaluado después de retirar mensajes mide dependencia, pero por sí solo no demuestra causalmente que la comunicación sea necesaria.
- **Mensajes manipulados:** con políticas congeladas y nuevos entornos, bloquear mensajes, permutar interlocutores o entregar mensajes válidos de un mundo distinto. Observar si disminuyen precisión, recuperación tras shocks o velocidad de coordinación. Controlar cambios colaterales del protocolo.
- **Atajos individuales:** política homogénea clonada, cambio aleatorio con parada, actor greedy basado en feedback global, política sin entrenar y estrategia simple de imitación local. Si cualquiera consigue el mismo resultado y estabilidad, no atribuir ventaja específica a negociación colectiva.
- **Heterogeneidad e interdependencia:** intercambiar las identidades o parámetros de parte de los agentes, reconfigurar conexiones o sustituir roles (sin alterar arbitrariamente la dificultad) para examinar si la población se reorganiza. Que un agente aislado no pueda corregir por sí solo un histograma de cientos de individuos es una obviedad combinatoria, **no** una prueba suficiente de cooperación.
- **Generalización:** evaluar con nuevas inicializaciones, tamaños, k inéditos, topologías y perturbaciones; medir si la organización se reconstituye y si depende de la interacción en situaciones nuevas. Varias semillas de entrenamiento, no solo muchas sociedades evaluadas con los mismos pesos.
- **Falsación:** si C1 o una política individual homogénea obtiene la misma solución que C2, o si la manipulación de mensajes no tiene efectos tras controles razonables, el resultado es reparto autoorganizado o coordinación débil; no proclamar cooperación comunicativa fuerte.

Predefinir el umbral de relevancia, el presupuesto total de interacciones, el número de semillas y los tests reservados antes de realizar la batería final. Reportar intervalos de incertidumbre y los resultados completos, también negativos.

## 6. Neuroarquitectura a examinar, no a dar por demostrada

Comparar redes pequeñas y grandes, política recurrente con memoria de trayectorias, codificación equivariante de estados, memoria explícita de ofertas, preferencias y su fiabilidad, además de cabezas de decisión separadas para cambio propio y comunicación. Los agentes podrían aprender convenciones locales que, a través de la red, conduzcan a acuerdos globales. Es una hipótesis empírica: el aumento de «neuronas» no implica automáticamente más razonamiento ni coordinación.

La señal colectiva debe ser común; cualquier método que asigne explícitamente a cada individuo un crédito contrafáctico, un supervisor de roles o una política conjunta centralizada deberá presentarse como control comparativo y no como condición principal de aprendizaje puramente colectivo.

## 7. Qué debe alcanzar el resultado principal

Afirmación fuerte que querríamos justificar:

> Una población de agentes autónomos, sin acceso individual a la distribución global ni a la respuesta óptima, desarrolla mediante aprendizaje y comunicación local convenciones y ajustes recíprocos que producen y reparan un reparto funcional global. La ventaja no se reproduce mediante una estrategia individual homogénea, azar con parada, observación global privilegiada ni mera memorización de etiquetas o posiciones.

**Estado actual:** esto sigue siendo una hipótesis; no se ha observado de manera convincente. V8 es un control parcial y una pista de reformulación, no su confirmación.

## 8. Restricción de continuidad

El usuario ha pedido trabajar con GitHub antes de cambiar de PC. Guardar código, pruebas, protocolos, resultados pequeños y modelos compactos reproducibles en la rama remota. Los pesos locales de V6 y V7 pueden tener otros archivos y ubicaciones: verificar su disponibilidad antes de afirmar que están todos replicados remotamente. Conservar identificadores de commit, comando de clonación y ruta de trabajo en el documento de traspaso. No destruir ni sobrescribir V6–V8.
