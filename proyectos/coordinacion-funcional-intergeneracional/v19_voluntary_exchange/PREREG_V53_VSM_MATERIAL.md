# V53 — Prueba material de mecanismos inspirados en el Modelo de Sistema Viable de Stafford Beer

**Prerregistro 2026-11-13, anterior a la simulación V53.** Este experimento no asume que el Modelo de Sistema Viable (VSM) sea correcto ni que las cinco funciones sean necesarias o suficientes. Comparamos la productividad neta, la supervivencia y los costes de mecanismos regulatorios concretos, no etiquetas organizacionales.

## Fundamentación

Stafford Beer (1984, 1985) formula las funciones operativas S1, coordinación S2, cohesión/control interno S3 con auditoría S3*, inteligencia adaptativa S4 y política/identidad S5; enfatiza la recursión de sistemas viables. La ley de variedad requerida de W. Ross Ashby impone límites a la capacidad de regulación dada la diversidad de perturbaciones y respuestas posibles. La evidencia empírica cuantitativa es heterogénea: Crisan Tran (2008/2009) no confirmó por separado las cinco hipótesis de startups; Schwaninger y Scheef (2016) informaron de apoyo a su conjunto en organizaciones. Estas publicaciones no suponen una demostración de universalidad. Lecturas y DOI: Beer 1984 https://doi.org/10.1057/jors.1984.2 ; Ashby 1956 https://ashby.info/Ashby-Mechanisms_of_intelligence.pdf ; Crisan Tran https://doi.org/10.1504/IJASS.2008.022795 ; Schwaninger & Scheef https://doi.org/10.1080/01969722.2016.1209375 .

## Alcance operacional y anclaje a nuestra simulación

48 personas en 12 equipos K4 con cuatro ocupaciones complementarias **ya diferenciadas** y decisiones de regalo cooperativas **idealizadas**. Este es un *límite favorable* derivado de la economía de V25/V51/V52, NO un nuevo entrenamiento ni una reproducción idéntica de los logits V52. Cuando todos están operativos y cooperan, cada uno recibe tres tipos, y su comida física es exactamente 0,20+0,55+0,25−0,04×3=0,88 por ronda. No asignamos nuevos recursos por instalar regulación. Un actor operativo regala a los compañeros vivos, pagando 0,04 por receptor; una baja productiva temporal impide enviar bienes, aunque la persona pueda seguir consumiendo; una muerte elimina permanentemente producción y consumo de esa persona. Roles, equipos y conectividad permanecen exógenos: V53 aísla la viabilidad material posterior a la emergencia de especialización.

Cada actor tiene un almacén personal de comida, inicialmente 1,20 unidades, capacidad máxima 2,20. Consume 0,75 unidades por turno. Si al final de un turno su saldo es negativo, muere y deja de producir. Se pierden los excedentes que superan la capacidad de almacenamiento (no se convierten automáticamente en alimento adicional). Horizonte de 96 rondas. La función alimentaria de V25 determina la entrada por turno; los costes de organización y transferencia se deducen físicamente antes del consumo. El almacén es un cambio explícito del entorno original V25 para hacer medible la viabilidad a largo plazo, no una característica del simulador previo.

Perturbaciones preprogramadas (mismas secuencias por semilla-mundo para todos los tratamientos):
- **QUIET:** ninguna interrupción productiva.
- **PATCHY:** cada equipo puede sufrir un evento independiente de interrupción de un productor, con probabilidad 0,09 por ronda, duración 4 rondas; el productor afectado no produce mientras dura el episodio.
- **SYSTEMIC:** eventos comunes a toda la sociedad con probabilidad 0,11 por ronda y duración 5 rondas; en cada equipo se interrumpe un productor, con identidad determinada exógenamente.
- **HEAVY:** perturbaciones independientes probabilidad 0,16/duración 5, más sistémicas probabilidad 0,035/duración 4.

Los eventos de interrupción prolongan bloqueos existentes y se sortean con generadores independientes de cualquier política de regulación; añadir un mecanismo no cambia la secuencia de sucesos. En el período siguiente se observa si un trabajador está disponible. Los pronósticos futuros se proporcionan exógenamente como un *oráculo de información*, no nacen espontáneamente de la sociedad.

## Arquitecturas y alternativas

Se comparan ocho regímenes de costes explícitos:

