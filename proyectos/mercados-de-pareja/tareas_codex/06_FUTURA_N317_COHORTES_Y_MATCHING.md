# Tarea futura para Codex · No activa · Sin presupuesto AB concedido

Fecha 2026-10-30. N297–N316 se completó **20/20 ejecuciones técnicas** sin Codex, con saldo **0**. El investigador ha prohibido utilizar Codex hasta nueva comunicación; **no iniciar ni encargar trabajo** a un ejecutor externo. Este documento solo conserva necesidades para una eventual reactivación o un nuevo bloque expresamente autorizado.

## Necesidades validadas al cerrar N297–N316

**Bloqueo de software original:** se recuperó el Python ESBM original SHA256 `f7e6b84000720cbdf2ee0800c2b10d136185facd00e4622756cbb5f8d8254d0b` y se ejecutó directamente en 60/60 escenarios, 960 ticks, 0 discrepancias en conjuntos de parejas y cinco métricas por tick frente a reconstrucción (auditoría posterior preregistrada en `3f1bedbf8d27528f28b8a36391b15678d1e4584f`). **No** se recuperó el TypeScript histórico ni se obtuvo paridad de todos los eventos dirigidos desde el Python original. Encontrar los bytes del ZIP N237–N256 (SHA256 `349414236fb7d075e9c024efb7c56faf616fd46d79454963e30db6d832aa144c`) solo si su procedencia/permiso es verificable, sin repetir indefinidamente accesos fallidos.

**Matching exacto:** N310 mostró 3/6 casos adversariales nuevos n143 donde el objetivo float64 quedó 2,1,2 unidades del residuo entero por debajo del máximo, aunque cardinalidad idéntica; documentar política de empate y coste de solver robusto. N316 observó Boost `SIGSEGV -11` en orden original del fixture sintético N25704 y solución **óptima** al invertir aristas. Debe determinarse la causa sin asumir que el fallo histórico N242 es idéntico. `robust_solver.py` intenta Boost y hace fallback a NetworkX int verificado para grafos probados, no aporta certificado de optimalidad universal externo n144. Oráculos independientes MILP/DP ejecutados solo hasta n18.

**Evidencia humana R5:** SRC114 Echenique/Robinson-Cortés/Yariv 2025 describe mercado de laboratorio de ofertas/aceptaciones humanas y oportunidades completamente conocidas, **no elección de pareja romántica**. Paquete de replicación enlazado por autores pero archivos/derechos de reutilización no inspeccionados. Buscar una fuente realmente independiente con elegibilidad/oportunidades observadas y dos decisiones nativas romanticas; no SSJY, no licencias aceptadas, ni contacto de autores. No usar SRC114 como validación romántica por analogía.

## Criterio de aceptación futuro, si la persona autoriza

Verificación de derechos, SHA y metadatos por archivo antes de cualquier dataset nuevo; preregistros completos A–J y hashes congelados antes de outcomes; comparador competente, reglas de paridad de datos, fallos y límites CPU/RAM/timeout; actualizar SOURCES/PRIORS/UPDATES; conservar ESBM/SRC104 y STOP_R5 humano, CT2 científico 7/100 hasta evidencia independiente. Sin merges experimentales a main ni CI costosa.

**Estado: ARCHIVED / NOT ASSIGNED / NO CODEX.**
