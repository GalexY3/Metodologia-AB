# Lema local: invariancia respecto a una historia inicialmente irrelevante

Resultado deducido bajo supuestos, sin acreditación de prioridad original. Se refiere al juego público de capital y roles fijos V202 y a una actualización oracular exacta. No es un teorema sobre aprendices humanos o todos los algoritmos naturales.

Sea h la historia pública (recuento de pagos y último resultado físico). Supóngase que todos los jugadores tienen inicialmente políticas que dependen de su señal actual s, pero no de h. La historia no modifica directamente tecnología, pérdidas o distribución de señales. En consecuencia la recompensa esperada de cada jugador es constante entre historias. Como beta<1, la solución única de Bellman es `V_i(h)=r_i/(1−beta)`.

Una vez alcanzada la oportunidad GOOD, la diferencia entre pagar y no pagar es entonces

`A_i^pay(h,s)=−tau+beta{E[V_i(h'|pay=1)]−E[V_i(h'|pay=0)]}=−tau`.

La ventaja entre JOINT y AUTO también es independiente de h, aunque depende de s, pérdidas, otras políticas y pagos previstos. Para una Bernoulli con parámetro logit separado por historia y señal, escribamos p=Pr(acción=1), a=dp/dtheta y w la ocupación descontada del punto de decisión. El teorema de gradiente da `g=w a A`; la información de Fisher de esa decisión es `F=w a²/[p(1−p)]`. Su cociente es `F^+g=p(1−p)A/a`, independiente de h cuando la política es independiente de h. En la fase de pago w incluye la probabilidad de alcanzar GOOD conjunto; el mismo factor aparece en ambas expresiones y se cancela.

Para una mezcla exploratoria `p=epsilon/2+(1−epsilon)sigmoid(theta)`, a también es independiente de h. Con epsilon=0 la dirección natural del logit de pago es −tau. Con mezcla cambia su escala, pero no su independencia de la historia.

Los scores de fases y tiempos distintos tienen media condicional cero; sus covarianzas cruzadas desaparecen. Con logits tabulares separados, el Fisher causal descontado es diagonal. La pseudoinversa deja sin actualizar los parámetros no alcanzables y el pago inexistente del crítico. En esta parametrización y con soporte positivo, todos los demás puntos de decisión alcanzables tienen peso positivo. La proyección rectangular a [−12,12], aplicada de la misma manera a cada entrada, preserva la igualdad entre historias.

Por tanto, el campo natural exacto conserva el conjunto de políticas independientes de la historia. Lo preserva asimismo cualquier multiplicador temporal positivo por jugador que no dependa de h, y las actualizaciones deterministas por jugador que mantengan esa estructura. Esto no prueba nada equivalente para estimadores estocásticos: el ruido o una inicialización dependiente de h pueden romper la simetría.

Dentro de ese conjunto invariante, deshabilitar pagos cambia las transferencias y los registros, pero no las decisiones productivas. El efecto causal de retirar pagos sobre la tasa GOOD es cero. Por ello no puede aparecer el criterio funcional de V202, que exige una caída de tasa de al menos 0,10 al retirar pagos.

El gradiente euclídeo conserva el factor de ocupación w. Historias visitadas con frecuencias diferentes pueden separarse aun desde logits iguales. Eso no demuestra que vayan a formar cooperación: la integración registrada V203 comprueba esa trayectoria y su sensibilidad numérica.

La derivación usa gradientes de cada retorno propio manteniendo las políticas ajenas fijas en cada evaluación local. No incluye efectos de un incentivo sobre los siguientes pasos de aprendizaje de los demás, como los que estudian LOLA o LIO. Tampoco incluye inversión, movilidad o historias con efecto material directo.

Referencias metodológicas primarias: [Sutton et al., teorema de gradiente](https://papers.nips.cc/paper_files/paper/1999/hash/464d828b85b0bed98e80ade0a5c43b0f-Abstract.html), [Kakade, gradiente natural](https://papers.neurips.cc/paper_files/paper/2001/hash/4b86abe48d358ecf194c56c69108433e-Abstract.html). La métrica descontada y las decisiones jerárquicas se derivan aquí para este control; no se presenta como una ejecución del código experimental original de Kakade.
