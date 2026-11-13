# V47. Aprendizaje de reciprocidad con parejas cambiantes: ¿se forman convenciones transferibles?

Preregistro 13/11/2026, antes de los entrenamientos V47. Motivación: V46 consiguió donaciones voluntarias con retorno causal privado positivo en cuatro semillas, mientras NL y LOOK abandonaron cooperación. Sin embargo, cada actor de V46 se enfrentó siempre al mismo compañero durante el entrenamiento; la transferencia anterior únicamente cambió las parejas cuando las políticas estaban congeladas.

## Pregunta

¿La modelización diferenciable del aprendizaje ajeno conserva sus efectos cuando la identidad del compañero cambia entre episodios de aprendizaje, eliminando el emparejamiento permanente como posible soporte convencional?

## Tratamientos y controles

Se reutiliza **sin modificar** el juego material y el valor exacto de V46: N48, k4 como contexto de dos oficios complementarios por pareja, 24 parejas completas en cada episodio, una donación voluntaria simultánea hacia la contraparte, b0,20, v0,55/3, coste0,04, máxima duración48, supervivencia común q0,95, gamma0,995. Cada agente dispone de cinco logitos privados no compartidos (primer turno y memoria propia/del compañero), conoce la política y el gradiente hipotético del compañero actual por construcción del laboratorio y maximiza exclusivamente su valor descontado propio.

A diferencia de V46, **antes de cada actualización** se sortea un emparejamiento completo uniforme de las48 personas con PRNG dedicado, independiente de la inicialización neuronal. Se reordenan únicamente los tensores de parámetros para calcular las 24 partidas diádicas y se devuelve el gradiente privado a la identidad de cada actor. No se heredan habilidades, recompensas ni memoria entre parejas; la política sí conserva sus pesos neuronales entre episodios y usa la historia local dentro de cada juego.

Se entrenarán 12 poblaciones desde cero: NL α0, LOLA α5 y LOLA α20, cruzados con las cuatro semillas neuronal3111,4111,5111,6111. Todas durante1000 actualizaciones de Adam lr0,03, sin preentrenamiento, con mismo sesgo logit inicial pequeño N(0,0,05), mismo optimizador y misma duración. Se comparan con los 12 checkpoints V46 correspondientes con pareja fija. Esta comparación entre V46/V47 cambia la distribución de interlocutores durante el aprendizaje, no la regla de incentivo.

Se conservarán snapshots en u1,200,400,600,800,1000; no seleccionar el máximo intermedio.

## Evaluación congelada

Se fijan antes de entrenar las siguientes **12 semillas de emparejamiento fuera de entrenamiento**: 992101,992107,992109,992121,992131,992137,992141,992149,992153,992159,992163,992171. Para cada reemparejamiento se calcularán exactamente alimentación, donación mutua y retorno causal privado de forzar vs impedir el regalo inicial de cada uno de los48 actores, con el compañero libre y las políticas futuras congeladas. Se contrasta la continuidad de la respuesta aprendida ante extraños.

La segunda comprobación simulará128 mundos por cada una de seis semillas ambientales (993101,993107,993109,993121,993131,993137) en dos emparejamientos seleccionados por índice preestablecido y sin elegir a partir de su desempeño. Los valores empíricos deben aproximar los resultados analíticos dentro de0,015.

## Hipótesis falsables

H47a. LOLA α20 cumple en ≥3/4 semillas neuronales que al menos 9 de los12 emparejamientos reservados tengan ≥24/48 individuos con retorno causal positivo y mutualidad media>0,25.

H47b. NL mantiene 0–23 individuos con retorno positivo en al menos 3 de las4 semillas y no supera0,25 de mutualidad media sobre los12 reemparejamientos.

H47c. LOLA α5 cumple el criterio de H47a en ≥3/4 semillas. Esta es una hipótesis más difícil por la variabilidad previa de ese nivel.

H47d. Entre las ramas que superen H47a/H47c se observa una ventaja media de alimentación de al menos+0,025 frente al NL de la misma semilla, promediando los12 reemparejamientos.

Se reportará la tasa de transferencia de incentivos positivos por actor y su dispersión entre compañeros; no se confundirá una alta mutualidad con incentivo privado positivo.

## Limitaciones y seguimiento

Aunque los agentes cambian de compañero durante el entrenamiento, dentro de cada episodio continúan formando parejas aisladas y tienen una única contraparte. Las profesiones se asignan de modo exógeno para asegurar complementariedad. Esta versión no demuestra coordinación en redes simultáneas con múltiples socios, ni aparición endógena de profesiones. El cálculo de gradientes ajenos permanece disponible por diseño, lo que diferencia V47 de aprendizaje social experiencial.

El resultado V47 positivo **no equivale** al objetivo general del proyecto. La siguiente etapa deberá incluir vecinos múltiples, elección de profesión y nuevos agentes con aprendizaje privado, además de sensibilidad a variación de costes y topología.
