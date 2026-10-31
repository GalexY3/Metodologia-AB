# AB-H PIVOT Mercados de pareja · actualización 31/10/2026 · Windows nativo

**Estado vigente tras instalar ChatGPT on Steroids: 2 ciclos técnicos AB-H útiles ejecutados (N337 PASS, N338 negativo válido), 18/20 plazas N339–N356 autorizadas y pendientes.** La fase documental anterior había parado con 0/20 y queda preservada en [REPORT.md](REPORT.md); ese recuento es histórico de la revisión realizada antes de acceder al equipo, **no el saldo actual**. No se ha usado Codex.

**CT2 científica 7/100; STOP_R5 humano activo; grado científico nuevo 0/3.** Cualquier cambio de ingeniería o fidelidad software es distinto de validar una explicación sociológica sobre parejas reales. Continuamos sin nuevos microdatos románticos legalmente comprobados, exposición observada y decisiones bilaterales independientes.

## 1. Nueva capacidad instrumental realmente comprobada

El conector ChatGPT on Steroids permitió ejecutar comandos PowerShell de forma local en Windows y leer/escribir exclusivamente en una carpeta aprobada. Los originales del usuario no se modificaron. Se preparó una copia de trabajo en `C:\Users\Nitropc\CoS-Prueba\ESBM_AUDIT_N337_20261031`. Se verificó que el `esbm_dynamic.py` de Descargas coincide bit a bit con el código original, SHA256 `f7e6b84000720cbdf2ee0800c2b10d136185facd00e4622756cbb5f8d8254d0b`. Windows observó Node 24.16.0, Python 3.13.4, NumPy 2.4.3, NetworkX 3.6.1.

Se localizó el worktree Windows `C:\Programación\ESBM-W-ESBM-01` en commit `f3be098df714085c831ab2f1165d6322e30af685`, limpio, con la **réplica TypeScript corregida N207–N216** de 13 módulos. Sus fuentes proceden de un paquete privado original de usuario `ESBM_W_ESBM01_N207_N216_CODIGO_CORREGIDO.zip` (ZIP SHA256 `4e463f200b164edd7403efc0a3e26cfc17dd2fdb1b1f67927505ae2555d74ac0`). El matching usa **programación dinámica exacta exponencial por componente**, no Boost blossom. Este paquete **NO ES** el `ESBM_ABH_N237_N256_Blossom_60corridas.zip` histórico, todavía no localizado en búsquedas dirigidas de Descargas, Escritorio, Documentos/Codex ni archivos temporales. El paquete N207 ya contenía controles unitarios, pero **no** ejecución integral Python-vs-TypeScript oficial ni prueba de escalabilidad N144.

La carpeta aprobada contiene originales de trabajo y copias de código, inputs, manifests y resultados; no hay servicio residente, modificaciones del worktree del usuario ni ejecución de CI. La investigación se registra por GitHub; solo documentación estable podrá publicarse en `main`, sin merge.

## 2. N337: primera comparación integrada de Python original con TypeScript N207 independiente

**Prerregistro A–J + SHA antes de outcomes:** commit [`732d628dc8aa9f24620206c352eed5705fa40521`](N337_WINDOWS_NATIVE_TYPESCRIPT_20261031/PREREG_AJ_SHA_FREEZE_BEFORE_OUTCOMES.json). Se congelaron cuatro scripts nuevos, 13 módulos TypeScript de N207, Python original, seis ficheros sintéticos y manifiesto. Los scripts y el manifiesto también se incorporaron al árbol GitHub antes de ejecutar.

**Unidad y alcance:** N=8 agentes, T=6 períodos, K=3 perfiles, seis semillas predefinidas [101,211,307,401,503,601] y diez escenarios ESBM (60 trayectorias artificiales, 360 decisiones de matching por tick). La función `simulate()` del Python original **no se editó**, pero se ejecutó con entradas sintéticas pequeñas inyectadas y N/T/K globales modificados en memoria. El TypeScript `engine.replay()` utilizó las mismas matrices de shocks y variables personales, con un algoritmo de matching implementado de manera independiente por recurrencia de subconjuntos.

