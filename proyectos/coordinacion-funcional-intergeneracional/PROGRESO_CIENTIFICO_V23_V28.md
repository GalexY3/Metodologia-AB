# Estado científico de la aldea MARL: V23–V28

**Fecha de cierre:** 12 de noviembre de 2026. Documento de síntesis integradora para continuidad científica y evaluación de propuestas de investigación. Contiene resultados tanto positivos como negativos y diferencia los mecanismos demostrados de las hipótesis pendientes. Los datos, checkpoints, condiciones y preregistros están versionados en `v19_voluntary_exchange/`.

## Pregunta general

Bajo qué condiciones un conjunto de agentes inicialmente no coordinados, dotados de redes neuronales privadas y objetivos exclusivamente individuales, aprende simultáneamente intercambios voluntarios costosos y una división del trabajo funcional, sin asignación central de profesiones, recompensas colectivas, imitación de expertos ni políticas sociales preprogramadas.

**Criterio de «OBJETIVO COMPLETADO», todavía NO satisfecho:** cooperación voluntaria con retorno causal individual positivo y distribución de tareas aprendida desde cero, reproducible en varias semillas neuronales y sociedades reservadas, con transferencia robusta a cambios relacionales, múltiples profesiones, poblaciones mayores, perturbaciones y desaparición/reemplazo de personas. Una buena puntuación media de alimentación o un patrón ocupacional alternado no bastan.

## Resultados consolidados

### V23: aprendizaje simultáneo desde cero, N24 y k2

Las dos redes de cada individuo comienzan con parámetros privados aleatorios. Una aprende a donar o no donar un bien dirigido; la otra a cambiar de oficio en períodos discretos y con coste propio. Solo el retorno descontado de alimento propio entrena ambas políticas mediante REINFORCE.

Las cuatro semillas principales con currículo de costes progresivos alcanzaron en mundos congelados y reservados alimentos de 0,613, 0,698, 0,399 y 0,534. Sus efectos causales individuales medios de forzar una donación inicial fueron +0,344, +0,694, +0,375 y +0,098; la ablación de historial social redujo ese retorno a aproximadamente −0,12. Sus enlaces interprofesionales alcanzaron aproximadamente el 91–100%. En controles con historial social retirado durante entrenamiento, el reparto ocupacional puede seguir siendo casi perfecto mientras las donaciones desaparecen: una estructura potencial no implica que se realicen intercambios.

### V27: nuevas inicializaciones y reproducibilidad en otro ordenador

Se ejecutaron seis entrenamientos nuevos de la misma arquitectura V23 en GALEXY_TRAVEL (CPU), con semillas 7311, 8311, 9311, 10311, 11311 y 12311, sin aprovechar pesos ya entrenados. Cuatro nuevas políticas satisfacen el criterio preregistrado de alimentación superior en >0,05 al mejor de varios controles aleatorios y donación inicial causalmente beneficiosa en promedio. Las otras dos colapsan a no donar, aunque desarrollan una estructura de roles local.

Junto a los cuatro entrenamientos GPU originales, la tasa descriptiva es **8 de 10** inicializaciones. El intervalo Wilson binomial descriptivo al 95% es aproximadamente **0,490–0,943**, demasiado amplio para universalizar. La evidencia procede de dos instalaciones PyTorch distintas; debe reconocerse la diferencia de hardware y sistema de ejecución. Las seis semillas de mundos usadas para auditar cada red no son seis entrenamientos independientes.

**Conclusión empírica delimitada:** existe cooperación y división del trabajo conjuntamente aprendidas en una proporción no trivial de estas inicializaciones de N24/k2, pero la solución es dependiente de trayectoria y no aparece de manera garantizada.

### V24: salto a N48/N120 y cuatro profesiones

Se generalizó la política ocupacional privada a cuatro especialidades. La política donante seguía pudiendo emitir una única unidad por ronda. Cuatro entrenamientos de N48 y N120 con dos semillas por tamaño colapsaron al régimen sin intercambio, pese a conservar redes con elevada disponibilidad de profesiones complementarias. Un currículo posterior, V24b, que prolongó durante 800 actualizaciones el precio barato, también fracasó al imponer el precio final alto.

