# Exploración V8: control sin grokking mediante inicialización geométrica

09-11-2026. Documento previo a V8.

En los barridos V6, aumentar el weight decay no ha generado una condición que mantenga train≈100%, valid≈61% y generalice simultáneamente al ajuste temprano. La intervención de fuerte decay=10/20 hace que la red no ajuste los datos ni generalice; esto falsifica esa búsqueda simple dentro del rango probado.

Alternativa explícitamente exploratoria: mantener datos, arquitectura 150+150=300, salidas, pérdida, entrenamiento, número de pasos y weight decay iguales, pero en el grupo B sustituir *antes de entrenar* las representaciones embedding de la rama limpia por una codificación trigonométrica determinista de residuos mod31. Este sesgo geométrico podría facilitar el aprendizaje generalizador desde fases tempranas sin la meseta prolongada postmemorización. En A conservar embeddings aleatorios.

**Causalidad:** B recibe estructura algorítmica como conocimiento inductivo, por tanto, **no aísla el efecto puro de grokking**; si B se recupera mejor o peor, puede deberse directamente a inicialización geométrica. Usar como control instrumental negativo para falsar interpretaciones vagas de la 'historia grokking', jamás como comparación causal principal.

Condiciones piloto B WDclean=1 y 2.5, seed0, init_scale1.0, frecuencias k1..16 en 32 dimensiones, amplitud ajustada para aproximar varianza 1 de la inicialización normal, final a paso22000, validación para calibración, no inferencia confirmatoria. Se aceptará como candidato no grokking solo si curva de validación asciende aproximadamente en paralelo al ajuste inicial y permanece estable en el final; no basta que alcance 61%.
