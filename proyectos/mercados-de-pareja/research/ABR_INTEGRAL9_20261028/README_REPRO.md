# Reproducir ESBM · 66 corridas sintéticas

**Fuente principal** [simulator.py.gz.b64](simulator.py.gz.b64) y **anexo post hoc** [observational_equivalence.py.gz.b64](observational_equivalence.py.gz.b64), archivados de forma íntegra en texto gzip/Base64 en GitHub. La huella SHA256 de cada `.py` se congeló **antes** de ejecutar. Para restaurar archivos Python desde un clon GitHub:

```python
import base64, gzip, pathlib
for name in ("simulator.py", "observational_equivalence.py"):
    path = pathlib.Path(name + ".gz.b64")
    pathlib.Path(name).write_bytes(gzip.decompress(base64.b64decode(path.read_text().strip())))
```

Luego instalar `numpy` y `scipy` (requisitos de la versión ejecutada), y correr:

```bash
python simulator.py
python observational_equivalence.py
```

La primera corrida genera `RUNS.json`, `SUMMARY.json`, `SUMMARY.csv`, `QA.json`; después la segunda genera `EQUIVALENCE.json` usando los RUNS producidos. **No requiere dataset humano**. Verificar:
- SHA256 `simulator.py` = `dfe5dabc2c5c9cbd07a76471e0d855d85424a26705d1ea626b55ccb35289b279`.
- SHA256 `observational_equivalence.py` = `e9d75c80dcfe42f7378b1f75d72b3caad46a375860f256493c9719f0b59865e2`.
- SHA256 `RUNS.json` = `72f4cadd87dc45f1edcc5ec2370ba507f58f2e337ba886239ebf2767b86c5cd6`.
- SHA256 `SUMMARY.json` = `8cedf4fd0d59d046ee8ec0c0c1814dd971804d35fc68104e3cfd9847ce8a6ab9`.
- SHA256 `EQUIVALENCE.json` = `a2a3a86d175350c9db1dff92eac01bd3e0040b42ed0c1cb0eaf145a831b48af3`.

Los outputs compactos están en [RESULTS_COMPACT.json](RESULTS_COMPACT.json) y [EQUIVALENCE_COMPACT.json](EQUIVALENCE_COMPACT.json). La corrida principal usa 6 semillas × 10 escenarios = 60 ejecuciones; el anexo 6. **El anexo de equivalencia fue escogido retrospectivamente** tras observar la primera tabla, y NO es validación fuera de muestra.

La fuente en GitHub fue contrastada por longitud y FNV-1a64 del Base64 comprimido contra los bytes originales antes de subir: `8adc901d0fe83c1b` (principal), `6856d0f89d42cc` (anexo). Este hash de transferencia **no sustituye** la comprobación criptográfica del `.py` recién descomprimido. La repetición local sí reprodujo los archivos exactamente; **no hay prueba independiente en clon limpio por tercero**. Las ejecuciones producen únicamente perfiles sintéticos y estadísticas agregadas.

[Modelo y sus limitaciones](THEORY_AND_DIMENSIONS.md), [prerregistro](PREREG.json), [ledger](LEDGER.json), [informe](REPORT.md).
