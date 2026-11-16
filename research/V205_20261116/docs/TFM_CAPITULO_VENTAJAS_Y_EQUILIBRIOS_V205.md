# Qué se puede inferir de la alineación de ventajas: un contraejemplo con equilibrio aislado

Versión de investigación, 16/11/2026. Resultado matemático y computacional interno; originalidad y confirmación científica externa pendientes.

## La pregunta que motivó el cambio de experimento

V202 separó la existencia y conservación de una regla relacional de su adquisición desde un inicio sin ella. V203 comprobó que disponer del gradiente privado exacto no bastaba para adquirirla en los puntos iniciales especificados. V204 tampoco encontró esa adquisición con una forma conocida de anticipación del aprendizaje ajeno, LOLA, conservando los costes monetarios completos. Estos negativos no demuestran una imposibilidad general. Sí justifican auditar qué garantías ofrecen los mecanismos de modelado del oponente antes de incorporarlos al argumento del TFM.

Al revisar Advantage Alignment apareció una discrepancia precisa. Su formulación usa ventajas condicionadas a las acciones conjuntas; la prueba de conservación de Nash utiliza una propiedad de las ventajas marginales respecto a la acción propia. La distinción es decisiva cuando las políticas son mixtas: el equilibrio iguala las recompensas esperadas de las acciones propias del soporte, pero una combinación concreta con la acción ajena puede seguir produciendo una sorpresa positiva o negativa.

El objetivo de V205 fue resolver esa incertidumbre mediante una predicción discriminante, previa al cálculo primario. No se entrenó otro simulador buscando una curva favorable. Se construyó un juego pequeño donde calcular exactamente el equilibrio, el campo del algoritmo y una desviación unilateral posterior. La formulación y el código propios se publicaron antes de ejecutar la prueba. La construcción analítica ya era conocida al registrar el protocolo; no fue una búsqueda ciega.

## Diseño y resultado

Dos jugadores actúan simultáneamente durante dos rondas. Las acciones binarias iniciales, expresadas como signos, son x y z; las finales son f y g. La acción z determina el estado público de la segunda ronda. Con c>0, los pagos son:

| Ronda | Jugador 1 | Jugador 2 |
|---|---|---|
| Inicial | z(1+cx) | −cxz |
| Final | cfg | f(z−cg) |

Cada jugador dispone de una política Bernoulli independiente por estado. En el perfil uniforme todas las probabilidades valen 1/2. Por inducción hacia atrás, las diferencias entre acciones en la última ronda son 2c E[g] para el primero y −2c E[f] para el segundo, de modo que ambas medias deben ser cero. Las continuaciones tienen valor cero y el mismo razonamiento fija las dos políticas iniciales. El perfil es Markov perfecto y localmente aislado para c>0. La verificación simbólica da un determinante 4096c^6 para el Jacobiano de las seis condiciones de indiferencia. No se afirma que un equilibrio mixto sea estricto.

En ese equilibrio, el gradiente ordinario del retorno privado es cero. Sin embargo, la ecuación8 de Advantage Alignment produce un campo βγ^3/4 en cada uno de los dos logits terminales del jugador1. El jugador2 no cambia su política en ese paso. Tras un paso simultáneo de tamaño α, el primero pasa a tener media terminal m=tanh(αβγ^3/8). El segundo puede escoger z=+1 y g=−1 y obtener una ganancia de mejor respuesta exactamente igual a γ(1+c)m. Es positiva para α,β,γ>0. El perfil resultante ha abandonado el conjunto de equilibrios Nash.

En el caso registrado γ=.9, β=.3, α=.1, c=.1, cada componente terminal es .054675 y la ganancia de desviación es .0027064057579956335. La magnitud depende de la escala del juego y del paso; el signo positivo basta para refutar la conservación universal bajo ese operador. El control c=0 da el ejemplo mínimo; c=.1 elimina las acciones irrelevantes y descarta que el efecto dependa exclusivamente de un conjunto plano de equilibrios.

## Cómo se descartaron errores de implementación

Se enumeraron las16 trayectorias posibles y las8 políticas Markov deterministas de cada jugador para calcular sus mejores respuestas. La prueba principal contiene320 configuraciones deterministas, cruzando dos valores de c, cuatro descuentos, cuatro intensidades, dos variantes de la fórmula y cinco tratamientos de ventajas. No son320 observaciones independientes ni justifican un contraste estadístico con ese tamaño muestral.

