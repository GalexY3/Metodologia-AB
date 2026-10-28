# Cómo reproducir 60 corridas del ESBM v2

La fuente Python íntegra [esbm_dynamic.py](esbm_dynamic.py) se archivó después de un **freeze SHA anterior a la primera ejecución**, conservando el archivo original exacto. Requisitos: Python 3.10+, `numpy` y `networkx` (versiones usadas: numpy 2.3.5, networkx 3.6.1; el simulador anterior requería scipy, este nuevo no).

```bash
python esbm_dynamic.py
```

Genera `RUNS.json` (60 recorridos con estados temporales), `SUMMARY.json` (10 escenarios con estadísticos de 6 seeds), `SUMMARY.csv` y `QA.json`. `PAIRED_CONTRASTS.json` fue calculado posteriormente, **sin modificar la simulación**, usando `build_audit.py`, disponible en el ZIP descargable de la conversación.

Reproducir la salida por semilla guardada en el repositorio:

```python
import base64, gzip
from pathlib import Path
p = Path("RUNS.json.gz.b64")
Path("RUNS.json").write_bytes(gzip.decompress(base64.b64decode(p.read_text().strip())))
```

Comparar hashes:

```bash
sha256sum esbm_dynamic.py RUNS.json SUMMARY.json
```

Valores esperados:
- `esbm_dynamic.py`: `f7e6b84000720cbdf2ee0800c2b10d136185facd00e4622756cbb5f8d8254d0b`.
- `RUNS.json`: `ae6ea50be7bd36d1a4aa5b637f4048205742ea6ae228654ef759332a07bd4c67`.
- `SUMMARY.json`: `e0f04f702fec3ea58f029eb8b056949d039272c120aea38a1b3c8ca895b8c197`.

El programa se ejecutó dos veces sobre el mismo equipo y produjo resultados **idénticos byte a byte**. Esto es reproducibilidad interna, no verificación independiente por tercero. La metodología, contrafactuales y limitaciones se describen en [THEORY_V2.md](THEORY_V2.md), [REPORT.md](REPORT.md), [PREREG.json](PREREG.json), [LEDGER.json](LEDGER.json).

**Importante:** los 144 agentes, sus identidades/compatibilidad, parámetros de riesgo, preferencias y políticas son **completamente sintéticos**, no microdatos de población. Las relaciones simuladas no son relaciones reales ni observaciones de bienestar. La muestra de parejas activas al final está censurada a derecha: no calcular esperanza de duración humana con el promedio de rupturas observadas.
