# V13 — Topologías, número de enlaces y prueba exploratoria de multihiperuniformidad (MHU)

**Creado antes de los entrenamientos principales de V13.** Este documento evita convertir una observación retrospectiva en hipótesis confirmada. V13 reutiliza exactamente la economía, la política individual de 128 parámetros y el REINFORCE de V12, sin tocar V12. Archivo de código: network_v13.py. Archivo de medición: mhu_v13.py.

## Dos estructuras separadas

**Red social:** determina quién observa a quién y, cuando esté habilitado, de quién recibe anuncios. Se manipula el número de enlaces (grado medio objetivo d=4,8,12, más grados intermedios), su distribución y el alcance espacial.

**Campo espacial:** asigna una posición fija bidimensional a cada persona. Su profesión es una etiqueta o marca de ese punto. Una red social puede conectar puntos distantes o próximos. La ocupación física total de una retícula ya es hiperuniforme por construcción: eso jamás prueba MHU de las profesiones.

## Familias de red

- ring: anillo circulante original V12, grado fijo.
- torus: red de vecinos próximos en un toro 2D, grado 4/6/8/10/12.
- smallworld: enlaces locales del toro con aproximadamente 15 % de permutaciones de extremos, preserva exactamente cada grado.
- random_regular: red aleatoria con el mismo grado en cada vértice.
- modular: cuatro comunidades con redes regulares densas internamente y puentes intercomunitarios escasos.
- hubs: crecimiento preferencial tipo Barabási–Albert, heterogeneidad fuerte de número de enlaces; grado solicitado significa grado medio APROXIMADO, medido de nuevo.
- jitter_geo: posiciones obtenidas perturbando independientemente una retícula por desplazamientos acotados y conectadas mediante un árbol espacial más aristas cercanas hasta un grado medio objetivo; **la disposición TOTAL de puntos es similar a una estructura hiperuniforme**, pero las profesiones NO vienen prediseñadas.
- poisson_geo: posiciones uniformes aleatorias en el toro, mismo procedimiento de conexión espacial y similar grado medio de contactos; soporte espacial no hiperuniforme en el límite termodinámico.

Se calculan grado medio/min/máx, dispersión, clustering, longitud media de caminos, modularidad y longitud espacial de enlaces. Las redes se mantienen fijas dentro de cada entrenamiento con una semilla de construcción separada, y pueden cambiarse en un test de robustez sin volver a aprender.

## Prueba de MHU por componente

En el toro espacial 2D se calcula para cada profesión j ocupada:

A_j(q) = sum_{i:prof_i=j} exp(-2πi q·x_i).

Para los seis vectores de onda no nulos (1,0),(0,1),(1,1),(1,-1),(2,0),(0,2), registramos la media de |A_j(q)|² respecto a la esperanza matemática de una permutación aleatoria de etiquetas con los MISMOS n_j y exactamente las MISMAS posiciones. De esta forma, un grupo que se reduce de tamaño durante el aprendizaje no puede parecer ordenado exclusivamente por su tamaño. Ratio esperado por azar = 1; ratio <1 = fluctuaciones de baja frecuencia suprimidas, >1 = concentración/agrupamiento espacial. Solo se incluyen componentes con n_j≥4 y n_j≤N−4, y se informa la cobertura de componentes para detectar sesgos de especies pequeñas.

Se reportan el ratio medio por componente, el PEOR componente, la proporción con supresión y su variación entre semillas de mundo. **La desigualdad ratio<1 NO demuestra hiperuniformidad estricta**: es un diagnóstico de seis frecuencias y población finita. La definición física exige estudiar S_j(q) al aproximarse |q|→0 y la varianza de recuentos en ventanas crecientes y varios tamaños N.

Controles metodológicos:
- etiquetas aleatorias, con igual número de trabajadores por profesión, conservando posiciones y ocupaciones: ratio esperado=1;
- profesiones globalmente equilibradas pero espacialmente segregadas: ratio alto, no MHU;
- patrón construído deliberadamente minimizando amplitudes espectrales por intercambios de etiquetas, con ocupaciones k×N/k: ratio bajo por diseño. **Es un control positivo, no aprendizaje emergente.** Si se usa para inicializar una aldea, no se podrá atribuir a agentes la creación de MHU inicial.

## Contrastes de aprendizaje

Primera batería: N=120, economía idéntica a V12, entrenamiento mezclando k2/k4 y M10/M20, pruebas en M30/k5 y nuevas redes. Comparar d4/d8/d12 en toro espacial, y d8 en mundo pequeño, red regular aleatoria, hubs, comunidades, jitter_geo y poisson_geo. Congelar la recompensa individual/social y la información pública dentro de cada bloque experimental (preferentemente 100 % individual C0 para N60 y combinación pública 90/10 para N120, replicadas dentro del bloque). El número de enlaces se varía manteniendo constante la política.

Segunda batería: usar políticas congeladas de cada topología sobre distintas redes y semillas de simulación y comparar alimentación, D_k, número de ocupaciones y el ratio MHU por profesión, frente a controles con etiquetas barajadas manteniendo conteos exactos. No se permitirá usar la medida MHU para actualizar pesos durante este primer estudio: debe aparecer por autoorganización o no aparecer.

Las predicciones a comprobar, **no establecidas**, son:
H1. La conectividad vecinal influye en la velocidad y estabilidad de regulación de ocupaciones. Más enlaces no implica necesariamente mejores resultados.
H2. La heterogeneidad de grado y las comunidades pueden afectar los umbrales de coordinación.
H3. La mejor distribución global de trabajadores no presupone MHU espacial; en redes locales podría surgir segregación, mientras en redes heterogéneas quizá no aparezca orden espacial.
H4. Un soporte de puntos ligeramente perturbado desde una retícula puede facilitar o dificultar el aprendizaje por su estructura social, pero su hiperuniformidad total no implica la de cada profesión.

## Límites

Las profesiones siguen siendo materialmente equivalentes; la MHU espacial de sus marcas es un observable emergente, NO parte de la recompensa. Una señal MHU del entorno incorporada por construcción sería un sesgo, no descubrimiento. La comparabilidad entre grafos geométricos y regulares requiere reportar sus diferencias de distribución de grado, no atribuir todo a "tipo de red". El estudio no prueba ausencia de una estrategia individual ganadora ni que haya cooperación comunicativa aprendida.
