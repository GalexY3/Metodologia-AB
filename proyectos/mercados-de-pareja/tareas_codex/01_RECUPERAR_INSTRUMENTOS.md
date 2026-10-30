# Tarea Codex 01 · Recuperación forense N237–N256 (NO ES UN CICLO)

**Entrada:** `GalexY3/Metodologia-AB` rama `research/ab-h-esbm-event-parity-n257-n276-20261030`; iniciar contrastando HEAD y `AGENTS.md`, metodología AB3.2.1 O1–O7 y `proyectos/mercados-de-pareja/CURRENT.md`.

**Problema verificado:** existe informe de 60/60 paridad agregada N144/T16/K7 y fallos N242 `SIGSEGV -11` n143, N246 `timeout 12s` n144, pero no la totalidad de las fuentes/fixtures archivados. Archivo de conversación declarado, no presente por ello en GitHub:
`ESBM_ABH_N237_N256_Blossom_60corridas.zip`
SHA256 obligatorio: `349414236fb7d075e9c024efb7c56faf616fd46d79454963e30db6d832aa144c`.

**Acciones:**
1. Buscar únicamente entre archivos locales/adjuntos/herramientas autorizadas disponibles. No afirmar acceso a un chat o ordenador que Codex no tenga; si no existe, terminar `BLOCKED_MISSING_ARCHIVE` indicando cómo aportarlo.
2. Comparar tamaño 138891 bytes, integridad ZIP, enumeración de 110 archivos (según informe); registrar cualquier discrepancia sin reemplazar.
3. Extraer a carpeta separada, con preservación byte a byte, y comparar SHA de cada fichero frente a `proyectos/mercados-de-pareja/research/ABH_N237_N256_20261030/PREREG_AJ_SHA_FREEZE.json`. El original `esbm_dynamic.py` tiene SHA256 `f7e6b84000720cbdf2ee0800c2b10d136185facd00e4622756cbb5f8d8254d0b`.
4. Determinar si hay fixtures completos `N242`, `N246`, fuentes Boost C++, runner, scripts TS, generadores y 30 hashes de shocks y recibos por ciclo. Diferenciar `PRESENT_AND_HASH_VERIFIED`, `REGENERABLE_AND_SHA_CHECKED`, `MISSING`, `MISMATCH`.
5. Generar manifiesto JSON inmutable con `path`, `size_bytes`, `sha256`, `expected_sha256`, `provenance` y resultado. Registrar herramienta, versiones y ubicación de archivo, sin publicar datos privados.
6. Guardar informe y manifiesto en nueva subcarpeta de `research/ABH_N257_N276_20261030/` de la rama científica, nunca en el código original. Preparar puerta A–J para N257 y N258 pero **no ejecutar ni consumir plazas** en esta tarea.

**Aceptación:** listado verificable de artefactos y hashes, constancia explícita de material ausente y primer comando reproducible para N257/N258; 20/20 plazas pendientes. Si no se recupera el ZIP, resultado bloqueado, no supuesto PASS.

**Seguridad:** sin SSJY, aceptación de licencias, contactos, merges, cambios a ESBM/SRC104 ni CI costosa. CT2 7/100; STOP_R5 humano.