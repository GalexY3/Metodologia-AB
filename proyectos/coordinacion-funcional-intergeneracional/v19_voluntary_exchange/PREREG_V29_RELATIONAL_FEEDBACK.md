# V29. Registro real de destinatarios, concentración relacional y umbral de coste

**Fecha y preregistro:** 12/11/2026; redactado antes de cualquier entrenamiento V29. Línea de referencia: V25–V26 del commit 3484d113, cuyos controles de N48/k4 muestran retorno causal de regalar negativo en 48/48 personas por modelo.

## Diagnóstico de implementación

`v25_multi_capacity.roll` permite tres decisiones de donación por ronda, elegidas estocásticamente, pero `step_multi` conserva `w["prev_recipient"]=dests[:,:,0]`. El actor donante observa mediante `prior_target` solo a quién estaba dirigida la **primera** decisión de la ronda anterior, independientemente de si se emitió el regalo. Los destinatarios de los otros dos slots realmente enviados no figuran en esta característica. Es una limitación de observación y atribución privada, no una violación de conservación ni una recompensa preprogramada.

V29 cambia exclusivamente esa característica en los tratamientos de memoria precisa: `prior_target_{i→j}(t)` indica si i **envió efectivamente al menos un regalo** a su vecino j en la ronda inmediatamente anterior, contabilizando los tres slots. La función de recompensa, el coste por envío, la cantidad física de productos, el registro de `incoming`, las señales de confianza directa recibida, las profesiones y la arquitectura de nueve características permanecen idénticas. Un control `legacy` mantiene la señal anterior. No se premia enviar regalos ni se imita a un experto.

## Tratamientos primarios antes de observar resultados

Diseño factorial con 48 personas y cuatro profesiones, anillo de grado 6, tres oportunidades de donación, coste de movilidad 0,015, dos semillas neuronales 3111 y 4111. Factor A: la característica de destinatarios anteriores, `legacy` o `precise`. Factor B: precio material final por regalo, 0,04 (comparabilidad con V25) o 0,01 (precio bajo, PERO estrictamente positivo y fuera de la economía original); los resultados a 0,01 nunca serán presentados como éxito bajo c=0,04. Son ocho entrenamientos independientes. La comparación primaria es a un mismo coste, topología, semilla y horizonte.

Además, dos tratamientos exploratorios preregistrados de topología: memoria `precise`, coste 0,04 y anillo grado 4, semillas 3111 y 4111, con menos vecinos susceptibles de atraer o dispersar envíos. La política ocupacional sigue aprendiendo desde pesos aleatorios; el grado 4 permite tener las tres profesiones complementarias en la vecindad de anillos de roles periódicos 0–3.

Se ejecutarán otros dos controles negativos preregistrados con memoria `precise`, coste final 0,01, grado 6 y semillas 3111/4111, pero con historial privado de ayuda recibida y señales públicas de donación suprimidas durante el entrenamiento (`social=False` en ambos actores). Conservan observación de oficios, comida propia y sus acciones anteriores, y sirven para evitar atribuir una mejoría al mecanismo social si también aparece sin señales de interacción.

## Protocolo de entrenamiento

N=48, k=4, lote 12, 48 rondas, gamma 0,995, hidden20, init_scale8, dos redes privadas por persona, una donante de Bernoulli/destino dirigido y otra ocupacional categórica; REINFORCE con retorno propio y baseline entre mundos del mismo individuo. 850 actualizaciones. En cada condición coste 0,002 hasta actualización 400, transición lineal a su coste final entre 400 y 650, y coste final fijo hasta actualización 850. Evaluación cada 170 actualizaciones y final, siempre a coste final. Inicio alternando mundos monolíticos y ocupaciones aleatorias.

**Población y disponibilidad no elegidas según el resultado.** Las semillas neuronales y todas las condiciones se fijan aquí. Los entornos congelados se evaluarán con seis semillas ambientales reservadas, mundos monolíticos, aleatorios y equilibrados; anillos y reconexión, controles de movilidad aleatoria, bloqueo de todos los regalos y ablation de memoria recibida. Las políticas finales son las de actualización 850, nunca se escogen por mejor checkpoint.

## Falsadores

H29a: corregir la memoria de destinatarios aumenta alimentación y/o retorno causal individual de donar frente al control legacy, al mismo precio y grafo. Si solo aumenta donaciones pero el retorno individual continúa negativo, no se considera éxito de reciprocidad.

H29b: reducir el coste de 0,04 a 0,01 hace viable un régimen de intercambio con al menos una fracción apreciable de los agentes con retorno causal individual positivo. El precio es una intervención exógena, no una capacidad cognitiva superior. Sus efectos deben contrastarse con no-social.

H29c: concentrar relaciones reduciendo el grado de seis a cuatro mejora la coordinación material y los retornos mediante vínculos repetidos, sin destruir la cobertura potencial de los tres oficios complementarios. La mejora no debe ser atribuida a una topología mejor si se pierden las profesiones necesarias.

**Criterio de hallazgo principal:** alimentación media congelada ≥0,25 con coste positivo, ventaja ≥0,05 frente a ausencia de contribuciones, retorno causal de regalar positivo promediando los 48 individuos y ≥24/48 individuos con retorno propio positivo, en por lo menos dos inicializaciones por condición. Además, cambio de topología y reasignación de personas son pruebas de robustez separadas.

## Alcance

El éxito local con c=0,01, aunque genuino, no verifica el objetivo general de cooperación robusta ni la economía con coste c=0,04. Un modelo dependiente de posiciones o que no supere red reconectada se clasificará como solución frágil. Se documentarán los fallos. Se conserva el código original V25 inalterado; nuevos wrappers aplican modificaciones explícitas, y los tests mecánicos aseguran que solo se alteran campos informativos, coste o grado en cada brazo.
