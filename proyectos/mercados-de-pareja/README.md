# Mercados de pareja · acceso estable y estado verificable

**Actualizado 30/10/2026.** Este directorio en `main` es una **entrada documental, no un merge de la investigación**. Código fuente original, instrumentos, ledgers y resultados científicos continúan en ramas controladas. No usar el número de pruebas como validación sociológica.

## Campaña vigente cerrada: AB-H N257–N276

- **20/20 ciclos ejecutados, 18 PASS técnicos, 2 negativos válidos (N257/n143 y N258/n144), 0 pendientes.** Primeros intentos N259–N263: 5 fallos instrumentales de guardado, preservados y repetidos después de registrar reparación prospectiva. No se contabilizaron como plazas extra.
- **[Informe de cierre publicado en main](informes/ABH_N257_N276_20261030.md)**. [Informe canónico y preregistro de investigación](https://github.com/GalexY3/Metodologia-AB/tree/research/ab-h-esbm-event-parity-n257-n276-20261030/proyectos/mercados-de-pareja/research/ABH_N257_N276_20261030).
- **[Índice de recibos SHA](https://github.com/GalexY3/Metodologia-AB/blob/research/ab-h-esbm-event-parity-n257-n276-20261030/proyectos/mercados-de-pareja/research/ABH_N257_N276_20261030/RESULTS_INDEX_GITHUB.json)** y **[ledger completo A–J](https://github.com/GalexY3/Metodologia-AB/blob/research/ab-h-esbm-event-parity-n257-n276-20261030/proyectos/mercados-de-pareja/research/ABH_N257_N276_20261030/LEDGER_AJ_POSTOUTCOME_GITHUB.json)**. El código/hash A–J fue congelado antes de outcomes: commit `474cdae1cf04bf89912f7c6fa4f961bbe14c4483`.
- 60/60 comparaciones de **eventos dirigidos y parejas** a lo largo de 960 ticks entre **dos motores Python instrumentales** (uno usa NetworkX, otro Boost C++). **NO** se compararon bytes/trazas del antiguo TypeScript histórico ni se obtuvo el ZIP anterior. Las igualdades no demuestran unicidad de matching o portabilidad.
- **Fallos conservados:** n143 near-tie `SIGSEGV -11`; n143 plano timeout 4 s; n144 plano/near-tie timeout 5 s. Un ASan posterior preregistrado detectó `stack-overflow` en la ruta Boost `retrieve_augmenting_path` para un grafo **nuevo**, no el antiguo N242.
- N270: objetivo invariante en 6/6 comparaciones de permutación, pero **4/6 cambiaron la identidad de las aristas** en casos empatados/casi empatados; coincidencia de objetivos no equivale a paridad de parejas.
- **Archivo íntegro**: `ESBM_ABH_N257_N276_event_parity_results.zip` SHA256 `e0263af4ac85073b1ccbd8a32a4d9dc460b29f89147d765c20eaf2c90554bd5d`, 161 archivos, en Biblioteca del investigador `/Mercados-de-pareja/ABH-N257-N276/`. La Biblioteca no equivale a alojamiento en GitHub.
- [Tareas para Codex históricas archivadas](tareas_codex/README.md). **Actualmente no hay Codex ni encargos externos activos**.

## Punto de partida histórico y garantías

- [Cierre anterior N237–N256](https://github.com/GalexY3/Metodologia-AB/blob/research/ab-h-esbm-polynomial-blossom-n237-n256-20261030/proyectos/mercados-de-pareja/research/ABH_N237_N256_20261030/REPORT.md): 60/60 **resultados agregados** N144 T16 K7 con original Python y réplica TypeScript+Boost, pero no eventos individuales verificados; N242 `SIGSEGV` y N246 timeout 12 s en adversariales originales no reproducidos en esta campaña por ausencia de ZIP exacto.
- ESBM original SHA256 `f7e6b84000720cbdf2ee0800c2b10d136185facd00e4622756cbb5f8d8254d0b` y evidencia humana SRC104 **intactos**. **111 SOURCES, 34 PRIORS, 197 UPDATES** (U197 `NO_CHANGE_WITH_REASON`). Madurez previa 44,10% **no reestimada**.
- **CT2 científica 7/100; STOP_R5 humano activo, grado humano nuevo 0/3**. Sin sujetos nuevos ni validación causal, sin SSJY, licencias aceptadas, contacto de autores, fusiones experimentales ni CI costosa.

Esta entrada no modifica retroactivamente los resultados o contratos A–J del proyecto. Cualquier campaña posterior requerirá consentimiento/alcance propios y evidencia diferenciadora.
