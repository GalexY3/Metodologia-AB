# V175 — Memoria evolucionada y medición de riqueza colectiva

15/11/2026. Pregunta motivada por V173–V174, cuyos resultados se conocen. Estos demostraron capacidad de un observador PROGRAMADO; no que un agente descubra esa memoria. Esta cohorte no se ha ejecutado al redactar el protocolo. Congelación remota prevista antes del entrenamiento, en rama separada de los cambios previos del usuario.

## A. Estimando y alcance

En el juego de recurso renovable de Itao y Kaneko (arXiv:2507.22555v2, noviembre de 2026), ¿pueden evolucionar políticas con memoria genérica y sin medir riquezas ajenas que superen a políticas sin estado interno adicional? Fitness: riqueza individual media de pasos100–999; Q es la suma media de riquezas por grupo, no porcentaje de cooperación ni resultado humano. Unidad independiente: semilla de evolución, NO grupo, agente, generación o tiempo. El piloto tiene dos semillas nuevas y no permite inferencia poblacional ni acreditación2/3.

## B. Antecedentes y rivales

El artículo ya prueba RNN de4unidades con entradas recurso, riqueza propia y riqueza colectiva (Fig.S2), y por separado políticas sin señal de pares (Fig.S15). No se encontró en el texto el cruce RNN×ausencia de medición social. Eso es una lectura localizada, no prueba de prioridad universal. Nuestro RNN será una especificación explícita estándar, no reproducción fiel de un algoritmo cuyos detalles completos no están en el código disponible. Monitoreo público, memoria recurrente y observadores son antecedentes, no novedades que atribuirse.

Rivales: la medición social es decisiva en esta arquitectura; la memoria del recurso sustituye su información; el filtro programado estaba resolviendo casi todo el problema; o el optimizador es incapaz de aprender redes de mayor dimensión incluso CON riqueza colectiva. Alta eficiencia puede ser un temporizador sin respuesta a infractores: por sí sola NO acredita una norma institucional.

## C. Diseño prospectivo de capacidad

Dos semillas175115,175116; N100grupos×M5personas,3000generaciones,1000pasos por generación, con reagrupación aleatoria entre generaciones. Mismo crecimiento R(x)=2x−x²,β=.9/M,κ=.25, recursos iniciales.1 y riquezas(1+N(0,.1))/M. Reproducción de exactamente500descendientes con probabilidad proporcional al fitness individual, mutaciónGaussiana.1 por gen, sin retorno grupal en la selección de una persona. El evaluador central necesita calcular las probabilidades de reproducción, como en el antecedente; no entregar fitness ajeno como entrada a la política.

Cinco condiciones, todas con cromosoma de37números para mantener una cinta aleatoria y dimensiones de muestreo comunes; los genes inactivos son neutrales, sin coste de complejidad:

1. LINEAR_FULL: regla original χ(x+S M y_i+A Σy). Solo primeros2genes activos. Control de física y de capacidad de la selección.
2. RNN_FULL: h_t=tanh(W_in [x,M y_i,Σy]+W_rec h_(t−1)+b); acción χ(w_out·h_t+b_out),4unidades,37genes. Estado inicial0. Riqueza colectiva solo disponible aquí y en LINEAR_FULL.
3. RNN_RESOURCE: mismo cromosoma y red, tercera entrada0. Solo recurso y riqueza propia observables; no información privilegiada de acciones ajenas, crecimiento, κ o extracción total. La recurrencia puede evolucionar; no se suministra el observador contable.
4. MLP_RESOURCE: idéntica representación genética aRNN_RESOURCE pero se ignora h_(t−1) al calcular la acción. Control con estado mental reiniciado, mismo presupuesto; riqueza propia conserva su memoria física. Los16genes recurrentes son neutrales en esta condición.
5. FILTER_RESOURCE: regla χ(x+S M y_i+A m_i), donde m_(t+1)=sigmoid(λ)m_t+b x_t+c x_t²+d x_(t+1), m0=0. Seis primeros genes evolucionan desde valoresN(0,.1); el resto es neutral. No se dan coeficientes de conservación ni etiquetas de riqueza colectiva. ES una familia de filtros estructurada por el investigador, con recurso cuadrático como característica diseñada; un éxito exclusivo aquí NO demostraría descubrimiento por memoria genérica ni originalidad del observador. Coeficientes verdaderos de V174 no se usan para inicializar, mutar o escoger políticas.

