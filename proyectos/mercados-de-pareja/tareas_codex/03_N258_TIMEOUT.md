# Tarea Codex 03 · N258: timeout adversarial N246 n144

**Dependencia:** tarea 01 y fixture N246 reconstruido con SHA exacto. De lo contrario `BLOCKED_MISSING_FIXTURE` (sin gastar N258).

**Pregunta A:** ¿el timeout de 12s en grafo casi completo n144 procede del coste algorítmico del backend Boost concreto, sobrecarga por subprocess/serialización, pesos degenerados, un bucle patológico o recursos del host? No deducir complejidad efectiva solo de la documentación O(V³).

**Diseño A–J y código congelados antes de outcomes:** falsador = salida incorrecta, segfault, límite de recursos o divergencia; comparadores = NetworkX max_weight_matching maxcardinality y alternativa exacta de uso legítimo instalada/verificada, sin instalar software bajo licencia no aceptada. Definir límites observacionales de CPU, wall-clock y RSS, puntos de perfilado, semillas, fixture, hashes, toolchain y arquitectura. Predefinir cómo tratar censura por timeout.

**Ejecución:** línea base fixture original, registrar etapas parse/construcción/matching/serialización y wall-clock; por etapas registrar pico RSS, host/compilador, código de retorno y versión Boost. Perturbar un único factor por prueba (densidad, n par/impar, pesos, degeneración, cardinalidad), siempre preservando baseline intacto. Guardar perfilado adversarial y primera divergencia. Reparaciones requieren freeze prospectivo nuevo.

**Criterio de aceptación:** diagnóstico con trazabilidad y al menos comparación exacta competente o razón verificable de imposibilidad; resultados negativos preservados. El presupuesto no se consume por una propuesta no ejecutada. Mantener STOP_R5 humano, CT2 7/100, ESBM/SRC104 intactos.