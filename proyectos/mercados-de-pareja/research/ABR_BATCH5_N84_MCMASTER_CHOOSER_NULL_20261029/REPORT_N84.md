# N84 · McMaster: control adversarial condicionado por persona y oportunidades

**Ejecución real:** un ciclo AB-R válido únicamente en alcance exploratorio (0/3 novedad); no validación externa ni inferencia causal. Contrato A–J [PREREG_N84.md](PREREG_N84.md) y [n84_actor_conditioned.js](n84_actor_conditioned.js) congelados ANTES de ejecutar este nuevo contraste en commit `028a3276a2b73225b9baa65c077a1771c4fe1378`. SHA256 del código `de6e83813da9d98fd0a31731da3c2636c84f6c1c47585329fea565b649ba5d7a`, Git blob `f0a4bffcddc3a9d82a5b2e5e07ae09c176e82c58`. CSV original de los autores [GitHub](https://github.com/curlsloth/SpeedDating-BodySway/blob/dadc819fbe99e99402b6d43f7e4f247a4bf55c2b/SpeedDatingOSF_20201218.csv) SHA256 `9685dfb09a610bbf150ee2d151b05d6dceff6af18fc5b21d3ac31eecabf63eb6`. La cohorte fue **previamente examinada** (SRC094/SRC096), por lo que NO es una prueba confirmatoria.

## Qué se congeló y qué se ha calculado
A–D: Pregunta: ¿más respuestas de sí/sí de lo que explica la selectividad individual a lo largo de las oportunidades realmente observadas? Null: conservar la red exacta de 719 registros dirigidos, 54 participantes, 2 sesiones, 357 parejas completas y los cinco registros sin contraparte, y permutar para cada persona entre sus oportunidades las respuestas sí/no sin cambiar su número total de «sí». Rival analítico E(T)=Σ_encuentros p_i p_j por actor (no multiplicación de tasas globales). Código preestablece **2.000** permutaciones Fisher-Yates, semilla `1badd00d`, con invariantes. E–G: ejecutado el código literal congelado, todas las condiciones satisfechas; resultados:
| Contraste | Valor |
|---|---:|
| Encuentros bilateralmente completos | 357 |
| Sí/sí observados | **70** |
| E(T) nulo exacto por actor | **73.3596** |
| Media en 2.000 permutaciones | **73.302** |
| SD permutado | 4.280 |
| Intervalo central descriptivo 95% | **65–82** |
| Diferencia observado menos E(T) | **-3.3596** |
| Cola bilateral descriptiva, corrección +1 | **0.4743** |

**Resultado negativo:** 70 no excede la expectativa de 73,36 dadas la red efectiva de oportunidades y la proporción de sí de cada participante. No observamos evidencia de una concentración extra de aceptación mutua según este estadístico y este null, **pero tampoco demostramos inexistencia de compatibilidad entre personas**. No hay comparación de predicción ESBM vs SRM; no se mide formación ni duración de parejas.

**R1:** aceptación indicada tras encuentro, no relación formada. **R2:** null que conserva cada oportunidad y actor, más competente que producto global; todavía no incluye todos los efectos actor-objetivo-orden y atributos de rivales Joel, Baxter, Chang, Pronk u Ogushi. **R3:** código preregistrado, pero decisión adaptativa tras ver resultados de la misma fuente: cola 0,4743 no es p confirmatoria. **R4:** repetición de personas/elección no aleatoria de la muestra, solo dos sesiones, supuesta intercambiabilidad dentro de actor, cinco direcciones sin inversa. **R5:** mantener STOP_R5 de confirmación humana externa y grado original 0/3. Esta es una prueba adversarial útil, no demostración de superioridad de ESBM.

**Registro:** N84 válido exploratorio, [LEDGER_N84.json](LEDGER_N84.json), [RESULTS_N84.json](RESULTS_N84.json); U132 P-RECIPROCITY y U133 P-COMPETENT_NULL cualitativos `NO_CHANGE_WITH_REASON`. Total 97 SOURCES, 30 PRIORS, 133 UPDATES; **18/40 válidos, 22 pendientes**, de los que **N85–N87 (3)** liberados y **N88–N106 (19)** reservados. CT2 N84=7 ordinal, [SVG completo y ampliado](CT2.svg); no N2. Madurez 38.85% ≈ 39%, solo QA mejora 51→53. Un intento de escritura postresultado se abortó por un error tipográfico del hash esperado y se corrigió sin modificar el código preregistrado ni contar otro ciclo. Clon independiente no verificado, no se publican microfilas, ni se fusiona main.
