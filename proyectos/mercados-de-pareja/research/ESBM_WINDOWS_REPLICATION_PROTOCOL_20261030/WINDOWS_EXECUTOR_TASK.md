# TAREA CONCRETA PARA EJECUTOR WINDOWS · ESBM independiente · AÚN NO AUTORIZADA PARA EJECUTAR

**Modalidad:** especificación/ticket de implementación. Preparado 2026-10-30, **sin ejecutar** simulaciones, tests de la implementación, instaladores ni accesos al PC del usuario. No es un ciclo AB nuevo. El ejecutor real solo puede comenzar tras un nuevo mensaje explícito autorizando el trabajo concreto y el presupuesto requerido.

## Ticket W-ESBM-01 — implementación y validación separada

**Objetivo:** construir en Windows 10/11, con Node.js 22+ LTS / TypeScript o Rust, un motor nuevo que reproduzca **trayectorias** del original Python ESBM v2 desde matrices de shocks congeladas, no un script que importe el original ni uno que solo recalcula resumen. Un segundo ejecutor humano/Codex en Windows ha de documentar sistema real, versión runtime, librerías y checksums; no confiar en un campo OS ficticio del JSON.

**Repositorio privado** `GalexY3/Metodologia-AB` rama de referencia `research/esbm-independent-replication-spec-20261030`. Es descendiente de `research/ab-h-esbm-r5-replication-gates-20261030` @ HEAD `58e2b09800aca306013bd4bfb81d9d7f678b4fda`. **NO crear rama de ejecución ni tests efectivos en esta fase de protocolo**. Archivo de autoridad fuente `proyectos/mercados-de-pareja/research/ABR_ESBM20_20261028/esbm_dynamic.py` Git blob `5fc9f63fd44ff81ce9ff6c900ba6bf24153356f2`, SHA256 `f7e6b84000720cbdf2ee0800c2b10d136185facd00e4622756cbb5f8d8254d0b`.

**Material de la tarea:** [SPEC.md](SPEC.md), [UNIT_INPUTS.json](UNIT_INPUTS.json), [REFERENCE_PLAN.json](REFERENCE_PLAN.json), [ACCEPTANCE_MATRIX.md](ACCEPTANCE_MATRIX.md), [FREEZE_INDEX.json](FREEZE_INDEX.json). Los casos `UNIT_INPUTS.json` son **manuales y no ejecutados**; el ejecutor debe tratarlos como hipótesis de un verificador aún no probado contra el Python original parametrizado. Si no coinciden con el código original, registrar `SPEC_OR_FIXTURE_ERR` antes de corregir.

### Entregables del futuro ejecutor

1. `windows-replica/package.json` (package-lock y licencias verificadas), `tsconfig.json`, `src/{compatibility,selection,decision,state,matching,metrics,cli}.ts` (o los equivalentes Rust). Un solver general de **matching ponderado de máxima cardinalidad** propio o dependencia autónoma permisivamente licenciada, **no** greedy y no Python/NetworkX/puente Python; indicar si es traducción de algoritmo publicado o módulo de tercero.
2. **Interfaz de entradas**: `people_<seed>.json` (tipos y q binary64) y cinco tensores `float64LE` C-order `[t,i,j]` con manifiesto SHA256, tal como `REFERENCE_PLAN.json`; no mezclar versión historical con symmetric_pair.
3. **CLI contractual a implementar, no existente ahora**:
   - `node ./dist/cli.js lint-fixtures --fixtures ./fixtures/UNIT_INPUTS.json --out ./evidence/unit.json`
   - `node ./dist/cli.js replay --inputs ./frozen_inputs --scenarios ./fixtures/REFERENCE_PLAN.json --trace-dir ./evidence/traces --out ./evidence/runs.json`
   - `node ./dist/cli.js diff --expected ./reference/RUNS.json --actual ./evidence/runs.json --out ./evidence/first_divergence.json`.
   Estos son **comandos de aceptación futuros**, no se afirma que `dist/cli.js` exista ni que se hayan lanzado.
4. **Artefactos de evidencia** por ejecución: `environment.json` capturando `node --version`, `process.platform=win32`, `os.release()`, CPU/arquitectura, dependencias y lockfile; `git rev-parse HEAD`, `Get-FileHash ... -Algorithm SHA256`, `input_manifest.json`, `source_manifest.json`, `unit.json`, `runs.json`, `stage_trace.jsonl`, `first_divergence.json` incluso si FAILED, `REPORT.md` y ZIP/manifiesto de integridad con SHA256.
5. **Bitácora de procedencia y riesgo**: `clean_clone_verified`, `independent_implementation:true/false` con detalles, `independent_OS:true/false` sustentado en ejecución; `matching_ties` explícitos; no afirmar certificación por solo correr Node en Linux.

### Preparación de Windows: instrucciones destinadas al futuro ejecutor (NO realizadas aquí)

