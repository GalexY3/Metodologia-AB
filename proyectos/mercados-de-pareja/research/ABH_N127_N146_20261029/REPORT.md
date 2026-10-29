# Informe de campaña AB-H N127–N146 · API explícita, redes, censura y control de identidad

**29/10/2026 · rama `research/ab-h-esbm-event-api-20261029` · aislada de `main` y de los PR #63/#66.** Cierro **20 ciclos A–J ejecutados**, de los cuales 19 terminaron en PASS y **N144 es un diagnóstico negativo técnicamente válido**, sin pretender que el control anterior aprobó la invariancia. 0 ciclos empíricos humanos nuevos, 0 grados científicos 1/3–3/3. Ningún ciclo de planificación ni saldo pendiente de los 20 autorizados. Los resultados comparten generador, atributos y supuestos; no son 20 descubrimientos independientes.

## Lógica operacional, precongelación y material

Leídos `AGENTS.md`, AB 3.2.1, O1–O7, `CURRENT.md` y [N107–N126](../ABH_N107_N126_20261029/REPORT.md). Se preserva **ESBM v2 histórico** byte a byte, SHA256 `f7e6b84000720cbdf2ee0800c2b10d136185facd00e4622756cbb5f8d8254d0b`. Nueva rama desde `7533f3db5e1128a54819d5dda4905e40c5ef8cca`. Se trabajó sobre originales ya disponibles en esta conversación y se contrastó el Git blob de cada fichero del código realmente ejecutado con el de GitHub.

| Bloque | Prerregistro A–J antes de outcomes | Congelación de fuente y runner antes de ejecutar |
|---|---|---|
| N127–N131 | [PREREG_A.json](PREREG_A.json) `c424e34fa0138abb89f88568ea711e8a49781b70` | [esbm_event_engine.py](esbm_event_engine.py) `ec7368b84510850523d1a43dd4db958a5aa323c6`, [run_A.py](run_A.py) `327807ba70a9e46fbae669d29026f2d079d41e8b`; [mini_world.py](mini_world.py) `d4cec03b5e9ac65e5226a80ee786972ab8c01099` |
| N132–N136 | [PREREG_B.json](PREREG_B.json) `0f91ba7df0f14720765f12009873397c35078619` | [social_graph.py](social_graph.py) `9af3a551854ee0793531d17b51f2e53977c49fc0` y [run_B.py](run_B.py) `91e5bcdd5c3c4a04361a533c9b877ebd75b3d8bc` |
| N137–N141 | [PREREG_C.json](PREREG_C.json) `e0ff2456fb2e7d63f6cb532e91108e4b3399da9c` | [run_C.py](run_C.py) `5f3a6f4d32588e6781a5ae9b80eee3c1b5fe0f63` |
| N142–N146 | [PREREG_D.json](PREREG_D.json) `8daed203673985e0fb3df9c0e2d9ab883a645abd` | engine input guard `ede5bb9a954c2bbce9ad26cc8fb59c8f5135174a`, [social_graph_equivariant.py](social_graph_equivariant.py) `4ca9d95fb1016789d13c478b6843f961939acb11` y [run_D.py](run_D.py) `0672050bbd62f16950c55206d985ae6cf31d85f2` |

[RESULTS_INDEX.json](RESULTS_INDEX.json) reúne endpoints de los 20 ciclos, SHA256 de cada resultado íntegro (A–D), freeze SHA y estado del control N144. [LEDGER_A.json](LEDGER_A.json), [LEDGER_B.json](LEDGER_B.json), [LEDGER_C.json](LEDGER_C.json) y [LEDGER_D.json](LEDGER_D.json) aportan contratos completos A–J, controles y sucesor condicionado. Los cuatro JSON completos por semilla y el JSON de auditoría post hoc **se encuentran en el ZIP descargable entregado en la conversación**, no se pretende que se hayan subido como ficheros íntegros a GitHub. El código de cada runner congelado permite regenerarlos con la versión de dependencias adecuada.

## A · Motor sin transformación dinámica: N127–N131

La anterior instrumentación usaba `inspect`/`exec` para reemplazar el cuerpo de una función a tiempo de ejecución. El nuevo módulo [esbm_event_engine.py](esbm_event_engine.py) contiene la implementación del bucle explícitamente. La API admite un proveedor de agentes y compatibilidad, un `scheduler` inyectable, un número de agentes/pasos y un `trace` de eventos ordenados con `t, stage, i, j`: exposición, propuesta, respuesta positiva/negativa, formación y ruptura. Importa los shocks y la compatibilidad histórica únicamente bajo verificación de SHA del archivo original.

