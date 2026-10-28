# AB-R EVIDENCE20 · Cierre parcial por R5 (N21–N27)

**Programa:** Mercados de pareja, Alejandro Panera Pascual. **Fecha:** 28 de octubre de 2026. **Rama:** `research/ab-r-mercados-pareja-20261028`, sin fusionar a `main`. **Autorización:** 20 ciclos BRANCHING AB-R adicionales. **Ejecución efectiva:** 7 ciclos A–J válidos de alcance limitado (N21–N27), 0 inválidos, **13 plazas autorizadas no iniciadas**, detenido por R5. No se ha producido experimento con humanos. Ningún hallazgo 2/3 o 3/3 acreditado.

| Identificador | Tipo real | Estado |
|---|---|---|
| N21 | DOCUMENTARY_AB · datos independientes publicados | Cerrado, sin microdatos |
| N22 | DOCUMENTARY_AB · acceso a registros de interacción | Cerrado, DATA_ACCESS_BLOCKED |
| N23 | FORMAL_AB · prueba de teorema y enumeración | Cerrado, identidad matemática conocida |
| N24 | EXPERIMENTAL_AB · control sintético por sectores | Cerrado, resultado modelo-dependiente |
| N25 | REANALYSIS_AB · condicionamiento por match | Cerrado, mismos datos anteriores |
| N26 | DOCUMENTARY_AB · reputación y rechazo | Cerrado, efecto social no identificado |
| N27 | PLANNING_AB_ONLY · puerta confirmatoria/R5 | Cerrado, prueba humana NO EJECUTADA |
| N28–N40 | Sin contrato ni ejecución | **NO INICIADOS**, 13 plazas de saldo bajo stop R5 |

## Procedencia / freeze–run
[Contrato antes de la ejecución](PREREG.json), commit `8949077025a8d585fecdc3cec09ec13710cd5a72`. Fuente Python [audit.py](audit.py), SHA-256 `30417b2a58368f2e3df952d567923d5fb8c435c1d3b15e89d82ec62f053a6f45`, hash congelado en [SOURCE_FREEZE.json](SOURCE_FREEZE.json), commit `f7e8e2d6328ffda72745e1018625bf6464ae2dcc` antes de la primera corrida. Fuente íntegra archivada en commit `5d8a3291fa73eff1a3a20468a38aa85cef575bbb`; longitud exacta 3.138 bytes y FNV-32 local/remoto 1355783298. Entorno: Python 3.13.5, NumPy 2.3.5. [Resultados verificables](SEGMENT_NULLS.csv), [enumeración](EXACT_ENUMERATION.csv), [QA](QA_RESULTS.json), [ledger A–J](LEDGER.json). Segunda corrida local produjo los mismos resultados y checksums CSV, pero **CLEAN_CLONE_NOT_VERIFIED**, sin revisión externa del código. Las fuentes sociales y sus límites están en [SOURCES_AND_LIMITS.md](SOURCES_AND_LIMITS.md).

