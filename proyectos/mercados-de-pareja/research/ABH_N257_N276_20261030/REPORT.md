# AB-H PIVOT N257–N276 · paridad individual instrumentada y robustez de matching

**Cierre 30/10/2026 — 20/20 ciclos reales ejecutados, 18 PASS técnicos y 2 negativos válidos.** Sin datos humanos nuevos, sin validación causal ni prueba de reproducibilidad plena histórica. Rama `research/ab-h-esbm-event-parity-n257-n276-20261030`; origen autorizado `28ee845cca88e16f13f25962e4b103335484d9a1`. Ningún merge experimental a main.

## Secuencia de integridad

El commit **`474cdae1cf04bf89912f7c6fa4f961bbe14c4483`** congeló **antes del primer outcome** los contratos A–J para N257–N276, hashes de motores, runner, binario Boost y el archivo de instrumentos. ZIP de fuentes preregistrado: `ESBM_N257_N276_INSTRUMENTS_PREOUTCOME.zip`, SHA256 `458d421fb86824ec1e1aaf0536dde58c03902cc73a10333862a63553c1d3a473`, custodiado en biblioteca `/Mercados-de-pareja/ABH-N257-N276`.

El ZIP completo del lote anterior N237–N256 **no fue recuperado**. Se dispone de la fuente original ESBM en GitHub, SHA256 `f7e6b84000720cbdf2ee0800c2b10d136185facd00e4622756cbb5f8d8254d0b`, pero las fuentes exactas de TypeScript y los fixtures de N242/N246 están ausentes en este entorno. Las pruebas presentes son **controles nuevos**: no afirmar que N257/N258 reejecutaron los bytes históricos de N242/N246.

El diseño de la comparación de trayectorias contiene una **reconstrucción instrumental de semántica original Python/NumPy** con matching NetworkX y un **segundo bucle de estado codificado separadamente en Python-listas** con matching Boost C++; ambos comparten el generador sintético de personas/shocks y los requisitos del ESBM. La reconstrucción **no es una copia byte-idéntica** del `esbm_dynamic.py` original y el antiguo motor TypeScript **no se ejecutó**. La independencia es limitada, no una reproducción multilenguaje completa de 2026-10-30.

## Resultados nuevos

**N257 (negativo válido).** En cuatro grafos sintéticos nuevos n143, dos familias de pesos continuos coincidieron en cardinalidad y suma exacta frente a NetworkX; un caso `flat` (3.015 aristas) excedió 4 s en Boost y un caso `near_tie` (3.117 aristas) terminó `SIGSEGV -11`.

**N258 (negativo válido).** En cuatro grafos sintéticos n144, los controles `flat` (10.096 aristas) y `near_tie` (9.716 aristas) excedieron cada uno 5 s. Dos grafos con pesos continuos sí obtuvieron objetivo exacto coincidente con NetworkX. Los límites de tiempo se predefinieron para estos controles.

**N259–N268 (10 PASS técnicos).** Se ejecutaron diez escenarios de ESBM, semillas `101,211,307,401,503,601`, N144/T16/K7: **60/60** comparaciones completas de **eventos dirigidos y parejas**, 960 ticks, 120 trazas JSON comprimidas contrastadas con SHA. Las dos implementaciones instrumentales concordaron en el orden de exposiciones, propuestas, decisiones de respuesta, candidatos aceptados, vínculos, disoluciones y estado por periodo. Los tiempos de cálculo se excluyeron del comparador. Estas comparaciones **no** sustituyen las ausentes trazas del TypeScript histórico ni demuestran unicidad de los óptimos.

Para dimensionar estrictamente las nuevas **trazas artificiales de referencia**, se contabilizaron 358.348 exposiciones, 103.103 propuestas, 103.103 respuestas, 27.507 respuestas positivas, 13.668 nuevas parejas y 10.028 disoluciones. Son sumas de **60 mundos simulados**, no prevalencias humanas ni generalizaciones sociológicas.

**N269 (PASS técnico):** ciclo de 4 vértices y dos emparejamientos óptimos distintos de igual objetivo; empate real aun cuando los dos motores escogieron las mismas aristas en esa realización. **N270 (PASS del control, contraejemplo sobre identidad):** en seis pruebas de relabeling se preservó el objetivo en 6/6 pero la identidad de aristas cambió en **4/6** casos de pesos empates/casi empates. Por tanto, paridad de objetivo **no implica** paridad de parejas bajo permutación de identidades.

