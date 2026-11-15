# Disponibilidad funcional, equilibrio y formación

## Tres problemas que requieren pruebas distintas

La organización colectiva no puede reducirse a una fotografía de la composición del grupo. Conviene distinguir la existencia de una configuración individualmente estable, la posibilidad de alcanzarla mediante un proceso de adaptación y la disponibilidad de sus funciones a lo largo del tiempo. Estas propiedades pueden variar por separado. Una configuración puede existir sin ser accesible desde el estado inicial, y una función puede estar disponible durante gran parte del tiempo aunque las personas que la sostienen tengan motivos para cambiar su conducta.

El programa examinó esta distinción en un juego de ocupaciones complementarias, primero mediante mejores respuestas y después mediante contratos y aprendizaje. Este capítulo sintetiza la línea identificada por los archivos `V153_ENDOGENOUS_OCCUPATIONS_MEMBERSHIP_SEQUENCING.json` a `V167A_EXACT_CERTIFICATION_AUDIT.json`. Algunos números de versión se reutilizaron en una línea paralela: la unidad documental es el nombre completo y su hash, no el número aislado. La auditoría V166 y su verificación posterior de hashes preservan la procedencia de los resultados.

## Incentivos y equilibrio en el juego de ocupaciones

La utilidad material de una persona i en un grupo de k integrantes se define como

u_i = f(d) − δ 1[r_i=c] + β(1[r_i=c]−n_c/k),

donde d es el número de profesiones representadas, c la profesión costosa y n_c el número de personas que la ejercen. La compensación es de suma cero. El término β es una regla diseñada y compartida por el grupo, no una institución descubierta por sus participantes. Cambiar de ocupación tiene coste s.

En el caso de cuatro profesiones, la ganancia material por completar la cobertura es B=f(4)−f(3)=13/30, el coste crítico δ=0,5 y el coste de cambio s=0,015. La enumeración de las 256 configuraciones ordenadas y sus desviaciones permite identificar equilibrios sin depender de una simulación particular. Sin compensación hay 36 estados localmente estables, todos con tres profesiones. Con β=0,125 hay 24, todos completos. La cobertura incompleta no es aquí un fallo de cómputo para encontrar un equilibrio completo: el incentivo privado lo excluye bajo esas reglas.

El coste de reasignación produce dos umbrales:

β_salida = (4/3)(δ−s−B) = 0,068889;

β_entrada = (4/3)(δ+s−B) = 0,108889.

Entre ellos coexisten configuraciones completas e incompletas. En β final=0,09, 64 mundos con historia inicial sin incentivo terminan con 0% de grupos completos; con historia inicial β=0,125 terminan con 100%. Al eliminar el coste de reasignación, ambas historias alcanzan 100%. Es una intervención que identifica el papel del coste en la divergencia histórica dentro del juego. La histéresis, sin embargo, es un fenómeno conocido y no constituye por sí sola una contribución sociológica original.

La remuneración excesiva también puede generar monocultivo de la profesión subvencionada. V158 y V160 muestran una segunda región de coexistencia: con el mismo β final=1,0, una historia moderada conserva grupos completos y una historia de compensación muy alta conserva monocultivos. Este resultado delimita una interpretación lineal de los incentivos: compensar la función menos atractiva y sobrerrecompensarla tienen consecuencias distintas en la misma economía artificial.

## Desde la mejor respuesta hacia el aprendizaje

Las reglas de adaptación modifican qué puede inferirse de una trayectoria. V154 compara una mejor respuesta con contrafactuales de todas las profesiones, un ensayo reversible de una alternativa y un bandit privado sin contexto. Los dos primeros alcanzan cobertura completa; el bandit conserva aproximadamente el 6,6%, cerca del control aleatorio. El resultado no establece una imposibilidad general del aprendizaje privado: los procedimientos tienen información diferente, el bandit mantiene exploración y carece de contexto.

Esta limitación motivó los experimentos posteriores de aprendizaje conjunto, contratos y agentes tabulares contextuales. Su lectura debe conservar el problema de identificación: un algoritmo que recibe la utilidad exacta de cambiar unilateralmente resuelve un problema distinto del de una persona que solo observa el resultado de su acción después de que otros también cambien. Los experimentos de secuenciación son pertinentes, pero sus efectos no pueden atribuirse automáticamente a negociación institucional.

## Compensación voluntaria y disponibilidad sin estabilidad

V159 introduce un protocolo de oferta y aprobación local que reparte el coste de la función crítica. La viabilidad del acuerdo está limitada por el excedente total: si la carga y los costes superan kB, las transferencias internas no pueden crear el beneficio que falta. Con excedente suficiente, un precio moderado permite formar equipos y una pretensión excesiva es rechazada. La propuesta, los derechos de aceptación y el cumplimiento son reglas del investigador.

Retirar la vinculación permite a los donantes revocar el pago. En el corte terminal de V159 aparecen aproximadamente tres cuartas partes de equipos completos. La auditoría exhaustiva de V162 encuentra que ninguno de los grupos simultáneamente completos es localmente estable frente a todas las desviaciones consideradas. La composición final no describe su equilibrio de incentivos.

