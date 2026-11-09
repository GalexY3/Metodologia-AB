# P0 — Factibilidad de coordinación funcional intergeneracional

**Estado:** diseño computacional exploratorio, anterior a ejecutar simulaciones. No se presupone que aparezcan equilibrio, generalización ni grokking colectivo. Se parte del concepto aportado por el usuario (ver QUEUE.md) sin haber verificado los DOCX/PDF originales citados en el pegado.

## Unidad y restricción de información

N=120 agentes en red no dirigida de anillo con conexiones ±1 y ±2 (grado 4). Una interacción/tick consiste en emparejamiento aleatorio máximo sobre las aristas: **ningún agente tiene más de una pareja por tick**. Cada par comunica solo el estado actual del otro (una etiqueta), sin acceder a contajes globales ni valores globales de recompensa.

Hay k funciones legalmente disponibles por episodio, 1≤k≤8 inicialmente. Un agente solo puede desempeñar una. Los agentes saben k pero no conocen cuántos individuos globales hay por estado. Mantienen memoria local ponderada de etiquetas observadas por comunicación (un número real por función, con descuento temporal); la memoria NO es un censo global. La dimensión variable k se resuelve mediante características compartidas por cada posible acción, no por una tabla fija de IDs.

La distribución inicial será deliberadamente desequilibrada: mayoría de 70% en estado0 y 30% entre el resto; para k=1, todos son0 y el episodio es un control trivial. Todas las reglas y métricas cuantitativas se fijarán antes de los barridos de semillas.

## Políticas y mecanismo de aprendizaje

Cada agente posee θ_i=[ponderación del estado poco observado, preferencia por permanecer, preferencia por imitar] y puede cambiar su función tras una comunicación. La política considera para cada color c las características [-frecuencia_local_observada(c), indicador_estado_actual, indicador_estado_del_vecino]. Se elige mediante softmax durante aprendizaje y argmax (con desempate conservador) en evaluación. Estas características incluyen **un sesgo inductivo programado de sensibilidad a la rareza local**, por lo que el aprendizaje NO inventa desde cero una solución universal.

La recompensa individual se calcula exclusivamente a partir de la observación/memoria individual al tomar la acción, como 1−frecuencia_local(c) menos pequeño coste de cambiar de rol, sin consultar el equilibrio global. Los agentes actualizan θ_i con REINFORCE de una acción, centrándola respecto a la recompensa media de su experiencia; las actualizaciones nunca utilizan las etiquetas/errores de un conjunto de evaluación global. Los agentes cuya política está congelada siguen observando estados y actualizando memoria, pero **no los parámetros θ**.

Controles: no cambiar estado; estados aleatorios con la misma restricción de comunicación; copia de pareja; heurística explícita de rareza local (diseñada a mano, no aprendida); política θ inicial sin entrenamiento; y política θ tras entrenamiento. Ningún baseline recibirá los contajes globales para elegir acciones. Un oracle global separado podría verificar factibilidad pero se etiquetaría como inadmisible para explicar emergencia; el algoritmo comprueba el mínimo matemático de desequilibrio discreto.

## Train, validación y test

Entrenar únicamente con episodios k=2,3,4 (k=1 es control), nuevas inicializaciones sesgadas y semillas de entrenamiento separadas. Los k=5,6,7,8 quedan **sellados durante ajuste de hiperparámetros** para la prueba de extrapolación. Comparar políticas entrenadas y sin entrenar con episodios test de mismas semillas, poblaciones y k. Evaluar además nuevas configuraciones de k=2,3,4 sin aprendizaje para discriminar memorización de episodio y transferencia.

En test **zero-shot de parámetros**, los agentes pueden observar vecinos y cambiar de estado pero no actualizar θ; memoria de comunicación sí se actualiza, y debe describirse como inferencia contextual, no ausencia total de adaptación. Medir separadamente un test con adaptación online, si se ejecuta después y se identifica como condición distinta.

## Criterios externos, no observables por agentes

Desequilibrio global TV=0.5 sum_c |n_c/N−1/k|. El mínimo discreto para N no divisible por k se calcula con cuotas floor/ceil. Churn=fracción de agentes que cambian color por tick. Estabilidad estricta: TV≤0.06 y churn≤0.05 durante 10 pasos consecutivos, con k>=2; k=1 control trivial. Distinción **equilibrio global** vs **diversidad de funciones locales**: riqueza media de etiquetas en el entorno relacional (ego+vecinos) normalizada por min(k,grado+1) y, como sensibilidad, entropía local normalizada por log(min(k,grado+1)).

Evaluación de episodios 150 ticks con mismo presupuesto de comunicación para controles; 10–20 semillas según coste. No seleccionar escenarios por resultados favorables. Informar medias, dispersión y tasas de estabilidad por episodio y por k, no tratar ticks emparejados como réplicas independientes.

## Relevo generacional

Solo si una comunidad alcanza un estado estable en un episodio, iniciar dos intervenciones desde el MISMO vector de estados y el MISMO grafo: (i) resetear θ/memoria del 25% de los nodos (pérdida de conocimiento, preservando colores), (ii) control sham preservando θ pero reseteando memoria, o (iii) reemplazo demográfico con nuevos colores (choque de composición), anotando cuánto se aleja del equilibrio. Medir pérdida inicial y tiempo a equilibrio sostenido tras 150 pasos, bajo la misma regla de aprendizaje en los recién llegados. Si los episodios nunca se estabilizan, informar que la etapa de reconstrucción no puede aún estimarse con validez, en lugar de inventar una recuperación.

## Controles de integridad

Tests automáticos: k=1; dominio de estados; N constante; número máximo de comunicaciones por agente ≤1/tick; reproducibilidad con semilla; ausencia de acceso global a partir de políticas; no entrenamiento de parámetros durante test congelado; la cantidad de cuotas enteras 1/k y el mínimo TV discreto; una prueba de permutation equivariance de características si se necesita; máscara de un nuevo color k+1 dentro de acciones legales.

## Qué cuenta como resultado

Es un **modelo social artificial simplificado**, sin datos observacionales humanos ni efectos de causalidad social identificados. El éxito de una heurística local preprogramada demostraría que la tarea puede resolverse de forma descentralizada, no que una norma social compleja apareció espontáneamente. El éxito de REINFORCE sería aprendizaje de ponderaciones sobre características diseñadas. Un fenómeno análogo al grokking requeriría tren alto, test bajo mantenido y después mejora tardía en test SIN entrenar con test; las primeras exploraciones P0 no lo garantizan y no deben afirmar su existencia.