Además, se extrajeron por AST los cuerpos originales de cuatro funciones de los autores: cálculo GAE, términos de alineación, pérdida de alineación y pérdida del actor. Se verificaron los hashes de los archivos y se ejecutaron esos cuerpos sin modificarlos sobre el juego tabular, con valores privados exactos. Se sustituyeron las interfaces de red por probabilidades tabulares. Esto audita las pérdidas publicadas, no reproduce sus redes, entornos ni entrenamientos completos.

Las96 configuraciones con alineación producen movimiento y una desviación rentable; los48 controles sin alineación quedan inmóviles dentro de la tolerancia registrada. El resultado persiste con λ=0,.95,1, float32/float64, normalización de ventajas activada o desactivada y pérdida proximal o directa. Las variantes integradas y separadas tienen escalas diferentes; no se comparan sus pasos como si fueran idénticos.

Un enumerador escrito por separado en JavaScript comprobó los320 campos y las144 políticas posteriores de los auxiliares originales. Su discrepancia máxima en mejores respuestas fue 1.25×10^−16. SymPy confirmó exactamente el campo, los16 certificados de retorno unilateral cero, el determinante del equilibrio y la fórmula de regret. Esta triangulación reduce el riesgo de un error del programa, pero sigue siendo trabajo de la misma autoría. No sustituye la revisión por investigadores externos.

## El mecanismo: una esperanza condicional no puede trasladarse sin más al producto

Un análisis posterior al resultado registrado mantuvo las ventajas pasadas conjuntas y el gradiente privado ordinario, y sustituyó únicamente la ventaja actual del oponente por su esperanza respecto a la acción del jugador que aprende. Con acciones actuales independientes, ventajas separadas del grafo de gradiente y un peso pasado medible antes de actuar, esa sustitución deja un coeficiente independiente de la acción actual propia. La esperanza del score de una política normalizada es cero; por tanto, desaparece todo el término de alineación de la ecuación8.

En12 perfiles fuera del equilibrio, el gradiente ordinario permanece igual hasta error numérico, mientras la norma del término de alineación cae por debajo de 2.64×10^−18; con ventajas conjuntas era al menos .0239. La sustitución cambia el operador. No es una reducción de varianza que conserve la misma esperanza. La discrepancia no necesita ruido de muestreo ni un critic mal aprendido: aparece en la enumeración exacta de toda la distribución.

La condición sobre el pasado limita el argumento general: un retorno GAE pasado puede contener recompensas futuras, por lo que no siempre es medible antes de la acción actual. No se extiende la cancelación a cualquier implementación GAE. El fallo de conservación en los auxiliares originales fue comprobado por separado. También se distingue la fórmula conjunta de la lectura literal con una esperanza interior adicional que aparece en la ecuación66 de la prueba; esa lectura definiría otro coeficiente.

## Alcance para una sociología de agentes autónomos

Abandonar Nash no equivale a empeorar el bienestar: en un dilema social puede ser precisamente lo que se busca. V205 cuestiona una garantía matemática concreta, no el rendimiento empírico del método ni la posibilidad de cooperación. Tampoco contiene una institución aprendida. La relevancia para el TFM es metodológica y mecanística: la dependencia entre señales privadas puede generar una fuerza colectiva aun cuando las ventajas propias esperadas se anulen. Antes de atribuir esa fuerza a reciprocidad aprendida o estabilidad institucional hay que identificar qué información utiliza y qué campo de actualización produce.

La contribución candidata consiste en un contraejemplo analítico y una explicación causal de la discrepancia entre ventajas conjuntas y marginales. Su prioridad no está establecida. Una búsqueda pública acotada no encontró una corrección idéntica, pero el acceso al foro de OpenReview quedó bloqueado y la revisión de antecedentes no es exhaustiva. No se contactó con los autores. El historial CT2=61 permanece intacto; esta rama D2 carece de puntuación nueva y no recibe automáticamente ningún nivel AB.

La nota matemática completa, el protocolo previo, las fuentes propias, los resultados íntegros y las instrucciones de reproducción acompañan este capítulo. El programa conserva abiertas la adquisición de organización funcional y la validación externa: V205 resuelve una incertidumbre técnica importante, pero no las reemplaza.

Referencia principal: [Duque et al., Advantage Alignment Algorithms, ICLR2025](https://proceedings.iclr.cc/paper_files/paper/2025/hash/5185aa776fd64ae3b4c6dae1af1066b1-Abstract-Conference.html). Código contrastado: [repositorio de autores, revisión fija](https://github.com/jduquevan/advantage-alignment/tree/2065e43c0c36694965cf4476dc692512e3892dcc).
