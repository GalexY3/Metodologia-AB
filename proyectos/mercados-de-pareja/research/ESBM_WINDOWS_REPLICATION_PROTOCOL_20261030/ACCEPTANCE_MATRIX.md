# Matriz de aceptación y falsadores · ESBM v2 Windows

**Tipo:** protocolo pendiente de ejecución, no resultado ni ciclo AB. Precedencia: fuente histórica (SHA256 `f7e6b84000720cbdf2ee0800c2b10d136185facd00e4622756cbb5f8d8254d0b`) > especificación explicativa > tests de juguete derivados manualmente (nunca probados por oráculo Python). Versiones `historical` y `symmetric_pair` separadas. Fuente de verdad de casos grandes N144: original archived output `RUNS.json.gz.b64`, Git blob `d8dbf04ec52337d46892e555cceee49ef224efc6` (salida existente no «ciega»), más trazas intermedias a producir **futuramente** mediante adaptador preregistrado.

| Puerta | Entradas congelables | Salida y criterio | Primer fallo que exige STOP |
|---|---|---|---|
| G0 procedencia | Commit base, Git blob fuente, SHA256 de 11.913 bytes, dependencias | Identidad de original y de fixtures validada, sin editar source | `ORIGINAL_HASH_MISMATCH` |
| G1 elegibilidad | UT01, UT02 | Aristas esperadas exactas, no loops | `COMPATIBILITY_DIFFERENCE` |
| G2 ruptura y duración | UT03, UT11 | Hazard, disolución tick-start, duración, censura idénticas | `WRONG_HAZARD_OR_TICK_ORDER` |
| G3 oportunidades Gumbel | UT04, UT05 | Puntuación y picks dirigidos, mismo *orden de visita* top-k | `EXPOSURE_OR_SCHEDULER_ORDER` |
| G4 enviar-responder | UT06, UT07 | Respuesta solo tras propuesta, shocks índices invertidos, aprendizaje inmediato | `DIRECTED_DECISION_DIFFERENCE` |
| G5 matching | UT08, UT09; UT12 no determinante | Primero cardinalidad, luego peso, direcciones colapsadas y solo elegibles | `MATCHING_SUBOPTIMAL` y `MATCH_TIE_DIAGNOSTIC` distinto |
| G6 toy trajectory | UT10, UT11 | Contadores y `track` exactos del caso de dos agentes | `TOY_EVENT_STATE_DIFFERENCE` |
| G7 tensores | 6 seeds, 5 shocks float64LE por seed, sha por archivo | Misma persona/choques en Windows, índice (t,i,j) correcto | `INPUT_TENSOR_BYTES_DIFFER` |
| G8 histórico completo | Seis seeds × diez escenarios = 60, N144 T16 K7 | 60/60 totales y cada tick con enteros exactos, parejas idénticas si óptimo único, tiempos y estados según oracle | `FIRST_UNEXPLAINED_EVENT_OR_STATE_DIFFERENCE` |
| G9 métricas continuas | Mismas trayectorias congeladas, `RUNS` histórico | error absoluto ≤1e−12 en probabilidades/intermedios, ≤1e−9 en métricas; **ninguna** discrepancia de decisión se perdona | `FLOAT_THRESHOLD_CROSSING` / `AGGREGATE_MISMATCH` |
| G10 independencia | Código JS/Rust propio, Node/compilador, Windows OS real, clean clone, library licences | Evidencia de ejecución independiente y hashes, reportes fallo/éxito | `NOT_INDEPENDENT` / `CLEAN_CLONE_NOT_VERIFIED` |

### Comparación event-by-event

**Orden exacto:** (1) rupturas existentes procesadas por i ascendente; (2) exposed singles y `risk_edges`; (3) remitente i ascendente; (4) candidatos elegibles ascendentes; (5) score y *orden dentro del top-k*; (6) exposición, posible propuesta, posible respuesta, actualización de feedback inmediata; (7) creación del grafo dirigido-aceptado/no-dirigido de matching; (8) matching y parejas iniciadas; (9) `track`. Los eventos de formación se comparan como conjunto no ordenado en cada tick salvo que el observador esté comparando el orden interno de NetworkX (ese orden no se interpreta como causal). Las decisiones de envío/respuesta son ordenadas; IDs de participantes permanecen fijos en `historical`.

**Paridad de matching:** si la solución de máximo cardinalidad y peso es única (margen no cero entre la mejor y la segunda, evaluado sin trucos de redondeo), exigir aristas idénticas; en empates, conservar todos los óptimos o una prueba exacta de calidad y clasificar `MATCH_TIE_DIAGNOSTIC`, sin atribuir causalmente el futuro a una regla no fijada. Si un empate cambia parejas y siguientes eventos, **la trayectoria completa NO es paritaria** hasta que se fije un mismo contrato de desempate; no otorgar PASS por ignorar el resto.

**Choques y umbrales:** los valores `U` se leen del tensor congelado sin transformaciones salvo el `clip` específico de Gumbel; `sigmoid` clipea la utilidad pero no `U_send/reply`. Una diferencia `p` dentro de 1e−12 que invierta un `U < p` es fallo de decisión y debe diagnosticarse como umbral numérico, no ignorarse. Las cifras enteras no admiten tolerancia. Si `NaN` o inf aparecen, no convertir a cero.

**Identificadores:** tests de permutación de IDs solo aplican a la variante optativa simétrica bajo un protocolo **aparte**; no exigir invariancia completa al motor histórico. Los `u_hazard` y `u_match` usan el par orientado min/max, así que renombrar IDs sin preservar estos convenios puede cambiar trayectorias legítimamente.

**Blindaje contra sesgo retrospectivo:** preparar unit inputs ahora, generar inputs de shocks después de congelar protocolo y fuente del oráculo; implementación JS/Rust debe tener hash de código ANTERIOR a acceder a referencia completa de casos y conservar un registro de qué resultados se habían visto. Como `RUNS.json.gz.b64` ya existe en GitHub, la prueba nunca puede declararse «holdout jamás visto» sin registro de exposición real del implementador. Tests futuros solo con autorización AB.

**Resultado de esta fase documental:** G0–G10 son criterios escritos, **ninguna puerta ejecutada ni certificada**. Los 12 fixtures son expectativas manuales por inspección estática. Las entradas grandes de seis seeds aún no se han materializado en bytes; no existen SHAs de esos ficheros. CT2 7/100, STOP_R5 y madurez 43.80% intactos.
