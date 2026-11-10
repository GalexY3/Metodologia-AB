# V2-D — protocolo fijado antes de escalar, auditar estrategias y contrastar controles

**Fecha:** 2026-11-10. La primera cohorte seed221 y las replicaciones seed222/223 ya fueron entrenadas, y sus tests N=36/120 ya se inspeccionaron. **Todo lo siguiente es un análisis posterior** de esas redes, con nuevos escenarios. No convertirlo retroactivamente en confirmación de las hipótesis de las primeras fases.

## Datos que deben preservarse sin selección

- Redes de A2C con recompensa única de progreso global (credit0) y refuerzo global **más contribuciones contrafactuales calculadas por entrenador** (credit2), para las semillas 221,222,223, actualización180. Checkpoints originales y logs de entrenamiento íntegros. No seleccionar el mejor checkpoint.
- Test original N=36, N=120 con 96 o 60 sociedades para seed221 y test replicado seed222/223 con 64 o40; jamás tratar todos esos mundos como entrenamientos independientes. Guardar siempre el **0% de estabilidad sostenida** de las condiciones puramente aleatorias (que sí pueden alcanzar momentáneamente D baja, pero continúan cambiando colores). También conservar 0% de critic0 cuando se observe.
- Exponer tanto el criterio estricto de estabilidad como el porcentaje que llega *alguna vez* a D≤.06, la D final, cambios de color y precisión **exacta** D=0. «100% estable» no es «100% de agentes en distribución exacta».

## Nuevos tests de transferencia de escala (sin reentrenar)

Redes 10×24=N240, 20×24=N480, 30×32=N960, con 5 vecinos para interiores y menos en bordes, k=2,3,4. Semillas NUEVAS de mundo = 1010000+100000*N+1000*train_seed+100*k, mismo seed para crédito2/credit0/random/stay en una cohorte. 24 sociedades paralelas para N240, 16 para N480 y 8 para N960. Horizonte **90 pasos** para comparar con el anterior. Usar pesos finales fijos de seeds221,222,223. Total (3 tamaños ×3 k ×3 cohortes ×4 condiciones)=108 evaluaciones de lote, 1728 sociedades test. Métricas: TV final y última decena, estabilidad final, exactitud final, churn, fracción de peticiones enviadas/aceptadas, carga de receptor. Si computacionalmente costoso, ejecutar por tamaños ascendentes y reportar honestamente cobertura, sin imputar resultados.

## Controles adversariales de mecanismos

En N120, cohortes221,222,223, k=4, 40 mundos independientes de todos los anteriores por cohorte, horizonte90:
- B1 learned_credit2 (normal): receptor recibe observación de su vecino emisor completa.
- B2 quitar el **snapshot del emisor** pero conservar quién pidió qué color (sin acceso indirecto a 2 saltos).
- B3 ocultar los colores de vecinos en **la observación del actor** (mantener identidad del color propio, validez de las posiciones, k y feedback) sin cambiar el grafo ni los mensajes; hacer que todos los mensajes contengan ese mismo snapshot mutilado.
- B4 ocultar último feedback global durante ejecución (entrenamiento sí tuvo recompensa global y señales contrafactuales).
- B5 permitir solo un emisor (física: la cuota de exceso de color mayoritario no puede repararse con ≤5 cambios inducidos por un único emisor).
- B6 control factible SIN aprendizaje «peticiones al azar y aceptar al azar durante T=8 rondas, después todos callan y permanecen», T=8 predefinido; compara la hipótesis alternativa «randomizar una vez y congelarse», no es una política aprendida ni recibe feedback. Es un control con calendario global común (señal de tiempo externa); puede superar el baseline aleatorio que nunca calla.
- B7 igual pero T=24 para sensibilidad; estos dos horizontes se fijaron antes de ejecutar. Ni B6 ni B7 usan censo global y sus autores son el investigador.

Los controles B2–B4 alteran información a una política entrenada en otro régimen (shift covariate), por lo que NO prueban por sí solos que el canal sea indispensable para cualquier política entrenable. B5 prueba necesidad estructural de MULTIPLICIDAD DE ACCIONES si la tarea debe corregir un exceso inicial mayor a 5 agentes; no prueba que exista coordinación explícita entre identidades.

## Descifrado conductual sin atribuir intencionalidad

Usar la política credit2 seed221 y seed223 en N120, k2,k3,k4 y al menos ocho sociedades frescas, 90 ticks, sin actualización de pesos. Registrar por ronda: número de peticiones recibidas por nodo, destinatarios, color pedido, probabilidad de aceptación, movimiento real, matriz origen/color_destino, si movimiento favoreció el déficit global (solo analista), si color pedido era raro en observación del emisor, si es raro en observación del receptor, si la petición supone cambio vs redundancia, cota de emisores por nodo, distribución por grado3/4/5 (borde vs interior). Registrar también primeros30 pasos y últimos30 para comprobar si cambian las conductas tras aproximarse al objetivo.

«Roles» solo si hay diferencias medibles y replicables de actividad/orientación/recepción, persistentes por nodo y por múltiples episodios, más allá de la posición topológica y el color actual. Por defecto las redes usan **un actor neuronal compartido** con memoria episódica de **un único feedback previo**; no atribuir especializaciones de parámetros individuales inexistentes. Si hay roles contextuales, describirlos como posiciones funcionales dinámicas, NO clases sociales inferidas.

## Auditoría de validez: puntos críticos previos

1. No hay heurística «elige color deficitario» en el **código de actor**; el actor recibe colores propios/locales y peticiones y aprende parámetros. Pero el **entrenador credit2 accede a recuentos globales** para construir la recompensa marginal de cada acción, es decir, un **oráculo evaluador contrafactual durante aprendizaje**: la afirmación «aprender solo del cambio total D(t)-D(t+1)» **es falsa para credit2**. Solo credit0 cumple recompensa únicamente de equipo (más crítico central con censo global).
2. El crítico recibe histograma global durante TRAINING, no durante ejecución. Esto es una forma de entrenamiento centralizado / ejecución descentralizada, no comunicación emergente pura sin supervision global.
3. Números fijos de acciones 21 sender y6 receptor; no son k-variable por construcción, solo k≤4. No afirmar extrapolación a k>4.
4. Los canales de salida están ordenados por índice de vecino y color, lo que puede facilitar reglas posicionales fijas. Las etiquetas mayoritarias se aleatorizan en el entrenamiento credit2.
5. Estado global de progreso previo se pasa al actor como escalar. Contrastar ablation B4.
6. El 0% de estabilidad de aleatorios depende de un criterio que exige churn≤.05 durante diez pasos; un randomizador que no se detiene puede fallar incluso si D es pequeña. Control B6/B7 es obligatorio para interpretar «ganar a lo aleatorio».
7. Los casos test dentro de cada red comparten pesos y NO representan replicaciones de entrenamiento independientes. Comparar por semilla primero, después descriptivo entre las tres semillas.
8. N=960 es **extrapolación por tamaño de población**, no demostración de generalización conceptual a más k ni sociología humana.

## Resultado que valdría la pena investigar

Si credit2 mantiene TV baja y churn bajo incluso con muchas más personas, y surgen reglas condicionales reproducibles que dependen de información local, eso sostiene que el entrenamiento permitió **control colectivo distribuido en simulación**, no que haya emergido necesariamente consenso institucional o roles sociales. Si los agentes solo ejecutan «reasignación aleatoria y luego parar», se debe decir. Si los controles sin información local mantienen el éxito, no afirmar que la red y negociación son causalmente necesarios. Preservar resultados positivos y negativos, tests y archivos.