**Resultado formal de factibilidad:** cada persona necesita k−1 categorías distintas, pero cada donante emite como máximo un bien. La proporción de personas plenamente abastecidas está acotada por la fracción de donantes dividida por k−1. La alimentación media máxima satisface

`F_media ≤ 0,20 + g(0,80/(k−1) − c)`.

Con k=4, g=1 y c=0,12 el máximo teórico es solo 0,3467, y como máximo un tercio de la población puede completar sus necesidades en una misma ronda. Para k≥8 con c=0,12, ningún plan de regalos unitarios puede superar en alimento medio la línea base de 0,20. Estas propiedades obligan a normalizar escalas e impiden usar k=2 como referencia bruta.

### V25: tres unidades posibles por persona, cuatro profesiones

Se permitieron hasta tres donaciones voluntarias dirigidas por ronda y persona, sin programar cómo repartirlas. Un oráculo constructivo demuestra que en red circular de grado seis existe abastecimiento completo con ese flujo material, alcanzando comida 0,64 a c=0,12 o 0,88 a c=0,04, sin movilidad adicional. El oráculo es una prueba matemática y **no participa en el entrenamiento**.

En cuatro redes independientes de N48/k4, dos por coste, los agentes adquirieron contribuciones durante la etapa inicial barata, pero las abandonaron casi completamente cuando el coste subió. En sus políticas finales congeladas, el retorno causal individual de forzar un regalo adicional fue −0,12 a coste 0,12 y aproximadamente −0,04 a coste 0,04, **con cero personas de 48 obteniendo retorno medio positivo** en cada tratamiento.

La capacidad suficiente no genera por sí sola una relación de ayuda remunerada por comportamientos futuros de los vecinos. La contabilidad material y la incentivación intertemporal son condiciones separadas.

### V26: vida media del recuerdo de favores

Se conservó el motor V25 y se cambió exclusivamente la persistencia de la señal individual `trust` de cada vecino, pasando de decaimiento nulo (δ=0, el control V25) a δ=0,94 y δ=0,99. Cuatro entrenamientos independientes a precio final c=0,04 recuperaron alimentos próximos a 0,201–0,202 y escasos regalos. En auditoría de políticas congeladas los retornos de forzar la donación oscilaron entre −0,046 y −0,048, con cero personas de 48 obteniendo beneficio causal medio positivo.

La mera extensión de memoria de donantes no basta para producir cooperación individualmente rentable en este problema de cuatro especialidades. Esto restringe explicaciones demasiado simples del fracaso basadas en que cada actor olvida el favor al cabo de un turno.

### V28: horizonte finito, racionalidad limitada y último turno

La estructura de acciones compartida por V23–V26 impone un coste privado positivo a cada regalo. Si no hay posibilidad de respuesta después de la última ronda, regalar al final tiene una pérdida estricta de c para el donante, cualquiera que sea el beneficio contemporáneo del receptor. Bajo racionalidad secuencial, conocimiento común del horizonte finito y ningún valor terminal, el argumento se propaga por inducción hacia atrás: el juego admite una trayectoria de equilibrio perfecto en subjuegos sin contribuciones.

Esta restricción estratégica es independiente del techo material de V24. En evaluación temporal congelada, las políticas cooperativas V23 siguen regalando en sus últimos ocho turnos casi lo mismo que en los ocho primeros. Por tanto, la cooperación aprendida puede ser una convención conductual beneficiosa **contra las políticas que los agentes vecinos efectivamente despliegan**, sin constituir un equilibrio perfecto en subjuegos entre agentes idealmente racionales. V25 conserva unos pocos regalos y estos tienden a disminuir durante el episodio.

## Distinciones mecanísticas necesarias

**Estructura social potencial:** la red y los roles ofrecen socios de profesiones complementarias. No implica que se emitan productos. Se mide mediante disponibilidad de clases distintas en vecindad, separada de la cobertura real.

