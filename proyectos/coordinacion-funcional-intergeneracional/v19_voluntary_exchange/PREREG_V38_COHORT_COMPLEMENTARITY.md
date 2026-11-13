# V38 — Umbral de competencia e integración de cohortes: ¿hay complementariedad entre agentes nuevos formados?

Preregistro del 12/11/2026. Se define sobre el diseño V37 y antes de inspeccionar sus resultados definitivos de evaluación congelada. V38 no modifica el entrenamiento y no transforma los agentes originales de V31. Es un análisis causal factorial de **composición de la nueva cohorte**.

## Pregunta

En una sociedad contractual de120 personas donde30 recién llegados reemplazan a30 residentes, ¿el beneficio social de que los nuevos adquieran competencia individual se agrega de forma aproximadamente lineal o depende de la proporción de nuevos agentes que ya han aprendido? La hipótesis de complementariedad social sugiere que un nuevo agente formado puede beneficiar a sus compañeros formados y no formados al incrementar la probabilidad de lograr intercambios recíprocos y aportar especialidades útiles.

## Tratamientos y población

Se conservan los cuatro pares de políticas V37, cada par formado por las redes aleatorias guardadas de los30 agentes nuevos y sus redes después de700 actualizaciones de aprendizaje privado. En cada sociedad se reemplazan exactamente las mismas30 posiciones preregistradas en V37, con roles iniciales aleatorios y memoria reiniciada. Se deja entrenado solo un porcentaje de esas30 personas, evaluando seis niveles enteros **0/30, 6/30, 12/30, 18/30, 24/30 y 30/30**. En todos los niveles, las 90 políticas incumbentes permanecen congeladas e idénticas a V31.

En cada semilla ambiental, el subconjunto de nuevos individuos formados se elige de modo reproducible mediante una única permutación aleatoria de las30 posiciones y la asignación por prefijos sucesivos; así los niveles son **anidados**, las personas que ya estaban formadas en6/30 continúan formadas en12/30, etc. Distintas semillas ambientales reciben sus propias permutaciones; la cuota y el orden de asignación son exógenos para identificar el efecto de composición, nunca una cuota social aprendida por los agentes.

Para cada uno de los cuatro checkpoints V37, las seis semillas ambientales reservadas, dieciséis mundos por semilla, 48 turnos, choque t24 después de elección de oficio y antes de transferencia, precios finales0,04 y0,12. Repetir idénticos pesos no implica más entrenamientos independientes. No se actualizan redes durante estas pruebas.

## Métricas e inferencia

Media de comida de los30 sustitutos, media de los90 residentes, comida total y excedente conservado frente al control original sin reemplazo; rondas25–32,33–40 y41–48. También se registra el número de contratos físicos por persona para distinguir disponibilidad social de bienes y exceso de propuestas. Efecto de formación (\Delta(q)=Y(q)-Y(0)) y desviación de linealidad (\operatorname{Synergy}(q)=Y(q)-[(1-q)Y(0)+qY(1)]), usando q∈{0,0,2,0,4,0,6,0,8,1}. Los extremos0 y1 definen exactamente el segmento lineal, por construcción su sinergia es0; los niveles intermedios identifican complementariedad no aditiva en el nivel de la población completa. Una sinergia positiva no implica automáticamente una transformación institucional, porque la estructura contractual es exógena.

Criterio H38a: al menos3 de4 modelos exhiben sinergia social media positiva en las cuatro proporciones intermedias. H38b: al menos3 de4 muestran alimento de residentes no decreciente conforme crece la cuota formada, admitiendo fluctuaciones descriptivas pero no una pendiente media negativa. H38c: a c=0,12 se observa recuperación ≥85% del excedente sin necesitar que100% de recién llegados estén formados en al menos una de las dos semillas neuronales; este último umbral define si existe efecto de difusión de competencia.

## Limitaciones

La heterogeneidad entre identidades de los30 nuevos puede producir diferencias por selección de prefijos y estructuras locales; seis semillas ambientales con seis permutaciones no bastan para inferencia universal. El orden de formación es una intervención experimental exógena y no demuestra transmisión espontánea de conocimiento entre novatos. No se atribuirá efecto de enseñanza, imitación o cultura a lo que solo sea externalidad material de intercambio.
