# Reproducir V204

Registro prospectivo inmutable: f8e9a55263584cfbd6248917b7c533d71af0a14a. Las once fuentes con hashes más el manifiesto están en `research/V204_20261116/registered_sources/`. Python 3.12.16, NumPy 2.5.4, SciPy 1.18.1, Numba 0.68.0, Torch 2.11+cu128; el cálculo se hizo en CPU float64. Respetar hashes y conservar también el recibo `V204_REGISTRATION_RECEIPT.json`.

En un directorio nuevo, copiar las fuentes con sus rutas relativas y ese recibo. Definir OPENBLAS_NUM_THREADS=2, OMP_NUM_THREADS=2 y MKL_NUM_THREADS=2 antes de iniciar Python. `run_v204_lola.py` valida hashes y exige que su carpeta de salida no exista. El helper de recursos contiene la afinidad específica del equipo original; cualquier portabilidad a otro equipo se adapta explícitamente y se registra, sin hacer pasar la adaptación por fuente idéntica.

Ejecutar `python run_v204_lola.py`: diez trayectorias y dos precisiones, eta=20 fijo, sin barrido. El script conserva fallos y su último argumento RHS, que no debe confundirse con un checkpoint aceptado por el integrador. Los resultados originales terminaron todos con código 0 y H1 FAIL. No volver a registrar esta campaña como prospectiva tras conocer el resultado.

Auditoría: `audit_v204_opponent_gradient.py` comprueba derivadas en puntos técnicos; `prepare_v204_node_audit.py` genera entrada y fuente JavaScript a partir del evaluador independiente V203, que se incluye junto al de V202. Ejecutar Node después de la preparación. Los scripts rechazan sobrescribir resultados de auditoría.

Diagnóstico posterior: ejecutar `v204_posthoc_gradient_decomposition.py` y `certify_v204_uniform_payment.py` en la copia fresca. La fórmula no forma parte de H1. Para la síntesis/figuras, añadir Matplotlib, la SUMMARY EPG V203 incluida como control y ejecutar `analyze_v204_lola.py`. La fuente matemática íntegra está en `V204_CLOSED_FORM_PAYMENT_GRADIENT.md`.

El paquete conserva fuentes, NPZ, JSON, logs y auditorías. Su verificación HTTP no es una nueva reproducción de todas las integraciones ni confirmación externa. No se ha afirmado que otro investigador o equipo haya confirmado el mecanismo.
