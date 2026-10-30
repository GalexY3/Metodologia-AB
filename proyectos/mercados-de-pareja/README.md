# Mercados de pareja · entrada estable

**Estado final verificado: 30/10/2026.** Esta página es documentación publicada en `main`, **no** un merge de ramas de investigación. Evidencia humana de validación causal **no** aportada.

## Última campaña AB-H N297–N316 · 20/20 cerrados

[Informe N297–N316](informes/ABH_N297_N316_20261030.md) · [Rama científica, prerregistros y ledgers](https://github.com/GalexY3/Metodologia-AB/tree/research/ab-h-esbm-robust-exact-n297-n316-20261030/proyectos/mercados-de-pareja/research/ABH_N297_N316_20261030).

- 20 ciclos técnicos realmente ejecutados, 0 excepciones del runner, **0 plazas disponibles**. Contratos A–J y seis hashes congelados antes de resultados: commits `ab43890677b27a8f3848263ad8f8baf27fd365ba`, `e3896d8a252e3448cf4521cb8d8f9fa32caa7e3b` y `7495312512fbcfd9f48cdb05588ae74a10b555d9`. **Ejecutado no equivale a PASS:** se registran crashes, timeouts y contraejemplos.
- Nuevo fallback seguro en controles probados: Boost C++ intenta el matching; ante `SIGSEGV`/timeout/objetivo incompatible se conserva solución de `NetworkX` con **pesos enteros exactos**. N297 reprodujo `SIGSEGV -11` del fixture sintético n143 N25704, no el antiguo fixture N242; N298–N300 tres timeouts de 1 s Boost en nuevos grafos planos/ULP.
- **Cinco de cinco** grafos pequeños n18 comparados entre NetworkX, MILP HiGHS en dos fases y DP obtuvieron objetivo idéntico. N310 observó **3/6** nuevos grafos n143 de casi-empates donde el float quedaba 2,1,2 unidades residuales por debajo del objetivo entero, sin diferencia de cardinalidad. La proporción corresponde solo a grafos adversariales, no a personas.
- N316: el orden original de aristas provoca caída `-11` de Boost en el fixture N25704; invertirlo devuelve resultado óptimo de cardinalidad 71 y objetivo entero 15.407, pero con parejas distintas. Diagnóstico adicional registrado antes de repetir; no corrige universalmente Boost.
- **Original Python ESBM ahora recuperado y verificado byte a byte**: SHA256 `f7e6b84000720cbdf2ee0800c2b10d136185facd00e4622756cbb5f8d8254d0b`. Auditoría adicional preinscrita en `3f1bedbf8d27528f28b8a36391b15678d1e4584f`: ejecución original directa 60/60 casos N144/T16/K7, 960 ticks, 0 diferencias de parejas seleccionadas, cinco campos del track y seis agregados respecto a reconstrucción. **No** se capturaron todos los eventos dirigidos nativos originales y **no** se recuperó ni ejecutó el TypeScript histórico.
- Archivo de resultados e instrumentos: `ESBM_ABH_N297_N316_RESULTS_AND_AUDITS.zip` SHA256 `559e49f762033b1e8027cbf49e9a9f6d998bc78b48811039bc2f8ff3525a96dd`, 36 archivos, Biblioteca `/Mercados-de-pareja/ABH-N297-N316/`. Código antes de outcomes: ZIP SHA256 `5df54b85ccb3ef4bb2c568ec4a665ac07032dd9e3941108f2cb20e689dabe55b` (6 fuentes/binario).
- **114 SOURCES, 34 PRIORS, 204 UPDATES**. SRC114, Echenique et al. 2025, es estudio humano de matching **no romántico**, solo rival teórico/comparativo. No se le atribuye validación ESBM. **CT2 científica 7/100, STOP_R5 humano activo, grado humano nuevo 0/3**. Madurez 44,10% anterior **no reestimada**.

## Historia reciente y trabajo futuro

[Informe N277–N296](informes/ABH_N277_N296_20261030.md) · [Informe N257–N276](informes/ABH_N257_N276_20261030.md). El ESBM y SRC104 originales permanecieron intactos; no SSJY, licencias aceptadas, contacto de autores ni CI costosa. [Tareas para Codex archivadas](tareas_codex/README.md), incluida la [futura especificación inactiva](tareas_codex/06_FUTURA_N317_COHORTES_Y_MATCHING.md); **Codex no está autorizado ni disponible hasta nuevo aviso**. Nuevas plazas AB requieren autorización adicional y resultados realmente independientes para superar R5. No mezclar estabilidad estratégica con solución centralizada de peso máximo por equivalencia implícita.
