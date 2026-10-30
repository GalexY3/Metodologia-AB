# ESBM v2 · Especificación independiente de transición y reproducción

**Estado:** PROTOCOL_ONLY / INPUT_FIXTURES_ONLY / NEVER_EXECUTED. Fecha 2026-10-30. **0 ciclos AB**. Rama de trabajo `research/esbm-independent-replication-spec-20261030`, separada de `research/ab-h-esbm-r5-replication-gates-20261030` en HEAD `58e2b09800aca306013bd4bfb81d9d7f678b4fda`. Ningún cambio al motor histórico, SRC104, fuentes humanas, CT2 7/100 o STOP_R5. No se pide habilitar CI costosa.

## 0. Autoridad, alcance y discrepancias

**Código de autoridad único:** `proyectos/mercados-de-pareja/research/ABR_ESBM20_20261028/esbm_dynamic.py` @ rama padre y SHA Git blob `5fc9f63fd44ff81ce9ff6c900ba6bf24153356f2`, SHA256 bytes `f7e6b84000720cbdf2ee0800c2b10d136185facd00e4622756cbb5f8d8254d0b`, 11.913 bytes. El adapter posterior `research/ABH_N127_N146_20261029/esbm_event_engine.py` Git blob `2c2848181af3e8a31f7d084251dd07bc14ba7986` proporciona trazas auxiliares, NO sustituye fuente histórica. Los motores opt-in `symmetric_pair` y `symmetric_hazard` son **otros programas**: no se mezclan sus fixtures con `historical`. 

**Tres preguntas diferentes:** (A) reglas individuales pequeñas con shocks inyectados = equivalencia funcional; (B) trayectorias completas del motor original con *las mismas* personas/shocks y escenarios = equivalencia de ejecución; (C) distribuciones con RNG distintos = reproducibilidad estadística, **sin exigir mismos números aleatorios ni matching por empate**. Esta especificación cubre (A) y (B). (C) necesita protocolo estadístico independiente futuro y no implica verdad humana.

## 1. Datos y generación

En el motor histórico original, configuración fija `N=144`, `STEPS=16`, `K=7`, seis seeds `[101,211,307,401,503,601]`, diez escenarios `SCENARIOS` (orden de inserción en Python preservado). Para cada seed, `rng=np.random.default_rng(seed)`, **en este orden exacto**: `genders = permute([F]×60+[M]×60+[X]×24)`; `scopes = permute([all]×72+[same]×36+[other]×36)`; `norm = integers(0,3,N)`; `q = random(N)`; `age = integers(19,51,N)`; y CINCO tensores `random((STEPS,N,N))` por orden: `u_send`, `u_reply`, `u_hazard`, `u_expose`, `u_match`. Todos los escenarios de una semilla usan el **mismo** conjunto de personas y shocks, no RNG consumido según política.

**Fase de portabilidad:** primero leer JSON/JSONL de personas y cinco shocks generados en el oráculo (después de autorización futura, con hash frozen antes de mostrar outcomes); no implementar PCG64/NumPy al principio. Una fase RNG independiente debe mostrar algoritmo, inicialización, generación de permutaciones, `rng.integers` y transcodificación float, o usar vectores de bytes salidos de NumPy; no comparar semillas «idénticas» si los algoritmos RNG son distintos.

**Dos niveles de fixtures:** `UNIT_INPUTS.json` son mundos **de juguete** con N=2/3/4 por inyección para la implementación secundaria. NO son instancias que el módulo `esbm_dynamic.py` pueda ejecutar sin parametrización (tiene N/STEPS/K globales). `REFERENCE_PLAN.json` enumera 60 corridas originales N144×T16 que el ejecutor solo puede producir/evaluar **después** de una autorización y freeze de resultados; NO almacenar supuestos outputs en fixtures.

## 2. Elegibilidad y estado al principio de cada tick

`genders∈{F,M,X}`, `scope∈{all,same,other}`; compatibilidad `general`: `i≠j` y el scope **de ambos** admite el género contrario (scope same exige mismo género, other distinto). Modo `FM_only`: únicamente pares F–M, **ignorando scopes**. `eligible[i,i]=false`. Riesgo no dirigido de `eligible` entre `available`, cada arista contada una vez.

