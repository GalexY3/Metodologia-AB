# AB-R EVIDENCE6 · Informe de cierre N15–N20

**Programa de investigación:** Alejandro Panera Pascual. **Corte:** 28 octubre 2026. **Rama:** `research/ab-r-mercados-pareja-20261028`, no fusionada en main. **Método:** AB 3.2.1/O2–O7. **Estado:** 6 autorizados, 6 cerrados según su alcance, de los cuales 2 experimentales sintéticos N17–N18, 3 documentales N15/N16/N19 y 1 de planificación N20. **Intentos inválidos en este bloque: 0**. **45 corridas computacionales** de 9 condiciones por 5 semillas (dos ciclos sustantivos, no 45 hallazgos); 0 confirmaciones externas. N1 nuevos: 0; N1 histórico auditado: NO_AUDITED; N2=N3=0. CT2 de esta línea: **17→17**, ordinal no probabilidad. DRIFT D0,0, misma pregunta con controles mejorados.

Prerregistro [PREREG.json](PREREG.json), commit `4c8cf495326d28faa8ae3ccb42c0b99469655e6c`; fuente congelada primero como SHA-256 en [SOURCE_FREEZE.json](SOURCE_FREEZE.json), commit `792ff4393701e5021d40aa5dd8bcd3b77efb0653`; fuente íntegra ahora en [experiment.py](experiment.py), commit `746221a2e570c34ade50cc7c58ecf3f683d41a94`, SHA-256 `2028d687102c211a2bc31994a80985d643aaf48752a5da21b3bf5ae0e1072dc3`; [RUNS.csv](RUNS.csv), [SUMMARY.csv](SUMMARY.csv), [QA](QA_AND_ERRATA.json) y [LEDGER A–J](LEDGER.json). La huella FNV del archivo subido coincidió con la fuente local byte a byte y el SHA-256 local se conserva; **clon limpio no ejecutado**. La ficha de congelación tenía `bytes=6909`, tamaño real `6972`; constan errata y hash original correctos. La ejecución local se repitió con resultados CSV idénticos; no es replicación de campo.

## Objetivo y resultado científico
Se quiere saber cuándo dos agentes que maximizan calidad absoluta de pareja acaban mostrando homogamia de **valor relacional**, sin preferir semejanza por sí misma. La variable principal sigue siendo `r(V_h,V_m | par formado)`, necesariamente acompañada de `coverage` calculada sobre todos los individuos y de la mediana de diferencia absoluta de valor. La unidad son agentes **sintéticos** de preferencias 60/40 cruzadas, estatus y belleza independientes Uniforme(0,1), parejas binarias heterosexuales y grafos regulares de exposición. No se ha calibrado una muestra de solteros españoles.

### N15 · DENOMINADOR ESPAÑOL: `DOCUMENTARY_VALID; DATA_ACCESS_BLOCKED`
Se localizaron las seis distribuciones y formatos de la tabla nacional **INE ECP 59583** (CSV, XLSX, JSON), edades simples, fecha y sexo. Las aperturas directas de `59583.csv` y del endpoint API resultaron inaccesibles, y la conexión HTTP desde el contenedor falló por DNS. **No se descargaron bytes ni se calculó población de 20–39 años por sexo al 1/7/2026**. Las cantidades secundarias antiguas no se presentan como comprobadas. Aun con la tabla oficial, la población disponible románticamente requiere estado de pareja, orientación, intención y uso activo: no sustituir esos denominadores.

[Auditoría completa de acceso](INE_ACCESS_AUDIT.md). Fuentes oficiales: https://datos.gob.es/es/catalogo/ea0042823-poblacion-residente-por-fecha-sexo-y-edad-ecp-identificador-api-59583 ; https://www.ine.es/jaxiT3/Tabla.htm?t=59583

### N16 · MATRIZ EDUCATIVA: `DOCUMENTARY_VALID; MATRIX_ACCESS_BLOCKED`
Se identificó la tabla oficial **INE MNPM 60268** de matrimonios por estudios de ambos cónyuges. Tampoco se pudo acceder a sus CSV/JSON para obtener los `n_ij`. **No se ha calculado homogamia educativa neta**, ni se han inventado números. El protocolo distingue proporción diagonal observada `O=Σn_ii/N`, diagonal esperada por independencia `E=Σ(n_i+/N)(n_+i/N)` y O/E; excluir No consta en análisis principal y tratarlo como sensibilidad, controlar clasificación, año y cohortes. Una matriz de matrimonios no mide matches de app. Fuente: https://datos.gob.es/es/catalogo/ea0042823-matrimonios-por-nivel-de-estudios-de-los-conyuges-mnpm-identificador-api-60268 .