Inicialización de todos los genesN(0,.1). Misma semilla y consumo de números aleatorios por condición; los historiales y probabilidades de selección se separan como consecuencia de la intervención. Guardar población, curvas, hashes y RNG en checkpoints cada500generaciones. Evaluación principalQmedio de últimas500generaciones. No seleccionar el mejor checkpoint ni cambiar semilla, mutación o arquitectura tras mirar los resultados.

## D. Auditoría antes de entrenar

Motor independienteNumba float64, sinfastmath, frente a NumPy de referencia para las cinco condiciones y frente a `play_generation` original para LINEAR_FULL. Comprobar todos los pasos de las trazas de acciones, física y fitness con estados y políticas aleatorios; no entrenar aún. La comparación se limita a física y ejecución, no a replicación científica independiente. Confirmar que alterar riqueza de otros sin cambiar x ni ypropia no cambia las acciones deRNN_RESOURCE,MLP_RESOURCE,FILTER_RESOURCE en ese instante, y que la tercera entrada deRNN_FULL sí puede hacerlo. La evolución deFILTER_RESOURCE no recibe objetivos de estimación de riqueza.

PrioridadBelowNormal y afinidad de seisCPU verificadas con firmasWindows de64bits, con3threadsNumba porworker y máximo2trabajos. Numba.68/llvmlite.50 se instalan sin cambiar NumPy2.5.4 niPyTorch. Las pruebas de instrumentación son anteriores a la congelación remota; NO son resultados de la cohorte.

## E–G. Ejecución, crítica y límites inferenciales

Primario de capacidad: RNN_RESOURCE Q≥.70 y RNN_RESOURCE−MLP_RESOURCE≥.15 en AMBAS semillas. Gate de diagnóstico: RNN_FULL≥.70 en ambas; si falla, un resultado negativo deRNN_RESOURCE no identifica insuficiencia informacional. Control LINEAR_FULL debe alcanzar≥.70; si no, investigar implementación o condiciones y no llamar confirmada la física solo por una gráfica.

FILTER_RESOURCE≥.70 con RNN_RESOURCE<.70 apoya únicamente capacidad de un filtro estructurado y delimita un problema de búsqueda/representación. Mostrar las diez corridas completas y todo criterio fallado. No pruebas de significación con generaciones o grupos como réplicas; dos semillas son piloto. No son nuevas observaciones humanas ni validación de la ventaja sociológica de evitar monitoreo.

Tras un positivo de memoria genérica, el siguiente experimento independiente será lesiones de memoria y explotación por agentes invasores, y una cohorte nueva con el mecanismo ya congelado. Si solo mejora el filtro o ambas redes fallan, no ampliar automáticamente a decenas de variantes: revisar el mecanismo y el optimizador con un rival competente. No interpretar una red eficaz como reconstrucción deZ sin medirlo; cualquier probe con etiquetas deZ será diagnóstico separado y no entrenamiento.

## H–J. Dictamen y gobernanza

BRANCH D1 de la rama ecológicaV173: cambia infraestructura cognitiva conocida por memoria evolucionada, conserva generador y estimando. CT2histórico del programa61 permanece sin aumento; rama nueva no recibe puntuación por sumar semillas. N2=N3=0,N1históricoNOT_AUDITED. Confirmación independiente externa y prioridad siguen pendientes. Autorización amplia de investigación vigente; no pedir un cupo por fórmula. No modificar resultados antiguos ni el índice local del repositorio para publicar. Si el análisis fuese conocido o la ventaja desaparece frente al control, conservar negativo y STOP_LOCAL a la reivindicación correspondiente.
