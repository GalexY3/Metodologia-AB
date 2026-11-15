# V194 — Capacidad del aprendiz binario con interlocutores correctos

15/11/2026. V192 terminó. V193 está ejecutando las congelaciones registradas; sus resultados no seleccionan los parámetros de este control. No se ha entrenado V194. Auditoría previa:408pagos de fixtures aleatorios, sin fallos, coincidencia entre cálculo directo del pago observado y tabla contrafactual. No se cuentan como evidencia científica.

## A–C. Incertidumbre y rival decisivo

V192 muestra generalización tardía en4/4pares privados con información contrafactual y fracaso de4/4pares con regresión bandit ponderada. Sus estimadores tienen el mismo gradiente esperado condicional, pero aún no sabemos si el aprendiz bandit puede resolver la tarea cuando el interlocutor ya es competente. El fallo puede ser genérico del aprendiz bajo feedback escaso y no un problema específico de interacción endógena.

Esta carencia debe resolverse antes de atribuir el contraste a un mecanismo colectivo o diseñar una institución de asignación de información. No se probarán aquí otras tasas, arquitecturas o variantes para rescatar al aprendiz. Es un control de capacidad de un algoritmo conocido, no una aportación original. Los antecedentes de crédito contrafactual y reducción de varianza siguen restringiendo la interpretación.

## D–F. Condición congelada

ORACLE_BANDIT_IS: los mismos cuatro bloques de datos e inicialización192115–192118de V192, dos redes por bloque. Cada una se enfrenta para su feedback a un interlocutor virtual que conoce f(a,b)=a+b mod31 y explora epsilon-greedy con epsilon=.1. El aprendiz recibe exclusivamente el pago de su acción realizada. Los interlocutores oráculo y su convención0se suministran externamente. Los dos aprendices reales se evalúan juntos, pero sus feedbacks proceden de dos ensayos con interlocutores virtuales independientes, como ORACLE_FULL de V192.

Reutilizar exactamente arquitectura, pérdida bandit, tasa, regularización, número de pasos y ley de exploración de V192:128unidades cuadráticas,31salidas Q, AdamW .001, weight_decay1, betas(.9,.98),60000actualizaciones completas. Cada red tiene384pares locales de entrenamiento y577retenidos. El término de pérdida es `(Q_U−r)^2/(31*q_U)` con probabilidad de muestreo desprendida del grafo. La función de pérdida no recibe f_i ni pagos contrafactuales.

La ley y el consumo de aleatoriedad coinciden con el control ORACLE_FULL: dos vectores de monedas por bloque y la misma permutación de emparejamientos en cada actualización. Los objetivos condicionales virtuales siguen así la misma secuencia. Las políticas de los aprendices pueden divergir y por tanto recibir distintos pagos observados. No se exige identidad de trayectorias.

La comparación de referencia es ORACLE_FULL original, que terminó con test conjunto1.0en los cuatro bloques. Se reutilizan raíces y contextos, no se presenta como confirmación independiente. La precisión conjunta se evalúa sobre productos cartesianos de entradas locales retenidas de ambos aprendices. Se guardan métricas cada100pasos y pesos, optimizadores y RNG cada5000. Sin selección de picos ni parada por test.

## G–J. Criterio, interpretación y decisión

El control de capacidad pasa si al menos3/4bloques terminan con test conjunto codicioso>=.95. Registrar también t_memtras cinco evaluaciones train>=.99 y t_gentras cinco evaluaciones test>=.95, precisiones locales bajo desfase elegido con entrenamiento y conducta exploratoria por separado. La prueba principal usa el punto final60000.

Si falla, no se atribuirá el fracaso PRIVATE_BANDIT_IS de V192 específicamente a aprender con interlocutores endógenos. Su estimador concreto no habrá demostrado capacidad con interlocutores correctos bajo este presupuesto. No se concluirá imposibilidad de aprendizaje binario ni superioridad universal del feedback rico. Cualquier estudio de asignación institucional o de ruido necesitará primero un rival bandit competente.

Si pasa, queda abierta una explicación de la dificultad por el feedback de interlocutores que todavía aprenden. Se podrá registrar un contraste nuevo con presupuestos de información igualados y antecedentes específicos; este control no lo demuestra por sí solo. El beneficio genérico de marginalizar acciones y reducir varianza no se presenta como nuevo.

Un procesoGPU, dos hilosCPU, BelowNormal,seisCPU,máximo35%memoriaGPU y descansos. No ejecutar simultáneamente con V193. Guardar código, registros previos y negativos. CT2 histórico61, rama nueva sin puntuación; N2=N3=0. Ni este control ni las convenciones del juego acreditan una institución material aprendida o una ley sociológica.
