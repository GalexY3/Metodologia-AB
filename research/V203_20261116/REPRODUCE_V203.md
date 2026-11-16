# Reproducir V203

Registro anterior a integraciones: a73932856b9f88d27b166f3d0abc74be3dd154bb. Las fuentes inmutables están en `research/V203_20261116/registered_sources/`. El manifiesto contiene hashes y versiones (Python 3.12.16, NumPy 2.5.4, SciPy 1.18.1, Numba 0.68.0). Los archivos de evidencia posteriores no reemplazan ese registro.

En un directorio nuevo, copiar las fuentes manteniendo sus rutas relativas y `V203_REGISTRATION_RECEIPT.json`. Verificar hashes del manifiesto; instalar NumPy, SciPy y Numba en un entorno aislado. `research_resource_limits.py` fija BelowNormal, seis CPU lógicos y dos hilos Numba en este equipo. En otra máquina revisar su afinidad antes de ejecutar, registrando cualquier adaptación como tal. Definir OPENBLAS_NUM_THREADS=2, OMP_NUM_THREADS=2 y MKL_NUM_THREADS=2 antes de iniciar Python.

Ejecutar `python run_v203_exact_flows.py`. El runner rechaza una carpeta de resultados existente y valida todos los hashes. Produce 20 NPZ de sensibilidad y cuatro NPZ de precisión, sus JSON y SUMMARY. No reutilizar las carpetas originales ni repetir el registro prospectivo como si aún no se conocieran sus resultados.

Auditoría posterior: copiar `prepare_v203_node_audit.py`, `analyze_v203_exact_flows.py` y la fuente inmutable `validation_node/v202_independent_audit.cjs` (SHA256 e3130a034e71e072102c0bf74c333475d4d7ec54199dc6a58e1eef255118c65b). Ejecutar la preparación, `node validation_node/v203_independent_audit.cjs` y el análisis. Estos scripts también rechazan sobrescribir sus resultados. Matplotlib solo es necesario para la figura. Las verificaciones deben repetirse sobre una copia fresca si se desea nueva evidencia de reproducción.

La evidencia publicada incluye los estados y los datos de entrada de la auditoría JavaScript. Esa auditoría terminó aquí con código 0 y es una segunda implementación interna, no una réplica externa del programa científico. No se ha afirmado una reproducción nueva de todos los flujos en una máquina distinta.