- N127 **60/60 resultados dict completos exactos** para las diez condiciones y seis semillas ESBM históricas.
- N128 **6/6 resultados exactos** frente al adaptador anterior en N24×4 con políticas y slots, quitando sólo la clave con representación distinta de categoría ausente.
- N129 **2/2 trazas** con conciliación exacta de todos los recuentos de etapas y límites temporales/de ID.
- N130 las categorías ausentes reciben `None` (JSON `null`) en el porcentaje de participación, **nunca cero** ni `NaN`; valores de categoría no vacía se mantienen.
- N131 otro proceso Python `-I` sobre un directorio temporal vacío de otros scripts (mismas librerías del sistema) reproduce una simulación histórica y una miniatura y rechaza modos/slots inválidos; el nuevo engine no llama a `exec/eval/compile` en tiempo de ejecución.

## B · Red de oportunidades y control competente N132–N136

Para 30 semillas N24×4 construimos una red anular de cuatro contactos por actor (48 aristas, conectada) ordenada por `q` sintético, y otra mediante `networkx.connected_double_edge_swap` con **el mismo grado y número de aristas**. Ambos son grafos inventados, no observaciones de una red de pareja humana. N132/N133 comprueban estructura y grados en 30/30 cada uno. N134 verifica 60 conjuntos de riesgo: la equivalencia de grados **no implica** igualdad de aristas elegibles por compatibilidad ni igualdad de oportunidades realizables. N135 ejecuta 60 trayectorias artificiales pareadas y arroja para red anular menos red reordenada vieja: media de parejas activas **+0.0333** (10 signos positivos, 12 negativos y 8 empates), y de impresiones **−0.7333**. N136 registra puentes entre normas ficticias y distancia media de atributo `q`.

**Rectificación posterior N144:** el comparador antiguo `rewired` **NO era invariante a permutar ID**. En consecuencia, los contrastes con ese control dentro de N133–N141 son **válidos como ejecuciones que diagnostican software, pero NO como pruebas causalmente limpias de una ventaja topológica**. No descartar las observaciones negativas: conservarlas con estado `WITHDRAWN_FOR_TOPOLOGY_INFERENCE`. Esta salvedad prevalece sobre cualquier conclusión favorable del bloque B/C. N132 red anular mantiene integridad; N135 comparación histórica debe leerse junto al posthoc canónico.

## C · Calendarios, censura y calidad artificial N137–N141

Se amplió a red × 1/2 rondas de citas en **120 simulaciones N24×4** con el mismo motor, trazas y shocks por semilla. N137: de una a dos rondas la diferencia media de parejas activas es **+1.0667** para red anular y **+1.1333** para el viejo rewire, ambos sólo condicionales al generador, antes de la corrección de identidad. N138: las exposiciones de mercado no son presupuestos idénticos después de divergir trayectorias, aunque cada red conserve su grado.

N139 reconstruye exactamente las cohortes de relaciones, las rupturas y la censura derecha desde eventos `formation/dissolution`. Para red anular con dos rondas: **146 formaciones**, 100 censuradas, media de duración **solo de relaciones terminadas** 1.5435 y diagnóstico de supervivencia restringida `RMST(tau=3)` 2.5141. Esta diferencia es ilustración de **selección por censura** dentro del generador, no estimación poblacional humana, y los episodios repetidos de los mismos actores no son independientes.

N140 define **ex ante** proxy técnico de calidad `Q_ij=1−|q_i−q_j|` (sin calibración humana ni satisfacción observada), con utilidad agregada de los vínculos y vínculos-tiempo. Cambios de cantidad de parejas y suma de Q no son intercambiables. N141 registra Gini de exposición y número de actores nunca mostrados, que no son por sí mismos justicia distributiva. La sensibilidad a red vieja afecta de nuevo los contrastes topológicos, no la semántica de cálculo/contabilidad de los eventos.

## D · Falsación adversarial y reparación N142–N146

