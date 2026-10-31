# AB-H PIVOT N357–N376 | informe parcial hasta N357 | 31-10-2026

**Autorización:** 20 ciclos, uno válidamente ejecutado, 19 pendientes (N358–N376), 0 inválidos, 0 de planificación, 0 intentos instrumentales fallidos. **STOP_R5 humano, CT2 científico 7/100 y 0/3 científico humano.** No se ha alterado el ESBM original ni SRC104; no SSJY/Codex, licencias aceptadas, autores contactados, merges a main ni CI costosa.

## N357 — reparación en esquema serializado BigInt

Prerregistro A–J, instrumentos exactos, casos y SHA congelados en commit GitHub `07a22a1d1dbc6995714b57f2b37f975178b61b42` antes de cualquier outcome. Los 12 casos N356 se usaron como controles de regresión, no como nuevos ciclos, y se añadieron 9 controles de estructuras nuevas. Se corrigió exclusivamente una **copia nueva**, manteniendo el wrapper histórico N339/N356 intacto. La propiedad `full_units_in_2_power_minus52` pasó de `Number` a cadena decimal producida con `BigInt`, `full_units_schema_version=2`, `full_units_format=decimal_bigint_string`, incluido el grafo vacío.

Resultado: **21/21 sumas exactas y 21/21 certificados presentes**, comparadas con reconstrucción exacta JavaScript y el oráculo Python `fractions.Fraction` escrito separadamente. En estos mismos casos, **15/21 salidas de la fórmula antigua de Number habrían sido inexactas**. Este control es reparador del defecto de publicación numérica N356; **no prueba equivalencia en todos los inputs ni mejora validación humana**.

JS outcome SHA256 `119878216085a10a00317a649507819d7e6e8af2ab1f1031042358abe17e3c6c`; oráculo SHA256 `fef0ebf34c35494bd1f5806fa7aa25e54a00b65d57cafb0f8c0fe8ae920d161b`. Código JS `ecfb50efedfa483818bad14e9d4090038865cc532876df809346bea3d027fb43`; Python `f69d0d887503baa03e1a884f3bd4d99d6c628e18fe96e05c9813c1255ffa458d`; wrapper corregido `feacf8ea1399b0425b0692549cc6fc7bbbabf285ad70e3e374828e0b33d1dbf6`.

**Límite de compatibilidad:** un consumidor que espera un valor numérico debe adoptar explícitamente el nuevo campo de cadena. No se ha desplegado sobre el ESBM original ni se ha reejecutado ninguna de las 60 trayectorias históricas.

## Descubrimientos documentales, sin consumir ciclos

**SRC120** Kluger et al. (2025), <https://doi.org/10.1177/25152459241279522>, material <https://osf.io/vuen2/>. El artículo especifica `order`, `actorID`, `partnerID` y `date.again` para 187 estudiantes y ocho eventos Northwestern 2007. Es **la misma cohorte registrada en SRC084**, no una muestra independiente adicional. OSF API dice `node_license=null`; no hay autorización de reutilización de datos verificada ni microdatos leídos.

**SRC121** Huang et al. (2017) <https://doi.org/10.1037/pspi0000097>, OSF <https://osf.io/8k7rf/>, junto con el reanálisis de Kluger y Malloy 2019 y la corrección de 2025. La bibliografía refiere 110 personas y 1.961 puntuaciones dirigidas en tres sesiones, con decisión de segunda cita; OSF muestra `study3/study3.csv` (426.013 bytes) pero la base no se ha leído. `node_license=null`; su `LICENSE.txt` de 1.048 bytes es licencia MIT explícita para software/documentación, no una licencia de dataset humano inequívoca. Tampoco hay comprobación primaria de ronda o par nativo. Por ello no se ha concedido R5. La revisión de 2019 y la réplica de 2025 no constituyen una nueva cohorte cada una.

**Contadores:** 121 SOURCES, 35 PRIORS, 225 UPDATES; U222 registra el resultado de software, U223–U224 el R5 documental con `NO_CHANGE_WITH_REASON`. Se corrigió además una incongruencia de metadatos heredada del Atlas N337–N356, cuyo contador `valid_executed=19` no concordaba con su ledger canónico `20`; **esta reparación documental no consume ciclos**.

## AB-DECIDE

Continuar N358–N376 solo mediante nuevas propiedades técnicas verdaderamente falsables o evidencia humana independiente con licencia y orden originales comprobados; sin estudios sobre microdatos privados ni pruebas reiteradas sobre los 60 casos históricos. Hasta ese momento 19 plazas permanecen disponibles.

**SRC106 [U225]:** revisión primaria nueva, sin gasto de ciclo, del original Code.R (58.976 bytes, SHA256 6603f0b1c8eedf69c849f10eb96e0bfa82ad1496b2feea1c9c439f77ca2d204b) desde el enlace view-only publicado por Hall et al. (2026). El código modela aChoice/pChoice con gID, MaleCode/FemaleCode y Dyad; OSF API mantiene public=false y node_license=null. Ni el fichero .sav de personas ni sus filas se descargaron: R5 requiere derechos de base y secuencia temporal verificables. No se ejecutó experimento de validación humana.
