# V33 — ¿Se aprende una verdadera organización laboral con entrenamiento prolongado?

Preregistro exploratorio fechado el 12/11/2026. Se formula después de observar V30, que sostiene intercambios contractuales con cuatro profesiones pero mejora la alimentación solo +0,011 frente al mejor control de movilidad profesional aleatoria. El resultado establece el problema: la coordinación de intercambios puede ser funcional sin que la propia distribución laboral aprendida supere sustancialmente los repartos por azar.

## Hipótesis

La política ocupacional de V30 fue entrenada durante 700 actualizaciones junto con el donante, y alcanzó una elevada disponibilidad local de especialidades. Puede que la ventaja de roles sea pequeña por insuficiencia de aprendizaje después de que la economía contractual se estabilizase. V33 prolonga exactamente las mismas políticas desde sus checkpoints hasta 2100 actualizaciones acumuladas, sin alterar el juego ni ofrecer información global de cuotas, bajo el precio fijo final0,04.

## Condiciones

Dos semillas originales 3111 y 4111 de contratos V30, cada una con dos continuaciones independientes a partir del mismo checkpoint y optimizadores Adam originales:

- V33-JOINT: optimización simultánea de las políticas privadas de propuestas y profesiones, ambas desde sus pesos ya entrenados en V30, durante 1400 actualizaciones adicionales.
- V33-ROLE: congelación de la política de propuestas y optimización exclusiva de la política ocupacional privada, usando el alimento propio. Se declara explícitamente **aprendizaje escalonado** en esta condición; sirve para aislar la capacidad de aprendizaje de roles bajo un mercado de propuestas estable.

En todos los casos N48, k4, grado6, 12 sociedades por lote, 48 rondas, coste fijo 0,04 por unidad, coste de cambio 0,015, gamma0,995, tasas de aprendizaje y entropías originales, valoración de desarrollo a actualizaciones totales 701, 900, 1100, 1400, 1700 y 2100. Semillas del mundo derivadas del identificador y actualización, sin seleccionar nuevos checkpoints por la evaluación.

## Medidas y criterios

La hipótesis H33 requiere que la ventaja de alimentación sobre el mejor de tres controles de movilidad aleatoria pase de aproximadamente +0,011 a ≥+0,05 en evaluación congelada de nuevas sociedades. También deberá aumentar la diversidad de tipos complementarios accesibles localmente, la cantidad de contratos físicos y el abastecimiento; una subida por reducción de donaciones o costes sin mejor estructura profesional no valida H33.

Se preservan roles fijos, movilidad aleatoria, no contratos, reasignación de personas y redes reconectadas como controles. La mejora del entrenamiento conjunto frente a roles congelados será otra evidencia de la importancia del acoplamiento entre subsistemas, pero el diseño no permite afirmar que **las instituciones contractuales mismas** se inventaron espontáneamente. Si las políticas alcanzan una meseta, se documentará como límite de optimización/identificabilidad social, no como imposibilidad universal.

Los cuatro tratamientos parten de pesos ya entrenados y no son cuatro inicializaciones neuronales independientes. Reportar y respetar esta dependencia.
