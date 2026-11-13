# V50 — Transferencia de reciprocidad aprendida a redes funcionales de cuatro profesiones

**Preregistro prospectivo 13/11/2026**, después de V47–V49 y antes de evaluar V50. Se pretende acercar el éxito diádico a las sociedades originales V25: cuatro profesiones, tres bienes complementarios y múltiples socios simultáneos.

## Pregunta

¿Pueden estrategias privadas de reciprocidad aprendidas con una sola pareja conservar contribuciones y retornos causales positivos cuando cada persona mantiene simultáneamente tres vínculos con ocupaciones diferentes y necesita bienes de esas tres categorías?

## Diseño material

48 agentes, cuatro profesiones **asignadas exógenamente** con12 agentes por categoría. Cada ronda, el entorno forma un grafo tripartito en enlaces entre las cuatro clases: seis emparejamientos bipartitos independientes (uno por pareja de profesiones) hacen que cada individuo tenga exactamente un vecino de cada una de las otras tres profesiones. Las mismas parejas se mantienen inicialmente y se sortean nuevas relaciones con probabilidades r∈{0;0,25;1} por ronda, conservando las tres especialidades necesarias en todo momento. El matching por clases es una restricción favorable que **no constituye organización laboral aprendida**.

Cada agente decide, simultánea e independientemente, una donación dirigida a cada uno de sus tres vecinos usando su política V47 con memoria de una ronda. Cada regalo cuesta0,04 al donante, hasta tres regalos por turno; la recompensa propia viene de la **fórmula original** V25, no de una simplificación diádica:
`food_i=0,20+0,55*(distintos tipos complementarios recibidos/3)+0,25*(3 tipos completos)-0,04*(número de regalos enviados)`.
En una sociedad de tres vínculos recíprocos, el alimento máximo por persona es0,88. La especialidad entregada viene del rol de su remitente. Se utilizará el motor V25 como **oráculo de paridad física** con roles, socios y decisiones fijados, verificando el pago alimento en varios casos extremos.

Se congelan las políticas de las cuatro inicializaciones neuronales de V47 para NL, LOLA α5 y LOLA α20, un total de12 checkpoints. No se reentrena. La probabilidad de continuación de toda la sociedad por turno es q0,95, truncamiento máximo48, gamma0,995. No hay garantía de reciprocidad, recompensa grupal ni docente.

## Memoria informativa

Tres canales preregistrados:
- **carry:** cada decisión mantiene señal del regalo recibido de ese puesto de vínculo en el turno previo, aunque la persona actual sea diferente.
- **public:** cada individuo observa si el compañero actual donó en el turno previo a **otra persona de la misma profesión que el receptor actual**; la identidad y profesión del autor se preservan, pero la transmisión es un registro público exógeno.
- **none:** el canal del regalo previo del otro se fuerza a0, preservando memoria propia y el resto de parámetros.

En todos los brazos los agentes conservan una última acción propia diferenciada por tipo de contraparte, y se distingue claramente identidad propia de compañero previo. No se añaden nuevos pesos al actor congelado.

## Muestreo y causalidad

Semillas ambientales **996101,996107,996109,996121,996131,996137**, reservadas antes de la evaluación. Se prueban 12 modelos ×3 tasas de rotación ×3 canales =108 escenarios. 64 mundos por semilla para alimento/cobertura/donación; cuatro mundos por semilla para el contraste causal individual del primer regalo en el vínculo hacia la especialidad siguiente, con los 48 individuos intervenidos por separado. En cada par de ramas se emparejan exactamente vidas, emparejamientos y secuencias de decisiones; la diferencia privada inmediata debe ser−0,04, mientras los beneficios futuros se evalúan con las respuestas condicionadas de los demás. Los 64 mundos por seed permiten estimar el alimento y la cobertura; los cuatro mundos por seed son un compromiso explícito de precisión Monte Carlo que deberá reportarse.

## Falsadores preregistrados

H50a: bajo r=0 y canal carry, ≥3/4 de las semillas LOLA20 consiguen ≥24/48 individuos con incentivo causal positivo, alimentación media≥0,55 y cobertura completa en≥0,50 de las persona-rondas.

H50b: bajo r=0,25 y canal public, ≥3/4 de LOLA20 mantienen ≥24/48 personas causalmente positivas y alimentación≥0,55.

H50c: bajo r=1 y canal public, ≥3/4 de LOLA20 mantienen ≥24/48 personas causalmente positivas y alimentación≥0,55.

H50d: bajo r=1 y canal public, las cuatro políticas NL quedan por debajo de alimentación0,30 y no llegan a24 individuos con incentivo positivo.

H50e: el canal public supera a none en retorno causal privado al menos+0,025 en≥3/4 de las semillas LOLA20 bajo r=1.

Se conservarán todos los resultados, incluidas falsaciones. Se hará revisión de estabilidad del estimador causal con ocho mundos por semilla si las ganancias están cerca de cero; esa réplica complementaria no sustituirá los umbrales fijados.

## Alcance

Un éxito demostraría transferencia de estrategias individuales condicionadas a tres vínculos simultáneos y complementariedad de cuatro profesiones; **los roles y matching siguen siendo externos**. V50 no demuestra que los agentes hayan inventado reputación, aprendido profesiones ni construido alianzas autónomas. La capacidad de conocer gradientes de aprendizaje ajenos fue suministrada durante entrenamiento V47; la transferencia congelada no resuelve aprendizaje estratégico en redes complejas. No declarar objetivo general completado.
