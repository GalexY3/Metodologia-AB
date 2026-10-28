# Mercados de pareja: homogamia emergente sin preferencia por semejanza

**Proyecto AB-R (autoría de investigación: Alejandro Panera Pascual)**. Proyecto hermano de `proyectos/politics-fantasy-league/`, deliberadamente más ligero. **Estado: piloto exploratorio, sin hallazgo 2/3 ni calibración empírica.** Rama de trabajo: `research/ab-r-mercados-pareja-20261028`. Corte: 28/10/2026.

## Pregunta
¿Puede aparecer similitud en valor relacional de los integrantes de una pareja a partir de búsqueda individual de la mejor opción alcanzable, aceptación bilateral y salida del mercado, aunque nadie prefiera directamente la semejanza? ¿En qué condiciones la búsqueda, el estatus dinámico, la población elegible y la fragmentación modifican esa estructura?

**Valor**: deseabilidad según el sexo opuesto. En el piloto las mujeres ponderan estatus 0,6 y belleza 0,4; los hombres, estatus 0,4 y belleza 0,6. Son **supuestos**; los agentes son binarios y heterosexuales en este prototipo, nunca una descripción exhaustiva de España. `Status` y `looks` sintéticos están en [0,1]; no se emplean datos personales reales.

## Orientación metodológica
- [Contrato previo, 10 ciclos](research/ABR_MATE10_20261028/PREREG.json): `3fce00eb`, antes del código/resultados.
- [Código congelado antes de ejecutar](research/ABR_MATE10_20261028/experiment.py.gz.b64): commit `a5ca4215`; SHA-256 del **Python descomprimido** `ca792b6c685beb075153659b862475425ed9a4ead74ad4e36e65729ceef6df7e`.
- [Resultados por condición](research/ABR_MATE10_20261028/SUMMARY.csv), [ledger A–J](research/ABR_MATE10_20261028/LEDGER.json), [informe](research/ABR_MATE10_20261028/REPORT.md), [estado](CURRENT.md).
- Contrato AB 3.2.1 R1–R5, O2 freeze-run y O4 niveles 0–3. Cuatro ciclos `PLANNING_AB_ONLY` basados en fuentes; seis `EXPERIMENTAL_AB` sintéticos; **no se intercambian**.
- Es imprescindible contrastar contra la literatura, especialmente Hitsch et al. (2010), que ya documenta sorting derivado de preferencias. Originalidad aún **NO_ACREDITADA**.

## Reproducir
El archivo congelado es gzip + base64 debido a la interfaz de conservación remota. Descifrarlo y ejecutar desde el directorio de la campaña:
```bash
base64 -d experiment.py.gz.b64 | gzip -dc > experiment.py
sha256sum experiment.py  # esperado: ca792b6c685beb075153659b862475425ed9a4ead74ad4e36e65729ceef6df7e
python -m pip install numpy pandas scipy
python experiment.py
```
Produce `RUNS.csv`, `SUMMARY.csv` y `NULLS.csv`. `CLEAN_CLONE_NOT_VERIFIED`; la ejecución comprobada se realizó en un contenedor local, no en un clon limpio. El script implementa swipes **simultáneos**, no Tinder asincrónico; los candidatos pueden reaparecer entre rondas. La regla de pérdida de estatus `delta` se aplica solo después de rechazo unilateral y es globalmente visible a todos los candidatos.

## Mapa de preguntas
```mermaid
flowchart TD
    R["Homogamia de valor emergente"]
    R --> M["Mecanismo y rivales"]
    R --> D["Datos y validez española"]
    R --> E["Contrastes internos"]
    M --> C01["C01: Estado del arte"]
    D --> C02["C02: Elegibilidad"]
    D --> C03["C03: Medida de estatus"]
    D --> C04["C04: Validez externa"]
    E --> C05["C05: Feedback"]
    E --> C06["C06: Preferencias"]
    E --> C07["C07: Pools locales"]
    E --> C08["C08: Pérdida real estatus"]
    E --> C09["C09: Gusto idiosincrático"]
    E --> C10["C10: Sexo y nulos"]
```
Las relaciones son de agenda/investigación, **no** de causalidad demostrada.

## Límites éticos y epistémicos
Las ponderaciones de género son convenciones experimentales sin validación normativa ni empírica. «Belleza» no se aplica a seres humanos reales. Las simulaciones sintéticas no identifican efectos sociales causales ni justifican puntuación individual de personas. Antes de probar sectores españoles, definir usuarios elegibles, consentimiento, cohortes y variables con fuente, sesgos y restricciones.

