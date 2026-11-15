# V176 — ¿Qué hace la recurrencia evolucionada?

15/11/2026. Protocolo prospectivo de intervenciones sobre poblaciones congeladas, motivado por los diez resultados YA CONOCIDOS de V175. No es una réplica independiente de la evolución ni un rescate de su criterio primario fallado.

## A–C. Pregunta, antecedentes y diseño

V175 obtuvo Q=.4703/.5160 con RNN_RESOURCE, .4700/.5132 con RNN_FULL, .00154/.00382 con MLP_RESOURCE y .8116/.7905 con LINEAR_FULL. Ambos controles RNN_FULL fallaron el gate .70. La ventaja entre arquitecturas entrenadas mezcla diferencias de trayectoria selectiva y uso de memoria en ejecución. Antes de atribuirla a una institución, separar memoria causal, respuesta sensorial, heterogeneidad y resistencia a explotación.

Antecedentes fuertes: Itao y Kaneko arXiv:2507.22555v2 ya obtienen turnos cooperativos y prueban RNN con observación colectiva; Akiyama y Kaneko (2000,2002) ya estudian normas y dinámica cooperativa; Hamon et al. (GECCO2023,10.1145/3583133.3590703) evolucionan forrajeadores recurrentes con información local. Memoria, sostenibilidad o diversidad por sí solas NO son una novedad. Ningún contraste de este protocolo confirma una ley sociológica.

Poblaciones: las dos semillas finales completas de RNN_RESOURCE, RNN_FULL, MLP_RESOURCE y LINEAR_FULL de V175; no seleccionar individuos por rendimiento. No reentrenar. Ocho lotes nuevos, semillas176115–176122,128grupos de5 por lote y1000pasos, fitness individual medio pasos100–999. Muestrear cromosomas de la población con reemplazo; conservar índices y riqueza inicial comunes entre intervenciones. Q=sumatorio del fitness individual medio por grupo. La unidad de evolución sigue siendo la semilla original (n=2), no los1024grupos de prueba.

Intervenciones completas sobre cada población:

1. INTACT: política congelada sin cambios.
2. RESET: estado recurrente reiniciado antes de cada decisión. Misma población, entradas, física y condiciones iniciales. En políticas sin recurrencia debe ser idéntico a INTACT.
3. RESOURCE_CLAMP: entrada de recurso constante .1, conservando el recurso físico y las otras entradas normales. En el perceptrón original se cambia también el término observado de recurso.
4. SENSORY_CLAMP: recurso observado .1, riqueza propia observada1/M y colectiva observada1. Conserva genotipos, estado recurrente y física. Una Q alta aquí es compatible con un reloj interno o una mezcla de fenotipos; no demuestra respuesta a infractores.
5. CLONAL_GROUPS: todos los miembros del grupo reciben el genotipo del primer miembro sorteado. Mantener riquezas iniciales individuales. Intervención sobre diversidad genética intragrupo, no sobre identidad de experiencia o riqueza. Cambia la distribución conjunta, no el marginal esperado de genotipos.
6. ALWAYS_HARVEST_INVADER: solo persona0 fuerza extracción en cada paso; las demás conservan sus políticas. Comparar fitness de esa misma persona, de los demás y Q frente a INTACT, pareando grupo e inicialización. Un incremento privado demuestra explotabilidad frente a ESTE invasor; su ausencia no prueba equilibrio ni estabilidad evolutiva general.

Transferencia secundaria congelada a M3,8,16: solo INTACT y RESET para RNN_RESOURCE y LINEAR_FULL, mismos ocho lotes; escala de entrada M*y permanece explícita, sin suministrar riqueza ajena a RNN_RESOURCE. Sin entrenamiento ni criterio de generalización científica externa.

## D–G. Auditoría y criterios

Antes de intervenir, comparar el nuevo kernel con el de V175 en las cuatro arquitecturas, M3,5,8,16, con estados y parámetros aleatorios: fitness, acciones y recurso deben coincidir hasta1e−12; verificar también el fitness almacenado en las diez poblaciones finales de V175. RESET debe ser idéntico a INTACT para MLP_RESOURCE y LINEAR_FULL. Registrar hashes, límites de recursos y poblaciones antes de ejecutar. Congelar protocolo y código en commit remoto antes de las pruebas de políticas congeladas.

Contrastes mecanísticos de capacidad, definidos ahora y separados del primario de V175: necesidad de recurrencia en ejecución si Q_intact−Q_reset≥.15 en AMBAS poblaciones RNN_RESOURCE; capacidad sin señal variable si Q_sensory_clamp≥.30 y diferencia absoluta respecto a INTACT≤.05 en AMBAS; explotabilidad si fitness_invasor−fitness_residente≥.02 en AMBAS. Mostrar valores por semilla y lote, sin p-valores de pseudorréplicas. No denominar equivalencia estadística a una distancia puntual≤.05.

Informar tasas de extracción y cambios de acción y distribución de Q por grupo. Estos diagnósticos no convierten una regla eficaz en norma o institución: no hay comunicación, decisión de monitorear, acuerdo colectivo ni aprendizaje de un aparato de sanción en este juego.

## H–J. Decisión y alcance

V176 es una auditoría causal D1 de la interpretación de V175, no una nueva arquitectura. El fracaso de gates se conserva. Si no hay resistencia al invasor o la sensorialidad es prescindible, STOP_LOCAL a la reivindicación institucional de estas poblaciones. CT2 histórico61 permanece sin aumento y N2=N3=0; no acreditar originalidad por más lotes. La investigación siguiente requiere un rival informacional competente o una predicción nueva, no ampliar automáticamente esta ablación.
