# Mercados de pareja | AB-H PIVOT N357-N376 | actualización N358

**Vigente:** **2/20 ciclos técnicamente válidos N357 y N358**, 0 inválidos AB, 0 de planificación AB; **18 N359–N376 todavía autorizados y no consumidos**, un intento instrumental fallido en N358 conservado. 121 SOURCES, 35 PRIORS, 226 UPDATES. **CT2 científico 7/100 y STOP_R5 humano activo**.

## N357 conservado

Corregido únicamente en nueva copia de Blossom el campo auxiliar `full_units_in_2_power_minus52` como string decimal BigInt, esquema v2. 21/21 grafos con serialización exacta reconstruida en Python; 15 de ellos perderían unidades si se usara la vieja suma como JS Number. Prerregistro antes de outcomes `07a22a1d1dbc6995714b57f2b37f975178b61b42`; recibos en `N357_BIGINT_SERIALIZATION/`. Ningún ESBM original modificado ni paridad histórica repetida.

## N358: límite temporal realmente preemptivo por aislamiento

**Novedad diferenciada:** el límite `maxWallMs` del antiguo wrapper síncrono se comprobaba solo después de que `blossom.withState` retornase; no podía interrumpir un solver bloqueado. Se construyó un adaptador separado usando `child_process.spawnSync` con `timeout`, límite de heap y salida, entrada acotada y validación exigente de respuesta certificada. Esto no sustituye ni modifica el ESBM original.

Contratos A–J e instrumentos N358 congelados antes de toda ejecución en commit `bd0b74ef08d121747790d1d9f8fc20cb5f3ccd7f`. Se ejecutaron ocho controles nuevos: tres matching reales (vacío, estrella n144 y grafo n144 disperso) **PASS**, dos límites temporales **RESOURCE_HARD_WALL**, un JSON incorrecto **INVALID_WORKER_JSON**, un error del proceso hijo **WORKER_FAILURE** y una salida excesiva **RESOURCE_OUTPUT**. **8/8 estados esperados**, sin aceptar resultados parciales como certificados. En el control de CPU estancada 2.000ms, timeout de 300ms, tiempo total observado del padre **308,879ms**; el presupuesto de 1ms tardó **6,484ms** en abortar, debido a arranque y coordinación del SO.

El primer auditor Python falló antes de generar recibo por suposición incorrecta de serialización `[a,b,w]` vs `{pair:[a,b],weight:w}`. Se reparó exclusivamente el lector Python tras congelar cambios en commit `d5605e747ef8f8debd8b956aaaca494da1031b8e`, sin repetir los ocho outcomes JS. El verificador independiente final confirmó **8/8 estados** y **3/3 sumas exactas** por `fractions.Fraction`.

SHA256 outcome JS: `5040466f5517142808052aab9d17128d0f526307bb9a587a09758cdc8c5d2b45`. SHA256 oráculo Python: `4d5ef0a769e2b546210fce3a19a721c49719f234ca6cac09a6d06d34e8e944ec`. Límite epistémico: este resultado verifica detención del proceso hijo y controles en Windows/Node24 **bajo las condiciones especificadas**, no un límite de tiempo real con precisión exacta ni la corrección formal de todo matching. El nuevo adaptador es prototipo separado: no se ha integrado al motor histórico.

## R5 y acciones restantes

El estudio humano SRC106 Hall et al. 2026 recuperado mediante enlace publicado view-only permite verificar la existencia del código de dos votos `aChoice` y `pChoice`, pero OSF sigue siendo privado, con `node_license=null`, sin derecho de reutilización de microdatos ni cronología nativa verificados. SRC120 Northwestern 2007 coincide con SRC084; SRC121 Harvard 2017 carece de licencia de datos explícita comprobada. Ningún contraste humano fue ejecutado. **Mantener STOP_R5 y CT2=7**.

**AB-DECIDE:** N359–N376 pendientes y autorizados. Continuar solo si aparece un falsador técnico sustancialmente distinto del N357/N358 o evidencia externa humana R5 capaz de discriminar modelos. Ninguna plaza por reparaciones documentales ni pruebas repetidas.
