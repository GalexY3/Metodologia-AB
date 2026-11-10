# V7. Prerregistro de pilotos sobre coordinación con recompensa exclusivamente colectiva

Fecha: 10 de noviembre de 2026. Se redacta antes de los pilotos científicos V7. Las ejecuciones denominadas smoke_* son verificaciones de ingeniería y no se utilizarán como evidencia ni para seleccionar el método ganador.

## Pregunta y alcance

¿Una política con decisión explícita de conservar el estado y memoria recurrente aprende mejor que la V6 en una tarea de selección endógena de k colores entre diez? ¿Puede la optimización de políticas poblacionales mediante perturbaciones antitéticas de parámetros mejorar la señal colectiva frente a REINFORCE? ¿La comunicación aprendida aporta una ventaja adicional respecto a agentes con la misma facultad de cambio autónomo?

Los resultados negativos anteriores justifican probar métodos distintos sin suponer que la cooperación vaya a emerger. El número de neuronas no mide literalmente razonamiento. V7 no afirma disponer de planificación simbólica ni de un módulo de razonamiento deliberativo.

## Entorno e invariantes

Diez estados posibles. Objetivos públicos k=2,3,4. Ningún color específico está impuesto como ganador. Para N divisible por k, éxito exacto equivale a ocupar exactamente k colores con N/k agentes por color. Métrica D_k=1-suma_{j=1..k} min(p_(j),1/k) sobre las frecuencias ordenadas de los diez estados. La topología es el grafo toroidal de cuatro vecinos ortogonales y un emparejamiento diagonal, grado 5, **no** un retículo snub-square geométrico.

Cada agente tiene pesos independientes, que no se copian ni promedian entre vecinos. Las observaciones son locales, salvo el indicador público de error/recompensa global; no se da el histograma poblacional total ni un crítico centralizado. Los individuos pueden quedarse o cambiar de color. Con --messages, aprenden a elegir destinatario entre sus cinco vecinos o silencio y a solicitar un estado; las peticiones transmiten solamente el estado solicitado y las frecuencias locales del emisor. Sin mensajes, ese canal está completamente desactivado. La llegada de una propuesta no obliga a obedecerla.

Recompensa temporal exclusivamente colectiva r_t=N*(D_k(t)-D_k(t+1)) + 0.25*(1-D_k(t+1)), con complemento terminal 2*(1-D_k(T)), idéntica para todos los agentes de la sociedad. **No hay recompensas individuales ni beneficio programado de imitar un vecino.** El algoritmo ES usa la suma descontada de esta misma recompensa como fitness colectivo. REINFORCE incluye regularización explícita de entropía; ES utiliza exploración paramétrica, de modo que no se equipara su mecanismo de exploración.

## Brazos, comparaciones y controles

- legacy: actor V6, sin puerta explícita de conservación, REINFORCE; control histórico.
- gated: nuevo actor por color, decisión binaria mantener/cambiar, sin memoria entre turnos, REINFORCE.
- gru: mismo actor y número de parámetros que gated, pero con memoria aprendida por cada agente y por color, REINFORCE.
- es: el mismo actor recurrente que gru, optimizado mediante ES antitético y fitness **global**, no crítico individual.
- Para contrastar comunicación, correr gru tanto sin --messages como con --messages con igual entorno, horizonte, tamaño, inicialización y semillas.
- Controles no entrenados: distribución uniforme continua entre diez estados, distribución uniforme seguida de inmovilidad; y política inicial sin entrenamiento.

Las etiquetas de los colores son intercambiables dentro del actor recurrente: comparte su función entre los diez canales, con pesos exclusivos para cada individuo. La memoria por-color se reinicia entre sociedades. Una puerta de conservación inicializada con sesgo -1 induce una probabilidad de **proponer** cambio inferior al 50% en un actor sin entrenar; es un sesgo arquitectónico declarado, no un comportamiento aprendido. El estado inicial aleatorio se trata como fuente de ruido y eventual ruptura de simetría, no como evidencia de coordinación.

## Fase exploratoria — pilotos, no prueba concluyente

N=36, malla 6x6, hidden=12 para los pilotos, 12 sociedades por actualización, 12 turnos por episodio, aprendizaje 0.0007 (AdamW), semilla de inicialización 6123. Piloto de 40 actualizaciones por brazo, a efectos de depuración, sin usarlo para concluir éxito. ES: sigma=.035, cuatro direcciones antitéticas, es_lr=.008 y ocho evaluaciones de fitness por actualización (más las evaluaciones de desarrollo). La comparación entre ES y REINFORCE exige informar además del coste computacional: sus actualizaciones consumen distinto número de episodios.

Evaluación de desarrollo: semillas fijas con base 700101, **96 sociedades nuevas por revisión**, 32 por cada k, horizonte de 32 turnos, política greedy con pesos congelados. Revisión cada diez actualizaciones, sin optimización con los datos de desarrollo. Al terminar se indicará D inicial/final, ocupación, éxitos exactos, estabilidad durante últimos diez turnos (D<=.02 y churn<=.05) y churn final. Las mismas semillas facilitan comparación apareada entre brazos, pero no son nuevas replicaciones de entrenamiento.

HOLDOUT reservado: no se abre en estos pilotos. Después de fijar arquitectura, presupuesto y varias semillas de entrenamiento se puede preregistrar una prueba final independiente con 100 o más sociedades por k; sus resultados no podrán usarse para seleccionar el modelo.

## Criterio antes de escalar

No se escalará automáticamente a 144 o 324 agentes ni a un millón de episodios. Requerimos un descenso reproducible de D relativo a la distribución uniforme, una reducción real del número de colores ocupados hacia k y mejor estabilidad, sin depender exclusivamente de la inmovilidad. La comparación con los controles iniciales y congelados es obligatoria. Un piloto con ausencia de señal justifica revisar el estimador o la arquitectura, no entrenar un millón de episodios iguales.

## Integridad técnica

Tests unitarios previos incluyen: definición exacta de D; no filtración de mensajes en brazo sin comunicación; gradientes cero en parámetros de individuos no implicados al derivar la log-probabilidad de uno; equivalencia al renombrar etiquetas; reinicio de memoria; reproducibilidad del desarrollo; y gradientes/actualizaciones finitas. Checkpoints e historial se escriben por brazo en runs/<nombre>. Se conserva V6 intacta, incluida su ejecución detenida y sus checkpoints.

**Límites de inferencia:** la muestra de 36 agentes es piloto de ingeniería y posibilidad de aprendizaje, no evidencia de transferencia al régimen N=324. Que una arquitectura no aprenda bajo este presupuesto no refuta la posibilidad de coordinación colectiva. La difusión y las acciones están modeladas, pero no constituyen negociación lingüística libre.