Estado inicial: `partner[i]=-1`, `start[i]=-1`, `seen[i]=0`, `requests_received[i]=0`, `approvals[i]=0`, `private_bias[i]=0.0`, `public_score[i]=0.0`; contadores `formed=dissolved=listed=proposals=requests_accepted=0`. Al comienzo de cada tick t, recorrer agentes i **orden creciente**, mirar pareja j=partner[i] y procesar solo `j>i`. `h=min(.90,(.12+.065*I[norm_i≠norm_j]+.004*abs(age_i-age_j))*hazard_mult)`. Disolver si `u_hazard[t,i,j] < h`; registrar duración completada `t-start[i]`, vaciar pareja y start de ambos, aumentar `dissolved`. El shock en orientación i menor, j mayor es requisito **histórico**, no simétrico.

Calcular `available` inmediatamente después de todas las disoluciones, como IDs ascendentes sin pareja. `singles=len(available)` y `risk_edges` = número de elegibles no dirigidos entre available. El estado de nuevas parejas **no se altera durante las exposiciones del mismo tick**, solo al final del matching.

## 3. Exposición dirigida y orden secuencial

Por cada remitente i en `available` ascendente, construir `candidates=[j ∈ available (ascendentes) | j≠i & eligible[i,j]]`. `kk=min(K,len(candidates))`. Para cada candidato, `U=clip(u_expose[t,i,j],1e−12,1−1e−12)`, `g(U)=−ln(−ln(U))`. Puntuación: base g(U), +1.7 si `policy=same_norm` y normas iguales; +3.5*(q_j−.5) si `policy=popular`; −1.4*ln(1+seen[j]) si `policy=balance`; sin término para `random`. **Crítico:** `seen[j]` se actualiza durante el recorrido del mismo tick y puede alterar rankings de futuros remitentes bajo `balance`.

La selección original es `picks=candidates[np.argsort(scores)[-kk:]]`: top-k **sin reemplazo y recorrido en orden creciente de score dentro del top-k**, no de mayor a menor. Ties de `np.argsort` no garantizan orden estable: escoger shocks distintos en los fixtures de aceptación; marcar empate como `DIAGNOSTIC_UNSPECIFIED_ORDER`. Cada pick incrementa `listed`, `seen[j]`, `received_by_norm[norm_j]`, `norm_exposure_denom`, `norm_exp` si normas iguales y anexa exposición dirigida `(i,j)`.

## 4. Propuesta, respuesta y aprendizaje en el mismo tick

`sigmoid(x)=1/(1+exp(−clip(x,−25,+25)))`. `same=I[norm_i==norm_j]`, `gap=abs(age_i−age_j)`. `send_util=−.85+1.6*(q_j−.5)+same_pref*same−.012*gap+private_bias[i]`. Proponer si y solo si `u_send[t,i,j] < sigmoid(send_util)`. La propuesta aumenta `proposals`, `tick_proposals`, `approvals[i]`, `requests_received[j]`, `sent_by_norm[norm_i]`. Si no propone, **no existe respuesta observada** y no se actualiza aprendizaje.

`reply_util=−.85+1.6*(q_i−.5)+same_pref*same−.012*gap+(public?public_score[i]:0)`. Respuesta positiva si y solo si `u_reply[t,j,i] < sigmoid(reply_util)`, **ojo índices inversos** del tensor de respuestas; `requests_accepted++`, anexa arista dirigida `mutual.add((i,j))`. Si negativa, con `private=true`: `private_bias[i]=min(.80,private_bias[i]+.08)`; con `public=true`: `public_score[i]=max(−1.8,public_score[i]−.08)`. Efecto **inmediato**, visible por siguientes propuestas/respuestas de la ronda según rama. Un solo sí del receptor tras propuesta basta para la arista candidata: NO son dos votos independientes poscita.

## 5. Formación de parejas y duración

