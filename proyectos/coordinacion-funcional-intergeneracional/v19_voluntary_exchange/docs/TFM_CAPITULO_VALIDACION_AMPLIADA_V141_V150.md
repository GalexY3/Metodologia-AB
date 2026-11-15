# Ampliación de la validación generativa y de los rivales humanos

## Tres redes y una diferencia que no es universal

La primera comparación generativa del manuscrito utilizó una red humana completamente libre. V141 amplía el contraste a las tres redes con libertad del 100% del archivo de Jia y colaboradores. Cada red se excluye del ajuste y se generan 256 poblaciones por modelo y red. Las estadísticas globales de esos datos ya se habían visto al formular la investigación; la exclusión de entrenamiento no convierte las redes en una confirmación retrospectivamente virgen.

El modelo mejor en pérdida a un paso difiere del mejor en trayectoria agregada en las tres redes. En la primera, joint_context vence en predicción y dyadic_context en la trayectoria; en la segunda se invierte su orden; en la tercera gana dyadic_context a un paso y context en la trayectoria. Esto no significa que un modelo complejo pierda siempre: promediando las tres redes, joint_context tiene tanto la menor pérdida logarítmica (0,2333) como el menor error absoluto de la curva (0,0810).

La conclusión defendible es que los objetivos no son intercambiables y sus rankings dependen de la unidad evaluada. No se sostiene una ley según la cual mejorar predicción perjudique necesariamente la generación colectiva. La independencia condicional Bernoulli de acciones, la red toroidal fijada y el uso de la primera ronda observada siguen siendo supuestos del generador.

V142 separa algebraicamente error bajo historiales humanos y desviación inducida al cerrar el bucle. El error absoluto agregado con historiales humanos es aproximadamente 0,0184 para dyadic_context y 0,0187 para joint_context, mientras el de la simulación cerrada es 0,0868 y 0,0806. La descomposición de error cuadrático incluye un término cruzado: no debe interpretarse cada sumando como contribución causal independiente. La identidad ayuda a localizar discrepancias; no identifica por sí sola la causa de la exposición a estados nuevos.

## Una segunda fuente humana y la incertidumbre del ranking

V143–V144 incorporan el archivo público de Yamamoto y Goto (2024, OSF d3qpw), con 156 díadas, 312 participantes y cuatro condiciones de interacción. Se excluyen díadas del ajuste en cinco particiones y, después de la primera ronda, no se inyectan decisiones humanas futuras en las simulaciones.

El modelo con historial observable logra la mejor predicción a un paso en las cuatro condiciones. Sin embargo, base_time tiene menor error de la tasa agregada en tres y memory1 en la restante. El modelo rico sigue siendo el mejor para otro resultado, cooperación mutua, en las cuatro. La selección del indicador colectivo forma parte de la pregunta científica; no puede cambiarse después para declarar ganador a un método.

V144B vuelve a muestrear díadas 10.000 veces sin volver a ajustar los modelos. En la condición alternante estándar, el intervalo del cambio de error de cooperación agregada entre el modelo rico y el simple incluye cero, aproximadamente [−0,0327;0,0311]. Los rankings puntuales no autorizan una diferencia confirmada en todas las condiciones. El bootstrap cuantifica incertidumbre condicional a los modelos ajustados, no toda la incertidumbre de su estimación.

Estas pruebas proporcionan una segunda fuente pertinente para la validación de trayectorias de decisión. No miden profesiones complementarias ni confirman las utilidades del modelo ocupacional. La generalización de una observación metodológica no debe confundirse con validación sustantiva de otra economía artificial.

## Pivotalidad, rescate y variables derivadas

La línea V147–V150 analiza contribuciones humanas en tecnologías con umbral. La pregunta era si estar en posición de completar unilateralmente la producción aportaba una explicación específica de la respuesta. Antes de estimar se reconstruyeron parámetros y tablas desde los materiales originales, distinguiendo sesiones con personas ya observadas y grupos emparejados de nuevo.

V148 muestra por qué un rival flexible es necesario. Añadir una señal de pivotalidad a un modelo simple reduce el error cuadrático por díada en aproximadamente 0,000174, con intervalo bootstrap que excluye cero. Pero frente al rival M4, que ya representa de forma flexible las variables físicas relevantes, añadir la señal en M5 cambia el error en +0,0000189, con intervalo [−0,0000237;0,0000620]. La comparación utiliza 277 díadas de la primera sesión como unidades independientes.

La pivotalidad se calcula de las contribuciones previas y de la tecnología. No aporta información nueva a quien ya observa esas variables: puede aportar una representación útil o un sesgo inductivo. La pérdida de ventaja frente al rival limita la reivindicación de un mecanismo adicional. No prueba que las personas ignoren la pivotalidad.

V149 no establece una diferencia del coeficiente de pivotalidad entre grupos de dos y cuatro personas: los intervalos de la diferencia incluyen cero en ambas sesiones. El tamaño no fue aleatorizado para ese contraste y la segunda sesión reutiliza participantes, por lo que no procede interpretarlo como efecto causal ni sumar ambas sesiones como muestras independientes.

V150D conserva también el resultado inicialmente invalidado y la comparación corregida de «rescatador único». Una asociación condicional positiva en parte de los datos no produce una ventaja predictiva estable frente al rival físico flexible. El registro identifica el archivo inválido en lugar de incorporarlo al conjunto favorable.

## Qué se ha validado

La ampliación sostiene una exigencia metodológica concreta: evaluar predicción a un paso, generación cerrada y resultados colectivos distintos, conservando la dependencia de las unidades y la fuerza del comparador. No establece una relación universal entre complejidad y error generativo. Las hipótesis de dependencia contemporánea y choques comunes de V146 se conservan como exploración y no como variables identificadas causalmente.

Los originales de V141, V142, V144, V144B, V148, V149 y V150D contienen las cantidades aquí citadas y las restricciones de sus diseños. Este capítulo sintetiza esos registros anteriores; no ejecuta una nueva cohorte humana ni reestima toda su cadena. El análisis V179 añade después una reconstrucción independiente más estrecha de un ensayo de monitoreo, que conserva su propio estimando y su unidad de asignación.
