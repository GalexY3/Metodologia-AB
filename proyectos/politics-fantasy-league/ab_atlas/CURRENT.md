# AB Atlas — Politics Fantasy · CURRENT (26-10-2026, rama de investigación)
- **Rama activa:** `research/pfl-abh-branch20-20261026`, basada en `main` (Atlas 0.3). El estado de `main` NO ha sido modificado por este bloque.
- **Modo:** AB-H; AB-R (contrastes de fuentes/identidades) y AB-P (código de guarda) diferenciados.
- **Último lote:** `PFL_ABH_BR20_20261026_R5`; archivo `updates/0001-abh-br20-20261026.json`, `parent_batch=""`. Seed intacto; visor HTML sigue siendo snapshot anterior.
- **Campaña:** 20 BRANCHING nuevos autorizados; **C01-C04 ejecutados y cerrados; 16 sin gastar** (STOP_R5 por insuficiencia de nueva evidencia original). [Ledger](../research/ABH_BR20_20261026/CAMPAIGN.json) · [Informe](../research/ABH_BR20_20261026/REPORT_FINAL.md).
- **Antecedente:** AB20B 20/20 completados documentados en PR #15 (DRAFT, NO merge). AB20 previo 20/20 según informe final aunque su ledger antiguo quedó en 12/20; no contabilizar dos veces.
- **C01:** recurso JSON institucional de todas las legislaturas referenciado en catálogo pero no descargable en este entorno (CACHE_MISS): existencia de ID estable, NO VERIFICADA.
- **C02:** Rufián `XIV:187` vs `XV:312` y Díaz `XIV:171` vs `XV:342` en composiciones del Congreso. Dos casos predefinidos de códigos cambiantes; no adjudican crosswalk universal ni tasa poblacional. 
- **C03:** Ministerio del Interior ofrece procedimientos SIA 992323/992324/992320, pero no se obtuvo ficha registral original; partido legal ≠ candidatura ≠ grupo.
- **C04:** `typed_refs.py` importado de AB20B y seis pruebas locales de staging PASS; **sin integración HTTP, clon limpio ni CI**. Scoring de personas reales deshabilitado.
- **AB-P:** demo sintética en localhost. Índice contractual PFL-V1 rev.3 **36,35%**, sin cambio; **seis puertas de lanzamiento pendientes**, ninguno acreditado.
- **AB-R:** CT2 identidad **29/100** (ordinal); VSDS **1/3**, N1/N2/N3 científicos nuevos = 0. No inferir descubrimiento de tests locales.
- **Complaints:** tres abiertas registradas en el delta; dificultad de obtención del export, registro jurídico sin evidencia adquirida, guardia no conectada.
- **Validación Atlas:** preflight en memoria de IDs/edges/referencias sobre seed real PASS; **`atlas_delta.py check` pendiente de ejecución local sobre checkout real**. No declarar validez total de lote hasta hacerlo.
- **Coste:** commits con `[skip ci]`; cero GitHub Actions solicitadas. No crear PR automática que reactive CI sin revisar minutos disponibles.

**Para reanudar:** comprobar autorización 16 pendiente y ultimo delta; obtener nueva evidencia discriminante (ficha RPP de fuente primaria, ID longitudinal/crosswalk adjudicado y cronología `effective_at`/`first_public_at`), comprobar permisos de uso; después AB-P puede integrar guards y medir funcionalidad/safety con CI cuando presupuesto permita. Si no llega fuente, preservar STOP_R5. No regenerar HTML sin necesidad.
