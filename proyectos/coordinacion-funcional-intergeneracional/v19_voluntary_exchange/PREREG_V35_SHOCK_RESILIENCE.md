# V35 — Resiliencia de cooperación y especialización frente a perturbaciones

**Preregistro exploratorio 12/11/2026, anterior a la simulación V35.** Depende de los checkpoints contractual-voluntarios V31 N120, k4, grado6, entrenados por recompensa privada. Los modelos han sido evaluados al coste material final0,04 y0,12 en sociedades reservadas.

## Pregunta

¿Una economía contractual voluntaria con 120 individuos y cuatro profesiones conserva o recupera cooperación funcional cuando cambian las relaciones, las profesiones o una cuarta parte de sus participantes? La capacidad de las políticas aprendidas para responder **sin reentrenamiento** es una medida diferente de la capacidad de reaprender ante el choque. V35 prueba exclusivamente respuesta conductual con redes neuronales congeladas.

## Diseño antes de ver los resultados

Se utilizarán cuatro modelos V31 finales, dos semillas neuronales 3111/4111 por coste c∈{0,04,0,12}, sin selección posterior. Por modelo, seis semillas ambientales reservadas, 16 mundos por semilla y 48 rondas. Se introduce el choque **justo antes de tomar decisiones en la ronda 25 (índice t=24)**. Se compara con una condición no perturbada evaluada sobre las mismas semillas y red de referencia.

Cuatro condiciones:
* Control sin perturbación, misma sociedad y políticas.
* Reconexión de toda la red al patrón aleatorio regular `rewired` de grado6, conservando professions y pesos privados; se limpia la memoria por posición de vecino al cambiar la identidad de los contactos.
* Reasignación aleatoria de las profesiones entre individuos manteniendo exactamente las cantidades globales de cada ocupación de ese mundo; sus pesos y vínculos permanecen.
* Sustitución del **25% de agentes** por individuos nuevos con sus propias dos redes de propuestas/roles recién inicializadas aleatoriamente; cambian además sus oficios a categorías aleatorias. Los otros 90 miembros mantienen pesos aprendidos. El historial personal de recién incorporados se reinicia y los vecinos pierden la memoria de la identidad sustituida, conservando las demás relaciones.

La liquidación de contratos bilaterales sigue siendo exógena como en V30/V31. Los individuos continúan eligiendo propuestas y profesiones en la simulación, con peso congelado y coste unitario final. Se registrará actividad profesional y contratos por persona y ronda y se separará el bienestar inicial y posterior.

## Medidas de recuperación

Alimento medio rondas 1–24, alimento rondas 25–32, 33–40 y 41–48; media de contratos físicos, cobertura material e indicador de potencial ocupacional. El criterio estricto de recuperación exige que en **ambas semillas por precio** el excedente final sobre0,20 sea al menos el 85% del excedente final de su control no perturbado, con recuperación parcial desde el primer bloque postchoque. Este umbral se predefine y no equivale a constatar que el alimento sea superior al régimen sin contratos.

Se calculará un contraste pareado por semilla ambiental entre episodio perturbado y control, sin inflar las unidades independientes por mundos. Para sustitución se informará además el bienestar de 30 recién incorporados y el de los 90 residentes, evitando presentar una media global como prueba de inclusión equitativa.

## Límites

La reconexión de relaciones y la sustitución de actores son intervenciones exógenas destinadas a medir la resiliencia, no generadas endógenamente por los individuos. El choque de professions conserva cantidades, pero puede alterar parejas complementarias. Un modelo que colapsa después de las perturbaciones no deja de ser una prueba positiva de cooperación contractual antes del choque. Sin reentrenamiento los resultados no cuantifican la capacidad de aprender nuevas convenciones entre generaciones.
