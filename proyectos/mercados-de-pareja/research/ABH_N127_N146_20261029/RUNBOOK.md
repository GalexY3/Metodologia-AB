# Reproducibilidad — AB-H N127–N146

**Archivo completo de esta conversación**: `mercados_pareja_ABH_N127_N146_codigo_resultados.zip` (51.366 bytes; SHA256 `6f0d24e5fd51ed9b48c2502a8da17a08e770714631717ca1a5e809dd8dbfd9df`). Incluye un manifest verificable, cuatro recibos JSON completos por semilla, cinco archivos código propio con módulos de soporte, el original ESBM v2 inalterado, control antiguo y resultado post hoc, README. **No se ha subido este ZIP binario al repositorio GitHub**; el enlace de descarga está en el chat que originó el trabajo. No inventar URL GitHub del ZIP.

**Código versionado bajo esta rama:** `esbm_event_engine.py` (motor explícito, SHA256 final `5c850182407c9a450060b2ba93a0f36142fb887848447472271457d713b269bb`), `social_graph.py` (control antiguo **sensible a etiquetas**), `social_graph_equivariant.py` (reparación rank-canonical), `mini_world.py`, `run_A.py`, `run_B.py`, `run_C.py`, `run_D.py`.

El simulador original es `../ABR_ESBM20_20261028/esbm_dynamic.py` SHA256 `f7e6b84000720cbdf2ee0800c2b10d136185facd00e4622756cbb5f8d8254d0b`. Debe colocarse **sin modificaciones** en la misma carpeta que los scripts en el entorno de ejecución. Al importar el motor nuevo, su SHA es comprobado y rechazará una fuente distinta.

**Entorno realmente usado:** Python 3.13, NumPy 2.3.5 y NetworkX 3.6.1. De Python se ha verificado reproducibilidad en un segundo proceso con otra carpeta de fuentes **pero con las mismas bibliotecas instaladas y mismo sistema operativo**. No hay validación clean-room independiente de entorno operativo.

```bash
# Desde el directorio que contiene los scripts nuevos:
cp ../ABR_ESBM20_20261028/esbm_dynamic.py ./esbm_dynamic.py
python -m pip install numpy==2.3.5 networkx==3.6.1
python run_A.py
python run_B.py
python run_C.py
python run_D.py
```

Los runners generan `RESULTS_A/B/C/D.json`. Los resultados de etapas y contrastes se preservaron con semillas y registros completos. Los archivos JSON contienen tiempos de ejecución en segundos, por lo que al regenerarlos los SHA de *bytes exactos del documento* pueden diferir. Los controles relevantes son igualdad de salidas simuladas/estadísticos, series, IDs, riesgos y shocks; se recomienda eliminar las claves `seconds`, `elapsed_seconds` al comparar nuevas ejecuciones con recibos originales. Los SHA exactos originales de A–D figuran en [RESULTS_INDEX.json](RESULTS_INDEX.json).

La ejecución `python posthoc_canonical_audit.py` genera `POSTHOC_CANONICAL_RESULTS.json` (comparador corregido) y es **post hoc, 0 ciclos**; NO sustituye a las corridas preregistradas N133–N141.

**Limitación adversarial crítica:** N144 detectó que el viejo `social_graph.py` para `rewired` dependía del orden de identificadores de actor. Los ciclos previos que lo compararon con `ring` permanecen en el registro por integridad y no se reclaman como contraste de topología libre de artefactos. El nuevo generador se verificó en 40/40 grafos y 8/8 decisiones de exposición bajo relabeling. Los tests no son prueba externa de una teoría sobre personas.

**Reglas:** no usar SSJY, no aceptar licencias ni contactar autores, no modificar SRC104, no merge a main, sin datos humanos nuevos. **CT2 científico 7/100, R5 externo STOP.**