```powershell
# Con permisos del propietario del repositorio privado.
git clone https://github.com/GalexY3/Metodologia-AB.git
cd Metodologia-AB
git switch research/esbm-independent-replication-spec-20261030
git rev-parse HEAD
Get-FileHash .\proyectos\mercados-de-pareja\research\ABR_ESBM20_20261028\esbm_dynamic.py -Algorithm SHA256
node --version
npm --version
```

Tras comprobar el SHA original, **no ejecutar simulaciones** hasta que el usuario conceda la fase de ejecución con un prereg A–J y fuente SHA congelados. El ejecutor puede escribir software independiente a partir de SPEC, pero no debe descargar microdatos humanos, aceptar términos, activar CI cara, modificar ESBM, reescribir resultados pasados, ni fusionar PR.

### Secuencia de pruebas futura, con puertas

**P0 (preparatoria, no científica):** el nuevo código compila limpiamente en Windows; generador y solver no importan Python/NetworkX; `GET SHA256` coincide con referencia; 12 fixtures *manualmente derivados* son evaluados (UT12 empate diagnóstico, no exact pair). Si fixture incorrecto, bloquear y registrar discrepancia, no cambiar ambos lados sin revisión.

**P1 (determinista sin RNG):** seis ficheros de atributos y cinco tensores por seed se producen desde el original por un oráculo controlado, sin revelar outcomes; hashes congelados GitHub ANTES de que nueva implementación los consuma. Comparar eventos ordenados y estado tick-by-tick en escenarios **sin óptimos empatados**. Para empates múltiples reportar margen e identificar las soluciones óptimas, no sobreajustar al desempate accidental de NetworkX. Borrar dependencia de Python para ejecución de la réplica.

**P2 (historical 60)**: solo **con autorización futura** reproducir los seis seeds × diez escenarios del original y contrastar primero eventos, luego tick y resumen. El histórico `RUNS.json.gz.b64` ya existe y no fue prospectivamente ocultado; la independencia exige declarar si el autor vio esa salida antes de congelar su código. Exigir 60/60 en enteros y eventos salvo empates diagnosticados, tolerancias de `SPEC.md` para floats. NO reclasificar empate o diferencia numérica que cambia outcome como PASS.

**P3 (reproducción independiente real):** guardar comprobante de ejecución en Windows, runtime y máquina/CPU; si se usa VM sobre host Linux, explicitarlo, no inferir otra máquina. Reproducir como mínimo una tanda limpia posterior a freezes. Opcionalmente segundo host distinto, pero no proclamar validación externa humana.

### Principales falsadores

- Eligibilidad diferente F/M/X + scopes; confundir `FM_only` con `general`.
- Tick con disolución después de exposición en lugar de antes; diferencias de duración/censura.
- Gumbel top-k ordenado DESC en vez de orden `np.argsort(scores)[-kk:]`, alterar feedback/seen durante el tick.
- Respuesta por `u_reply[t,i,j]` en vez de **`u_reply[t,j,i]`**, o tratar respuesta como voto independiente sí/no.
- Emplear `private_bias`/reputación del receptor equivocado; actualización diferida en vez de inmediata.
- Seleccionar peso máximo con una pareja cuando dos parejas maximizan cardinalidad, usar greedy o emparejar no elegibles.
- Tratar `u_hazard[t,i,j]` y `u_match[t,min,max]` como shocks simetrizados en modo historical.
- Empates genuinos: no condenar un emparejamiento igualmente óptimo, ni ocultar que puede alterar la trayectoria futura. Sin regla común, la prueba de paridad completa queda **INDETERMINADA_POR_TIE**.
- Forzar igualdad de RNG entre `np.default_rng` y JS `Math.random`, mezclar N24/T4 optativo con N144/T16 histórico, o comparar solo media/Gini.

**Criterios de aceptación escritos:** (i) hash original correcto; (ii) firma de nuevo código antes de outputs; (iii) 12 fixtures clasificadas con evidencia, sin inventar validación Python; (iv) 60/60 trayectorias con mismos shocks, reportes completos y optimizadores únicos, admitiendo ties solo como discrepancia *explicada y acotada*, no como prueba de equivalencia universal; (v) stocks y métricas exactas según `ACCEPTANCE_MATRIX.md`; (vi) evidencia de Windows real y control de independencia; (vii) cero modificación de los módulos originales; (viii) reporte de TODAS las diferencias. Ante cualquier fallo bloqueante, declarar `STOP_REPRODUCIBILITY` y entregar estado previo/primera divergencia.

**Declaración a preservar:** esta tarea no afirma que la teoría ESBM describa correctamente a seres humanos ni que SRM/B6* estén superados. `CT2=7/100`, `STOP_R5=active`, **0 nuevos ciclos**, **0 experimentos en esta fase**.
