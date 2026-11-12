# V39 — ¿Qué parte de la cooperación depende de la garantía contractual?

**Fecha:** 12/11/2026. Preregistro anterior a la ejecución y lectura de cualquier simulación V39. Hipótesis exploratorias derivadas de V29, V30 y V31. No hay entrenamiento neuronal nuevo, recompensa adicional ni optimización de políticas.

## Población y modelos congelados

Se analizarán **seis** checkpoints del mismo protocolo contractual de mutua aceptación y agentes privados REINFORCE, sin elegir mejores semillas por el resultado:

- V30 N48, cuatro profesiones, grado6, coste c=0,04, inicializaciones 3111 y 4111.
- V31 N120, cuatro profesiones, grado6, coste c=0,04, inicializaciones 3111 y 4111.
- V31 N120, cuatro profesiones, grado6, coste c=0,12, inicializaciones 3111 y 4111.

Cada modelo se evalúa sobre seis semillas ambientales reservadas (970001,970007,970009,970021,970031,970037), 12 mundos por semilla con N48 y 8 con N120, 48 rondas, origen ocupacional monolítico y reglas de profesión cada ocho rondas. Se conservan los mismos pesos privados, precio, topología, longitud y generadores pseudoaleatorios en todos los brazos.

## Intervenciones preespecificadas

Todas las trayectorias usan la regla bilateral consentida de V30 durante rondas1–24, sin alteraciones:

**CONTROL.** El intercambio condicionado por consentimiento recíproco continúa las 48 rondas.

**CIERRE8.** La institución deja de liquidar bienes en rondas25–32: los agentes conservan capacidad de proponer, pero no se ejecuta ninguna propuesta ni se cobra coste. En rondas33–48 vuelve la liquidación contractual.

**UNILATERAL8.** En rondas25–32 la regla bilateral se sustituye por la regla original de regalos unilaterales: toda propuesta voluntaria se entrega, paga coste y genera productos, aunque la contraparte no haya propuesto nada. En rondas33–48 retorna la liquidación bilateral normal. Es una sustitución institucional diferente de bloquear intercambios.

**UNILATERAL_PERMANENTE.** Desde ronda25 hasta48 se aplica la regla original unilateral, sin recuperación contractual.

La política neuronal ya entrenada sigue actuando estocásticamente y no conoce explícitamente que el mecanismo cambió, salvo por las consecuencias materiales que observa de regalos y alimento. No se altera la red ni la asignación profesional. Las intervenciones son exógenas. Sus efectos no demuestran creación institucional espontánea.

## Resultado primario y falsadores

Por semilla, modelo y condición, registrar alimento y propuestas/entregas físicas por persona en cuatro ventanas t1–24, t25–32, t33–40, t41–48. Comprobar igualdad exacta del preperiodo entre todos los brazos emparejados (misma semilla RNG) y que todos los modelos proceden de pesos realmente finales.

**H39a, dependencia de liquidación contractual:** durante el brazo UNILATERAL8, la alimentación cae ≥0,030 raciones respecto del control en al menos cuatro de los seis modelos. Se falsaría si reemplazar contratos por regalos unilaterales conserva o aumenta la alimentación (comprobar emisión y coste físico antes de interpretar).

**H39b, bloqueo material:** durante CIERRE8, la alimentación cae ≥0,10 frente al control en los seis modelos; prueba de integridad de que la circulación real de bienes sostiene el excedente, no una métrica inventada.

**H39c, reversibilidad institucional:** en al menos cinco de los seis modelos, tras ocho rondas sin contratos el último bloque t41–48 conserva ≥90% del excedente del control `(F_trat-.20)/(F_ctrl-.20)`, y muestra mayor bienestar que el bloque durante el cierre. Esta es una prueba de robustez conductual de políticas congeladas, no de reentrenamiento.

**H39d, efecto de permanencia:** compare UNILATERAL_PERMANENTE con UNILATERAL8 en rondas41–48 para atribuir recuperación a la reinstalación del protocolo en vez de evolución temporal común.

Los seis ambientes no equivalen a seis nuevas semillas neuronales: emparejar diferencias por ambiente, intervalos bootstrap agrupados por semilla ambiental **solo descriptivos**. Publicar efectos positivos y negativos, trazas JSON por ronda y hashes de preregistro/scripts.

## Interpretación

Este experimento cuantifica la dependencia institucional **de políticas aprendidas bajo un contrato**. No es una prueba de que las mismas redes puedan aprender desde cero a cooperar sin el contrato. Si se recupera el bienestar al restaurar la regla contractual, ello muestra resiliencia a una interrupción, no origen endógeno de las normas. Si la alimentación unilateral sube, registrar posibilidad de mayores beneficios colectivos con incentivos privados futuros desfavorables, antes de suponer que el contrato era superior en todas las dimensiones. El objetivo general continúa abierto.