V163 observa cada instante durante 12.000 oportunidades y 64 mundos nuevos. La disponibilidad funcional media es 72,5015%, similar en ventanas tempranas y tardías. Solo 5,506 de los 30 grupos tienen un contrato activo en promedio, y un 54,149% está completo sin contrato vigente. Es posible sostener disponibilidad por renovación de personas, ocupaciones y acuerdos aun cuando cada configuración actual admita una mejora privada. Eso no demuestra legitimidad, adhesión normativa o autogobierno: el mecanismo de renovación sigue siendo diseñado.

## Un modelo micro–macro que puede comprobarse exactamente

V164 implementa decisiones microindividuales en otra tecnología, manteniendo una estructura reducida de tres clases de estados. I designa un grupo incompleto con dos candidatos capaces de cubrir la función ausente. B designa cobertura completa con contrato vigente y U, cobertura completa tras la revocación, antes de que salga el trabajador crítico. Si se selecciona uniformemente una persona entre N=30k por evento, las probabilidades de transición por evento son

I→B: 2/N; B→U: (k−1)/N; U→I: 1/N.

Las demás selecciones dejan el estado de esa cadena sin cambios. La conservación de flujo iguala π_I·2/N, π_B·(k−1)/N y π_U/N. Al normalizar se obtiene

π_I=(k−1)/(3k−1), π_B=2/(3k−1), π_U=2(k−1)/(3k−1).

La disponibilidad funcional es π_B+π_U=2k/(3k−1). Para k=4 predice 72,7273%, compatible en magnitud con la campaña anterior. Los nuevos experimentos cubren k=2,3,4,5,6,8, con 64 mundos por tamaño y 30.000 decisiones. Los seis valores exactos quedan dentro de los intervalos descriptivos de sus simulaciones.

Este contraste es una verificación entre implementaciones de una estructura probabilística diseñada, no seis observaciones sociales independientes. La duración de un episodio funcional se expresa como N/(k−1)+N eventos globales. El crecimiento de ese número al aumentar k incorpora el crecimiento de N; no puede traducirse en mayor duración de reloj sin definir una escala temporal comparable.

## Consentimiento, correlación y tamaño

Si cada uno de k−1 avisos favorables llega con probabilidad q independiente, la entrada I→B se multiplica por q^(k−1). La disponibilidad pasa a ser

F(k,q) = [1+1/(k−1)] / [1/(2q^(k−1))+1+1/(k−1)].

Para q<1 fijo, F tiende a cero al crecer k. La restricción es una propiedad de la transmisión conjunta exigida por la regla de unanimidad; las preferencias de los donantes no están evolucionando en esta prueba. V165 conserva una discrepancia: en k=8,q=0,8 el valor teórico queda fuera del intervalo bootstrap inicial. V165B, diseñado después de observarla y con 128 mundos nuevos, resulta compatible con la teoría. La segunda campaña no convierte retrospectivamente la primera en confirmación prospectiva.

V167 mantiene q=0,8 pero sustituye parte de los avisos independientes por una señal común. Si ρ es la fracción de encuentros en que todos reciben esa misma señal, la aprobación conjunta vale

P_aprobación=(1−ρ)q^(k−1)+ρq,

y F=2P_aprobación·k/(k−1) / [1+2P_aprobación·k/(k−1)]. Para ρ>0 fijo, la disponibilidad límite es 2ρq/(1+2ρq); para ρ=0 y q<1 desaparece. En k=12, la simulación pasa de 16,04% con avisos independientes a 63,42% con señal totalmente común.

Las nueve celdas fueron verificadas con aritmética racional y sus intervalos contienen las predicciones. La conclusión está condicionada al protocolo: correlacionar mensajes favorables aumenta la entrega simultánea de un paquete requerido. El modelo no contabiliza daños de errores comunes, captura de un canal público ni poder de decisión sobre la señal. Publicar o centralizar información no queda recomendado universalmente por esa identidad.

## Conexión con las nuevas pruebas y alcance sociológico

V169–V172 sustituyen parte de las mejores respuestas por aprendizaje privado y retiran la profesión preparada. V175–V180 añaden un modelo ecológico externo, aprendizaje de políticas recurrentes y apertura de una clase de decisión. Estas extensiones permiten contrastar dependencias que no estaban presentes en el mecanismo exacto de tres estados. Su coincidencia temática no hace que un modelo valide al otro: cambian el recurso, la tecnología, el significado de función y el proceso de adaptación.

La continuidad conceptual es más limitada y más defendible: disponer de una configuración estable, descubrirla, conservarla y mantener una función mediante renovación son preguntas diferentes. Este capítulo ofrece mecanismos exactos y falsadores para separarlas. La aportación al TFM consiste en hacer explícitas esas condiciones y confrontarlas con aprendizaje y evidencia externa. No acredita una ley sociológica original, ni confirma una interpretación de sistemas viables o de instituciones humanas a partir de identidades del simulador.
