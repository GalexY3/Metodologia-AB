# Mercados de pareja · BRANCHING AB-R N47–N55 · Informe final por R5

**Fecha:** 28/10/2026. **Investigador:** Alejandro Panera Pascual. **Rama:** `research/ab-r-mercados-pareja-20261028`, sin merge a `main`. **Autorización:** 20 ciclos BRANCHING AB-R adicionales. **Trabajo realmente ejecutado:** 9 ciclos A–J válidos (N47–N55), cero inválidos, uno `PLANNING_AB_ONLY` y uno documental, **11 ciclos autorizados no iniciados**. **AB-DECIDE:** `STOP_R5` por falta de observables prospectivos y novedad discriminante; las 11 plazas no se computan como trabajo. No hubo una intervención con humanos ni confirmación causal.

**Nivel:** 0 hallazgos 1/3 nuevos, 0 hallazgos 2/3 o 3/3. El 1/3 local previo N46 permanece en su formulación descriptiva exacta, pero su extrapolación sobre preferencia masculina está **debilitada** por N53, registrado como actualización adversarial sin borrarlo. N1 global histórico `NOT_AUDITED`. CT2 de **17/100 a 13/100** de forma ordinal, **NO probabilidad**, por identificabilidad y antecedentes. DRIFT D0,5 (misma rama, dos controles más competentes).

## Procedimiento reproducible y trazabilidad

Se leyó `CURRENT.md`, `AGENTS.md` y protocolo AB 3.2.1 O3–O6. El contrato [PREREG.json](PREREG.json) quedó en GitHub commit `4eeaee46511aba8547d62d4ee97ed3e9ea54fdcf` **antes** de los nuevos contrastes. [SOURCE_FREEZE.json](SOURCE_FREEZE.json) commit `c7037894f8bf25fc494467a54b1dd3790b3e3682` congela `analyze.py`, SHA256 `1c0c14a47082f07f60200f0cf9d99cbc8b3ee4e37de2fef9b781a0dac92b414c`; el archivo proviene de ZIP local con código y lector Parquet. **No** subir datos identificables/pseudónimos a este repositorio. Parquet Columbia original aportado por el usuario, SHA256 `a0fe55d6172d01f81d6c7e2546330828cb98d1f631b2598fec4d4f4660eaa37d`. Se reejecutó el script congelado dos veces con resultado idéntico, salida JSON SHA256 `b636df29004b0dcd355f598c105547f611a721dcaf69752fc694bd10d6fd6743`, y un script portátil con importaciones relativas volvió a producir idéntico JSON. **Clon limpio por tercero NOT_VERIFIED**. [Resumen de resultados](AGGREGATES.json) y [ledger A–J](LEDGER.json). No se ajustaron los coeficientes del simulador original.

Los modelos de Columbia se ajustaron con regresión lineal de respuesta binaria, controles de actor y de candidato mediante residualización de Frisch–Waugh–Lovell y `scipy.sparse.linalg.lsqr`. Los errores estándar se agruparon por actor que decide, no por candidato ni evento; las correlaciones bilaterales siguen siendo una limitación. Todo resultado es exploratorio porque el dataset Columbia y Mixmosa ya habían sido usados para elegir hipótesis. Se distingue asociación **dentro de la muestra** de predicción nueva y causalidad.

## N47 · Calidad y estimando
Columbia contiene 8.368 decisiones dirigidas (4.184 encuentros de ambos lados), 551 participantes, 21 sesiones. Hay 188 decisiones con edad incompleta y 164 con disciplina incompleta. El subconjunto común de los regresores tiene **4.071 decisiones por sexo**. No se hallaron IDs con cambios de edad/disciplina dentro de la persona en la auditoría anterior y se conservaron pares espejo. **Los 551 participantes aparecen en una única wave**, de modo que no puede observarse su popularidad en eventos anteriores como predictor disponible antes de esa cita. Este es el principal bloqueo prospectivo.

## N48–N50 · Controles simultáneos por actor y candidato

Bajo efectos fijos de **ambos extremos** de la decisión, `same_field` es un atributo relacional no constante entre todas las aristas y puede estimarse; la popularidad global del candidato está absorbida por su propio efecto fijo. Se estimó por sexo:

| Especificación 2-FE con edad absoluta + misma disciplina (n=4.071/sexo) | Mujeres decidiendo | Hombres decidiendo |
|---|---:|---:|
| Coeficiente de distancia absoluta de edad / DE | −0,01226 (SE 0,01143) | −0,02945 (SE 0,00949) |
| Coeficiente de **misma disciplina** / DE | **+0,02805** (SE 0,00880) | **+0,03030** (SE 0,00808) |
| R² parcial respecto a residual de dos FE (dentro muestra) | 0,00438 | 0,00733 |
| Especificación **solo distancia de edad**, coef./DE | −0,01470 (SE 0,01159) | −0,03208 (SE 0,00960) |

**Interpretación:** hay una señal local modesta de coincidencia de disciplina académica que no desaparece completamente al controlar ambos participantes. Eso desautoriza una tesis de «la semejanza no importa nunca». `field_cd` codifica **área académica**, no clase social, educación alcanzada ni posición jerárquica; no se ha podido reproducir esta variable idéntica en Mixmosa. Los intervalos son descriptivos bajo SE de cluster único y modelos múltiples. Ningún coeficiente mide una preferencia causal ni el «valor» total del candidato.

**N49 — Identificabilidad:** `edad_target−edad_actor` es combinación exacta de dos efectos fijos; tras residualizar, su norma relativa es ≈3,48×10⁻¹¹ y se eliminó. Asimismo una puntuación fija de popularidad del candidato se absorbe exactamente por el FE del candidato. No se inventa un coeficiente de popularidad en el modelo 2-FE ni se compara de forma ilegítima con el FE de actor solo.

## N51 · Control adversarial que conserva ambos grados de aceptación

Se construyó una cadena de intercambios 2×2 sobre el grafo de citas **observado**, dentro de cada `wave` y sexo de quien elige, que mantiene por construcción **(i) el número de sí que emite cada decisor, (ii) el número de sí que recibe cada candidato, (iii) las oportunidades concretas**. 106.000 propuestas por sexo, con 6.000 de calentamiento y 250 muestras espaciadas; 15.803 cambios aceptados entre mujeres y 10.645 entre hombres. La auditoría comprobó exactamente los grados al final.

| Indicador (diferencia entre aceptados y oferta media) | Observado | Referencia cadena, media | Cuantiles 2,5–97,5 % |
|---|---:|---:|---:|
| Mujeres, diferencia absoluta de edad | −0,055 años | −0,005 | [−0,084; +0,062] |
| Hombres, diferencia absoluta de edad | **−0,187 años** | −0,111 | [−0,154; −0,071] |
| Mujeres, misma disciplina | **+0,01249** | −0,00264 | [−0,01072; +0,00618] |
| Hombres, misma disciplina | **+0,02197** | +0,00900 | [+0,00409; +0,01431] |

**Resultado importante:** al preservar ambas propensiones, la cercanía de edad femenina ya no queda fuera de esa referencia de simulación, mientras la masculina sí aparece relativamente cercana. La coincidencia de disciplina es mayor que la referencia en ambos sexos. **Son cuantiles de una cadena MCMC, no intervalos de confianza ni valores-p exactos**. Solo se realizó una cadena por género; no se verificó mezcla ni uniformidad en el espacio de grafos, y el diseño social no es aleatorio. El resultado se etiqueta `EXPLORATORY_MCMC_NULL`, no confirmatorio.

## N52 · Importancia aparente del candidato

La inclusión de efectos fijos del candidato reduce la suma de cuadrados residual de un modelo solo con FE del actor en **23,7 % para mujeres y 25,8 % para hombres**, **en la misma muestra**. Esto no equivale a afirmar que popularidad exógena «causa» un cuarto de las elecciones: los parámetros de candidato son numerosos y pueden sobreajustar; sin predicción ex ante y nuevas personas la interpretación debe restringirse al ajuste dentro muestra.

## N53 · Contraste de edad con Mixmosa bajo dos efectos fijos

