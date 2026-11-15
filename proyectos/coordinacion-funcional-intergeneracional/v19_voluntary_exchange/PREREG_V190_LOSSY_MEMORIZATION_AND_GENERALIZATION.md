# V190 — Memorización social comprimida y generalización posterior

15/11/2026. V188 terminó:32entrenamientos, ocho historias emparejadas. Test medio FIXED_PROTOCOL .9911,REINFORCE .3227,URN_PURE .1797,URN_LIMITED .0425. Falla el gate prospectivo de transferencia; ningún aprendiz privado guarda checkpoint de memorización informativamente completa. No se ejecutan congelaciones sin su condición. V189verificó9600cotas de precisión y construyó un primer contraste; se conservó y revisó porque no igualaba frecuencias de las etiquetas. V189Bcorrige esa limitación antes de cualquier entrenamiento sobre los nuevos soportes.

## A–C. Pregunta causal y límites de novedad

El piloto anterior no entra en memorización completa, por lo que no puede decidir si existe generalización tardía después de ella. Cambiar la geometría de las interacciones permite separar la cantidad de datos de la información que exige un código eficaz. Pregunta: ¿pueden aprendices privados memorizar todas las interacciones con un código que pierde información y, mucho después, reorganizarlo para generalizar?

Las cotas de información, la coloración de grafos y la agrupación parcial de significados son antecedentes conocidos. No se presentan como teoremas nuevos. Un resultado candidato tendría que mostrar la dinámica aprendida de expansión del código tras memorizar, con separación frente al grokking de un receptor que recibe un diccionario adecuado. Los soportes son diseñados por el investigador; ninguna coloración o asignación de mensajes se entrega a los agentes privados.

## D–F. Diseño congelado

Cuatro pares de contextos certificados en `results/V189B_MATCHED_CONTEXTS/pair_0..3.npz`. Cada par tiene372ejemplos de entrenamiento y589de test,sobre Z31. Ambos soportes son simétricos y tienen12ejemplos por cada valor de a y b. Se igualan exactamente también las frecuencias de y. Las cuatro parejas varían la relación entre el grafo y la tarea aritmética. Hay dos semillas neuronales por pareja,190115–190122; la unidad contextual son cuatro parejas,no ocho contextos independientes.

En LOW el grafo de confusión tiene número cromático16,certificado por una coloración explícita y ausencia de triples independientes. En HIGH es completo y requiere31colores. En LOW una convención oráculo de16símbolos puede acertar todos los ejemplos conocidos; manteniendo esos aciertos,su máximo en test es124/589=21.05%. Este resultado es impuesto por el soporte, no emergencia. Solo se usó para verificar el entorno y no para inicializar políticas.

Dos métodos por cada soporte y semilla: FIXED_PROTOCOL,diccionario biyectivo aleatorio conocido,control individual; PRIVATE,el REINFORCE privado de V188. Mismos receptores de128unidades cuadráticas,AdamW .001,weight_decay1,betas(.9,.98); emisor tabla31x31,Adam .03,entropía .01,baseline privado .95.60000actualizaciones full batch. Solo cambia el soporte de ejemplos. El emisor observa a y acierto propio; no b,etiquetas ni parámetros/gradientes del receptor. El receptor recibe mensaje,b y su etiqueta posterior. Intereses comunes,canal y papeles siguen programados.

Evaluar cada100actualizaciones y guardar todos los resultados. No detener por test ni prolongar tras un negativo. Reportar precisión codiciosa y esperada,train/test,NLL,símbolos,entropía,cota informacional y pesos.

Gate de interpretabilidad: FIXED_PROTOCOL debe alcanzar test>=.95 en al menos6/8historias de cada soporte. De no cumplirse,no usar el fallo privado como evidencia de un fenómeno colectivo específico.

Entrada en el régimen de interés: cinco evaluaciones consecutivas con cero errores codiciosos de entrenamiento y menos de31símbolos. Guardar el primer checkpoint por historia sin mirar test. En HIGH ese régimen es imposible por construcción y debe servir de control de implementación; no contar su ausencia como descubrimiento.

Primario exploratorio de transición social con generalización tardía: en LOW,al menos4/8historias provenientes de al menos dos parejas deben entrar en el régimen anterior y después alcanzar cinco evaluaciones test>=.95,finaltrain=100%,finaltest>=.95,y31símbolos. Exigir t_gen>=5*t_mem_lossy y diferencia>=2000actualizaciones. Se evalúa el punto final60000; no elegir picos. Si falla,no declarar demostrado el fenómeno; conservar casos individuales y distinguir existencia anecdótica de robustez. La expansión del vocabulario sería necesaria por información,pero no demuestra por sí sola reorganización de varios cerebros neuronales: el emisor de este modelo es tabular.

Control matemático en cada evaluación: para el protocolo estocástico pi,la precisión sobre todos los pares uniformes no supera `sum_m max_a pi(m|a)/31`. De ello se deriva `Ntest*acc_test <= 31^2*Bpi-Ntrain*acc_train`. Para un protocolo determinista conKsímbolos,el techo esK/31. No confundir estas desigualdades conocidas con nueva evidencia empírica ni combinar métricas esperadas y codiciosas en la misma comprobación.

## G–J. Auditoría y decisión

Contrastar los nuevos índices por historia y el cálculo de métricas con receptores independientes; conservar aislamiento de gradientes verificado en V188. Congelar datos,código,protocolo y dependencias en remoto antes de entrenar. Un procesoGPU,dos hilosCPU,memoriaGPUlimitada al35%,BelowNormal,seisCPU y ventanas de descanso como V188.

Si se observa un candidato,las congelaciones usarán su checkpoint previo,con cota de información y presupuesto igualado,en una campaña separada. Si no se observa memorización o falla el primario,no seguir añadiendo variantes del mismo algoritmo para rescatar una etiqueta. Esta línea seguirá sin acreditar formación institucional material ni cooperación surgida de intereses opuestos. CT2histórico61,nueva rama sin puntuación,N2=N3=0.