**Resultado:** las **60/60** ejecuciones TypeScript terminaron sin excepciones; el comparador halló **0 discrepancias** en todos los campos del resultado (incluidos los tracks de período) y en todos los conjuntos de parejas seleccionadas por tick. Los **360/360** estados TS de matching reportaron `UNIQUE_OPTIMUM`. Los datos artificiales implicaron **4.132 exposiciones, 1.292 propuestas y 236 formaciones de pareja**. Un mutante que altera `track[0].impressions` fue detectado correctamente en `$.result.track.0.impressions`. Se usó igualdad exacta de enteros, identidades de pareja y tolerancia absoluta 1e-9 para flotantes.

[Recibo N337 con hashes](N337_WINDOWS_NATIVE_TYPESCRIPT_20261031/N337_OUTCOME_RECEIPT.json) · [archivo reproducible completo de 28 archivos codificado base64](N337_WINDOWS_NATIVE_TYPESCRIPT_20261031/N337_DIRECT_PY_TS_RESULTS.zip.b64), ZIP original SHA256 `53bcb886bb1dc033a9cc16ee1d6afd8ecd178306966c3e8ce0ff6fa676796406`. ZIP local en `CoS-Prueba\ESBM_AUDIT_N337_20261031\N337_DIRECT_PY_TS_RESULTS.zip`; código, 13 fuentes TS, inputs, resultados Python/JS y auditoría incluidos.

**Alcance limitado:** esto NO reproduce el N144 oficial, NO captura exhaustivamente los eventos dirigidos nativos del Python original y NO ejecuta el antiguo motor TS+Boost N237. La concordancia de 60 *escenarios artificiales pequeños* no es una replicación de cohortes humanas. Se cuenta **una sola plaza N337**, no 60 ni 360.

**Incidencia instrumental conservada:** un primer comando manual de comprobación PowerShell llevaba una cadena SHA abreviada errónea para `state.ts` y abortó **antes de ejecutar TypeScript**. El hash de 64 caracteres **ya congelado en GitHub era correcto** y coincidió byte por byte con el archivo real. Se repitió el preflight leyendo directamente las hashes del prerregistro, verificando los 13 TS y seis inputs antes del outcome. No hubo reparación del código ni cambio de instrumentos.

## 3. N338: ejecución por primera vez de N144 nativo con el solver TypeScript exponencial

**Prerregistro A–J + SHA antes de outcomes:** commit [`9ee375c058cbeb3a678c403bcc2653207fc4690f`](N338_WINDOWS_FULLSIZE_20261031/PREREG_AJ_SHA_FREEZE_BEFORE_OUTCOMES.json). Se congelaron cuatro scripts nuevos, el manifiesto fuente, el Python original, los SHA de los cinco tensores float64 de 16×144×144 y el archivo de personas `people(101)`. Se seleccionaron **a priori** los escenarios `mixed_random` y `private_rejection_learning`; límite de 22 nodos por componente del solucionador TypeScript, 50.000 estados, 2,5 s por búsqueda y 90 s externos, sin ajuste tras outcomes.

El verdadero Python original `simulate()`, sin modificación de N/T/K oficiales (N144/T16/K7), terminó las **dos** trayectorias. En cambio, el motor TypeScript N207 completó el **primer tick** y luego se detuvo en el tick `t=1` en ambos escenarios. En `mixed_random`, tras **4.207 eventos TS**, su grafo de matching contenía una componente conexa de **27 nodos**, superior al máximo preregistrado de 22: `MATCH_RESOURCE_LIMIT:COMPONENT:27>22:states=5`. En `private_rejection_learning`, tras **4.264 eventos**, la misma barrera `COMPONENT:27>22:states=6`. No se incrementó el límite ni se introdujo solución aproximada.

Una inspección **posterior y descriptiva** verificó que las parejas del primer tick coinciden entre Python y TypeScript: 37 parejas en el escenario aleatorio y 38 bajo aprendizaje privado. Este control **NO** convierte las trayectorias incompletas en paridad de 16 períodos. El auditor preregistrado reporta **0/2 ejecuciones TypeScript completas, 2/2 paradas de recursos**. La limitación es computacional del solver exponencial, no una observación de conducta humana ni una divergencia comprobada de decisiones.

