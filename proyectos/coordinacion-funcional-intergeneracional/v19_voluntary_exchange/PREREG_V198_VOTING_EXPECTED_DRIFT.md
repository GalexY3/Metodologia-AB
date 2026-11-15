# V198 — Distinguir el ruido de retornos de la deriva privada media

15/11/2026. Diagnóstico registrado después de conocer V195–V196 de votación y la corrección numérica V197, pero antes de integrar ninguna trayectoria de deriva media de sus padres. No es una confirmación independiente. Las fixtures aleatorias anteriores al registro no utilizan las políticas parentales para producir resultados.

## A–C. Pregunta y rivales

Retirar la exploración conjunta degrada las políticas Q privadas de V196 en seis escenarios, incluso con epsilon0. Esa observación no demuestra por sí sola que los incentivos medios hagan imposible conservarlas: eliminar exploración de acciones no elimina el ruido de estado, señal y retorno. El alpha constante y la selección codiciosa pueden convertir retornos adversos ocasionales en cambios de política. El diagnóstico pregunta si la deriva condicional media ya produce el deterioro, o si es necesario el ruido muestral de esas actualizaciones para reproducirlo en este operador.

Los rivales conocidos incluyen selección estratégica por pivotalidad (Feddersen y Pesendorfer1998) y tolerancia a retornos adversos en aprendizaje multiagente (Panait y colaboradores2006/2008; Matignon y colaboradores2007). No se reclama nueva matemática de voto, teoría de stochastic approximation ni un nuevo algoritmo de aprendizaje. Tampoco se han ejecutado aún los algoritmos originales de esos antecedentes.

## D–F. Intervenciones y cálculo

Padres: Q finales JOINT_SIGNAL_PULSE_10 de los seis escenarios V195 de votación, k4/8/12 por unanimidad/mayoría,32mundos×20grupos, pérdidas privadas1/7. Conservar cada padre, sin ajustar parámetros ni escoger grupos por resultados. Mismo entorno GOOD.6, señal de precisión.8, rechazo0, aprobación +1o−L_i. Horizonte8000rondas adicionales, alpha.10, actualizaciones simultáneas calculadas con las políticas anteriores al paso. Guardar Q inicial y a2000,4000,6000,8000, sin selección de picos.

Dos condiciones: MEAN_EPS08 y MEAN_EPS00. Sustituir cada incremento Q realizado por su esperanza condicional exacta dado el perfil Q actual:

`Delta Q_i(s,a) = .10 * Pr(s) * pi_i(a|s) * (E[r_i|s,do(a),pi_-i] - Q_i(s,a))`.

Las señales son independientes condicionalmente en el estado y las acciones usan ruido privado independiente. Calcular las probabilidades Poisson-binomial de los otros votantes mediante exclusión de cada individuo; el propio voto cambia el umbral de ratificación. `Pr(s=1)=.56`, `Pr(s=0)=.44`. Integrar ambas fuentes de aleatoriedad del entorno y las acciones ajenas. Mantener la cobertura de visitas multiplicando por `Pr(s)pi(a|s)`; NO actualizar todas las acciones con la misma tasa.

La ley de elección es la del entrenador, corregida por V197: ruido uniforme independiente de ancho1e−12en cada valor, que produce CDF triangular cerca del empate, y mezcla epsilon-greedy por encima. La fórmula trata el ruido como continuo ideal; no pretende reproducir la discretización finita del generador ni redondeos máquina.

Este operador necesita conocer el modelo del mundo y el perfil completo. Es un contrafactual diagnóstico oráculo, NO un aprendiz ejecutable que solo observa pagos privados. Su trayectoria tampoco es la esperanza de las trayectorias estocásticas: la actualización y la selección de política son no lineales. No interpretar una discrepancia como una demostración universal sobre todo algoritmo privado.

Auditoría previa: comparar objetivos condicionales contra enumeración explícita de votos de otros jugadores en50fixtures independientes, tamaños3/7, mayoría/unanimidad y epsilon0/.08. Validar masas de probabilidad de la división polinómica usada para excluir individuos. No integrar padres reales antes del registro remoto. Comprobar hashes y descargar bytes remotos del protocolo/código/manifiesto antes de ejecutar.

## G–J. Criterios y alcance

Métrica principal: bienestar final de la política del paso8000evaluada sin epsilon ni pulso, usando la ley de desempate corregida, dividido por el bienestar de su padre bajo la misma ley. Medir los seis escenarios. Referencia estocástica: finales V196 originales corregidos por V197, con cero de seis conservando75%para epsilon.08. Esos resultados ya eran conocidos; no se crean nuevas raíces científicas.

Si MEAN_EPS08 conserva>=75%en al menos4/6, la eliminación del ruido de las actualizaciones es suficiente para evitar el fracaso bajo este operador en esas condiciones, pero todavía no se acredita una solución privada realizable. Si MEAN_EPS08 falla el75%en al menos4/6, el ruido muestral por sí solo no explica todo el deterioro: la deriva media puede reproducirlo. Si se divide3/3, se registra heterogeneidad sin forzar una de las dos explicaciones globales.

MEAN_EPS00 es un discriminante secundario fijado de antemano. Compararlo con el final estocástico epsilon0de V196, corregido por V197. Una diferencia permite identificar la importancia conjunta de ruido y discontinuidades de selección aun sin exploración exógena. No permite declarar que las políticas sean equilibrios bayesianos: la evaluación estratégica V195A ya detectó oportunidades de desviación y ausencia de exploración puede ocultarlas.

Si el diagnóstico favorece el papel del ruido, el paso siguiente debe comparar primero contra hysteretic/lenient Q y explicaciones de aprendizaje conocidas, antes de diseñar una supuesta institución original. Si favorece deriva privada destructiva, revisar incentivos y compromisos voluntarios con rivales MATE/contratos conocidos, no atribuir el fallo solo a poca memoria.

Dos hilos NumBa, BelowNormal y afinidad existente; no GPU. Registrar todos los negativos, no cambiar alpha, umbrales o horizonte tras observar. CT2 histórico61sin cambios, rama nueva sin puntuación, N2=N3=0. DRIFT D1: diagnóstico analítico de una línea ya existente de votación; no cambio de objetivo sociológico ni reivindicación de institución aprendida.