N142 congela un **control fail-closed** de los encuentros inyectados: seis casos inadmisibles (actor consigo mismo, índices negativos, fuera de rango, pareja no elegible, pareja duplicada y exceso de encuentros por actor) producen error y **no se convierten en votos/matches silenciosos**. N143 comprueba **60/60 equivalencias históricas** y **6/6 equivalencias con adaptador anterior** incluso después de introducir la validación.

**N144 — resultado negativo sustantivo en auditoría de software:** al permutar identidad de todos los agentes y llevar consigo atributos y matrices de shocks, la red anular anterior fue equivariante **20/20** veces. La red reordenada anterior fue **NO equivariante en las 20/20**. El procedimiento de intercambio sobre etiquetas nominales introducía una perturbación espuria. Queda registrada la falsación del control adversarial previo.

**N145 — reparación prospectivamente congelada:** el rewire se efectúa en **coordenadas canónicas del ranking continuo artificial q**, y después se transporta a las etiquetas de los agentes. Se obtuvieron **40/40** identidades exactas de grafo y **8/8** decisiones de encuentro invariantes bajo las permutaciones examinadas. Se exige ausencia de empates en q, que no está garantizada en todos los contextos humanos.

**N146:** reproducible en directorio limpio y subproceso Python aislado **en el mismo entorno instalado**, con SHA original, comparación histórica exacta y nuevo grafo; la corrupción intencional de una copia aislada del original se rechazó. No se ha usado otro sistema operativo ni replicación independiente externa.

**Auditoría POSTHOC del control corregido, 0 ciclos:** sobre semillas 3000–3029, el contraste de parejas activas anular−aleatorizada pasa, con una ronda, de **+0.0333** (antiguo) a **+0.1000** (canónico); con **dos rondas**, de **+0.0333** a **−0.2333**. Signos mixtos y efectos pequeños. Esta recalculación ocurrió después de observar la avería del control; no es prueba confirmatoria preregistrada del comparador corregido. Se conservan todas las series en `POSTHOC_CANONICAL_RESULTS.json` dentro del ZIP.

## AB-DECIDE, O7, SOURCES y priors

**Total del bloque:** 20 ciclos AB-H técnicamente ejecutados, con **19 PASS y un N144 VALID_NEGATIVE_DIAGNOSTIC**, 0 ciclos completos inválidos, 0 planning, 0 restantes. N127–N146 no se suman al antiguo contador **AB-R 26 válidos históricos** como evidencia humana. N1/N2/N3 nuevos=0. El número de semillas y tests no constituye replicación social externa.

**Registros:** 106 SOURCES originales sin cambios; **32 PRIORS** (nuevo `P-NETWORK-INVARIANCE`, solo técnico), **176 UPDATES** (`U173` nuevo prior de fallo y reparación; `U174–U176` `NO_CHANGE_WITH_REASON` en P-SCHEDULE-CORRELATION, P-NOVELTY y P-OPPORTUNITY). **CT2 ordinal científica: 7/100**, sin subida. **Madurez ponderada subjetiva: 42.20→42.85 %**, +0.65 puntos porcentuales **solo** por simulador 68→71 y QA 67→69, sin modificación de teoría, literatura, datos reales, originalidad, validación o manuscrito. El nuevo defecto y los contrastes retirados impiden atribuir la mejora a nueva validez sociológica.

**R5 humano: STOP_R5_EXTERNAL**. No se han descargado o corregido archivos humanos, modificado SRC104, aceptado licencias o contactado con investigadores. Las pruebas N137–N141 usan definiciones y datos artificiales; la existencia de `Q_ij` no convierte ese proxy en bienestar real. La red no representa una población de Salamanca, España ni de aplicaciones reales.

**Siguiente puerta científica:** predicción ESBM diferencial y pre-outcome ante B0/B1/SRM/B2/B4/B6 usando oportunidades observadas, dos votos nativos, derechos/ética y cohorte independiente con holdout legal. **Siguiente puerta de software:** comprobar identidad completa de trayectorias bajo permutaciones y el control canónico en N144–N146, calibrar límites de tiempo en N144 y verificar una instalación limpia independiente. STOP científico no detiene mejoras AB-P útiles; consumir otros ciclos sin nuevas clases de instrumento no se justifica.

**Nota de reproducibilidad:** los SHA256 de cuatro resultados completos A–D y los Git blob de código fuente están en `RESULTS_INDEX.json`. Este informe no confunde resultados agregados guardados en GitHub con el ZIP de recibos completo de la conversación.