[Recibo N338](N338_WINDOWS_FULLSIZE_20261031/N338_OUTCOME_RECEIPT.json) · [resultados y scripts de auditoría, ZIP de 10 archivos en base64](N338_WINDOWS_FULLSIZE_20261031/N338_OFFICIAL_N144_NEGATIVE.zip.b64), ZIP SHA256 `bd535039aaf30e872c95e3601d8d1a17dc2a88d1da00ea38ded49251780a5f87`. El archivo ligero incluye código, manifiesto, personas sintéticas y resultados. **No** contiene los cinco tensores binarios originales (13,27 MB): permanecen en el área de trabajo del PC, y pueden regenerarse determinísticamente con `prepare_official_101.py`, el código original y la versión NumPy congelada; sus SHA completos constan en el manifiesto preregistrado.

Se cuenta **una sola plaza N338 como resultado técnico negativo válido**. Se rechaza expresamente afirmar que un solver exponencial que pasa pruebas n8 es viable para n144. Una integración futura necesita un matching **polinómico exacto y certificado**; reutilizar NetworkX directamente como motor de los dos lados eliminaría independencia del algoritmo de matching y tendría que declararse como contraste del bucle de eventos únicamente.

## 4. Priors, fuentes y límites científicos

U214 añade a `P-TRAJECTORY-INVARIANCE` estas dos observaciones técnicas, con decisión `NO_CHANGE_WITH_REASON`: ni la paridad pequeña ni la limitación de escala contribuyen evidencia empírica sobre quién acepta a quién en mercados románticos reales. La búsqueda documental anterior sí registró SRC115–SRC117 y U209–U213, pero no obtuvo microdatos originales elegibles. Estado científico:

- **117 SOURCES, 35 PRIORS y 214 UPDATES**.
- **CT2 científica 7/100**, `STOP_R5` humano activo, 0 grados científicos humanos 1/3, 2/3 o 3/3 nuevos; madurez 44,10% histórica no reestimada.
- No nuevos datos humanos, NO SSJY, Codex, licencias aceptadas, contactos, merges experimentales, CI costosa, modificaciones originales ESBM/SRC104 ni ejecución del TS N237.
- No confundir `EVENT_STATE_AND_RESULT_EQUIVALENCE` del motor N207 cuando solo se comprobaron resultados+parejas pequeñas: no se dispone de un oráculo completo de eventos dirigidos desde el Python original. No hay causalidad nueva ni validez externa.

## 5. Ledger, grafo AB Atlas y decisión

[Ledger A–J completo de los dos ciclos](LEDGER_AJ_N337_N338_20261031.json) · [saldo real](STATUS_AND_BUDGET.json) · [puerta humana A–J condicional](A_J_CONDITIONAL_R5_GATE_NOT_EXECUTED.md) · [cribado R5 de 13 fuentes](R5_SOURCE_SCREEN.json) · [AB Atlas delta](AB_ATLAS_DELTA.json) · [CT2 escala completa y ampliada](CT2.svg).

**AB-H N337–N356: 20 autorizados, 2 ejecutados válidos (1 PASS técnico + 1 negativo válido), 0 inválidos, 0 planificación AB, 18 pendientes N339–N356.** El bloqueo `STOP_R5` continúa para validación humana; técnicamente puede investigarse un backend escalable **sin quemar** plazas con otra prueba del mismo solver exponencial. No abrir N339 sin una nueva pregunta diferencial, contrato A–J y hashes congelados de código y entradas **antes de su outcome**. No hace falta conceder otras 20 plazas.

**Decisión AB-DECIDE:** `CONTINUE_TECHNICAL_CONDITIONED_ON_NOVELTY / HUMAN_STOP_R5`. Solicitar *continuar las 18 plazas ya autorizadas*, no un nuevo bloque. El acceso Windows ha superado el impedimento de ejecución local, pero no ha resuelto el cuello de botella científico de observación romántica independiente.
