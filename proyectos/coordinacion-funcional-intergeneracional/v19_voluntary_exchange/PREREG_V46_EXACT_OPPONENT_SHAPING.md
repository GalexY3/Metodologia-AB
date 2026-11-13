# V46. Aprendizaje con anticipación del aprendizaje ajeno en relaciones diádicas

Preregistro prospectivo. Fecha 13/11/2026. Creado **antes** de entrenar V46. Los experimentos anteriores V41–V45 fracasaron al exigir retorno causal privado positivo de una donación unilateral, pese a identificar una estrategia cooperativa contrafactual viable en V42.

## Fundamento y pregunta

Se contrasta la hipótesis de que el obstáculo crítico es el gradiente miope del aprendizaje privado independiente. Un individuo puede mejorar su retorno esperado al donar si esa acción modifica la probabilidad de que la contraparte coopere en el futuro, y los agentes de V44–V45 no aprendieron en la práctica ese mecanismo. El método LOLA propuesto por Foerster et al. (2018) diferencia el valor propio respecto a un paso de aprendizaje anticipado del adversario, incluyendo un efecto de modelación de sus gradientes. Letcher et al. (2019) advierten que LOLA puede ser inestable, por lo que se incluirá un control con mirada al futuro sin derivada de segundo orden.

Fuentes:
- Foerster, J. et al. (2018). *Learning with Opponent-Learning Awareness*. AAMAS. https://arxiv.org/abs/1709.04326
- Letcher, A. et al. (2019). *Stable Opponent Shaping in Differentiable Games*. ICLR. https://arxiv.org/abs/1811.08469

**RQ46.** ¿La anticipación explícita de la actualización de la contraparte permite desarrollar una cooperación individualmente rentable en un juego de regalo repetido donde los agentes solo maximizan recompensa propia?

## Entorno y parametrización

Se conserva el subsistema material de V44 con 48 personas emparejadas en 24 parejas disjuntas de oficios complementarios asignados, b=0,20, v=0,55/3, coste de donar c=0,04, duración máxima T=48, probabilidad de continuación por mundo q=0,95 y descuento gamma=0,995. No existe contrato, sanción programada ni recompensa social. Las profesiones y parejas son fijas: este diseño estudia **solo** reciprocidad, no división endógena del trabajo.

Cada agente posee cinco parámetros logit privados: probabilidad de donar en el primer turno y probabilidades de donar en función del estado (última decisión propia, última decisión de la pareja) para los cuatro estados 00, 01, 10 y 11. El agente observa únicamente sus acciones previas y las recibidas, como en V44. No se comparten parámetros ni gradientes entre agentes.

La expectativa descontada del alimento propio se calcula **exactamente** mediante una cadena de Markov diferenciable de cuatro estados y horizonte48, con supervivencia q. La matriz P por pareja contiene productos de Bernoulli de ambas decisiones. Desde t0, se integra el primer regalo y todos los estados futuros durante T turnos: J_i = r_i(t0) + beta * pi0 @ [sum_{k=0}^{T-2} (beta P)^k] r_i, donde beta=gamma*q. La expresión se valida por enumeración exhaustiva en horizontes pequeños y por Monte Carlo de episodios antes de entrenar. La capacidad de computar expectativas exactas es una **ventaja de laboratorio** no disponible para los individuos en sistemas sociales reales.

## Tratamientos

Cada política empieza con logitos independientes cercanos a cero, sin sesgo inicial prosocial, y es entrenada para maximizar exclusivamente J_i. Cuatro semillas de inicialización neuronal 3111,4111,5111,6111.

1. **NL exacto**: gradiente de J_i con respecto solo a los cinco logitos de i, congelando j en la derivación.
2. **LOLA exacto one-step**: el individuo i estima el próximo cambio de los parámetros de j en dirección al gradiente privado de j, θ'_j=θ_j+α∇θ_j J_j(θ_i,θ_j), y maximiza J_i(θ_i,θ'_j) *diferenciando también a través de la influencia que i ejerce sobre ese gradiente*. Se contrasta α∈{0, 1, 5, 20}. α=0 coincide con NL y se ejecuta una única vez por semilla, no duplicado.
3. **LookAhead sin shaping** (si se implementa y supera paridad): igual paso hipotético del otro, pero la actualización del otro se trata como constante durante el cálculo del gradiente de i. Es un control adicional del término de segundo orden, no evidencia externa de cooperación.

El optimizador real se mantendrá idéntico entre condiciones; el α indicado representa la magnitud del aprendizaje de j **anticipado**, que puede diferir del paso real de Adam. El reporte distinguirá esta hipótesis de modelización y no llamará a la política «plenamente informada» sin esta salvedad. Entrenamiento inicial preregistrado: 1000 actualizaciones, Adam lr=0,03, sin regularización prosocial y sin selección del mejor checkpoint. Los pares se actualizan simultáneamente.

Controles negativos: q=0,20 para el nivel de α que resulte más favorable **seleccionado solo a partir de la especificación analítica y las hipótesis antes de examinar resultados**, o, preferiblemente, los 4 niveles de α bajo q0,20 para ambas semillas3111 y4111. Se distingue esta segunda extensión de la prueba primaria. La ausencia de ayuda rentable bajo q0,20 es una predicción sobre esta arquitectura, no una imposibilidad absoluta.

## Evaluación y criterio de éxito

Primario: la diferencia exacta J_i(force t0 donar)−J_i(force t0 no donar), con el compañero libre, recompensa propia descontada y políticas fijas, debe ser positiva en ≥24/48 individuos y en ≥3/4 semillas de al menos un α distinto de cero. Se exige además tasa de donaciones mutuas >0,25 por agente-ronda vivo y alimentación media superior a la de NL de la misma semilla en ≥3/4 semillas. Los tres criterios son necesarios. Esta regla evita declarar éxito si el algoritmo genera ayuda masiva solo por sobreoptimismo de actualización ajena.

Secundario: sensibilidad conductual p(donar|compañero donó)−p(donar|compañero no donó) bajo mismo estado propio; prevalencia de convenciones recíprocas; beneficio material individual y colectivo por ronda, y robustez de los pesos en semillas ambientales nuevas de simulación Monte Carlo sin usarla para elegir mejores checkpoints. Auditar también políticas al cambiar el compañero por permutación del par, y ensayar 24 parejas reorganizadas para ver dependencia de identidades; no esperar generalización automáticamente.

Se registrarán los 1000 pasos y snapshots a 1,200,400,600,800,1000. Se guardan todos los pesos, Adam, semillas, hashes, scripts, pruebas y resultados, incluso si todos los tratamientos fallan.

## Riesgos y límites

LOLA dispone de las derivadas de retorno privado de su oponente, información excepcional en el laboratorio. Se comparará un gradiente exacto con el REINFORCE ruidoso de V44–V45 **sin afirmar que la diferencia causal sea exclusivamente la anticipación**; solo el contraste NL exacto contra LOLA exacto comparte representaciones y calidad de gradiente. La estimación de un paso anticipado no equivale a observar realmente el aprendizaje del otro ni a un contrato. No se atribuirá emergencia de cooperación a la sociedad completa si solo ocurre en parejas fijas.

No declarar «OBJETIVO COMPLETADO» sin transferir después la reciprocidad individual estable a un mundo con socios diversos, elección profesional libre y agentes nuevos.