Al terminar TODAS las exposiciones dirigidas del tick, crear `ug` con nodos available y aristas no dirigidas para cada `(i,j)` aceptada, colapsando direcciones repetidas en `x=min(i,j),y=max(i,j)`. Peso `w(x,y)=1.0+1e−4*u_match[t,x,y]` (historical `min/max`, no media de shocks). Resolver `max_weight_matching(ug,maxcardinality=True,weight='weight')`: primero **mayor cardinalidad**, luego **mayor suma de pesos**. Si varios óptimos comparten cardinalidad y peso y difieren en pares elegidos, la equivalencia de un matching particular de NetworkX NO está garantizada; el ejecutor reporta `MATCH_TIE`, grafo y todos los óptimos relevantes sin esconder ambigüedad. En grafos de óptimo único, exigir pares sin orden exactos.

Cada par asigna `partner[i]=j`, `partner[j]=i`, `start[i]=start[j]=t`, `formed++`; si normas iguales aumenta `new_norm`. No se forman parejas que no sean elegibles o ya emparejadas. `active_pairs` después del matching = número de `partner[i]>=0` dividido por dos. `track[t]` contiene `{t,singles,risk_edges,impressions,proposals,reciprocals,new_pairs,active_pairs}`. `reciprocals` **cuenta respuestas positivas dirigidas**, aunque dos direcciones vayan al mismo par y colapsen en una arista. Por tick `formed−dissolved=active_pairs`, `new_pairs≤reciprocals≤proposals≤impressions` (esta última cadena por tick no siempre en todas versiones instrumentales; en el histórico actual sí).

Al terminar t=STEPS−1: una pareja activa con `partner[i]>i` contribuye censura derecha `STEPS−start[i]`; otra que rompió en t contribuyó duración observada `t−start[i]`. Exponer estas distinciones y no llamar duración real humana al resultado.

## 6. Controles del resumen original

Preservar **claves y valores** del `result` Python original: distributions Counter de género/scope, `possible_compatibility_pairs`, `agents_no_eligible_partner`, contadores, tasa activa, `never_displayed_receivers`, `receiver_impression_gini` (Gini 2·weighted_sorted/(n·sum)−(n+1)/n o 0 si suma cero), proporciones por norma, duración media completada o null, censura, promedio activos por tick, medias bias y public_score, impresiones por género, tasa activa por género, `track`. Los `SUMMARY` de escenarios se agregan por seed con media y desviación muestral ddof=1 y redondeo a 6 decimales, pero **no sustituyen comparación por tick/evento**. Archivar hash de archivos JSON, schema, versión y sistema operativo por separado; el orden de claves/espacios JSON puede diferir sin desacuerdo semántico.

## 7. Obligaciones de falsación y tolerancias

**Exactas:** partner/start enteros, elegibilidad, nodos activos, `available`, exposición/propuesta/respuesta con orden dirigido, contadores, mismo conjunto de parejas *cuando el óptimo es único*, balances y cronología `tick`. **Flotantes:** `abs(a−b)≤1e−12` para probabilidades/intermedios finitos; métricas agregadas finales `≤1e−9` en escala absoluta; ninguna tolerancia alrededor del umbral puede convertir una decisión opuesta en PASS. Si una diferencia flotante cruza un shock, registrar `FLOAT_THRESHOLD_CROSSING`, inputs/operaciones precisos y STOP hasta analizar, no redondear outcomes. NaN, missing, sesgos por IDs y matching empatado → diagnóstico explícito no «PASS».

**Primera divergencia:** congelar estado *previo* y obtener reporte con `scenario,seed,t,stage,sender,receiver,u,p,pre_state,observed,expected`, los hashes de fixture/oracle/implementación, versiones de OS/runtime y semilla; no permitir reajustar el código original. Se considera replicación independiente de mecanismo únicamente si el segundo código fue escrito sin reutilizar la implementación Python y su ejecución real en Windows/entorno diferente está documentada. Ver `WINDOWS_EXECUTOR_TASK.md`.

**Gobernanza:** fase presente prepara documentos y fixtures; **ningún resultado ni nuevo ciclo**. Antes de ejecutar experimentos, el usuario debe conceder presupuesto AB y fijar A–J/código; no usar los hashes de referencia *preparados ahora* como prueba de que se corrieron. Sin licencias aceptadas, SSJY, microdatos humanos ni cambios en SRC104; CT2 científico 7/100, madurez 43.80 %, STOP_R5.