**N271–N276 (seis PASS técnicos):** igualdad de objetivo y aristas ante seis inversiones de orden de aristas en grafos probados; cuatro contrastes de bucles de estado usando el mismo NetworkX para aislar el matching; cuatro auditorías de conservación de propuestas/respuestas y parejas; siete mutaciones adversariales detectadas correctamente en los eventos; tres controles de exclusión de canales de aprendizaje/feedback y tres repeticiones de trazas completas con hashes iguales. Ninguno elimina la existencia de empates o fallos de Boost en otros grafos.

## Diagnóstico ASan posterior preinscrito, sin nueva plaza

Después del resultado N257, se preregistró **antes de ejecutar el sanitizer** un diagnóstico específico en commit `2643d4fb03fd28ec81dc3152fe1ca95745d9ab47`. Sobre el nuevo fixture n143 `near_tie`, SHA256 `0cf31966ff1839a5cf9ca31255b8412eaf6bd5e66502657df90b3ba253b88ee2`, AddressSanitizer confirmó **desbordamiento de pila** con llamadas repetidas a `boost::weighted_augmenting_path_finder::retrieve_augmenting_path` (`maximum_weighted_matching.hpp` líneas 615/624). El stderr completo y el binario ASan están preservados en el ZIP de resultados. Esto diagnostica el nuevo control, **no identifica definitivamente la causa del viejo N242**, cuyo fixture falta. Etiqueta: `POST_HOC_FOCUSED_DIAGNOSTIC`, no ciclo AB adicional.

## Intentos inválidos preservados y reparación

Los primeros intentos N259–N263 produjeron `FileNotFoundError` al archivar `results/events/` (directorio ausente). Los **cinco recibos negativos instrumentales** permanecen en `failed_attempts/` con SHA individuales en el archivo completo; no se llamaron PASS ni se gastaron como plazas nuevas. El retest se **preregistró prospectivamente** en commit `89decd3b840bb654cd743ea80bf210c876293d39`: crear directorio, preservar los primeros recibos y correr de nuevo con código SHA inalterado. Los cinco retests alcanzaron 6/6 semillas cada uno.

## Evidencias, saldo y alcance

- [Prerregistro A–J/código](PREREG_AJ_SHA_FREEZE_20261030.json) · [prerregistro de reparación](REPAIR_PREREG_EVENTS_DIRECTORY_1.md) · [diagnóstico ASan preregistrado](ASAN_DIAGNOSTIC_PREREG_N25704.md).
- [Índice SHA de 20 resultados](RESULTS_INDEX_GITHUB.json) · [ledger A–J post-outcome de 20 ciclos](LEDGER_AJ_POSTOUTCOME_GITHUB.json).
- ZIP completo `ESBM_ABH_N257_N276_event_parity_results.zip`, **SHA256 `e0263af4ac85073b1ccbd8a32a4d9dc460b29f89147d765c20eaf2c90554bd5d`**, 4.722.609 bytes, 161 archivos, verificado byte a byte contra manifiesto. Disponible en biblioteca `/Mercados-de-pareja/ABH-N257-N276/`. Contiene 20 recibos, 120 trazas de eventos, código, los 5 fallos iniciales, diagnóstico ASan, ledger, gráfico CT2 y manifiesto. Los archivos brutos completos **no se presumen alojados en GitHub**.
- **Contabilidad:** 20 ejecuciones válidas, 18 PASS técnicos, 2 negativos válidos, 5 primeros intentos inválidos reparados; **0 plazas N257–N276 pendientes**. No contar la auditoría post hoc ni el ASan posterior como ciclos.
- **Ciencia:** sin evidencia humana independiente, sin nueva predicción empírica diferencial frente a B0/B1/B2/B4/B6, sin universalidad de desempates o portabilidad Windows, sin mejora de CT2. Mantener **CT2 científico 7/100**, **STOP_R5 humano**, madurez previa de referencia **44,10% no reestimada**, grado científico humano 0/3. ESBM original, SRC104, licencias, autores y main no afectados; no SSJY.

**AB-DECIDE: CERRAR N257–N276.** La prioridad siguiente es recuperar los instrumentos y fixtures exactos históricos, comprobar paridad de eventos del verdadero Python original frente al verdadero motor TS o sustituir el backend Boost en los grafos degenerados. No afirmar reproducibilidad histórica plena a partir de este contraste nuevo; tampoco abrir ciclos adicionales sin una autorización nueva.
