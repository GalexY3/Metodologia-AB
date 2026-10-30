# Mercados de pareja · acceso estable

**Estado verificado 30/10/2026.** Este directorio en `main` es una entrada **documental**, no un merge del historial experimental.

## Última campaña: AB-H PIVOT N277–N296, cerrada

- **20/20 ciclos técnicos ejecutados y 0 plazas pendientes**, con contratos A–J y hashes de código congelados **antes** del primer resultado en commit `4d92e8002bc24af3dfe6009603e1bc95d2b806ca`.
- [Informe completo en main](informes/ABH_N277_N296_20261030.md) · [rama científica y recibos](https://github.com/GalexY3/Metodologia-AB/tree/research/ab-h-esbm-exactness-n277-n296-20261030/proyectos/mercados-de-pareja/research/ABH_N277_N296_20261030).
- **N277:** 60/60 trayectorias sintéticas instrumentadas idénticas entre NetworkX con pesos `float64` y objetivo entero exacto sobre el mismo motor reconstruido. **No es paridad con TS histórico o ejecución directa del ESBM original.**
- **N280:** dos contraejemplos sintéticos n143 con el mismo número de parejas (71): matching float64 pierde **2 y 3 unidades del residuo entero** (no parejas) frente al óptimo exacto, corroborado por Boost en una auditoría post hoc previamente preregistrada.
- **N290:** dos tiempos límite de 5 s de Boost sobre grafos casi completos de pesos planos/ULP. Otros controles de MILP HiGHS y programación dinámica concuerdan en grafos pequeños. Los empates pueden cambiar las identidades de los pares sin cambiar el objetivo.
- **Archivos completos:** `ESBM_ABH_N277_N296_exactness_results.zip` SHA256 `cc8be3d25a1cb158e01a407a347b972dad1d1eb711a1c051eee6f6862e009552`, 30 archivos, Biblioteca `/Mercados-de-pareja/ABH-N277-N296/`; código pre-outcome ZIP SHA256 `8e4e6705954d9d9e864da6ea0b1607f7ca061ec87d1c9e9ede14b951e2a2ba67`. Los ZIP están en Biblioteca, no en este árbol de GitHub.
- **Fuentes y límites:** 113 SOURCES, 34 PRIORS, 201 UPDATES; SRC112 Lock5Data es Columbia reempaquetado, SRC113 Fledge.Love son encuestas individuales, no decisiones diádicas observadas. Sin nuevos microdatos humanos. **CT2 7/100, STOP_R5 humano activo**, grado 0/3, madurez previa 44,10% no reestimada.

## Antecedentes necesarios

- [Informe N257–N276](informes/ABH_N257_N276_20261030.md): 20/20 ejecuciones técnicas, 18 PASS, 2 negativos. Comparación de eventos individuales entre **dos reconstrucciones instrumentales**, no TS original.
- [Informe N237–N256 en rama histórica](https://github.com/GalexY3/Metodologia-AB/blob/research/ab-h-esbm-polynomial-blossom-n237-n256-20261030/proyectos/mercados-de-pareja/research/ABH_N237_N256_20261030/REPORT.md): 60/60 paridad agregada entre Python ESBM original y TypeScript+Boost; histórico N242 SIGSEGV y N246 timeout 12 s; no paridad individual histórica acreditada.
- ESBM original SHA256 `f7e6b84000720cbdf2ee0800c2b10d136185facd00e4622756cbb5f8d8254d0b` y SRC104 **sin alteraciones**.
- [Tareas para Codex archivadas](tareas_codex/README.md) y [propuesta futura no activa](tareas_codex/05_FUTURA_N297_EXACT_MATCHING_Y_DATOS.md). Codex no está disponible por ahora; esas tareas **no están en ejecución**.

**Gobernanza:** sin SSJY, sin aceptación de licencias, sin contactos de autores, sin fusiones experimentales a main ni CI costosa. Cualquier nuevo bloque AB requiere nueva autorización, prerregistro y evidencia nueva; mejorar el software no sustituye verificación humana independiente.