1. **NONE:** solo producción S1, sin gestión ni transferencia; coste organizacional 0.
2. **LOCAL:** igualación de reservas dentro del equipo, proxy limitado de coordinación S2, coste administrativo 0,004 por persona viva/ronda y pérdida material del 5 % del volumen transferido.
3. **GLOBAL:** ayuda entre equipos enviada con un turno de retraso y sin igualación local, proxy parcial de metasistema S3, coste 0,008 por persona viva/ronda y 5 % de pérdida del alimento enviado.
4. **LOCAL_GLOBAL:** combinación de las dos anteriores, coste 0,012.
5. **FORECAST:** LOCAL_GLOBAL con conocimiento verdadero de interrupciones del siguiente turno, coste adicional de 0,008 por persona viva/ronda, proxy de S4.
6. **PLACEBO:** LOCAL_GLOBAL con señal del siguiente turno **permutada entre equipos**, misma capacidad de información y coste que FORECAST.
7. **POLICY:** LOCAL_GLOBAL con un umbral de reserva común sensible a la tasa de interrupciones observadas, coste adicional de 0,003; proxy muy parcial de S5, no de una identidad colectiva aprendida.
8. **FULL_PROXY:** LOCAL_GLOBAL + FORECAST + POLICY; no contiene todos los canales ni recursiones formales de Beer, y por eso no se denomina VSM completo.

Todas las transferencias son conservativas salvo pérdidas explícitas. La igualdad local redistribuye el almacén del equipo sin creación de comida. La transferencia global solo usa excedentes almacenados en equipos vivos y llega al período siguiente; los envíos se hacen de forma proporcional a necesidades anunciadas y excedentes, sin premiar al receptor fuera de la asignación de recursos ya existentes. Los avisos anticipatorios no redistribuyen mágicamente ni crean alimentos. S5 no es una persona ni un mandato: aquí solo una regla de umbral compartido. La comparación principal sigue siendo NONE vs LOCAL, NONE vs LOCAL_GLOBAL, LOCAL_GLOBAL vs FORECAST, FORECAST vs PLACEBO, POLICY vs LOCAL_GLOBAL, FULL_PROXY vs LOCAL_GLOBAL.

## Resultados, criterio y falsación

Seis semillas ambientales nuevas (999101, 999107, 999109, 999121, 999131, 999137), 128 mundos por semilla/condición, 96 turnos. 8 mecanismos×4 regímenes de perturbación =32 celdas; **24.576 mundos** en total, antes de contar las realizaciones internas. No hay búsqueda posterior de semillas «favorables».

Resultado primario: porcentaje medio de personas vivas al final; indicador de equipos con cuatro especialistas vivos; alimento neto por persona viva-ronda y pérdida material organizacional total. El contraste de supervivencia entre tratamientos usa la **misma semilla y mundo** para reducir varianza; intervalos descriptivos bootstrap por seis semillas, sin tratar los 128 mundos o 48 personas como seis experimentos neuronales adicionales. Un mecanismo solo tiene ventaja material si mejora supervivencia sin producir comida de la nada; también se informará su balance de costes.

- H53a: en PATCHY, LOCAL conserva al menos +5 puntos porcentuales de población viva frente a NONE.
- H53b: en PATCHY, LOCAL_GLOBAL añade ≥+5 puntos a LOCAL, descontando costes.
- H53c: en PATCHY, FORECAST añade ≥+3 puntos a LOCAL_GLOBAL.
- H53d: PLACEBO no supera FORECAST en supervivencia en PATCHY; contraste de identidad de la información.
- H53e: en QUIET, NONE tiene mayor alimento neto medio por persona-ronda que FULL_PROXY; penalización por capas innecesarias.
- H53f: en SYSTEMIC, FULL_PROXY no puede mantener todas las sociedades completamente viables cuando la secuencia de interrupciones produce una pérdida material superior a la capacidad máxima de sus reservas; se comprobará empíricamente la tasa de fallo, pero las restricciones de conservación son anteriores a la simulación.

**Las hipótesis no implican que cinco funciones sean condiciones necesarias/suficientes de viabilidad.** En particular, probar equivalencia material de un proxy no prueba equivalencia conceptual de S1–S5. El objetivo es identificar en qué regímenes hacen falta información local, coordinación de reservas o anticipación, y en cuáles su coste domina. Deben documentarse fallos de diseño, bootstrap, costes, efectos de casos extremos y limitaciones.

## Continuación científica

El resultado V53 indicará qué canales tienen rendimiento material neto. Solo después se justifica una V54 que permita a agentes individuales **inventar, abandonar o pagar voluntariamente** esos mecanismos, comparando sus trayectorias con gobernanza policéntrica, información reputacional y control central. La mera implantación de un regulador no demuestra su emergencia espontánea.
