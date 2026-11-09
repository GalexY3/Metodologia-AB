# Pilot V7 - réplica experimental exploratoria preespecificada

Fecha 2026-11-09. Este registro antecede a entrenamiento de semillas nuevas. NINGÚN objetivo de originalidad/hipótesis científica confirmatoria.

**Objeto:** evaluar viabilidad y consistencia de un efecto de resistencia/recuperación postlesión a igual capacidad final. Las condiciones WDclean=1.0 y 2.5 han sido seleccionadas de forma exploratoria por la calibración V6; ambas muestran generalización tardía, por lo que **NO son todavía las dos categorías requeridas por el usuario (semigrokking genuino frente a aprendizaje continuo sin grokking)**. Es una comparación de latencias de generalización, no de presencia/ausencia de grokking.

**Entrenamientos:** seeds 0,1,2, mismas muestras y data split seed2731, p31, 961 casos limpios y 640 casos aleatorios, 300 neuronas (150 por rama), misma inicialización dentro de cada seed, solo WD de rama limpia distinto. Rama aleatoria WD=.05. lr=.001, 22.000 pasos, registrar cada200. Seed0 ya explorada; seeds1/2 totalmente nuevas aquí. Checkpoint final 22000 predefinido, NO elegir por trayectoria de daño.

**Gate de comparabilidad:** cada red train>=.99, clean validation>=.98, global validation entre .58-.64 y diferencia absoluta entre brazos de la misma seed<=.02; si no cumple, reportar fallo y excluir de comparación principal, retener resultado exploratorio.

**Lesiones:** semilla de máscara 101..105, exactamente 60/150 neuronas en la rama limpia y 0/150 en la aleatoria (20% total red, 40% rama limpia). Misma identidad de máscara por índice dentro de cada par de seed. 650 pasos de reparación, AdamW NUEVO de igual lr0.001 y WD=.1 para todos, control sin lesión. Medir daño inicial, recuperación condicional clean_val a >=.95 de su basal, área bajo déficit CLEAN vs control en 650 pasos. Resultados sobre validación en este piloto, test sellado no usado en inferencia.

**Unidad de replicación:** red=semilla, máscaras repetidas anidadas en red. No tratar 5 máscaras como 5 experimentos independientes. Informe descriptivo separado por seed y agregado; no p-values engañosos. Además diferencias del daño inicial y pérdida funcional basal pueden explicar diferencia de recuperación; registrar estratificación y área normalizada por daño inicial.

**Protección conceptual:** techo 61% creado por rama aleatoria no es semigrokking intrínseco. Si efectos existen no significan que grokking facilite reconstrucción: podrían ser simplemente WD, norma de pesos o estructura de soluciones distintas.

**Vía al experimento real:** reproducir semigrokking genuino (Varma) y desarrollar control gradual con mismo desempeño estable; solo entonces una réplica prospectiva ciega y multi-seed.
