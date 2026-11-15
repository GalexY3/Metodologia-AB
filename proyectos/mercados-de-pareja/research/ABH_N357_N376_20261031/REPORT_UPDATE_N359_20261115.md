# AB-H PIVOT N357–N376 · actualización verificable al ciclo N359

Fecha de la ejecución: **15 de noviembre de 2026**. Protocolo vigente AB 3.2.1 con O1–O7; instrumentos AB-M038–M042 añadidos el 14/11/2026 siguen en fase de **piloto no validado**, no equivalen a reforma normativa. Se leyó el protocolo de `main` antes de abrir N359.

**Saldo:** 20 autorizados, **3 ciclos AB técnicamente válidos y ejecutados (N357, N358, N359)**, 0 inválidos AB, 0 de planificación AB, 17 N360–N376 pendientes. Un intento de oráculo Python fallido en N358 registrado separadamente. N359 no requirió reparaciones. **123 SOURCES, 36 PRIORS, 229 UPDATES. CT2 científico 7/100, STOP_R5 humano activo, novedad sociológica 0/3.**

## N359 — cotas exactas para parejas mutuamente aceptables bajo oportunidades incompletas

### Pregunta y estimando

A diferencia de N345 (verificación de selección de oportunidades y eventos del modelo original), de N351–N355 (asignación DA/rotaciones y mundos dinámicos) y de N356–N358 (instrumentación de exactitud y recursos), N359 investiga la **identificación parcial** de una cantidad contrafactual específica a partir de dyadas no observadas. DRIFT **D2.0**: cambia el estimando a identificabilidad observacional, conservando disciplina y mercado bipartito sintético.

Para conjuntos finitos F y M y un conjunto conocido O de parejas efectivamente observadas, la conducta binaria de ambas partes determina `E_yes_obs`. Toda pareja fuera de O puede ser compatiblemente mutuamente aceptada o rechazada. Las cotas nítidas del máximo número `K` de emparejamientos mutuamente aceptables son

`L=matching_max(E_yes_obs)`,
`U=matching_max(E_yes_obs union E_unobserved)`.

Estos son **extremos alcanzables** de completaciones del propio registro observado si todas las parejas no observadas son legal y materialmente factibles, no una banda de confianza estadística ni predicción de enlaces futuros. La formulación es un caso elemental del programa de identificación parcial de Manski (2005, DOI 10.1016/j.ijar.2004.10.006) y Horowitz–Manski (2006, DOI 10.1016/j.jeconom.2005.02.007). **Novedad de esa teoría: NO ACREDITADA.**

### Freeze–run

Prerregistro A–J y ambos instrumentos congelados públicamente en rama GitHub por commit **`929da09f7eb74e53bf39d252865a2fbd37f35aae` antes de cualquier outcome**. Código JavaScript SHA256 `5e0bd21476825d240fd3d8b5f05c1c55c8c2d84d6dbc25e0e2b23e76b712caa2`. Oráculo independiente Python SHA256 `8981671a0bb851e4a7d56a42d17bad8e375154584dffabef8de891f8ad118734`.

Se ejecutó una vez el instrumento JS sobre **504 mundos sintéticos n=9+9**: 480 combinaciones (3 mecanismos de exposición × 4 tasas × 40 mundos predefinidos), más **24 controles de cobertura completa**. Se ejecutó una vez el auditor Python con programación dinámica sobre **504/504 triples exactas L,U,K**; todos concordaron. El grupo de control con datos completos dio `L=K=U` **24/24**. Un ejemplo adversarial n=4 con cuatro encuentros diagonales negativos y las parejas cruzadas desconocidas es compatible tanto con `K=0` como con `K=4` sin cambiar una sola respuesta observada.

### Medidas registradas

Anchura media `U-L` (número de personas emparejadas dividido entre dos), por nivel de exposición nominal:

| Mecanismo | 15 % | 35 % | 60 % | 85 % | 100 % |
|---|---:|---:|---:|---:|---:|
| MCAR independiente | 7,450 | 5,800 | 4,475 | 2,675 | 0 |
| Exposición dependiente de actor | 7,675 | 6,100 | 4,625 | 2,775 | 0 |
| Exposición dependiente del resultado (MNAR sintético) | 7,025 | 5,075 | 3,825 | 3,125 | 0 |

Cada punto incompleto resume 40 mercados. El generador incorpora preferencias, compatibilidad latente y selección como supuestos establecidos, de modo que **los patrones no son efectos causales empíricos de una plataforma de citas**. No se ha realizado ajuste con datos humanos ni un contraste confirmatorio externalizado.

SHA256 outcome primario JS `3d6b644e06e1657ef9cb9a9c202012af3a14837a4a4413f5d0571f847fa5c150`; auditor independiente `034bdf1785c296033245eba25d7a3c1d287e55333b9989717dfc444e82d32ecb`. El primer outcome guarda las 504 matrices sintéticas, por semilla, incluidas las decisiones contrafácticas simuladas exclusivamente para evaluar cobertura, y las quince agregaciones. El auditor comprueba también dos manipulaciones deliberadas de la tabla adversarial. No hubo intentos fallidos N359.

### Decisión epistemológica y próximos requisitos

El ejercicio demuestra dentro de sus supuestos una **restricción de identificación** que un modelo predictivo puede ocultar si trata encuentros ausentes como rechazos. Debe añadirse a la discusión de validez de los modelos ESBM como diagnóstico, no como aceptación empírica. Un futuro análisis deberá obtener el **conjunto realmente elegible de contactos**, identidades y temporalidad, decisiones nativas de ambas partes y derechos de reutilización válidos, y comparar escenarios/modelos competentes prospectivamente. Sin esas observaciones, no se valida la tesis con 17 baterías sintéticas adicionales.

Se preservaron código ESBM original y SRC104, ambas ramas históricas y los outcomes anteriores. No se usaron SSJY, Codex, aceptación de licencias, contacto con autores, merge de investigación a `main` ni CI costosa.

### AB-DECIDE

**CONTINUE solo con nueva evidencia diferencial y R5.** N360–N376 siguen previamente autorizados pero no deben consumirse por obligación. El cierre de esta fase intermedia no requiere nueva aprobación. CT2 7/100 y grado humano 0/3. Reproducción en clon limpio pendiente de verificar (CLEAN_CLONE_NOT_VERIFIED).

## Evidencia documental nueva posterior a N359, sin gasto de ciclo

**U229 / SRC092 — Münster, fuente original de solicitud de datos.** Una vía nueva de OSF https://osf.io/n7dw9/ (distinta de los enlaces fallidos históricos) identifica el proyecto público con `node_license=null` y los formularios `datemeforscience_data_request.docx` y `datemeforscience_reproduction_request.docx`. Se descargó únicamente el archivo R de selección original de variables de 77.239 bytes, SHA256 `d3f43ad7f2eda641538432d729eabb40fa132c6e726e3a9e1fd3a7ae40a3c9fd`. La lista de variables indica `d1_yes`–`d5_yes`, `d1_match`–`d5_match`, metapercepción `d1_yes_p`–`d5_yes_p`, fechas de cuatro cuestionarios de seguimiento y `f1_p_partnerid`–`f4_p_partnerid`. Estas **etiquetas de un selector de variables no acreditan respuestas originales accesibles, correspondencia nativa bilateral, cronología de rondas ni un seguimiento individual utilizable**. El CSV fuente de personas no se descargó ni procesó y los formularios de solicitud no se completaron. La licencia CC BY4 del paquete complementario PsychArchives SRC092 no acredita por sí sola autorización sobre el CSV OSF no publicado. Estado R5 sigue STOP; 17 plazas intactas.
