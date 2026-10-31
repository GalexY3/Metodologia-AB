# N356 · reparación prospectiva de oráculo Python después del primer outcome

## Evento conservado

- Congelación original antes del resultado JS: commit GitHub `dec8fa73876a0ac80b4add10b91d71e48bea3a04`.
- Script JS sin modificaciones: SHA256 `5b85db6726abe41e8920f8ad2f90a851a198023e10d6623109ed09a92162df74`.
- Resultado JS inicial, no repetido: 12 fixtures, 9 discrepancias declaradas, SHA256 `8ecf9395834ee96c98c9cb5c39ec692eea0f3944895b464515d9e6e7c9e2fef5`.
- Primer oráculo Python `7c3ac54531a160fa76d301267707ca2ed9aba6d16e59a551ee33529d28e7add0`: ABORT antes de escribir su recibo, `AssertionError` en línea 33.

## Causa diagnosticada

El JSON que serializa números IEEE-754 mayores de 2^53 usa la representación decimal mínima que recupera el mismo binary64. Al leerlo como entero decimal exacto, `json.loads` de Python **no** recupera necesariamente los mismos bits de ese número; la comparación original del oráculo entre `int(literal)` y `BigInt(Number)` resultaba falsa aunque fuese correcta la diferencia calculada en JS.

## Reparación congelada ANTES de reejecutar el oráculo

Se calcularán **por separado** la diferencia respecto al literal entero decimal leído por Python y respecto al valor binary64 efectivamente transportado por JSON mediante `int(float(literal))`. La segunda deberá concordar con el valor BigInt registrado en la ejecución JS. La diferencia decimal es una salida adicional, no un reemplazo de las hipótesis y controles originales.

El fichero JSON del primer resultado queda intacto, igual que el solucionador, los 12 fixtures, sus hashes y las condiciones R5. El primer intento fallido es **un intento instrumental**, no otro ciclo AB.

**Condición antes de ejecución:** publicar este documento y el nuevo SHA del oráculo reparado en GitHub en commit posterior al prereg inicial, y solamente entonces ejecutar el oráculo Python contra el JSON ya generado. Mantener sin modificar SRC104, ESBM original, CT2 7/100 y STOP_R5.
