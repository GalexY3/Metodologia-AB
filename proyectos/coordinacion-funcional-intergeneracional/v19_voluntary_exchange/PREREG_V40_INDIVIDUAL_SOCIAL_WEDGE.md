# V40 — Brecha causal entre beneficio privado y beneficio social de una oferta

**Fecha 12/11/2026.** Exploratorio y preregistrado **después de observar V39**. V39 mostró que un mecanismo de liquidación unilateral aplicado temporalmente a políticas aprendidas bajo contrato eleva el alimento poblacional a precio0,04, pese a que entrenar desde cero bajo donaciones unilaterales había fracasado. V40 estima el mecanismo causal inmediato y distingue el coste privado del producto útil recibido por otro.

## RQ40

¿Cuánto beneficio alimentario obtiene el receptor y cuánto alimento pierde el donante cuando se fuerza **exactamente una** de sus propuestas inicialmente aleatoria a ser una donación unilateral, frente a impedirla? ¿Cómo cambia la misma intervención al exigir consentimiento bilateral?

## Diseño y comparabilidad

Los mismos seis checkpoints V39 congelados: V30 N48/c0,04 dos semillas, V31 N120/c0,04 y/c0,12 dos semillas por coste. En cada uno, las seis semillas ambientales reservadas y 8 mundos por semilla para N120 y 12 para N48. La población comienza con un oficio monolítico; los agentes toman las mismas decisiones de profesión y propuestas en las primeras 24 rondas bajo regla bilateral normal. En ronda25, después de escoger el oficio y de generar las propuestas espontáneas, se fuerza **una sola propuesta** de cada uno de los N sujetos a 1 o 0, por separado. El objetivo del mensaje ya está elegido por la red. El resto de las propuestas es idéntico dentro de cada pareja contrafactual. Todas las redes permanecen congeladas; no hay intervención durante turnos posteriores.

Se evalúa el efecto de la oferta marginal cuando la entrega se liquida como donación unilateral y cuando se liquida como contrato bilateral. Para cada persona se miden: diferencia en alimento propio inmediato, diferencia del alimento total de todos los receptores **excluyendo al donante**, cambio en el alimento poblacional (multiplicado por N para expresarlo en unidades alimentarias totales) y si la nueva propuesta genera transferencia real. Bajo unilateralidad, el coste propio inmediato **debe ser exactamente −c**, independiente de la especialidad del destinatario. La ayuda a vecinos puede valer 0, 0,55/3 o 0,55/3+0,25 según redundancia de bienes y completitud.

## Hipótesis y falsadores

H40a: el efecto marginal privado unilateral es mecánicamente −c para 100% de individuos y mundos, confirmado en test; las tasas de ofertas observadas no equivalen a incentivos positivos de aportar.

H40b: a coste0,04, el efecto marginal *social total* (beneficio al receptor menos coste privado) es positivo en media para al menos tres de los cuatro checkpoints de coste bajo. Si fuera negativo, la mejora V39 al ejecutar todas las propuestas reflejaría complementariedad/no linealidad de varias entregas, selección de ofertas o composición, no positividad marginal promedio.

H40c: a coste0,12, el efecto marginal social neto no es positivo en al menos un modelo. La proposición es exploratoria y no universal.

H40d: las ofertas marginales bajo consentimiento bilateral presentan retorno privado inmediato medio no negativo en al menos cuatro de los seis modelos congelados. Los beneficios de los acuerdos mutuos pueden ser de contraprestación inmediata, pero requieren que el vecino también proponga intercambiar.

Se informarán fracciones de ofertas útiles y redundantes, distribución entre individuos y diferencias por coste. Seis entornos ambientales son seis pares bajo los mismos pesos, no seis nuevos entrenamientos neuronales.

## Implicación teórica

Un excedente **materialmente factible** y un incentivo **individualmente apropiable** son estimandos distintos. Que la regla contractual parezca reducir oportunidades de abastecimiento frente a ejecutar todos los regalos no supone que agentes bajo un juego unilateral vayan a elegir voluntariamente esos regalos. Una institución puede ser funcional por modificar la estructura de incentivos, incluso cuando limita transacciones instantáneamente provechosas para terceros. Se registrará también si los datos contradicen esta lectura.

V40 no prueba reciprocidad diferida autónoma, no permite inferir el surgimiento de nuevas normas y no completa por sí solo el objetivo general.