## N21 · Por primera vez, una ancla descriptiva española contemporánea
Se consultó [Funcas, *Focus on Spanish Society*, diciembre de 2025](https://www.funcas.es/wp-content/uploads/2025/12/2512-Focus_final.pdf), y se examinó la figura 3 de la página impresa 7. Los indicadores parten de ESS 2024 ronda 11 con ponderación `pspwght`, entre convivientes de 25–50 años en los países participantes. En España, **76 % de los hombres universitarios convivientes** convive con pareja universitaria frente a **53 % de las mujeres universitarias convivientes** (media femenina europea 64 %). Entre hombres sin universidad conviviendo, 30 % tiene pareja universitaria; entre mujeres sin universidad conviviendo, 12 %. Separadamente, la convivencia a los 25–29 años se sitúa en España 27 % frente a UE 42 %, y a los 30–35 en 58 % frente a 64 %.

**Son fracciones condicionadas a la educación y sexo de cada encuestado que ya convive**; no indican tasas de pareja de toda la población, la intención de encontrar pareja ni conducta de swipe. Tampoco identifican homofilia frente a oportunidad social sin controlar distribución educativa y selección para convivencia. No hay microdatos ESS extraídos en esta campaña ni incertidumbre muestral estimada. **Impacto metodológico:** un parámetro sexual fijo de preferencias 60/40 sin medición no puede explicar por sí mismo la asimetría observada; debe considerarse composición del mercado y diferencias por cohorte.

## N22 · Acceso a fuentes de interacción, no todavía datos analizables
[Josué Ortega, 2018, Universidad de Essex](https://researchdata.essex.ac.uk/85/) declara un experimento de campo prerregistrado en 2018, con archivo público anonimizado `AnonymizedData.xlsx` (67 kB, CC BY 4.0). Se verificó el registro, el país (Reino Unido), periodo, licencia y aprobación ética. **No se pudieron obtener sus bytes desde las herramientas de navegación ni de descarga de este turno**; sus columnas y suficiencia para recuperar quién evaluó a quién permanecen NO VERIFICADAS. [SwipeStats](https://www.swipestats.io/research) anuncia exportaciones voluntarias y resúmenes diarios; solo se leyó ficha y muestra de presentación, sin descarga ni validación de representatividad. Recuentos por perfil sin identificador de pareja no identifican el valor de ambos miembros de una díada. [Hitsch et al. 2010](https://doi.org/10.1257/aer.100.1.130) ya proporciona un antecedente de preferencias/matching estable. [Ershov et al. 2026](https://www.nber.org/papers/w34757) encuentra relaciones entre uso de plataformas y assortative matching que dependen de época tecnológica y atributo, en mercados estadounidenses, no trasladable automáticamente a España.

## N23 · Teorema de homogamia bajo consenso pleno de preferencias
Supuestos explícitos: n hombres y n mujeres, grafo bipartito completo, todas las mujeres prefieren al hombre de valor más alto y todos los hombres prefieren a la mujer de valor más alto, con ordenamientos estrictos coincidentes y sin opción exterior (todos los pares aceptables).

**Proposición:** el único matching estable empareja la persona de rango k de hombres con la de rango k de mujeres, para todo k. **Demostración por inducción:** si hombre 1 y mujer 1 no están juntos, ambos prefieren unirse mutuamente a sus parejas actuales, constituyendo un par bloqueante. Deben estar juntos. Retirados, el submercado restante conserva los mismos ordenamientos relativos; se repite el argumento para rango 2 y sucesivos. El algoritmo no necesita que los agentes prefieran explícitamente parejas *semejantes*; basta la coincidencia de rankings ajenos. El resultado no generaliza a rankings individuales, outside options, red incompleta ni perturbaciones del algoritmo.

Se verificaron exhaustivamente las `n!` asignaciones para n=2,…,6 (2,6,24,120,720) y se encontró una única asignación estable por tamaño, la identidad de rangos; véase [CSV](EXACT_ENUMERATION.csv). La enumeración es control del código, no la prueba general. **Este resultado tiene antecedentes en teoría clásica de matching y no se declara novedad 2/3**. Debilita cualquier pretensión de que alta r en ese caso sea «sorpresa emergente».

## N24 · Falsación del control aleatorio global como baseline suficiente
Cinco corridas sintéticas de 24.000 parejas cada una; cuatro sectores de 6.000 con valor medio `[.15,.35,.65,.85]`, error Gaussiano independiente sigma=.08 y asignación **completamente aleatoria dentro de cada sector**. No hay preferencia individual ni búsqueda. Se comparó correlación global, promedio de las correlaciones intragrupo, permutación de parejas dentro del mismo sector y permutación global:

| Medida (media cinco semillas) | Pearson r |
|---|---:|
| Parejas aleatorias dentro de sectores, agregado | **0,920017** |
| Correlación media dentro de cada sector | **−0,001363** |
| Parejas remezcladas dentro de cada sector | **0,920117** |
| Parejas remezcladas globalmente | **0,004727** |

La identidad que explica el resultado es `Cov(X,Y)=E[Cov(X,Y|G)]+Cov(E[X|G],E[Y|G])`. En estas corridas el componente entre grupos fue prácticamente el 100 % de la covarianza, mientras el término interno fue aproximadamente cero; se verificó la identidad a tolerancia 1e-12. **No implica que nuestros anteriores agentes estuvieran sometidos exactamente a esta segmentación**; demuestra que su nulo por permutación global es insuficiente para descartar sorting por composición de sectores, redes o geografía. El control competente debe preservar la estructura de exposición/grupo.

## N25 · El emparejamiento no es sólo r entre personas elegidas
Reanálisis del archivo [RUNS.csv de EVIDENCE6](../ABR_EVIDENCE6_20261028/RUNS.csv) (cinco semillas N17, sin nueva corrida). DA: `r=.9085`, cobertura `96,17%`, utilidad media **entre emparejados** `0,5406`; greedy `r=.0172`, cobertura `97,00%`, utilidad `0,5030`; q adaptativo `r=.4121`, cobertura `41,33%`, utilidad **entre emparejados** `0,7006`. La media de los emparejados del modelo adaptativo es mayor porque excluye un porcentaje muy elevado; sin función explícita de utilidad de soltería y bienestar agregado, no se debe calificar como «mejor» ese resultado. Documento [N25_REANALYSIS.json](N25_REANALYSIS.json). No es confirmación independiente: utiliza exactamente el mismo conjunto de datos que N17.

## N26 · Status objetivo, autoestima y reputación son conceptos distintos
Las fuentes [Campaioli et al. (2025/2026)](https://doi.org/10.1177/14614448251336437) y [*Swipe, Chat, Unmatch* (2026)](https://doi.org/10.1080/15213269.2026.2633228) analizan señales digitales, vigilancia y daños psicológicos del rechazo. No acreditan que cada swipe negativo, frecuentemente privado, reduzca **automáticamente** el prestigio que terceros atribuyen al rechazado. Para probarlo haría falta exponer y medir información reputacional de forma válida y ética; no utilizar evaluaciones identificables de personas sin consentimiento. La regla `S_i(t+1)=S_i(t)-δ` continúa siendo un mecanismo contrafactual simulado, no empírico. En el reporte se separan `S_material`, `R_private` y `R_public`.

## N27 · Decisión R5 y frontera de la investigación
Las cifras externas de Funcas son una ancla empírica descriptiva útil, pero no un dataset diádico de decisiones. No se ha recuperado el Excel de Essex ni las matrices completas INE 59583/60268 ni microdatos ESS con identificador de pareja y acceso autorizado. No hay un contraste con información real de swipes mutuos que pueda diferenciar los mecanismos. Por tanto **R5 decide detener a los siete ciclos**, sin convertir los trece restantes del cupo autorizado en ciclos ficticios. Posibles nuevos pasos: (i) obtener archivo Essex en Work/portal de la universidad; verificar esquema y derechos, (ii) microdatos ESS o INE con acceso y definición de parejas, (iii) estudio ético de exposición de terceros a señales reputacionales, (iv) comparar modelos con grafos de exposición observados, y (v) preregistrar resultado nulo y competidor competente. No abrir campañas sintéticas nuevas por mera disponibilidad de presupuesto.

## Auditoría de CT2, prior-art y niveles
CT2 de esta rama: `20` (MATE10, *post hoc*), `17` (BRANCH8), `17` (BRANCH6), `17` (EVIDENCE6), `17` en N21–N27. Es una apreciación **ordinal 1–100, NO probabilidad**. Nueva evidencia externa descriptiva y controles fuertes muestran qué no se puede atribuir, pero no elevan la perspectiva de hallazgo 2/3. [Serie y gráfica doble escala](CT2_TRAJECTORY.svg) y [datos](CT2_TRAJECTORY.json). N1 nuevos=0; N2=N3=0; N1 histórico auditable=NOT_AUDITED. DRIFT D0.0.

**Estado GitHub:** esta rama contiene el prerregistro, fuente audit.py, CSV por semilla, QA, fuentes, ledger A–J y gráfico. Verificación GitHub de la fuente mediante longitud 3138 caracteres y FNV-32 1355783298 contra archivo local. La ejecución reproducible se repitió localmente con hashes idénticos, pero no hay `CLEAN_CLONE_VERIFIED` ni replicación externa de la hipótesis social.

**AB-DECIDE:** `STOP_CAMPAIGN_R5` tras 7/20. **Saldo autorizado no iniciado 13**, sin fecha ni ejecución automática. La próxima acción de mayor valor no es ampliar agents o semillas sino obtener un archivo real accesible de interacción entre usuarios y auditar su estructura ética y estadística. No se solicita ampliación de ciclos adicionales mientras queden 13 sin usar; la continuación quedará supeditada a una fuente realmente nueva.
