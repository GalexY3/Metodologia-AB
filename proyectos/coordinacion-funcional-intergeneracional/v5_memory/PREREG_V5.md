# V5 — ¿Memoria local y mayor capacidad permiten aprender coordinación colectiva?

**Registro experimental previo a ejecutar el primer entrenamiento V5 (10/11/2026).** Se conoce el resultado negativo de V4 y del piloto diferencial V4D; V5 es una exploración posterior, no una repetición confirmatoria. No elegir modelos a posteriori.

## Objetivo inalterado

N=36 individuos auténticamente independientes, red geométrica con hasta cinco vecinos directos. Cada persona puede cambiar libremente entre diez estados, enviar hasta una petición a un vecino y recibir varias propuestas; el objetivo es seleccionar endógenamente **exactamente k estados entre diez**, con cuotas de 1/k, para k=2,3,4. Todos reciben feedback global común; ningún actor ve recuentos mundiales, peso de otro agente ni mérito individual. La única recompensa de aprendizaje es la usada en el V4 original, `r=-D_k(t+1)-0.03·churn_t`, sin cambiarla mientras se evalúa arquitectura. El optimizador y feedback no se modifican entre brazos.

## Qué se entiende exactamente por memoria y «razonamiento»

- **Memoria explícita W8:** cada actor conserva la secuencia ordenada de hasta **ocho observaciones temporales propias**, incluyendo su color, frecuencia de cada color entre vecinos visibles, mensajes recibidos, sugerencias enviadas por él, feedback global y k. Se almacenan representaciones por candidato de color, NO los censos del mundo ni información que un actor no podía observar. Al comienzo de cada episodio se resetea a ceros. W1 observa solo el turno actual, sin acceso a historial pasado. La memoria es un buffer de historial, no una GRU; las dimensiones temporales se alimentan a un MLP entrenable.
- **Capacidad H64 frente a H128:** 64 u 128 unidades ocultas por capa para procesar cada opción de color. **Profundidad fija de dos capas ocultas** en las cuatro condiciones; las capas neuronales realizan transformaciones no lineales, pero no se considera que tengan planificación causal o deliberación simbólica. No atribuir «razonamiento» solo por tener más neuronas.
- La misma red interna de cada persona puntúa las diez etiquetas a partir de características relativas a cada candidato; pesos compartidos entre opciones de ESA persona para conservar **equivariancia por permutación de etiquetas**, pero pesos θ_i distintos y gradientes independientes entre personas. Memoria también se transforma al permutar etiquetas y conserva el orden temporal.
- Para los mensajes, la política compara potenciales destinatarios entre los vecinos directos y puede pedirles cualquier estado; las memorias guardan las peticiones que envió y recibió previamente.

## Diseño factorial, fase piloto

Cuatro condiciones, **todas con comunicación C2** (no se puede inferir causalidad comunicativa a partir de ellas; comparar C1 posteriormente si hay una señal de estrategia). Semilla apareada 521 para todas, 36 agentes, batch=12 mundos (4 de cada k), 32 turnos/episodio, `gamma=.98`, Adam lr=.001, `entropy_beta=.0005`, normalizador de ventajas 10, `grad_clip=10` por individuo, baseline LOO calculado solo con otros mundos del mismo k, recompensa `level` con coste churn .03:

| Nombre | Memoria observacional | Ancho neuronal | Capas ocultas |
|---|---:|---:|---:|
| W1-H64 | 1 turno | 64 | 2 |
| W1-H128 | 1 turno | 128 | 2 |
| W8-H64 | 8 turnos | 64 | 2 |
| W8-H128 | 8 turnos | 128 | 2 |

**Presupuesto piloto: 150 actualizaciones por condición** (1.800 episodios por configuración); checkpoint final fijo y registros de desarrollo a 1,50,100,150. Si los cálculos son costosos, el checkpoint disponible anterior al objetivo es exclusivamente técnico, no una conclusión final. Estas corridas prueban viabilidad técnica y orientación inicial de aprendizaje; 150 no bastan para declarar que un diseño nunca aprenderá. Los mundos de desarrollo usan seeds fijos distintos de la formación.

## Evaluación piloto reservada tras cuatro checkpoints finales

100 sociedades independientes por k y arquitectura, 100 turnos de evaluación, semillas `7200000+100*k` fijas y comunes a las cuatro configuraciones. Las políticas se evalúan congeladas, con memoria puesta a cero al comienzo de cada mundo; NO se entrenan en test. Bloqueo SHA256 de scripts/modelos y registro del protocolo antes de ejecutar. **Controles incluidos antes de entrenar:** para cada una de las cuatro arquitecturas evaluar el modelo entrenado y el mismo modelo SIN ENTRENAR, tanto con muestreo estocástico como mediante argmax determinista; incluir aleatorio siempre activo, aleatorio 24 turnos y después detenerse, e inmóvil. Estas comparaciones no suponen «planes» aprendidos. **Ablación adicional fijada antes del test:** para los modelos W8 entrenados, evaluar también una condición `no_history` que borra su buffer antes de cada turno, sin alterar pesos ni mensajes. Esto mide dependencia funcional de la información histórica de ESTAS políticas y conlleva cambio de distribución; no demuestra que la memoria sea necesaria en toda arquitectura. Métricas: D_k final, D/E[D_IID10] estimada por Monte Carlo con seed fijo, número de estados ocupados, soluciones exactas, estabilidad sostenida diez turnos, churn, AUC del error y curvas 0..T.

**Inferencia:** una única semilla de entrenamiento permite solo un piloto diagnóstico, no comparación estadística generalizable. En cualquier mejora observada, se exigirá repetir seeds de θ y evaluar perturbaciones nuevas sin seleccionar el mejor resultado. La memoria y el ancho son manipulaciones ortogonales, pero con una sola seed no puede estimarse una interacción fiable.

## Controles de implementación que deben pasar antes del entrenamiento

1. Cada θ_i es independiente; ∂logπ_i/∂θ_j=0 para j≠i.
2. Permutar consistentemente cualquiera de los diez nombres de estados produce logits y recuerdos permutados de modo idéntico, sin memorizar colores absolutos.
3. La memoria de i depende solo de sus observaciones y mensajes efectivamente recibidos. No puede filtrarse el snapshot de quien no envió nada ni el histograma de la sociedad.
4. W8 conserva los últimos siete estados temporales después de iniciar el turno siguiente; W1 carece de esa información. La memoria se reinicia entre mundos.
5. Ningún crítico centralizado, reward marginal por individuo, heurística programada de reparto o regla de parada global entra en la política.