### N17 · COMPARADOR CON GRAFO DE OPORTUNIDADES PREDEFINIDO: `VALID_SYNTHETIC_EXPLORATORY`
N=240 (120/120), cada agente con 20 aristas potenciales en grafo bipartito regular, utilidades observables del candidato con ruido fijo diádico de SD 0,05. Cinco semillas. Todas las políticas conocen las valoraciones del grafo ex ante. Se compara Gale-Shapley estable en el grafo, greedy que acepta casi cualquier candidato suficiente (piso 0,05) y aspiración q adaptativa desde 0,80 con fatiga 0,02 por fracaso; la salida tras match es irreversible.

| Procedimiento | r valor (media) | Cobertura media | Distancia mediana media | Bloqueantes medios |
|---|---:|---:|---:|---:|
| Gale-Shapley | **0,9085** | **96,17 %** | 0,0565 | **0** |
| Greedy, acepta pronto | **0,0172** | **97,00 %** | 0,2052 | 599 |
| Adaptativo secuencial | **0,4121** | **41,33 %** | 0,0850 | 882 |

El resultado favorece la explicación de que **preferencias y procedimiento de asignación** son decisivos para la homogamia observada dentro del generador. No demuestra ventaja del algoritmo adaptativo. A pesar del mismo grafo e información inicial, DA resuelve el matching global sin compromisos irreversibles tempranos, mientras la búsqueda se desarrolla secuencialmente. Estas son políticas distintas: no confundir paridad de conocimiento inicial con equivalencia de estrategias, tiempo o bienestar. No inferir realidad humana a partir de r. Novedad general no acreditada frente a Gale-Shapley (1962) e Hitsch, Hortaçsu y Ariely (2010).

### N18 · CONTROL NEGATIVO DE ASINCRONÍA: `VALID_SYNTHETIC_WITH_GATING`
El mismo grafo k20 es evaluado exactamente una vez por cada extremo para todas las condiciones; los matches **solo se adjudican después de evaluar todos los perfiles**, eliminando la selección de salidas durante la exposición. Cada actor ve el mismo conjunto de perfiles, y el orden cambia. Umbral fijo q=.75 versus q adaptativo por rechazo propio de perfiles (`-0,008` cuando la evaluación es izquierda); likes permanentes o caducados tras diferencia de cinco posiciones locales de exposición.

| Estrategia | r valor | Cobertura | Parejas medias |
|---|---:|---:|---:|
| q fijo, simultáneo | **0,4774** | 11,50 % | 13,8 |
| q fijo, async persistente | **0,4774** | 11,50 % | 13,8 |
| q fijo, async TTL5 | 0,4281 | 6,50 % | 7,8 |
| q adaptativo, simultáneo | 0,5129 | 22,67 % | 27,2 |
| q adaptativo, async persistente | 0,4907 | 20,50 % | 24,6 |
| q adaptativo, async TTL5 | 0,2953 | 13,83 % | 16,6 |

**Control exacto:** en cada una de las cinco semillas q fijo simultáneo y q fijo asincrónico persistente produjeron exactamente las mismas aristas recíprocas, mismos emparejamientos, r y gaps. Esto es **una identidad del diseño** bajo evaluaciones fijas y diferidas, no un hallazgo 1/3. Diferencias al introducir fatiga o vencimiento son consecuencias internas de las reglas. El mecanismo TTL en este laboratorio se expresa en **posiciones de visión por actor**, no minutos reales, y la correspondencia no abandona el feed antes de terminar de evaluar el universo. La r calculada con apenas 7,8–27,2 parejas por réplica es muy inestable: rangos por semilla registrados en [SUMMARY.csv](SUMMARY.csv). No atribuir efecto puro a Tinder real.

