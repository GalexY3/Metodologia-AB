# Tarea futura para Codex — NO ACTIVA, NO AUTORIZADA COMO CICLO

**Situación 30/10/2026:** El investigador ha indicado que actualmente no hay Codex disponible; ninguna ejecución externa está encargada. N277–N296 están cerrados con 20/20 plazas consumidas. Guardar esta especificación como referencia para un eventual entorno ejecutor, no interpretarla como nueva autorización N297.

## Objetivos verificables

1. **Reproducibilidad histórica.** Recuperar legalmente y comprobar SHA de `ESBM_ABH_N237_N256_Blossom_60corridas.zip` (`349414236fb7d075e9c024efb7c56faf616fd46d79454963e30db6d832aa144c`). No reintentar búsquedas previas idénticas; si el archivo sigue ausente, registrar `BLOCKED_MISSING_SOURCE`. Preservar el ESBM original SHA `f7e6b84000720cbdf2ee0800c2b10d136185facd00e4622756cbb5f8d8254d0b`.
2. **Contraste diferencial N280.** Investigar pesos float64 cerca de empate, donde las pruebas nuevas n143 mostraron un déficit exacto de **2 y 3 unidades residuales** con NetworkX float frente a matching entero de misma cardinalidad. Diagnóstico Boost independiente posterior coincidió con óptimo entero bajo commit de prereg `2ab26e6de4c781a3795684ead94736f7e8f15c34`. Formular semántica y política explícita de desempate, con oráculo independiente, pruebas exactas de cardinalidad y pesos, y no asumir que dos matching con peso igual tienen mismas aristas.
3. **Robustez Boost.** N290: dos grafos casi completos n144 `flat`/`ulp` excedieron timeout 5 s; comparar backend alternativo exacto y perfilar sin aceptar licencias. El N257 SIGSEGV por stack overflow de Boost en grafo nuevo **no** equivale a reproducción del N242 antiguo.
4. **Paridad original.** Correr el Python ESBM byte-idéntico y el viejo TypeScript original con mismos shocks N144 T16 K7, congelar ambos SHA, conservar todos los eventos individualmente y recuperar primera divergencia; el cierre N277 **solo** compara dos modalidades de matching dentro de una reconstrucción instrumental de Python, no el TS.
5. **Nueva validación humana.** No usar SSJY. Lock5Data SRC112 es Columbia primera cita (no cohorte independiente); Fledge SRC113 son encuestas individuales sobre agentes de IA (sin votos humanos diádicos); Topinkova/Diviak ya está en SRC021/22 y no debe duplicarse. Encontrar datos legalmente utilizables con oportunidades observadas y dos elecciones nativas, y probar predicción diferencial frente a controles competentes. No aceptar condiciones de acceso ni contactar a autores.

## Criterios y límites

Si el investigador autoriza un bloque futuro: contratos A–J y SHA antes de outcomes; estimandos y controles adversariales; recibos por caso, fallos intactos, límites RAM/CPU/tiempo y registro de incertidumbres. Mantener CT2 científica 7/100, STOP_R5 humano, ESBM/SRC104 original, prohibición SSJY, sin licencias, autores, merges a main ni CI costosa.

**Esta tarea es un recordatorio archivado para el futuro, no una acción en segundo plano ni un ciclo nuevo.**