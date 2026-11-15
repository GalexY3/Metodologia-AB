# V183 — ¿Redistribución de incentivos o también protección material?

15/11/2026. Rama D2 de auditoría mecanística de un antecedente publicado, posterior a V181. La reproducción descriptiva V182 ya conoce los 1.200 ajustes originales de Yaman et al. (2023), sus normas y sus recompensas archivadas. Todavía no se han evaluado nuevas vidas con el port ni con la intervención de orden temporal. No presentar la auditoría del código como originalidad sociológica.

## A–C. Cuello de botella, hipótesis y rivales

La búsqueda anterior mejora el TFM, pero no ha acreditado una predicción novedosa y confirmada independientemente. Antes de proponer otra institución hay que entender un antecedente fuerte con precisión causal. En el código original de `settlement maintenance`, las transferencias ocurren antes de los ataques que destruyen recursos en lugares sin soldados. Aunque cada transferencia conserva recursos, una redistribución entre lugares con protección distinta puede cambiar cuánto sobrevive al ataque. Esto abre un canal material además del cambio en el aprendizaje. No se presume que los autores lo hayan negado ni que este principio general de seguros sea nuevo.

Predicción discriminante acotada: una parte apreciable del rendimiento de las normas originales depende de ese orden temporal. Rival nulo: las transferencias solamente cambian incentivos de aprendizaje en esta instancia; mover los ataques antes de las transferencias no produce una diferencia relevante en recompensas nuevas. Un efecto negativo o nulo refuta la dirección propuesta y se conserva.

Identidad condicional previa a los experimentos: dados papeles, ingresos materiales r, transferencias ejecutadas con saldo neto delta y máscara de supervivencia A, la diferencia inmediata frente a aplicar cualquier redistribución conservativa después del ataque es `sum(A*delta)`. Como `sum(delta)=0`, si cada lugar sin protección es atacado con probabilidad p, su esperanza es `p*sum(P*delta)`, siendo P la máscara de protección. No confundir esta identidad de un paso con una descomposición aditiva del efecto de toda la trayectoria de aprendizaje.

## D–F. Muestra, intervención y análisis congelados

Usar TODAS las 300 normas archivadas de settlement maintenance con lambda=0 o .2: 30 procesos por cada uno de los cinco entornos y dos regularizaciones. No seleccionar éxitos. Cada norma recibe ocho vidas nuevas, T=500, alpha=.1, epsilon=0, Q inicial=10, rejilla 10x10, mismos papeles, física y cantidades que el original. Semillas de cintas 183115–183122. Las normas se mantienen fijas; los papeles sí se aprenden de nuevo. No reoptimizar normas en este contraste inicial.

Dos brazos emparejados: ORIGINAL, transferencias antes de ataques; ATTACK_FIRST, ataques antes de transferencias. Mantener desgaste, limpieza, vecindad, presupuesto sin deuda, reglas y orden aleatorio de transacciones. Usar las mismas cintas por vida, norma y entorno con generadores separados para permutaciones y uniformes, de modo que cambiar el momento del ataque no cambie la aleatoriedad exógena. Cada norma es una historia de optimización original, no ocho observaciones independientes nuevas.

Primario: promedio igualmente ponderado de `R_ORIGINAL-R_ATTACK_FIRST` en los 180 procesos con p>0 (tres entornos x dos regularizaciones x treinta), con R media de los últimos 101 pasos. Son 30 semillas maestras originales reutilizadas entre seis contextos; no asumir 180 historias independientes. Gate de relevancia: diferencia >=.25 unidades por persona y paso, y límite inferior del IC descriptivo bootstrap jerárquico 95% >0. Remuestrear los 30 bloques de semilla original conjuntamente entre entornos/regularizaciones y las ocho semillas de vida (comunes entre procesos), 10.000 veces con semilla 183999. No elegir otro margen tras observar resultados. Mostrar también cada uno de los seis estratos y todos los procesos, incluidos signos contrarios. Bootstrap no equivale a confirmación externa.

Controles negativos: en los dos entornos con p=0, exigir igualdad de trayectorias emparejadas hasta redondeo <=1e-10. Comprobar conservación de recursos en transacciones y la identidad condicional anterior. Registrar, además, el cambio material inmediato bajo los papeles realmente elegidos en ORIGINAL y su esperanza analítica. Son diagnósticos secundarios; no rescatar un gate primario fallido con ellos.

Reproducción secundaria: comparar los resultados ORIGINAL nuevos con los valores de entrenamiento archivados, sin declarar equivalencia por falta de significación. Reportar sesgo de selección y dispersión por proceso; la comparación se conoce después de seleccionar las normas originales. No tratar estas normas elegidas como muestras aleatorias de todas las instituciones posibles.

## G–J. Auditoría, decisión y límites

Gate técnico previo: port epsilon=0 contrastado con ejecución del código MATLAB original en GNU Octave mediante seis cintas comunes, con igualdad de papeles, sanciones, conteos RNG y curvas (tolerancia numérica declarada). No ejecutar V183 si el gate falla. Publicar protocolo y hashes de código antes de nuevas vidas. Máximo dos workers, tres hilos como máximo cada uno, prioridad BelowNormal y seis CPU.

Si el primario falla, cerrar la propuesta de ventaja positiva del orden temporal en este conjunto. Si pasa, no concluir que el otro orden impide cooperación: las normas fueron optimizadas para ORIGINAL. Antes de una afirmación de superioridad estructural serían necesarios optimización competente en ambos órdenes, otra implementación y auditoría de originalidad frente a seguros, redistribución y aprendizaje por incentivos (incluido LIO). Estas obligaciones no se dan por cumplidas por ejecutar más semillas.

Institución impuesta: los agentes eligen papeles, pero las normas fueron seleccionadas con fitness de grupo y su cumplimiento es obligatorio. V183 no demuestra formación institucional privada. CT2 histórico permanece 61; N2=N3=0. La nueva rama no recibe una puntuación numérica automática. Conservar resultados negativos y no contactar autores sin autorización específica.