Se añadieron los detalles de especificación antes de ejecutar la prueba en [N53_PREREG_ADDENDUM.json](N53_PREREG_ADDENDUM.json), commit `57a977dab7c6e915037e478e72d96f3209fe4251`, y el [código Mixmosa](mixmosa_twoway.js) se archivó **antes** de procesar los CSV en commit `0b8fc2bfc4120e42bca64c347aaee3d0406c9fa1`. Se descargaron los archivos originales del repositorio público [Mixmosa](https://github.com/dankras/mixmosa-anonymized-data), sin guardar IDs ni filas en GitHub AB. La ejecución dio el mismo JSON en dos pasadas, [resultados](N53_MIXMOSA_TWOWAY_RESULTS.json).

| Modelo de distancia de edad **sola** con actor+target FE | Mujeres | Hombres |
|---|---:|---:|
| Columbia n=4.071 decisiones/sexo | −0,01470 (SE 0,01159) | −0,03208 (SE 0,00960) |
| Mixmosa n=1.888 decisiones/sexo | **−0,04153** (SE 0,01542) | **−0,00094** (SE 0,02049) |

Las muestras y reglas de reclutamiento difieren; incluso Columbia usa 4.071 casos comunes con disciplina y Mixmosa 1.888 con edad completa, no igualar denominadores ni atribuir efectos de tratamiento al país. Sin embargo, **la anterior reversión de signo entre los hombres (N46, control unilateral por persona-evento) no persiste como inversión de coeficiente en 2-FE**: Mixmosa queda prácticamente en cero. Esto **debilita la extrapolación** del 1/3 descriptivo N46, que permanece registrado con su estadístico exacto y nueva anotación adversarial en [ledger 1/3](../FINDINGS_1_3/LEDGER.json); no se cuenta otro 1/3 ni se borra silenciosamente.

## N54 · Puerta prospectiva fallida, PLANNING_AB_ONLY
**551/551 personas aparecen en una sola ola Columbia.** No es posible entrenar su popularidad individual con decisiones de un evento anterior y utilizarla en la próxima ola. Un modelo de atributos transferibles de personas nuevas sería otro estimando; fingir «popularidad pre-evento» empleando votos de ese mismo evento violaría temporalidad. **N54 es un ciclo documental/de planificación válido**, no un experimento o replicación ejecutada.

## N55 · Antecedentes y revisión crítica, DOCUMENTARY_AB
Se consultaron [Fisman et al. (2006)](https://doi.org/10.1162/qjec.2006.121.2.673), que ya examina el propio experimento de Columbia, [Belot y Francesconi (2006)](https://cepr.org/publications/dp5926) sobre separación empírica de preferencias y oportunidades, y [Witmer, Rosenbusch y Meral (2025)](https://doi.org/10.1016/j.chbr.2024.100579) que compara atractivo y homofilia en 5.340 decisiones de usuarios de citas online. [PRIOR_ART.md](PRIOR_ART.md) documenta también Asendorpf et al. y Zhao et al. **Las ideas centrales son antecedentes publicados;** no asignar originalidad por volver a encontrarlas con otras regresiones.

## Decisión R5 y ética
**9/20 ciclos efectivamente cerrados y 11 plazas sin iniciar**. La mayor parte de pruebas adicionales sobre estos dos mismos conjuntos se convertiría en tuning retrospectivo. El siguiente experimento discriminante necesita **(i) medidas prospectivas de popularidad antes de exponer los perfiles**, **(ii) el conjunto de oportunidades por usuario y atributos comparables**, **(iii) variación nueva/aleatoria en visibilidad o elección con consentimiento**, y **(iv) un holdout humano independiente**. El rechazo privado como pérdida de reputación pública sigue sin medirse; no inferirlo de sí/no de citas.

**CT2 17 → 17 → 16 → 16 → 16 → 16 → 14 → 14 → 13** por ciclos N47–N55, puntuación ordinal de trayectoria a 2/3, NO probabilidad de una teoría. [Gráfico escala completa y ampliada](CT2.svg), [ledger](LEDGER.json).

**AB-DECIDE = STOP_CAMPAIGN_R5**. No solicitar ni ejecutar un nuevo bloque sobre el mismo dato ya adaptativamente explorado. Hay **11 plazas autorizadas vigentes sin iniciar**; solo deberían reabrirse ante una fuente prospectiva realmente discriminante, sin contar planificación de un estudio futuro como evidencia del estudio ya ejecutado. No merge a `main`.
