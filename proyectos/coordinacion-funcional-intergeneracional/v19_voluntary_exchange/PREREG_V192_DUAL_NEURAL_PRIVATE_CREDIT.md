# V192 — Dos redes, feedback privado y generalización de funciones locales

15/11/2026. Registro antes de cualquier entrenamiento científico V192. V191/V191B son fixtures:18contrastes numéricos exactos de pérdidas, gradientes y factorización;1848entradas de tablas de pago; aislamiento y pasos sintéticos GPU. Se conservan el primer generador que omitió una etiqueta y el error de serialización de un booleano NumPy. Se corrigieron antes del registro. Ningún fixture es una réplica científica.

## A–C. Problema y antecedentes

V190 se cerró como vía para identificar grokking colectivo: tenía un emisor tabular, solo un receptor neuronal y todos los valores locales del emisor ya conocidos. La nueva pregunta cambia esa limitación: ¿pueden dos redes con observaciones separadas aprender una convención que generaliza cuando ambas afrontan entradas locales nuevas? ¿Difiere el resultado al variar la información de crédito manteniendo igual el gradiente esperado de regresión?

La coordinación entre redes por aprendizaje mutuo tiene antecedentes fuertes (Kinzel/Kanter2002; Klein et al., NIPS2004). COMA (Foerster et al.,2018) ya aborda crédito contrafactual con un crítico centralizado; Expected Policy Gradients (Ciosek/Whiteson) ya marginaliza acciones para reducir varianza. El muestreo por importancia y la regresión de pagos no son algoritmos nuevos. No se presenta el contraste como ejecución de esos programas ni como superioridad frente a ellos.

Una curva tardía del par será solo un candidato descriptivo. Para atribuir necesidad de coadaptación habrá que seguir con intervenciones y excluir explicaciones individuales. Ninguna semilla interna, equivalencia algebraica o fixture acredita2/3.

## D–E. Diseño congelado

Juego de una etapa, dos agentes, P=31. Cada agente observa x_i=(a_i,b_i) y elige u_i. Ambos reciben el pago binario común1 si u_A+u_B=(a_A+b_A)+(a_B+b_B) mod31. Los datos locales ajenos, las etiquetas f_i=(a_i+b_i) mod31 y los parámetros del otro agente no se entregan a los aprendices privados. El entorno conoce el estado para calcular los pagos. No hay gradiente entre agentes ni parámetros compartidos. Los intereses comunes, la pertenencia al par, la tarea y el feedback siguen impuestos; no es una institución material inventada por los agentes.

Cuatro bloques independientes, semillas192115–192118. Cada bloque cambia contexto e inicialización, por lo que no separa sus efectos. Cada agente tiene384pares locales de entrenamiento y577retenidos. Se muestrean192pares no ordenados fuera de la diagonal y se incluyen sus inversos en la misma partición; las diagonales quedan retenidas. Se condiciona la selección a observar todos los valores marginales y etiquetas. Solo se rechazó el primer candidato del contexto192003 por no cubrir todos los valores, antes de entrenar; se conserva. Los datos reales están en `results/V191_DUAL_NEURAL_AUDIT_V2/context_s192115..192118.npz`.

Cada agente tiene128unidades cuadráticas y embeddings separados para a y b, con31salidas Q. AdamW lr=.001, weight_decay=1, betas(.9,.98). Sesenta mil actualizaciones completas, evaluación cada100, pesos cada5000. Política epsilon-greedy con epsilon=.1. Los parámetros e hiperparámetros son iguales entre condiciones; no habrá búsqueda ni ampliación del horizonte tras observar un negativo.

En cada actualización cada entrada local aparece una vez y una permutación aleatoria empareja las entradas A/B. Ambos actúan antes de actualizarse. El investigador calcula medias sobre el producto cartesiano de entradas; no se usan las entradas retenidas para aprender. La precisión conjunta se calcula mediante las distribuciones de errores modulares, contrastadas con enumeración independiente en V191. El desfase de la convención para evaluar funciones individuales se elige con entrenamiento, nunca con test.

Tres condiciones previstas:

1. ORACLE_FULL: cada red se enfrenta para su feedback a un interlocutor virtual que ya conoce la suma local, con la misma exploración epsilon-greedy. Recibe todos sus pagos contrafactuales. Control positivo externo: la convención correcta está suministrada al interlocutor virtual. Los dos aprendices reales se evalúan juntos, aunque no se entrenen mutuamente en esta condición.
2. PRIVATE_FULL: ambos interlocutores reales aprenden. Cada uno recibe el vector de sus31pagos contrafactuales manteniendo fija la acción realizada del otro. El vector es un oráculo informativo diseñado externamente; no se da la etiqueta local verdadera.
3. PRIVATE_BANDIT_IS: ambos aprenden con el pago de la acción realizada. La función de pérdida solo recibe Q propio, acción propia, pago propio y probabilidad propia de muestreo. No recibe el vector contrafactual ni f_i.

Pérdida completa: `(1/P)sum_u(Q_u−R_u)^2`. Pérdida bandit: `(Q_U−r)^2/(P*q_U)`, con q_U tratado como constante durante la actualización. La expectativa condicional de pérdidas y gradientes coincide. V191 lo verifica exactamente por enumeración, sin tolerancias de Monte Carlo. Las trayectorias de Adam pueden diferir. Se igualan episodios y actualizaciones, no información observada: la condición completa recibe31pagos por cada pago bandit. No se reivindica eficiencia de consultas.

## F–G. Reglas de ejecución y criterios

Primero se ejecuta ORACLE_FULL durante el horizonte completo. Debe terminar con precisión conjunta codiciosa en test>=.95 en al menos3/4bloques. Si falla, PRIVATE_FULL y PRIVATE_BANDIT_IS se cancelan sin ejecutarlas; el fallo no será evidencia de imposibilidad de aprendizaje privado. No se cambiará el objetivo o los parámetros para rescatar el control en esta campaña.

Si pasa el control, ejecutar las dos condiciones privadas completas desde las mismas inicializaciones emparejadas. La unidad de análisis es el par de agentes, no ocho agentes independientes ni los checkpoints. No detener por test ni escoger máximos de curvas.

Guardar el primer checkpoint después de cinco evaluaciones consecutivas con precisión conjunta de entrenamiento>=.99, sin seleccionar por test. t_mem es el final de esa racha. t_gen requiere cinco evaluaciones consecutivas con test conjunto>=.95. Un candidato tardío exige t_gen>=5*t_mem, diferencia>=2000actualizaciones y punto final con train>=.99 y test>=.95. El criterio exploratorio de robustez para PRIVATE_FULL es al menos3/4bloques candidatos. El resultado no se denominará grokking colectivo causalmente demostrado.

Contraste prospectivo distinto de crédito: PRIVATE_FULL termina test>=.95 en al menos3/4bloques y la mediana de las diferencias emparejadas FULL−BANDIT es>=.10. Reportar ambos criterios aunque diverjan. No convertir este contraste de feedback conocido en originalidad algorítmica.

Se reporta por separado precisión codiciosa de despliegue, precisión local bajo el desfase elegido en entrenamiento y precisión esperada de la conducta exploratoria. La exploración permanente impide que su precisión esperada llegue a1; no aplicar el umbral .95 a esa métrica por error. La identidad `Acc_joint=sum_g h_A(g)h_B(−g)` se comprueba para los conjuntos train/test de ambos agentes.

## H–J. Falsación, causalidad y evaluación

Las auditorías de gradientes y de GPU son independientes de los resultados científicos y no confirmación externa. Si aparece un candidato, registrar una campaña causal separada: congelar el compañero con la misma exploración y examinar la generalización local del aprendiz activo, junto con el límite informacional del feedback. La caída de precisión conjunta con un compañero que no generaliza puede ser trivial y no prueba necesidad de coadaptación.

Se conservarán condiciones canceladas como no ejecutadas, negativos, pesos, curvas y estados aleatorios. Un procesoGPU, dos hilosCPU, BelowNormal, seisCPU, límite35%de memoriaGPU y pausas regulares. Publicar fuentes y datos congelados antes de entrenar. CT2 histórico61, nueva rama sin puntuación; N2=N3=0. El objetivo científico global sigue activo y ninguna de estas convenciones equivale a una institución humana aprendida.
