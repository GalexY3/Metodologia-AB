# Protocolo V3B — Agentes individuales, colores permutables y recompensa de equipo única

**10-11-2026 · Corrección metodológica tras la crítica externa «Texto pegado(6).txt».**
Se registró antes de cualquier entrenamiento V3B. Los experimentos V2 y sus resultados siguen intactos en ramas anteriores; fueron realizados con pesos compartidos y, en la variante de mayor éxito, crédito individual calculado por el entrenador. NO responden a la pregunta central V3B.

## Principios del experimento
Cada uno de los N agentes tiene parámetros θ_i propios. Los tensores se apilan por eficiencia computacional, pero **no comparten ni gradientes, ni parámetros, ni optimizador estadístico entre índices**. Una comprobación de gradientes bloquea que logπ_i dependa de θ_j, j≠i. Toda la población recibe una única recompensa compartida por mundo/turno, calculada por el evaluador:

D(t)=1/2·Σ_{c=0}^{k−1}|n_c(t)/N−1/k|,  r_t=N[D(t)−D(t+1)].

Nadie conoce n_c, D ni la contribución contrafactual propia. Los actores ven solo su propio color, colores de vecinos directos, k público, feedback escalar anterior y mensajes legales entrantes. El evaluador sí calcula D para producir r_t, que es un canal global escalar público deliberado.

## Red y acciones: NO hay doble botón para el mismo color

Cuadrícula rectangular no periódica con aristas cardinales y una diagonal por nodo en bloques 2×2 (cinco vecinos por nodo interior, menos en bordes). Cada turno síncrono tiene **dos decisiones** de cada agente:

A. Enviar nada o una petición a un solo vecino: destinatario + color sugerido. La carga informativa es el snapshot local de quien envía (propio color y colores vecinos). Un receptor puede recibir varias peticiones simultáneamente, independientemente de enviar la suya.

B. Después de recibir esos mensajes, elegir **exactamente un color siguiente entre los k legales**, incluido el actual. Los mensajes son información y sugerencias (*cheap talk*) para esa decisión; NO existe una acción adicional «aceptar la petición», porque sería físicamente equivalente a elegir el mismo color de forma voluntaria. Una coincidencia entre la elección y la petición se registrará como **coincidencia observable**, NO como prueba de obediencia causal. Las actualizaciones de todos los estados se hacen simultáneamente.

La comunicación se puede desactivar sin impedir el cambio voluntario. El control SIN mensajes conserva la observación directa de colores de vecinos, permitida por el usuario.

## Equivariancia por etiquetas, sin heurística explícita

Los pesos neuronales son independientes por persona, pero cada red individual evalúa candidatos de color con un **mismo submodelo dentro de esa persona**. Un cambio de etiquetas π de los colores produce una permutación exactamente equivalente de los logits de emisión y de elección, sin preferir «color rojo» por índice. Se verifica por tests de permutación. Eso es sesgo arquitectónico de simetría, NO una regla explícita de organización.

La red recibe, entre otras, características relativas a cada candidato: si es el propio color, frecuencia LOCAL del candidato en vecinos observados, número de peticiones de ese color, proporción de ese color en snapshots recibidos y feedback previo; el modelo aprende sus ponderaciones, sin instrucción «escoge el menos frecuente». El test de simetría debe pasar y el atributo de feedback no debe permitir conocer el censo global.

**Cautela:** permutar aleatoriamente los nombres de los colores en la inicialización no basta para impedir repartos fijos por identidad, pues D es simétrica al nombre de los colores. La arquitectura equivariante evita memorizar un COLOR ABSOLUTO, pero aún permite convenciones dependientes de identidad/posición relativas al entorno. Comprobar con permutaciones de identidad, graph rewiring y perturbaciones una vez haya resultados.

## Condiciones para prueba comparativa

C1. **Solo cambio autónomo:** agentes independientes, se desactiva físicamente enviar peticiones y se entrega cero mensajes; conservan observación local directa, todos los k colores voluntarios y r_t colectivo.

C2. **Cambio autónomo + peticiones:** mismas redes independientes y presupuesto, pero cada agente puede enviar como máximo una petición y recibir hasta grado(i) mensajes y snapshots. Misma recompensa exclusiva de equipo.

C3. **Ablación de inferencia:** coger θ_i de C2, congelarlos, y evaluar con mensajes eliminados, pero cambios voluntarios intactos. Una diferencia respecto a C2 mide dependencia de ese canal en ESTA política bajo cambio de distribución; no una necesidad universal de comunicación.

Baselines externos: (i) quedarse quietos, (ii) elegir al azar cada turno, (iii) actuar al azar T=24 y después no cambiar. Ninguno se presenta como argumento definitivo de que el feedback sea necesario. C1 y C2 deben recibir la misma cohorte/semillas de aprendizaje, arquitectura, optimizador y presupuesto, y deben evaluarse en las mismas sociedades nuevas; repetir varios entrenamientos independientes.

## Entrenamiento: local independiente, recompensa única

REINFORCE con parámetros θ_i por agente; cada logπ_i del mensaje/estado recibe un retorno de equipo común, sin cálculo de diferencia por i. Se permite línea base de reducción de varianza **compartida y dependiente del paso** estimada solo con retornos de otros mundos del minibatch (leave-one-out) para no utilizar la propia acción en el baseline. No hay crítico que vea n_c, D ni los colores globales.

Primer piloto N=36 en cuadrícula6×6 y k∈{2,3,4}, mayoría inicial aproximada70% de un color que se permuta aleatoriamente entre episodios y distribución restante aleatoria. Entrenar C1 y C2 desde pesos iniciales apareados. Primero comprobar tests y evolución del entrenador, después guardar test virgen; si el aprendizaje no avanza, conservar evidencia negativa y no cambiar a V2 crédito individual ocultamente.

## Evaluación: NO utilizar «% de aciertos» ambiguo

Calcular esperanza exacta iid uniforme E[D_azar] = k/(2N)·Σ_{x=0}^N |x−N/k| Pr[Bin(N,1/k)=x]. Registrar D, ratio D/E[D_azar] (nombre: **desequilibrio relativo al azar**, NO «hiperuniformidad»), precisión exacta D=0 cuando sea matemáticamente posible, churn, AUC, número de mensajes, coincidencias petición/acción y estabilidad durante diez rondas.

D/E[D_azar] <1 indica menor error que la referencia aleatoria IID en media, no prueba cooperación por sí solo; es necesario comparar con baselines factibles de igual información/actuación. El valor mínimo matemáticamente alcanzable depende de N mod k, no de 1/√N. La hiperuniformidad espacial requiere examinar varianza de conteos en ventanas espaciales, asunto distinto.

## Consecuencias y alcance

Una población con θ_i independientes requiere un protocolo de nacimiento/aprendizaje para añadir más individuos. No copiar arbitrariamente 36 identidades a N=960 y afirmar generalización. Se pueden estudiar poblaciones nuevas con pesos vírgenes, reproducción cultural mediada por mensajes autorizados, o reglas de distribución de políticas especificadas, siempre distinguiendo supuestos. Tampoco basta un 0% de estabilidad del aleatorio continuo para demostrar que el aprendizaje colectivo funcione.

Hasta ejecutar experimentos con C1/C2/C3, **no hay resultado científico V3B sobre emergencia de cooperación**. La evidencia V2 anterior queda archivada como demostración de un algoritmo experimental distinto con aprendizaje centralizado y pesos compartidos.