### N19 · SEÑAL DE RECHAZO Y ESTATUS ANTE TERCEROS: `DOCUMENTARY_VALID; SOCIAL_MECHANISM_NOT_IDENTIFIED`
La literatura consultada confirma que los swipes negativos no suelen notificarse a terceros como feedback de valoración, aunque la ausencia de match pueda informar indirectamente al usuario. Los estudios de rechazo miden ghosting, dolor y autoestima; diarios estudian señales de actividad y vigilancia, no un coeficiente universal de pérdida de status social observada por terceros. Unmatching puede perjudicar necesidades psicológicas sin implicar descenso reputacional público. Por ello **no se valida la ecuación S_i(t+1)=S_i(t)-δ** para la población humana; permanece contrafactual sintético condicionado a una red de observación. [Revisión de fuentes y DAG](N19_REPUTATION_REVIEW.md).

### N20 · PRUEBA CONFIRMATORIA FUTURA: `PLANNING_AB_ONLY`
Los rivales `STATIC_PREF`, `DYNAMIC_SELECTION`, `VISIBLE_REPUTATION` y `SELECTION_ARTIFACT` requieren preferencia medida ex ante, grafo de exposición, denominador de usuarios elegibles y resultados reales. Una prueba ética de señales de reputación necesitaría consentimiento, auditoría, potencia y ausencia de perjuicio a personas. [Contrato de confirmación no ejecutada](N20_CONFIRMATORY_GATE.md). No se ha manipulado a usuarios ni accedido a logs de una aplicación.

## Auditoría adversarial F y Gate O2
- **PASÓ:** DA sin pares bloqueantes en las cinco semillas, unicidad de parejas, mismo conjunto de aristas, invariancia exacta del control q fijo y liked persistente, segunda corrida local idéntica byte a byte.
- **NO PASÓ / NO EJECUTADO:** descarga INE de matrices/edad, validación sobre solteros activos, comparación con datos de app, archivo source en clon limpio, replicación experimental externa.
- Fuente Python íntegra está en GitHub; firma sha256 registrada, pero clone-and-run por tercero `NOT_VERIFIED`.
- Distinguir condicionamiento al matching (correlación alta solo entre quienes forman pareja) del resultado poblacional de exclusión. N17 adaptativo excluye aproximadamente 58,7%: correlación positiva entre los emparejados no implica eficiencia, justicia o preferencia realista.
- Se mantienen evidencias que no favorecen teoría: DA supera fuerte a adaptación; mercado local N10 no fue monotónico; efecto privado de rechazo N05 fue nulo; descalibración española continúa; q fijo/async persistente empatan exactamente.

## CT2, grados y decisión AB
`CT2=17` antes y después de cada ciclo N15–N20. Se conserva trayectoria MATE10 post hoc `20`, BRANCH8 `17`, BRANCH6 `17`, EVIDENCE6 `17` en [JSON](CT2_TRAJECTORY.json), y [gráfica de escala completa y ampliada](CT2_TRAJECTORY.svg). Se trata de confianza ordinal sobre viabilidad de alcanzar hallazgo 2/3, **no probabilidad**. No hay hallazgos nuevos de nivel 1/3, 2/3 ni 3/3, porque el contraste mecánico es conocido o impuesto y faltan datos externos. N1 histórico no auditado. DRIFT D0,0.

**AB-DECIDE = STOP_CAMPAIGN por R5.** Se ha mejorado la auditoría de comparadores y de temporización; la fuente de mayor valor informativo siguiente es externa: CSV oficial materializable, matriz educativa con márgenes y/o registro ético de exposiciones, preferencias y reciprocidad de usuarios. Aumentar N de agentes o repetir seeds sin cambiar fuente no resuelve esos bloqueos.

**Propuesta de próxima autorización (NO ejecutada):** pedir excepcionalmente `BRANCHING 20 CICLOS` condicionados a **nueva evidencia primaria accesible**, de los cuales los primeros se dedicarían a materializar/validar datos demográficos y matrimoniales, análisis ponderado de homogamia educativa, identificación de logs de exposición legalmente accesibles y revisión adversarial de prior art. En ausencia de fuente nueva, R5 pararía antes del límite; no llenar 20 plazas con el mismo generador.

`SOLICITO BRANCHING 20 CICLOS CONDICIONADOS A NUEVA EVIDENCIA`