## Segunda campaña · BRANCH8 (28/10/2026)

**Autorización expresamente concedida, ocho ciclos completos A–J en sus alcances**, de los cuales cinco fueron experimentos sintéticos exploratorios y tres ciclos documentales/de planificación. Informe [BRANCH8](research/ABR_BRANCH8_20261028/REPORT.md), [ledger](research/ABR_BRANCH8_20261028/LEDGER.json), [contrato previo](research/ABR_BRANCH8_20261028/PREREG.json), [métricas por semilla](research/ABR_BRANCH8_20261028/RUNS_COMPACT.csv), [gráficas CT2](research/ABR_BRANCH8_20261028/CT2_TRAJECTORY.svg). Las dos implementaciones observadas se diferencian por hashes y no se cuentan como campañas adicionales. El resultado N03 sobre tamaño local fue inconcluso por baja cobertura; N08 no ejecutó una confirmación humana. Ningún nuevo hallazgo 2/3.

**Prioridad actual**: baseline Gale-Shapley con paridad, similitud de oportunidades de exposición, calibración sociodemográfica por población elegible y observación reputacional bajo condiciones éticas. [Estado vigente](CURRENT.md). [Próximos 6 ciclos propuestos, sin autorización](NEXT_6_PROPOSAL.md). El visor HTML es una vista estática del mapa piloto, no un replay canónico certificado; consultar `ab_atlas/seed.json` para el grafo más reciente.

## Tercera campaña autorizada · EVIDENCE6

[Prerregistro](research/ABR_EVIDENCE6_20261028/PREREG.json), [informe N15–N20](research/ABR_EVIDENCE6_20261028/REPORT.md), [ledger A–J](research/ABR_EVIDENCE6_20261028/LEDGER.json), [fuente Python congelada](research/ABR_EVIDENCE6_20261028/experiment.py) y [CSV por semilla](research/ABR_EVIDENCE6_20261028/RUNS.csv). Se cerraron **6 ciclos** con alcance limitado (2 pruebas sintéticas, 3 documentales y 1 planificación), sin 2/3 y sin calibración humana externa. La equivalencia exacta de sincrónico/asíncrono con q fijo es un control negativo construido, no un descubrimiento sociológico. Se conserva la no-derivación de población soltera desde censos y el bloqueo de acceso a las tablas 59583 y 60268. [Estado canónico](CURRENT.md), CT2 [escala 0–100 y ampliada](research/ABR_EVIDENCE6_20261028/CT2_TRAJECTORY.svg). R5 detiene nuevos ciclos sintéticos hasta evidencia externa pertinente.

## Quinta campaña · EVIDENCE20: siete ciclos ejecutados, trece no iniciados por R5

El investigador autorizó **hasta 20 ciclos BRANCHING AB-R**. Se realizaron **siete ciclos A–J** N21–N27 (dos revisiones documentales de fuentes y una adicional sobre rechazo, una prueba formal, un experimento sintético, un reanálisis y una planificación), sin invalidaciones registradas. Los trece restantes **no fueron ejecutados ni consumidos**, en aplicación de R5; la autorización no equivale a resultados. [Estado](CURRENT.md), [informe](research/ABR_EVIDENCE20_20261028/REPORT.md), [ledger](research/ABR_EVIDENCE20_20261028/LEDGER.json), [prerregistro](research/ABR_EVIDENCE20_20261028/PREREG.json), [código Python](research/ABR_EVIDENCE20_20261028/audit.py), [CSV sintético 5 semillas](research/ABR_EVIDENCE20_20261028/SEGMENT_NULLS.csv), [CT2 doble escala](research/ABR_EVIDENCE20_20261028/CT2_TRAJECTORY.svg).

Hallazgos de corrección: (1) rankings comunes implican matching estable rank-rank bajo condiciones especiales y no requieren homofilia; (2) la mera segmentación puede generar r≈.92 global incluso si el apareamiento intragrupo es aleatorio, por lo que los nulos deben preservar el grafo de oportunidad; (3) Funcas publica datos ESS 2024 de educación de convivientes españoles, **no swipes ni valor romántico**; (4) la ficha pública del experimento de citas de Essex 2018 declara un Excel anonimizado pero la descarga y columnas permanecen sin verificar. Ningún descubrimiento 2/3 ni validación causal real.

