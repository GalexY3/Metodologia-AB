# V34 — Escasez de contactos complementarios e incentivos para organizar profesiones

Fecha 12/11/2026. Preregistro exploratorio antes del entrenamiento. Motivación: V30 tiene cooperación contractual exitosa con N48, k4, grado6, pero su política ocupacional solo añade ~+0,011 de alimento respecto al mejor control de cambio profesional aleatorio. A priori no se sabe si la política ocupacional es poco competente o si la red de seis vecinos hace tan frecuente la diversidad espontánea de roles que sobra poca ganancia adicional.

## Hipótesis estructural

En una red circular de cuatro vecinos (dos anteriores, dos posteriores), con cuatro profesiones, un trabajador necesita tres profesiones distintas entre cuatro contactos. Una disposición periódica de roles 0,1,2,3 consigue cobertura potencial de 3/3 para cada trabajador, mientras que una asignación aleatoria no lo hace siempre. Reducir el grado de seis a cuatro aumenta la escasez local de contactos complementarios sin hacer materialmente imposible la cobertura total; puede elevar el valor adaptativo de aprender posiciones de especialización.

La selección de profesionales sigue siendo endógena, con actores privados y retorno propio; la liquidación bilateral contractual permanece disponible de forma exógena como en V30.

## Diseño

Se conserva actor de ofertas V30, roles categóricos V24, REINFORCE individual, reglas de contrato bilateral, coste final c=0,04 por unidad, N48,k4, lote12, horizonte48, gamma0,995, hidden20, coste de movilidad0,015. **Único cambio respecto V30: grado social 4 en vez de 6**. Dos inicializaciones 3111 y 4111, 700 actualizaciones, precio0,002 hasta u300 y transición hasta0,04 en u500, precio fijo hasta u700. No se cargan pesos anteriores. Test cada 140 épocas, evaluación al coste final. Control histórico V30 con las mismas semillas pero grado6.

## Contrastes y criterio

H34a: el beneficio relativo de aprender profesiones sobre el mejor de tres controles de movilidad aleatoria (0,15,0,35,0,60) será mayor en grado4 que el +0,011 de grado6 y superará +0,05 raciones en al menos ambas semillas. H34b: habrá mayor diversificación local aprendida de profesiones complementarias por vecindario frente a movilidad aleatoria, no solo tasas de propuestas elevadas. H34c: las políticas mantendrán beneficio privado causal de contratar tras entrenar a coste alto y al menos 25/48 individuos con retorno positivo de una oferta inicial.

Se medirá la cobertura potencial de tipos, la cobertura material, entrega de contratos, la diversidad ocupacional final, el efecto de redes reconectadas, la asignación de personas a nuevas posiciones y la prueba de recompensas privadas. Una mejora de roles con contratos exógenos sigue siendo una forma condicionada de emergencia institucional; no acreditar la aparición de la regla contractual en sí.

## Observaciones de validez

El oráculo de contratos recíprocos para grado4 tiene una asignación constructiva de profesión 0,1,2,3 y pares simétricos a ±1 y una pareja de ±2 mediante emparejamiento alterno, lo que permite recibir tres especialidades complementarias al costo total de tres contratos por persona. No usarlo como profesor o recompensa, solo para verificar factibilidad. No confundir variación topológica y variación del tamaño de red.
