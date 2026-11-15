# V188 — Un rival clásico competente en la tarea neuronal

15/11/2026. V187 terminó con93/100 poblaciones LIMITED35 por encima de99% de precisión comunicativa, frente a0/100 PURE; medias .99776 y .743886. Pasa su gate previo. Es una reimplementación basada en el artículo de Spike etal2017, no ejecución de su código original, cuyo enlace devuelve404.

## A–C. Incertidumbre y controles

¿El cuello de botella V185–V186 persiste al sustituir REINFORCE por aprendizaje de convenciones con mecanismos clásicos? No afirmar nuevo el aprendizaje de señales, el olvido o el grokking individual. La transferencia desde agentes simétricos de urnas a un emisor y un receptor neuronal no está garantizada por V187.

Mantener la tarea `(a+b)mod31`, partición387/574 de V185, arquitectura y optimización del receptor. Ocho semillas nuevas188115–188122, inicializaciones del receptor emparejadas entre condiciones,30000actualizaciones full batch. Cada semilla mantiene parámetros y estados propios; agrupar los cálculos en un tensorGPU no comparte parámetros entre historias. El conjunto de test ya es conocido del piloto: nuevas semillas no son una confirmación independiente externa.

Cuatro condiciones:

- FIXED_PROTOCOL: diccionario biyectivo aleatorio fijado, control individual.
- REINFORCE: emisor de V185 con feedback binario,baseline privado,Adam .03,entropía .01.
- URN_PURE:31x31 conteos iniciales uno; probabilidad proporcional a la fila. Añadir un ejemplar `(a,mensaje)` por acierto; conservar todos.
- URN_LIMITED: mismo aprendizaje, con1345ejemplares como máximo por emisor, `floor(1.4*31*31)`. La razón1.4 reproduce la de35/25del caso clásico. Al añadir, borrar uniformemente un ejemplar anterior; si una fila queda vacía, muestrear uniforme. No imponer exclusividad entre significados ni reparar colisiones.

La adaptación a minibatches es explícita: muestrear mensajes de la política anterior al batch, observar los aciertos propios y aplicar sus refuerzos en orden aleatorio. El emisor no recibe b,etiqueta,gradientes ni estados del receptor. Generar por interacción tres uniformes con generadores separados por semilla: mensaje,borrado y orden. Consumirlos también en condiciones que no usan todos. Las diferencias entre métodos no alteran el número de números exógenos consumidos. El receptor recibe mensaje,b y su etiqueta de resultado, como enV185. Intereses comunes,canal y papeles siguen impuestos.

## D–F. Criterios prospectivos

Principal de transferencia competente: URN_LIMITED test codicioso final>=.95 y test esperado bajo su política estocástica>=.90 en al menos6/8historias; mediana de ventaja codiciosa pareada frente aREINFORCE>=.20. Informar todas las32ejecuciones y todos los signos. URN_PUREes un competidor adicional; sus éxitos no rescatan un fallo del criterio principal del mecanismo con memoria limitada. Si REINFORCEfunciona en la cohorte nueva,se reduce el alcance del fallo del piloto original.

Evaluar cada100actualizaciones: train/test codicioso,NLL,precisión esperada con mensajes estocásticos,número de símbolos,entropía y techos Bayes por soporte. La evaluación esperada integra exactamente todos los mensajes para cada par; no sustituirla por el rendimiento de un diccionario codicioso.

Mantener el criterio descriptivo de grokkingV185: cinco evaluaciones seguidas train>=.99 para t_mem y test>=.95 para t_gen; exigir finaltest>=.95,t_gen>=5*t_mem y diferencia>=2000. Un cambio tardío de acierto no prueba creación súbita de un mecanismo ni grokking específicamente colectivo.

Guardar un checkpoint causal por historia de URN_PURE y URN_LIMITED cuando se complete por primera vez una ventana de cinco evaluaciones con train codicioso>=.99 Y31símbolos distintos. La condición no depende de test. Estos checkpoints habilitarán congelar una convención ya informativamente completa sin introducir una reparación externa. Guardar pesos,optimizadores,urna y RNG; no ejecutar congelaciones durante la campaña base ni elegir el punto después de ver su test. Si no hay checkpoint elegible,se registra la ausencia.

## G–J. Validez y decisión

Antes de la campaña, comparar cálculos GPUagrupados con receptores independientes en doble precisión para salidas,gradientes y un pasoAdamW. Verificar que un objetivo de una historia no genera gradientes en otras y que el objetivo del emisor no atraviesa el receptor. Comparar actualización de urnas con referencia Python y conservación del número de ejemplares. La prueba del mecanismo clásico no equivale a paridad completa con el artículo ni a nueva evidencia sociológica.

Publicar código,protocolo y hashes antes de entrenar. Un procesoGPU y dos hilosCPU,BelowNormal,seisCPU. Conservar negativos; no ampliar capacidades o presupuestos para rescatar un gate. CT2histórico61 sin incremento,N2=N3=0,nueva rama sin puntuación. Tras la campaña, elegir la siguiente intervención por el cuello causal observado, no por la conveniencia de llamar colectivo a un efecto individual.