## Sexta fase · REALDATA13, primera evidencia diádica observada (28/10/2026)

Se reanudaron las **13 plazas restantes ya autorizadas de EVIDENCE20**, sin ampliar el cupo total de 20. Se cerraron diez ciclos N28–N37 de alcance limitado, con un intento instrumental inválido sobre ingresos reparado y **3 plazas sin iniciar bajo R5**. [Informe](research/ABR_REALDATA13_20261028/REPORT.md), [ledger A–J](research/ABR_REALDATA13_20261028/LEDGER.json), [prereg](research/ABR_REALDATA13_20261028/PREREG.json), [código de análisis](research/ABR_REALDATA13_20261028/analyze_mixmosa.js), [resultados empíricos agregados](research/ABR_REALDATA13_20261028/AGGREGATE_RESULTS_REPAIRED.json), [nulidad de popularidad](research/ABR_REALDATA13_20261028/N33_N35_EXTRA_RESULTS.json), [fuentes alternativas y acceso](research/ABR_REALDATA13_20261028/SECOND_SOURCE_AUDIT.md), [CT2 completo/ampliado](research/ABR_REALDATA13_20261028/CT2_TRAJECTORY.svg).

La fuente pública [Mixmosa](https://github.com/dankras/mixmosa-anonymized-data) permitió analizar realmente 1.895 citas rápidas presenciales completas en 30 eventos, 410 personas y 259 aceptaciones recíprocas. En la submuestra de decisiones mutuas, una popularidad leave-one-focal-date-out produjo r≈−0,016, compatible con control de permutación condicionado al evento. La fuerza de la asociación positiva con atractivo evaluado independientemente fue mayor que con categorías de ingreso autodeclarado, sin ajuste causal. **No** se valida una diagonal de homogamia como en los agentes sintéticos, ni una caída automática de estatus ante terceros por un rechazo. No se rehostean personas identificadas por pseudónimos ni datos brutos del repositorio de origen. La segunda muestra independiente quedó bloqueada. [Estado canónico](CURRENT.md), `CLEAN_CLONE_NOT_VERIFIED`, CT2=17/100 ordinal. Esta fase no constituye un experimento de usuarios españoles de Tinder.

## Puerta N38 · Réplica externa, sin datos procesados todavía

Nueva auditoría [N38](research/ABR_REPLICATION_GATE_20261028/GATE_REPORT.md), [ledger A–J](research/ABR_REPLICATION_GATE_20261028/LEDGER.json) y [matriz de fuentes](research/ABR_REPLICATION_GATE_20261028/SOURCE_ACCESS_AUDIT.json). Tras la continuación autorizada: **EVIDENCE20 = 18/20 válidos**, un intento instrumental inválido reparado, **2 autorizados sin iniciar (N39–N40)**. R5 detenido por ausencia de una segunda muestra con ambas decisiones de pareja accesibles y verificadas. Essex XLSX/eHarmony gzip sin bytes; original Columbia CVS sin contenido legible desde conector; derivado de Columbia 8.378 filas pero sin contraparte/evento/reciprocidad; Parquet limpio Columbia accesible como Base64 pero no procesado. **No se afirma réplica independiente**. Consulte [CURRENT.md](CURRENT.md).

## N39–N40 · Segunda muestra empírica finalmente procesada (Columbia)

El usuario aportó directamente `speed_dating_clean.parquet`, resolviendo la falta de acceso a binarios y evitando Codex/Work. La auditoría [Columbia + Mixmosa](research/ABR_COLUMBIA_N39_N40_20261028/REPORT.md) procesó 8.368 registros dirigidos, 121 columnas y **4.184 encuentros únicos** con decisiones de ambas personas verificadas, 21 sesiones, 551 participantes, 690 encuentros con aceptación mutua. Popularidad estimada sin la cita focal entre 690 mutuas: **r=+0,1244**, nulo por permutación del match dentro de sesión media `−0,03865` (cuantiles 95% [−0,1022,+0,0283]); Mixmosa anterior (259 mutuas) `r=−0,0159`, sin evidencia de diagonal fuerte. [Ledger N39/N40](research/ABR_COLUMBIA_N39_N40_20261028/LEDGER.json), [agregados](research/ABR_COLUMBIA_N39_N40_20261028/AGGREGATES.json), [prerregistro](research/ABR_COLUMBIA_N39_N40_20261028/PREREG.json), [freeze hash](research/ABR_COLUMBIA_N39_N40_20261028/SOURCE_FREEZE.json). Fuente original usuario preservada fuera del repo, código completo entregado como ZIP de conversación, clonado limpio no verificado.

**EVIDENCE20 20/20 ciclos AB válidos; ninguna plaza restante; R5 STOP.** Los hallazgos son observacionales descriptivos, no confirman ausencia de homofilia, ni efecto causal de rechazo sobre estatus real, ni generalización a España. CT2=17/100 ordinal. [CURRENT.md](CURRENT.md) es el estado canónico.

## N41–N46 · Popularidad y homofilia en dos muestras observadas (28/10/2026)

**Seis ciclos BRANCHING AB-R nuevos autorizados y ejecutados, saldo 0.** [Informe N41–N46](research/ABR_BRANCH6_SOCIAL_20261028/REPORT.md), [ledger A–J](research/ABR_BRANCH6_SOCIAL_20261028/LEDGER.json), [PREREG](research/ABR_BRANCH6_SOCIAL_20261028/PREREG.json), [resultados Columbia](research/ABR_BRANCH6_SOCIAL_20261028/COLUMBIA_SUMMARY.json), [resultados Mixmosa](research/ABR_BRANCH6_SOCIAL_20261028/MIXMOSA_N46_RESULTS.json), [CT2 escala completa y zoom](research/ABR_BRANCH6_SOCIAL_20261028/CT2.svg) y [ledger 1/3 local](research/FINDINGS_1_3/LEDGER.json).

En Columbia, modelos por actor demuestran que popularidad observada en otros encuentros se asocia mucho más al sí que aproximaciones sencillas de semejanza por edad o campo académico; sin embargo, se observa una contribución modesta de similitud de disciplina y, en hombres, edad. **El control por actor y evento** muestra un exceso de cercanía de edad de −0,156 años entre mujeres y −0,202 entre hombres, mientras Mixmosa da −0,210 y +0,117 respectivamente. **La diferencia masculina de signo entre mercados** recibe un único reconocimiento local **1/3 exploratorio**, no 2/3 científico ni resultado causal. Los datos son citas presenciales de diferentes épocas y países, no Tinder español. CT2 sigue **17/100**, ordinal, con `CLEAN_CLONE_NOT_VERIFIED`. [Estado canónico](CURRENT.md).

## N47–N55 · Efectos fijos de ambos extremos y nulo que conserva grados (28/10/2026)

El usuario autorizó 20 ciclos BRANCHING AB-R adicionales. Se ejecutaron **nueve ciclos A–J reales**, con un ciclo de planificación y uno documental, **cero intentos inválidos**, **11 autorizados no iniciados por R5**. [Informe](research/ABR_TWO_WAY20_20261028/REPORT.md), [ledger](research/ABR_TWO_WAY20_20261028/LEDGER.json), [prerregistro](research/ABR_TWO_WAY20_20261028/PREREG.json), [agregados](research/ABR_TWO_WAY20_20261028/AGGREGATES.json), [código JS Mixmosa](research/ABR_TWO_WAY20_20261028/mixmosa_twoway.js), [gráfica CT2](research/ABR_TWO_WAY20_20261028/CT2.svg), [prior art](research/ABR_TWO_WAY20_20261028/PRIOR_ART.md).

En Columbia, la distancia de edad y la coincidencia de campo académico son señales pequeñas tras controlar actor y candidato. La popularidad propia del candidato se absorbe en su efecto fijo y no permite un coeficiente independiente; la edad firmada se vuelve colineal. Una permutación tipo MCMC que conserva oportunidades y tasas de aceptación **de ambos lados** respalda descriptivamente una señal de campo compartido, pero no prueba mezcla ni causalidad. En Mixmosa, el coeficiente masculino de distancia de edad con dos FE resulta aproximadamente cero; por ello el antiguo 1/3 N46 de signo opuesto entre mercados se conserva **solo como resultado descriptivo de aquella especificación**, con alcance general debilitado. **N1 nuevos=0, N2=N3=0; CT2 17→13 ordinal**, y la teoría original no se valida para apps o España. [Estado canónico](CURRENT.md).

## Fuente y priors obligatorios para todos los descubrimientos documentales

La norma está incorporada a [AGENTS.md](../../AGENTS.md): **cada hallazgo documental debe guardar una referencia original, el dato exacto que aporta y sus límites; también debe actualizar un prior o justificar NO_CHANGE_WITH_REASON**. El registro común del proyecto está en [research/PRIORS/README.md](research/PRIORS/README.md), con [29 fuentes y qué aporta cada una](research/PRIORS/SOURCES.json), [14 priors cualitativos vigentes](research/PRIORS/PRIORS.json), [25 eventos de revisión históricos/versionados](research/PRIORS/UPDATES.json) y [plantilla](research/PRIORS/SOURCE_TEMPLATE.json). Los hallazgos antiguos se incorporaron como backfill **retrospectivo**, no como preregistro; ningún asiento de gobernanza consume ciclo científico AB.

**N56 y N57**: [informe y auditoría](research/ABR_THIRD_SOURCE_20261028/REPORT.md) / [fuentes](research/ABR_THIRD_SOURCE_20261028/SOURCE_AND_NOVELTY_AUDIT.md) / [ledger A–J](research/ABR_THIRD_SOURCE_20261028/LEDGER.json) / [CT2](research/ABR_THIRD_SOURCE_20261028/CT2.svg). [Topinkova y Diviak 2025](https://doi.org/10.1371/journal.pone.0327477) ya publicaron una versión empírica muy cercana de la homogamia por reciprocidad tras intentos aspiracionales en una aplicación, limitando la originalidad de nuestra proposición general. El fichero OSF anunciado **no se descargó**, falta exposición de perfiles y popularidad prospectiva; no reclamar replicación de sus datos ni pérdida causal de estatus ante terceros. **Última autorización 20: 11 ciclos A–J ejecutados (incluidos 2 documentales N56/N57), 9 sin iniciar por R5, CT2 7/100 ordinal**, N2=N3=0. [Estado canónico](CURRENT.md).

## N58–N66 · ESBM, marco socioecológico y simulador sintético reproducible

La autorización vigente de 20 ciclos AB-R terminó **20/20 completos** tras ejecutar N58–N66 (9 ciclos, cero inválidos), con **60 corridas sintéticas preregistradas + 6 corridas post hoc ilustrativas**, NO datos humanos nuevos. [Informe integrado](research/ABR_INTEGRAL9_20261028/REPORT.md), [modelo de 12 dimensiones](research/ABR_INTEGRAL9_20261028/THEORY_AND_DIMENSIONS.md), [ledger A–J](research/ABR_INTEGRAL9_20261028/LEDGER.json), [prereg](research/ABR_INTEGRAL9_20261028/PREREG.json), [resultados agregados](research/ABR_INTEGRAL9_20261028/RESULTS_COMPACT.json), [anexo de equivalencia post hoc](research/ABR_INTEGRAL9_20261028/EQUIVALENCE_COMPACT.json), [código principal íntegro comprimido](research/ABR_INTEGRAL9_20261028/simulator.py.gz.b64), [script anexo comprimido](research/ABR_INTEGRAL9_20261028/observational_equivalence.py.gz.b64) y [manual para ejecutarlos](research/ABR_INTEGRAL9_20261028/README_REPRO.md).

**Hallazgo demostrativo, NO novedoso ni causal:** alrededor de 50% de parejas del mismo grupo surge con preferencias explícitas por compartir grupo ante 25% de exposiciones same-group, o con preferencias sin homofilia ante 50% exposiciones same-group (configuración ajustada *post hoc* para ilustrar la no-identificación). La cobertura difiere 91% vs 81,5%. El modelo principal de calidad consensuada por sí solo **no** produjo fuerte homogamia Q, y los umbrales endógenos solo generaron rQ~+.084 en media. Política de recomendación sesgada hacia candidatos populares Gini visibilidad~.435 y menor cobertura dentro del toy. El modelo **no incorpora** pareja duradera, preferencias no binarias, señales reputacionales públicas ni datos de plataformas españolas; representar 12 dimensiones en el marco conceptual no equivale a simulaciones ejecutadas de las 12.

La última revisión documental añadió 12 fuentes/11 actualizaciones: el [registro versionado](research/PRIORS/README.md) suma ahora **41 fuentes**, **21 priors** y **36 eventos**. **N1 nuevos=0, N2=N3=0, CT2=7/100 ordinal**, R5 STOP y **cero plazas autorizadas pendientes**. El objetivo de explicar el fenómeno mejor que la literatura es una hipótesis competitiva futura, no una conclusión. [Estado canónico](CURRENT.md).

## ESBM v2 · N67–N75 · Compatibilidad mutua, tiempo y duración (28/10/2026)

**Última autorización:** 20 ciclos AB-R adicionales; **9/20 A–J válidos ejecutados** (N67–N75), cero inválidos; **11 autorizados no iniciados por R5**. [Estado canónico](CURRENT.md), [informe científico](research/ABR_ESBM20_20261028/REPORT.md), [ledger A–J](research/ABR_ESBM20_20261028/LEDGER.json), [teoría v2](research/ABR_ESBM20_20261028/THEORY_V2.md), [código Python íntegro](research/ABR_ESBM20_20261028/esbm_dynamic.py), [60 trayectorias por semilla](research/ABR_ESBM20_20261028/RUNS.json.gz.b64), [resumen de escenarios](research/ABR_ESBM20_20261028/SUMMARY.json), [comparaciones pareadas](research/ABR_ESBM20_20261028/PAIRED_CONTRASTS.json), [QA](research/ABR_ESBM20_20261028/QA.json), [reproducción](research/ABR_ESBM20_20261028/README_REPRO.md) y [CT2](research/ABR_ESBM20_20261028/CT2.svg).

Se ejecutaron **60 corridas sintéticas (10 escenarios × 6 seeds)** con 144 agentes artificiales, redes de compatibilidad consentida entre F/M/X sintéticos, propuestas/respuestas bilaterales, formación, rupturas, instituciones, ranking de popularidad y aprendizaje privado/reputación artificialmente pública. **No son proporciones de identidades ni elecciones humanas reales.** El escenario con equilibrio de impresiones reduce Gini de visibilidad de ~0,316 a ~0,216, pero simultáneamente aumenta relaciones nuevas y reduce proporción en pareja al final; no equivale a efecto probado de una app. El rechazo público del simulador tiene por definición un efecto negativo, **no hay evidencia de difusión real de esa información**. Duración más corta produce mayor rotación de parejas formadas pero menos parejas vigentes al final.

Se auditaron seis referencias y fichas externas de 2024–2026, sin descargar nuevos microdatos, con [auditoría de disponibilidad/licencias](research/ABR_ESBM20_20261028/EXTERNAL_VALIDATION_AUDIT.md). Registro de priors: **47 fuentes**, **24 hipótesis**, **44 eventos**; sin probabilidades bayesianas inventadas. CT2 sigue **7/100 ordinal**, niveles N1 nuevos=0 y N2=N3=0. El objetivo de explicación científicamente superior sigue sin validarse: **R5 STOP** hasta datos o hipótesis prospectivas discriminantes.

## N76–N77 · Auditoría externa AEA/OpenICPSR y panel Stanford HCMST (28/10/2026)

La nueva autorización de 20 AB-R en ESBM v2 tiene **11/20 ciclos completos** (N67–N77), incluyendo **dos auditorías documentales N76/N77** con A–J; **9 plazas no iniciadas bajo R5**. Se comprobó el [paquete AEA E218862V1](https://www.openicpsr.org/openicpsr/project/218862/version/V1/view) y su inventario de carpetas, pero **ningún fichero individual o LICENSE se descargó**, por lo que no se ejecutó la réplica. Se localizó [Stanford HCMST 2017–2022](https://data.stanford.edu/hcmst2017) y su [catálogo ICPSR 38873](https://doi.org/10.3886/ICPSR38873.v1): **una sola cohorte longitudinal** de 3510/2107/1722 participantes entre las tres olas, útil para investigar duración y ruptura de relaciones bajo pesos/atrición, pero no exposiciones de perfiles ni rechazos recíprocos. No hay microdatos abiertos/analizados en esta ejecución; restricciones y obligaciones de uso por depósito deben comprobarse antes de procesarlos.

[Auditoría de acceso/licencias](research/ABR_EXTERNAL_GATE_20261028/ACCESS_AND_SCOPE_AUDIT.md), [informe](research/ABR_EXTERNAL_GATE_20261028/REPORT.md), [ledger](research/ABR_EXTERNAL_GATE_20261028/LEDGER.json), [prerregistro del acceso](research/ABR_EXTERNAL_GATE_20261028/SOURCE_GATE_PREREG.json), [CT2](research/ABR_EXTERNAL_GATE_20261028/CT2.svg). Registros versionados ahora **50 fuentes, 25 priors, 52 actualizaciones**; CT2 sin cambio en **7/100** ordinal, nuevos niveles 1/3, 2/3 y 3/3 = cero. [Estado canónico](CURRENT.md).
