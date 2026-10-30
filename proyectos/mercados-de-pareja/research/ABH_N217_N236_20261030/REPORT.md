# AB-H N217–N236 · Paridad pequeña Python ↔ TypeScript y límite N144

**2026-10-30; punto de partida:** 4045061932d44fd6fc2dfa1077bf3696e9cf0481. **20/20 ciclos ejecutados y válidos técnicamente; 18 PASS y 2 diagnósticos (N234 y N235). Cero hallazgos humanos.**

## Resultados

- **N217–N226:** 10/10 políticas del modelo histórico coinciden entre adaptador Python y réplica independiente TypeScript, misma población artificial N=8, cuatro ticks, K=2, cinco tensores de shocks idénticos. Métricas exactas dentro de 1e−9, idénticos eventos dirigidos de exposición/propuesta/respuesta/ruptura y mismos pares formados tras ordenar su orientación.
- **N227–N230:** 4/4 casos adicionales coincidentes: N12 K3, orientación asimétrica de respuesta, compatibilidad F/M independiente de scopes y rupturas forzadas desde tick 1.
- **N231–N233:** empates fuera del top-k no bloqueantes; empates en el corte bloqueantes; matching con óptimos múltiples se etiqueta ambiguo.
- **N234:** un caso casi empatado por binary64 frente a BigInt no mostró inversión de pares seleccionados. Es diagnóstico, NO certificado universal de igualdad numérica.
- **N235:** choque artificial N144 con propuesta/respuesta garantizadas genera una componente conexa de 144 nodos y el solver TS detiene con MATCH_RESOURCE_LIMIT:COMPONENT:144>22:states=0. Parada segura validada; escalabilidad N144 y paridad de 60 corridas NO demostradas.
- **N236:** 24/24 grafos n6 comparados con oráculo independiente Python Fraction, coincidencia de cardinalidad, peso exacto y unicidad.

## Reparación instrumental registrada antes del reintento

Primer intento N217 comparó incorrectamente pareja Python (7,3) y TS (3,7) como diferentes, pese a coincidir métricas y eventos dirigidos. Fallo conservado en ZIP. Prerregistro reparación solo del orden de parejas: commit 5cd2f15a5098b37da87df409dbcf4a4f5f33f80d; nuevo SHA congelado antes de reintento: ea5f37e8636adad1ad1c6a696c73d3bc03518bd2. No se modificó original ni réplica. No se contó doble ciclo.

## Congelación y evidencias

Prerregistro A–J y SHA de scripts antes de outcomes: [PREREG_AJ_AND_FREEZE.json](PREREG_AJ_AND_FREEZE.json), commit 0e52b951702c41e2c2e543f4410c8e7de9f2b7bb. [Índice resultados](RESULTS_INDEX.json), [Ledger 1](LEDGER_AJ_1.json), [2](LEDGER_AJ_2.json), [3](LEDGER_AJ_3.json), [4](LEDGER_AJ_4.json). ZIP íntegro de código, JSON por caso y recibos del usuario: ESBM_ABH_N217_N236_paridad_y_limites.zip, SHA256 30ab8b41f225a2499e20ef4cc247a476736191b4281b36adfa37ec63ddf9a781. Script Python final SHA ab0541c39fc66df43a75ac0b0e4818946f64b34b61e15d6a4f6048379124751c, Node runner SHA 6f9fa90def3740f8ba84c71afa641796618dd67f8278a3a9234f277fd69b695a.

## Alcance científico

Las 14 comparaciones son escenarios sintéticos pequeños, con N8–12, T3–4, K2–3, no el histórico intacto N144×T16. El adaptador Python de la campaña N127 preserva la lógica de ESBM pero no es el archivo N144 sin parametrizar. Las 20 comprobaciones corrieron en Linux Python 3.13/NumPy 2.3.5/NetworkX 3.6.1 y Node 22.16; no se ejecutaron en Windows en esta campaña. Windows Node24 compiló en turno anterior, solo tipado/compilación. Ausentes 60 corridas históricas, equivalencia completa TRACE_SCHEMA_1 y datos humanos independientes. No usar licencias ni SSJY, no fusionar.

**AB-DECIDE:** 20/20 técnicos válidos; 0 inválidos definitivos, 0 solo planificados y 0 restantes. SOURCES110, PRIORS34, UPDATES195 (U195 NO_CHANGE_WITH_REASON). Madurez 43.90→44.00% únicamente QA; CT2 7/100 sin cambio, STOP_R5 humano activo y cero nuevo 1/3–3/3. Próxima puerta: solver exacto escalable y reproducción N144/60 con código/prerregistro congelados, sin asumir ya autorizados más ciclos.
