# Reparación prospectiva de archivo de trazas N259–N263 — PRE-OUTCOME RE-TEST

**Fecha:** 2026-10-30. **Instrumentos originales congelados:** commit `474cdae1cf04bf89912f7c6fa4f961bbe14c4483`. No cambiar `run_campaign.py`, `trace_engine.py` ni binario C++.

## Hallazgo inicial adverso (no ocultar)
Los intentos N259–N263 ejecutaron cálculo, pero **fallaron al guardar la primera traza** por `FileNotFoundError` para el directorio `results/events/` inexistente. Todos los 30 intentos seed-level devolvieron este error de archivo. Esos recibos no establecen paridad individual, ni son PASS. **Ciclo de primera ejecución inválido de carácter instrumental**, conservado en `failed_attempts/N259...N263_attempt1_missing_events_directory.json` con SHA:
- N259: `a179246c25ff5d20414623d2ae57d629d51653a1e3c019aaba4f2a669e52d4da`
- N260: `a387896f6ed1d98f0f2450e6e355bda440036b30e5f053d2fd9a93cfadc636fd`
- N261: `68475c46966e03fe789ad5888bd32831b107901bb76c3ce655f734ae4cab57f6`
- N262: `1c2ad285c70de96a7ce8b45a1d14c78192ff466ffb7c4bd3b6253529dd479861`
- N263: `2a14b3e0ac6ed99259cae599987d41555d89d3754f2fd1bf35e10852731620a8`

## Reparación preinscrita
1. Crear el directorio vacío con `mkdir -p /mnt/data/ESBM_N257_N276/results/events`.
2. Conservar los JSON iniciales en `failed_attempts/` y **solo después** retirar las cinco rutas `results/N259.json`–`results/N263.json` para permitir la ejecución de los mismos IDs sin sobrescritura. Archivar copias/hash de ambos resultados.
3. Ejecutar de nuevo N259–N263 con **el mismo** runner SHA256 `5d39ded9b8602a2d3e58e78934c3a62c0560c7993b85d4af24d60e9bc58302df`, engine SHA256 `c0c92061100a689ab59698a46e22a96e96d7bb3bd99a21ec292d7aaa30e4415a`, C++ SHA256 `47806e6b331e088d209e51143d18cb5d5cc7a2e2d3d6d8914478bff4b7b8c2d3` y binario SHA `96087f807c3845193da871aa8a8f83092c095a0dcf2ab0862ace85b76eebf995`.
4. Los posibles outcomes de diferencias emparejamiento/evento se evalúan con criterios congelados A–J; no recalibrar ni cambiar implementación después de observarlos.
5. N257/N258 negativos de runtime no se reparan ni convierten en PASS.

**Contabilidad:** intentos iniciales N259–263 = cinco inválidos instrumentales (no cinco slots adicionales). Rerun prospectivo bajo nuevo commit; descontar cada plaza solo tras intento útil completo y conservar ambas versiones. CT2 humano científico 7/100, STOP_R5 humano, sin humanos/SSJY/licencias/contactos/merges.