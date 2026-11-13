# V53B — Sensibilidad material de los reguladores inspirados en Beer

Preregistro 2026-11-13, después de conocer V53 BASE y antes de ejecutar las sensibilidades. Objetivo: comprobar que las conclusiones de V53 no se deban únicamente a la elección inicial de costes administrativos, límites de almacenamiento o hambre de mantenimiento. **No sustituiremos los criterios preregistrados de V53** aunque los resultados cambien.

## Factores y escenarios

Se conserva el mismo motor V53, los ocho regímenes de gobernanza, las mismas seis semillas ambientales999101/107/109/121/131/137,128 mundos/semilla y96 rondas. Se mantienen dos tipos de perturbación: PATCHY (interrupciones localmente heterogéneas) y SYSTEMIC (perturbaciones simultáneas por sociedad). Se cruzan con diez configuraciones de parámetros, variando de una en una las variables salvo cuando se indica expresamente:

1. BASE: coste de gestión original (local0,004; global0,008; forecast0,008; policy0,003), pérdida por transporte0,05, mantenimiento0,75, stock inicial1,20, capacidad2,20.
2. HALF_ADMIN: cada coste administrativo reducido a la mitad.
3. ZERO_ADMIN: costes administrativos iguales a cero, pero persiste pérdida de transporte0,05.
4. DOUBLE_ADMIN: costes administrativos duplicados.
5. FREE_TRANSFER: pérdida por transferencia0,00, costes administrativos originales.
6. LOSS20: pérdida por transferencia0,20, costes administrativos originales.
7. LOW_SUBSISTENCE: consumo0,68.
8. HIGH_SUBSISTENCE: consumo0,82.
9. SHORT_BUFFER: almacén inicial0,65 y capacidad1,25.
10. LONG_BUFFER: almacén inicial2,00 y capacidad3,00.

No hay parámetro seleccionado a partir de un resultado favorable. La producción cooperativa S1 continúa siendo el límite idealizado con cuatro especialidades K4 y regalos a todos los socios vivos, no una distribución empírica de entrenamiento V52.

## Preguntas falsables

- **Q53b1:** ¿La mejora de LOCAL_GLOBAL frente a LOCAL bajo PATCHY se mantiene positiva en al menos ocho de diez parametrizaciones?
- **Q53b2:** ¿Basta reducir el coste de la inteligencia anticipatoria (ZERO_ADMIN) para que FORECAST supere a LOCAL_GLOBAL bajo PATCHY? Se reporta como hipótesis abierta, sin reinterpretación post hoc.
- **Q53b3:** ¿Existe algún régimen en que FULL_PROXY obtenga un máximo de supervivencia sobre las ocho alternativas? Si existe, en cuáles y con qué costes; si no, no afirmaremos que las funciones de Beer sean materiales inútiles.
- **Q53b4:** ¿La ventaja del mensaje de forecast auténtico frente al mensaje reetiquetado PLACEBO cambia de signo cuando varía el coste? El coste de ambos mensajes debe seguir siendo idéntico en cada parametrización.
- **Q53b5:** ¿Qué ocurre si el recurso disponible y el mantenimiento se acercan a un límite físico? Comparar supervivencia y alimento neto evitando atribuir a «mal gobierno» situaciones donde la producción máxima0,88 por persona queda muy próxima al gasto material y administrativo.

## Precisión e interpretación

Diez parametrizaciones×dos ambientes×ocho reguladores×seis semillas×128 mundos = **122.880 sociedades** adicionales. Reportar porcentaje vivo, equipos con cuatro especialistas operativos y comida neta/persona viva y por persona inicial-ronda. Los bootstraps se harán por las seis semillas emparejadas y se distinguirán las trayectorias con supervivencia próxima a cero o al cien por cien. Este estudio mide robustez de un mecanismo ya diseñado y no aprendizaje emergente de políticas S2–S5. No permite probar la necesidad o suficiencia de la totalidad de funciones del VSM.