**Acción contributiva:** un individuo decide soportar un coste para enviar una unidad a otro. La frecuencia de contribuciones no prueba que sea sostenible.

**Consecuencia material colectiva:** alimento y cobertura alcanzados mediante bienes realmente recibidos. Puede aumentar mediante reglas exógenas de producción, que deben declararse distintas de las políticas aprendidas.

**Reciprocidad causal individual:** diferencia en retorno propio futuro entre donar obligatoriamente una unidad y no hacerlo, con el resto de actores siguiendo políticas congeladas y escenarios emparejados. En los V23 exitosos es positiva; en los V25–V26 finales es negativa.

**Robustez interinicialización:** fracción de políticas entrenadas desde distintas semillas que cumplen un umbral fijado antes de evaluarlas. No se estima a partir del número de mundos usados en cada auditoría.

**Estabilidad estratégica:** una conducta es óptima también frente a las posibles desviaciones de otros actores en cada continuación; no está demostrada en V23, e incluso existe una tensión formal con la finitud del episodio.

## Hipótesis prioritarias derivadas del conjunto

**H29a, continuidad de relaciones:** el aprendizaje de reciprocidad positiva en k4 requiere que la relación social tenga un valor futuro efectivo que no se pierda por un final terminal públicamente conocido. Contrastar trayectorias de duración desconocida y continuidad social con episodios de horizonte fijo, manteniendo recompensas individuales.

**H29b, reconocimiento de socios y tipos de bienes:** para k4 los agentes deben aprender no solo quién les ayudó, sino de qué oficio provino el bien y en qué tipo de reciprocidad futura pueden confiar. Contrastar actores con información de ayudas agregadas frente a memoria por socio y categoría, controlando el número de parámetros.

**H29c, formación de cuencas de cooperación:** V27 identifica inicializaciones exitosas y otras que colapsan bajo un protocolo idéntico. Comparar indicadores tempranos (donaciones dirigidas recibidas, densidad de enlaces complementarios, recurrencia de parejas, dependencia de señales sociales) para detectar puntos críticos de bifurcación sin seleccionar umbrales a partir de los desenlaces finales.

**H29d, persistencia y sustitución de individuos:** una sociedad puede mantener una convención si reestablece el reparto de especialidades y la confianza después de perturbaciones. Estudiar nuevas generaciones, recambio de agentes y enlaces reconectados.

## Archivos vinculados

Todos los scripts, pesos, historiales, JSON de auditoría, CSV resumen y pruebas de integridad se encuentran en `v19_voluntary_exchange/`. Los informes durables que constituyen la evidencia principal son:

- `v19_voluntary_exchange/results/RESULTADOS_INTEGRALES_V23.md` (coaprendizaje y auditoría causal).
- `v19_voluntary_exchange/results/RESULTADOS_INTEGRALES_V24.md` y `v19_voluntary_exchange/V24_TEOREMA_FACTIBILIDAD.md` (fracaso multiescala y límites de producción).
- `v19_voluntary_exchange/results/RESULTADOS_INTEGRALES_V25.md` (capacidad triple y sus controles).
- `v19_voluntary_exchange/results/RESULTADOS_INTEGRALES_V26.md` (memoria persistente).
- `v19_voluntary_exchange/results/RESULTADOS_INTEGRALES_V27.md` (diez inicializaciones y tasa de éxito).
- `v19_voluntary_exchange/results/RESULTADOS_INTEGRALES_V28.md` y `v19_voluntary_exchange/V28_FINITE_HORIZON_GAME_THEORY.md` (perfil temporal y argumento estratégico).
- `GLOSARIO_GLOBAL_SOCIEDADES_MARL.md` (definiciones globales consolidadas).

**Estado operativo:** V23–V28 completados, documentación y checkpoints versionados. Los tests automáticos del laboratorio han superado 56 comprobaciones en el PC principal tras V28; la réplica CPU y las seis nuevas semillas están documentadas separadamente. No afirmar éxito universal ni «OBJETIVO COMPLETADO».
