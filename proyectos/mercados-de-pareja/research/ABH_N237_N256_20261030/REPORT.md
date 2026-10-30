# AB-H PIVOT N237–N256 · Matching polinómico y reproducción histórica N144

**Cierre: 2026-10-30.** Base verificada de rama anterior: `b008f2eb6e864c4e4bb3090570f626ebe1416f62`. User granted 20 cycles; 20 genuine executions, **18 PASS técnico y dos negativos de fiabilidad de backend**, sin otros intentos contados como ciclos, 0 pendientes. Los contratos completos A–J y SHA de los **instrumentos previos a cualquier outcome** están congelados en [PREREG_AJ_SHA_FREEZE.json](PREREG_AJ_SHA_FREEZE.json), commit `2bc4b1ab0c42d817a433264907c7800e59dc45ba`. [RESULTS_INDEX.json](RESULTS_INDEX.json), [LEDGER 1](LEDGER_AJ_1.json), [2](LEDGER_AJ_2.json), [3](LEDGER_AJ_3.json), [4](LEDGER_AJ_4.json). Los recibos individuales, código exacto y todos los hashes están en un ZIP descargable de esta conversación, no pretendidamente versionados íntegramente en GitHub.

## Resultado empírico de software: 60/60

Se ejecutó el original **intacto** [esbm_dynamic.py](../ABR_ESBM20_20261028/esbm_dynamic.py) SHA256 `f7e6b84000720cbdf2ee0800c2b10d136185facd00e4622756cbb5f8d8254d0b` para seis semillas [101,211,307,401,503,601] y las diez configuraciones oficiales, **N144, T16, K7**. En paralelo, una réplica TypeScript derivada recibió los mismos cinco tensores y parámetros, y delegó exclusivamente el matching a un binario externo **C++ Boost.Graph**, no al antiguo solver exponencial de TS. Se compararon enteros y métricas float (tolerancia abs 1e−9) de los 60 JSON **incluido track de 16 períodos**. Resultado: **60/60 coincidencia de métricas y estado estadístico agregado**. No se ejecutó una comparación de TODAS las exposiciones/propuestas/respuestas/parejas individuales de los 60 casos. Se deshabilitó serialización de trazas en la copia TypeScript para este contraste; un flag explícito permitió avanzar con unicidad del óptimo no verificada y NO certifica desempate caso por caso.

La codificación se fijó antes de outcomes: cada peso `w=1+1e−4·U` en binary64, `delta=(w−1)·2^52` entero exacto, `B=floor(n/2)·max_delta+1`, nueva arista `B+delta`. El máximo de suma doblada se verifica dentro de Number.MAX_SAFE_INTEGER. Busca primero cardinalidad y después suma exacta de los pesos binary64; no garantiza identidad con cada decisión flotante de NetworkX para casi-empates. [Boost original documentation](https://www.boost.org/latest/libs/graph/doc/html/graph/algorithms/network_flow/maximum_weighted_matching.html) describe Blossom/Edmonds O(V³) y aritmética entera con pesos enteros. **C++/Boost es una dependencia externa; este resultado no convierte la réplica en Blossom puramente TypeScript ni verifica Windows nativo.**

## 10 controles adversariales N237–N246

- N237: 12 grafos n10, equivalencia exacta frente a NetworkX.
- N238: 7 grafos densos n24, equivalencia exacta.
- N239: 3 grafos dispersos n144, equivalencia exacta.
- N240: 2 grafos densos n144, equivalencia exacta.
- N241: 3 grafos de dos componentes n144, equivalencia exacta.
- **N242: NEGATIVO:** el proceso C++ devolvió **−11 (SIGSEGV)** para el grafo impar n143. No se obtuvo output de matching; recibo y traceback conservados. No atribuir causalidad definitiva sin depuración de Boost/encoding/entorno.
- N243: 9 controles de prioridad de cardinalidad, equivalencia exacta.
- N244: 5 controles de near-tie/ponderación, equivalencia exacta en las instancias probadas; no universal.
- N245: seis semillas, atributos y cinco tensores float64LE por semilla recuperados exactamente desde bytes con SHA de cada fichero.
- **N246: NEGATIVO:** el primer caso deliberadamente casi completo n144 excedió **12 segundos** de presupuesto y fue interrumpido; no se obtuvo resultado. La cota asintótica de Boost no certifica ausencia de problemas de implementación o condiciones numéricas.

Las diez políticas, N247–N256, 6/6 de resultados por ciclo, todas PASS. La suma aproximada de tiempo exclusivo de los 60 cálculos: Python original 5.70 s; Node/Boost 13.36 s. Medición observacional de este host, NO benchmark formal reproducido en Windows.

## Integridad, límites y alcance científico

Se conservaron código fuente, inputs humanos **NINGUNO**, generador determinista de población/shocks, SHA de 30 tensores, evidencia por ciclo y los 60 JSON de TS. El ZIP **ESBM_ABH_N237_N256_Blossom_60corridas.zip** (SHA256 `349414236fb7d075e9c024efb7c56faf616fd46d79454963e30db6d832aa144c`, tamaño 138891 bytes, 110 archivos) no contiene los ~80 MiB de shocks originales, que pueden regenerarse mediante el código y contrastarse con SHA; no distribuir el binario Boost Linux como si fuera portable a Windows. El ZIP pasó comprobación de integridad; los scripts llevan el SHA prereg. No se modificó el ESBM original ni SRC104, no SSJY, no acceptance de licencias, no contacto autores, no merges ni costosa CI.

**No hay validación humana** ni contraste B0/B1/SRM/B2/B4/B6* real nuevo. Esta campaña verifica reproducibilidad **de resultados agregados simulados** y detecta fallos de robustez del nuevo backend. SOURCE nueva **SRC111** documentación primaria oficial Boost; U196 `NO_CHANGE_WITH_REASON` en prior de trayectorias, sin probabilidad ficticia. Estado **111 SOURCES / 34 PRIORS / 196 UPDATES**, madurez ponderada **44.10%** (+0.10 pp QA76→77); **CT2 científica 7/100, STOP_R5 humano activo**, 0 nuevas evidencias científicas grado ≥1/3.

**AB-DECIDE:** Se cierra N237–N256 sin presupuesto restante. Siguiente obstáculo: depurar SIGSEGV/timeout y comprobar unicidad/empates, asegurar un backend exacto confiable bajo todos los grafos relevantes; después contrastar eventos individuales completos en Windows con derechos correctos. No abrir más ciclos sin autorización expresa. 
