# V180 — Abrir el espacio de políticas después de la cooperación

15/11/2026. V178 está completo y conocido. Su hipótesis primaria de ventaja privada afín FALLÓ; no se ejecuta M16. Los8controlesFULL lograronQ_tail .745–.815, mientras AFFINE_FULL logró .029–.040. Esta diferencia motiva una hipótesis nueva y NO era el primario de V178. Los resultadosV180 aún no se han ejecutado.

## A–C. Hipótesis, alcance y rivales

Pregunta: ¿añadir un intercepto entrenable destruye también una población cooperativa ya formada, o únicamente dificulta llegar a ella? La representación original usa χ[x+S M y_i+A Σy], con intercepto exactamente0; la extensión χ[x+S M y_i+A Σy+b] contiene la política original. Ambos son perceptrones clásicos. El juego, sus reinicios y la selección son los del preprint de Itao y Kaneko arXiv:2507.22555v2. El artículo ya reconoce dependencia de inicialización, estructura, transitorios y clases de estrategia y prueba RNN; no atribuirle una garantía universal que no formula.

Antecedentes: Schmid et al.2022 (10.1371/journal.pcbi.1010149) ya muestran que aumentar el espacio de estrategia puede perjudicar la cooperación. La mera caída al añadir un parámetro no es novedad general. Candidata específica aún por falsar: vulnerabilidad de la regla de turnos bajo desviaciones afines ordinarias, separando aparición, mantenimiento y mutación dañina. No hay nuevo mecanismo institucional aprendido ni confirmación social externa.

### Experimento de mantenimiento prospectivo

Ocho poblaciones FULL finales deV178 (semillas178115–178122), sin seleccionar individuos. Nueva semilla180115–180122, emparejada en ese orden. Reiniciar b=0 en AMBOS brazos: el tercer gen era neutral y había derivado, y no se debe activar accidentalmente su valor anterior. Conservar todos los S,A originales. Nuevos3000turnos generacionales,100grupos×5personas,1000pasos, mismos fitness privado y física; reagrupación y reproducción como enV178.

- LOCKED: políticaFULL, tercer gen neutral, se mutan los3genesN(0,.1).
- OPEN: políticaAFFINE_FULL, mismos3genes y mutaciones; el tercero ahora es un intercepto funcional.

Inicialización, cinta aleatoria y número de genes son comunes; selección y trayectorias divergen por el fenotipo del tercer gen. Dosworkers×3threads, prioridadBelowNormal, afinidad de seisCPU. Registrar curvas completas, poblaciones, checkpoints y RNG cada500generaciones.

Primario de pérdida de mantenimiento: Q_tail(OPEN)<.30 Y Q_tail(LOCKED)−Q_tail(OPEN)≥.50 en al menos6/8pares. Gate del control: LOCKED≥.70 en al menos6/8. Si no se cumple, no llamar generalizada la pérdida de mantenimiento. No elegir mejor checkpoint. La unidad de réplica es la evolución nueva emparejada, no las generaciones.

### Incentivos de invasión: selección y evaluación separadas

Poblaciones residentes originalesFULL deV178, bresidente=0. Persona0 es la mutante; las demás permanecen. En todos los grupos contrafactuales se conservan S,A y riqueza inicial. Fitness pasos100–999,1000pasos. Cuatro lotes180315–180318×128grupos por población.

DESCUBRIMIENTO: poblaciones178115–178118. CandidatosBIAS: b∈{−.1,−.03,−.01,−.003,0,.003,.01,.03,.1,.3,1}. Rival fuertePLANE: todos los49pares(ΔS,ΔA) de {−1,−.3,−.1,0,.1,.3,1}². Ningún intercepto enPLANE. Seleccionar por familia UN candidato común que maximice el mínimo incremento privado medio entre las cuatro poblaciones de descubrimiento; desempate por menor norma euclídea y después orden de la lista. NO seleccionar un mutante distinto por población o grupo.

EscribirSELECTION.json y congelarlo en remoto ANTES de validar. VALIDACIÓN: poblaciones178119–178122, nuevos lotes180415–180418×128grupos; no consultar sus pagos mutantes antes de congelar. Criterio de invasión destructiva: candidatoBIAS incrementa fitness privado≥.01 y reduce Q≥.05 en lasCUATROpoblaciones de validación. Informar también todos los resultadosPLANE. Si el rivalPLANE produce lo mismo, no atribuir especificidad exclusiva al intercepto. Un fallo de estos criterios se conserva, aunqueOPEN colapse: la mutación perjudicial o la búsqueda pueden ser alternativas.

Comprobar puntos finales y mutantes seleccionados con código original modificado SOLO en el score de decisión para sumar un intercepto; código original intacto en disco, modificaciónAST registrada. Esto verifica el motor, no constituye confirmación científica externa ni nueva muestra de evolución.

## D–G. Formalización auxiliar y falsadores

Para interceptos estrictamente no nulos, el signo de cada acción es constante en un entorno suficientemente pequeño del origen(x=0,y=0). SeaH+ el número de interceptos positivos. Con crecimientoR(x)=2x−x² yβ=.9/M, el Jacobiano triangular tiene autovalores 2(1−βH+) y .75 (este último Mveces). El origen es localmente asintóticamente estable si H+>M/1.8, e inestable en dirección del recurso si H+<M/1.8. No aplicar a interceptos0, que sitúan el origen en las fronteras de decisión. Con M5, H+≥3 estabiliza localmente el colapso.

Es una linearización de un sistema conocido, no una ley nueva ni prueba de que el tamaño de la cuenca cause toda la diferencia de entrenamiento. PRIVATE_THRESHOLD también puede satisfacer esa condición y aun así mantener una trayectoria de Q≈.53 bajo los reinicios del experimento. Por tanto, existencia de atractor de colapso NO basta para explicar la emergencia fallida. Verificar el Jacobiano con diferencias finitas y mostrar este límite explícitamente.

## H–J. Registro y decisión

BRANCH D2 respecto a la hipótesis informacionalV173: conserva juego y estimando material, cambia la pregunta de monitoreo a apertura del espacio de políticas y mantenimiento. V178negativo permanece;V180 no lo rescata. Congelación remota antes de ejecutar. Auditar A–J por estudio, no multiplicar ciclos por semillas. CT2 histórico61 permanece sin incremento; N2=N3=0. Si no aparece vulnerabilidad discriminante frente aPLANE o depende de mutación constante sin desviaciones ventajosas, formular la conclusión como limitación de representación/selección de este simulador.
