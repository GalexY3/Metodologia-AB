# A-ASSIGN — auditoría de originalidad, contraejemplos exactos y regla de descarte

**Tipo:** `NONCYCLE_POSTHOC_PRIOR_ART_AND_IDENTIFICATION_AUDIT`. **Fecha:** 2026-10-29. **Rama:** `research/ab-r-mercados-pareja-20261028`; **base HEAD efectivamente comprobada:** `d8eb21049dbe86687c2e0b74235a36707db3e782`. Referencias internas: [propuesta previa A-ASSIGN](../ABR_HFBTIME_ETHICS_ALTERNATIVE_NOCYCLE_20261029/REPORT.md), [blueprint de identificabilidad](../ESBM_IDENTIFIABILITY_AND_FALSIFICATION_BLUEPRINT.md), código [ESBM v2](../ABR_ESBM20_20261028/esbm_dynamic.py). El objeto es **auditar la pretensión de novedad**, no simular, medir participantes o ejecutar un AB-R A–J.

**DECISIÓN AUDITABLE: REJECT_A_ASSIGN_AS_ORIGINAL_ESBM_EXPLANATION.** Un ensayo sobre efecto de una política de oportunidades puede ser útil científicamente, pero **no contiene aún una predicción incremental identificadora del mecanismo específico ESBM**. Conservar A-ASSIGN únicamente como **posible infraestructura futura** de datos originales, si autorización legal, ética y novedad/valor informativo independiente lo justifican. No convertir esta conclusión negativa en «refutación del código ESBM», ni declarar probada una hipótesis social.

**Congelación de estado:** `STOP_R5_EXTERNAL`; 26/40 ciclos válidos **anteriores**; 14 N93–N106 **reservados**, ninguno liberado, **0 ciclos** nuevos válidos/inválidos/planning; CT2 ordinal **7/100** no probabilidad; madurez ponderada **41.20%** sin aumento; **103 SOURCES, 30 PRIORS, 154 UPDATES** tras U153/U154; **0 fuentes bibliográficas nuevas, 0 datasets humanos nuevos y 0 confirmaciones empíricas**. N83/N88–N92 y sus adversos, código original y hashes no se tocan. Registrar contraevidencia sin borrar la propuesta previa.

## 1. Distinción imprescindible: efecto de política no equivale a explicación estructural original

A-ASSIGN propone, con consentimiento, comparar por **eventos independientes** `Z=0` (sorteo de encuentros bajo elegibilidad/cupos) y `Z=1` (cobertura equilibrada bajo esos mismos límites), y contar slots con encuentro realizado y **dos sí nativos efectivos**. Con aleatorización de mercados y supuestos de consistencia/interferencia adecuados, el ITT `E[Y_g(1)-Y_g(0)]` identifica el efecto de **ese cambio de régimen** en los eventos participantes. Es útil para gestión y para documentar el conjunto de oportunidades. No identifica automáticamente preferencias por semejanza, aprendizaje, dinámica relacional, el `q` artificial de ESBM, estabilidad de pareja ni originalidad de un algoritmo específico.

Una mejora bajo `Z=1` puede proceder de una **reorganización puramente mecánica de las aristas**, heterogeneidad preexistente de preferencias/atractivo entre receptores, congestión de objetivos o límites de capacidad, sin adaptación temporal, feedback ni norma ESBM novedosa. Un nulo también es posible incluso con cobertura más equitativa. El desenlace positivo observado en un evento no distingue causas si B0/B1/B2/B4 disponen del mismo grafo de oportunidades, características previas y presupuesto.

**Objetivos que no son una predicción social:** menos Gini de visibilidad, más personas receptoras distintas y más cobertura son, en gran parte, **criterios de construcción de la política de balanceo**. Se comprobarían como QA de la intervención, no como prueba de que un mecanismo humano es cierto. Tampoco la identidad `sí/sí` de dos decisiones nativas demuestra vínculo exclusivo; ESBM v2 aplica un matching posterior distinto.

## 2. Antecedentes que impiden apropiarse de la idea general

| Registro preexistente, leído de nuevo | Fuente original, detalle comprobado | Consecuencia para una supuesta tesis «nueva» |
|---|---|---|
| `SRC017`, Belot y Francesconi (2006), DP5926; versión revisada 2013 del mismo trabajo | [CEPR original](https://cepr.org/publications/dp5926), abstract verificado: participantes asignados aleatoriamente a eventos y variación exógena de oportunidades; observan propuestas y matches bilaterales para diferenciar composición de preferencias | Ya utiliza la **variación exógena de oportunidades** y evidencia bilateral. «Las oportunidades importan para la homogamia» no es original. Una versión de publicación no es una cohorte adicional |
| `SRC032`, Chen, Hsieh y Lin (2023) | [Artículo original HTML completo, introducción y §§3.1–3.4](https://onlinelibrary.wiley.com/doi/10.1111/iere.12631): AppX Taiwan, un mes 05/08–05/09/2019, **690.857 cuentas** divididas en **Control, OLS y OLS-CS**; cobertura, Gini, Likes, respuestas recíprocas y match `Like/Like`. Los autores publican **5.729 pares con match** bajo OLS-CS y mejoras frente a rivales; son **matches de app**, NO relaciones duraderas | Es un **experimento de recomendación bilateral y desigualdad de exposición** a gran escala, anterior a ESBM. Reducir concentración y elevar `sí/sí` no diferencia por sí solo nuestra teoría. Los datos fuente personales no se descargaron ni se obtuvo licencia de reutilización |
| `SRC054`, Ríos, Saban y Zheng (2022/23) | [Artículo original, DOI](https://doi.org/10.1287/msom.2022.1107); [metadatos institucionales](https://gsbpreserve.stanford.edu/view/58101); ya describe predicción de likes y contrapartes, optimización dinámica de surtidos e intervención de mercado, con historial de matches e incentivos de ambos lados | Ya aborda selección de oportunidades y reciprocidad en plataforma real, con comportamiento adaptativo. Un algoritmo que optimiza cantidad de matches no aporta por sí solo originalidad social |

**Precisión:** estos estudios no son réplicas entre sí; sí constituyen **anterioridad científica de clases de mecanismo**. Tampoco hemos reanalizado sus microdatos, validado su causalidad independientemente ni atribuido sus cifras a ESBM. En Chen las cuentas se randomizaron entre tratamientos en un mercado interconectado; no asumir que ello equivale a eventos independientes sin discutir interferencia. En Belot–Francesconi no se ha leído un archivo de datos ni se ha vuelto a intentar el acceso Essex; solo el abstract CEPR existente. En Ríos no se ha descargado ni usado el dataset propietario ni reiterado una vía de acceso fallida. Otros rivales ya catalogados: `SRC002` Hitsch, `SRC016` Fisman (muestra Columbia, no cohorte adicional), `SRC021` Topinkova–Diviak, `SRC098` Jung. No crear SOURCE nueva para la misma publicación.

## 3. Resultado formal 1: un teorema de no-signo bajo afinidades estáticas

Esta sección presenta **deducción matemática elemental, no ejecución ni prueba empírica**. Fijar un evento con conjunto de aristas consentidas elegibles `E`, **M slots** planificados iguales en ambas políticas `z∈{0,1}`. Para cada arista `e=(i,j)`, `X_e(z)∈{0,1}` indica que esa díada concreta fue asignada al slot bajo la política. `μ_{z,e}=P[X_e(z)=1]` es la probabilidad marginal conocida de asignación **antes** de las respuestas. Supóngase que un encuentro asignado se realiza, que ambas decisiones se observan y que `p_e∈[0,1]` es la probabilidad **fija**, bajo ambos regímenes y sin interferencia, de `sí/sí` en esa díada. No se requiere independencia de votos dentro de díada; `p_e` es su probabilidad conjunta.

```text
Y(z) = (1/M) Σ_{e∈E} X_e(z) · B_e(z)
E[Y(z)] = (1/M) Σ_{e∈E} μ_{z,e} · p_e
Δ = E[Y(1)] − E[Y(0)]
  = (1/M) Σ_{e∈E} (μ_{1,e} − μ_{0,e}) · p_e
```

La identidad de la esperanza exige solo linealidad de la esperanza y `E[B_e(z)|X_e(z)=1]=p_e`; el supuesto científico fuerte es que el mismo `p_e` se aplica con ambas políticas. Como `Σ_e μ_{1,e}=Σ_e μ_{0,e}=M`, se deduce:

- Si `μ_{1,e}=μ_{0,e}` para toda arista, **`Δ=0` exactamente para cualquier matriz de propensiones fijas `p`**, incluso cuando la política equilibrada cambie drásticamente la **correlación entre asignaciones** y la cobertura de receptores.
- Si existe alguna arista con `d_e=μ_{1,e}-μ_{0,e}>0`, existe también alguna con `d_e<0`. Tomando `p_e=1` en las aristas con `d_e>0` y 0 en las demás se obtiene `Δ>0`; invirtiendo esa asignación de `p` se obtiene `Δ<0`. **No hay signo universal de una política de balanceo para toda afinidad diádica estática**. Es una construcción en el espacio del rival B1/B2, no estimación humana.
- Si el efecto no es nulo aun conservando todas las probabilidades marginales de arista, falla al menos uno de los supuestos del ejemplo (p ej. decisiones condicionadas por conjunto de competidores, congestión, orden, interferencia o no-show dependiente del brazo). **No demuestra qué mecanismo concreto falló ni que ESBM sea el responsable**. B4 puede representar capacidad/orden, B1/B2 relaciones y propensiones heterogéneas, y modelos institucionales ya tratan la exclusividad.

**Alcance preciso:** este argumento no prohíbe el **efecto causal de una política** en humanos; prohíbe inferir **su mecanismo ESBM único** solo de que la cobertura y la reciprocidad total cambien. Las matrices de `p` deben estimarse sin usar respuestas posteriores al evento de prueba, con paridad de información y por unidad dependiente.

## 4. Contraejemplo 2×2 exacto: mejor cobertura, igual resultado bilateral

Cuatro participantes abstractos consentidos: emisores `a,b` y receptores `x,y`, todas las cuatro aristas elegibles; cada emisor recibe un encuentro real (`M=2`) con destinatario diferente al otro **o no**, sin repetir una misma díada. No es un modelo de orientaciones humanas: son etiquetas de un grafo mínimo. Dos políticas:

- `U` (sorteo independiente): cada emisor elige `x` o `y` equiprobablemente e independientemente; asignaciones `xx,xy,yx,yy` cada una con probabilidad `1/4`.
- `B` (cobertura equilibrada): sortear entre `xy` y `yx` con probabilidad `1/2` cada uno, garantizando un encuentro para cada receptor.

En `U`, el número de **receptores distintos** es 1 en `xx,yy` y 2 en `xy,yx`, de modo que su esperanza es `(1+2+2+1)/4=1.5`. En `B` es **2** en toda realización. **Cobertura +1/3 relativa** (2 frente a 1.5), pero para cada una de las cuatro aristas `P(X_e=1|U)=P(X_e=1|B)=1/2`. Por tanto, para cualesquiera cuatro propensiones de `sí/sí` que dependan solo de la díada,

```text
E[total sí/sí | U] = E[total sí/sí | B]
  = (p_ax + p_ay + p_bx + p_by)/2.
```

No cambia la tasa por slot ni el número esperado de aceptaciones, pese a que la política garantiza mayor cobertura. **No se han efectuado lanzamientos aleatorios ni cálculos por simulación: son cuatro resultados algebraicamente enumerados.** Una mejor Gini/cobertura no es necesariamente una mejora en eficacia de matching.

## 5. Contraejemplo 2×2 de ganancia: la congestión B4 basta

Mantener el mismo `U` vs `B`, pero cambiar el **comportamiento receptor** de forma plausible aunque artificial: emisores siempre dicen sí; cada receptor puede decir sí a **como máximo una** de las personas que le fueron asignadas durante este bloque (escasez de capacidad/tiempo; si recibe dos, elige una sin influencia de ESBM). Si los dos emisores llegan al mismo receptor, hay **una** arista `sí/sí`; si van a receptores distintos, hay **dos**. Entonces:

```text
E[total sí/sí | U] = (1+2+2+1)/4 = 1.5
E[total sí/sí | B] = 2
Δ (por slot) = (2−1.5)/2 = +0.25.
```

La mejora procede **totalmente de la congestión/capacidad de respuesta**, no de `q`, `private_bias`, matching dinámico ni norma novedosa. Esta regla de «máximo un sí por receptor» **no es** una condición necesaria de los speed-dates reales (muchas personas pueden aceptar varias nuevas citas); es una construcción formal válida para mostrar equivalencia con el rival `B4`, no un supuesto transferido al mundo. Si la exclusividad se aplica **solo al operador final de pareja** y no a los votos nativos, este ejemplo cambia el endpoint y NO permite inferir un efecto en el primario `sí/sí`; no confundir ambos casos.

## 6. Contraejemplo de signo opuesto cuando se modifican aristas marginales

Dos emisores `a,b` y dos receptores `x,y`, dos slots y preferencias **fijas**. `P` concentra las dos ofertas en `x`; `B'` asigna `a\to x,b\to y`. Si `p_ax=p_bx=1`, `p_ay=p_by=0`, sin capacidad del receptor para rechazar por saturación, entonces `P` produce **dos** sí/sí y `B'` solo **uno**. Son políticas con distinto conjunto de aristas: la que equilibra cobertura puede reducir aceptaciones en un mercado con preferencias estáticas y fuerte heterogeneidad de receptor. **No** se presenta `P` como el sorteo neutral `U` anterior; es un contraste ilustrativo de que mejorar visibilidad no fuerza positividad frente a toda política comparable. N88 ya muestra, dentro de ESBM sintético, que cardinalidad máxima en cada grafo puede bajar formaciones acumuladas futuras; N92 muestra efectos mixtos del cambio de balanceador. Ninguno es evidencia humana.

## 7. Comparación obligatoria con rivales concretos (paridad R2)

| Rival competente y mismo acceso | Cómo produce o predice el observable de A-ASSIGN | ¿A-ASSIGN lo distingue? |
|---|---|---|
| **B0 composición/riesgo**: elegibilidad, tamaño de grupo, slots y composición de encuentros | Una reasignación cambia exposición a tipos diferentes y la mezcla de oportunidades; puede producir homofilia y tasas distintas sin preferencia nueva | **No**, salvo predicción adicional condicionada a idéntico universo/soporte |
| **B1 actor/target/SRM**: efectos de emisor, receptor, díada y evento, aprendidos exclusivamente de train | `p_ij` heterogéneo produce ganancia/pérdida cuando cambia la distribución marginal de aristas; dependencia entre votos ya representada | **No**, un efecto sobre `Y` no identifica `private_bias` ni factor «emergente» |
| **B2 homofilia directa**: preferencias por similitud predicha desde atributos legítimos pretratamiento | Cambiar el conjunto de parejas elegibles/asignadas cambia la fracción same y la probabilidad `sí/sí` | **No**, no inferir «no existe preferencia directa» de parejas finales |
| **B4 ranking/congestión/capacidad**: posición, carga del receptor, fatiga, disponibilidad y orden ex ante | Puede producir un **efecto positivo con identical edge marginals** (contraejemplo §5), o negativo por saturación/familiaridad | **No**, la mejora no requiere dinámica ESBM específica |
| **Belot–Francesconi (SRC017)** | Variación exógena en composición de citas, separación de oportunidades y preferencias en datos reales | **No**, esa clase de identificación ya se publicó |
| **Chen et al. (SRC032)** | Sistemas de ranking con cobertura, desigualdad y reciprocidad en un experimento de app con tres brazos | **No**, objetivos/resultados estructuralmente ya ensayados |
| **Ríos–Saban–Zheng (SRC054)** | Optimización bilateral dinámica y observación de historial de matches | **No**, la secuencialidad general y optimización no son nuevas |

**Regla de justicia:** todos los rivales reciben mismos campos, horizonte de entrenamiento, variables de exposición **previas al outcome**, esfuerzos de ajuste y muestras agrupadas por eventos/actores. La comparación causal de política `τ` y la comparación de ajuste de decisiones `p_ij` son **estimandos diferentes**; no usar un predictor incapaz de manejar la asignación para «ganarle» con una intervención cuya regla él desconoce. Si B1/B2/B4 ajustan `τ` de forma igual con mismo coste/variables, no hay victoria de ESBM. No prometer que un modelo de máxima flexibilidad no pueda representar ninguna dinámica: exigimos especificación previa de la familia rival y un margen de predicción nuevo.

## 8. Puerta estricta de descarte de hipótesis (R5 y originalidad)

**G0 / ORIGINALIDAD — VETO ANTES DE DATOS:** si la afirmación se reduce a (i) exposición determina distribución de encuentros; (ii) homofilia agregada emerge del conjunto de riesgo; (iii) balanceo baja Gini; (iv) balanceo aumenta o no número de `sí/sí` sin mecanismo de exclusión predicho; o (v) asignación multietapa importa para matches, **DESCARTAR A-ASSIGN COMO RECLAMO ORIGINAL**: SRC017/SRC032/SRC054 y contraejemplos lo cubren. El diseño puede conservarse como instrumento de muestreo, nunca como grado 1/3–3/3.

**G1 / MEJOR PREDICCIÓN DIFERENCIAL:** solo reconsiderar si se propone **ex ante** un mecanismo ESBM específico **no codificado como outcome por diseño**, con población, intervención, interacción y **predicción numérica o región de signo** que difiera de B0/B1/B2/B4 bajo **información idéntica**, clase rival justa, presupuesto de ajuste parejo y rango de parámetros plausible. Un `τ` positivo en una política diseñada para cobertura no satisface G1. Debe especificarse qué resultado de cada rival lo refuta y quién gana con dato adverso; no seleccionar la hipótesis después de un piloto confirmatorio.

**G2 / IDENTIFICACIÓN:** el outcome ha de corresponder al mecanismo (no `sí/sí` simultáneo como si fuera respuesta condicional a mensaje), y se debe observar grafo elegible antes de asignación, aristas ofrecidas, encuentros **realizados**, ambos votos nativos, reglas y timestamps, más no-respuesta/no-show separada. Identificar lo causal únicamente por asignación exógena y bajo interferencia tratada; N83 ya prueba que exposición y dos sí/no observados sin randomización no bastan.

**G3 / DISEÑO E INDEPENDENCIA:** múltiples mercados de asignación realmente independientes, consentimiento y protección de datos antes de humanos, licencia legal por archivo/custodia, SHA de originales, diccionario, prereg A–J + código SHA en commit **antes** de outcomes y plan de multiplicidad. Todos los votos de un mismo participante/evento y estudios con la misma muestra quedan juntos; impedir leakage de popularidad futura. Si no se puede demostrar no interferencia o se usan 2 mercados como N=millones por voto, **STOP**.

**G4 / CONTROL FUERTE y ADVERSO:** comparación en cohortes distintas, predicción **congelada** antes de test, calibración/log-loss/Brier para respuestas o ITT/intervalos por mercados para política; controles B0/B1/B2/B4 y las mejores variantes publ. superando mismos splits. Si ESBM no obtiene ventaja fuera de muestra y con relevancia práctica preestablecida, **aceptar nulo y descartar afirmación de superioridad**; no reutilizar el holdout y renombrar una interacción distinta como confirmatoria. Si una victoria consiste solo en describir una función de política o en añadir información que el rival no ve, no cuenta.

**G5 / DECISIÓN DE CAMPAÑA:** G0 falla **ahora**, G1 **no existe** aún y G2/G3/G4 tampoco están satisfechas. Clasificar `A-ASSIGN_EXPLANATORY_HYPOTHESIS = REJECTED_FOR_NOVELTY`, `A-ASSIGN_DATA_INSTRUMENT = OPTIONAL_CONDITIONAL` y `ESBM_CAMPAIGN = STOP_R5_EXTERNAL`. Esto **no solicita ni libera plazas**; la ruta futura, si aparece evidencia nueva, exige propuesta concreta al investigador antes de abrir N93–N106. No vender un experimento humano sin originalidad como prueba de una teoría.

## 9. Cierre y límites verificables

Es posible que exista una predicción de interacción verdaderamente exclusiva al refinar ESBM, pero **no se ha mostrado en A-ASSIGN**. Los ejemplos matemáticos pertenecen a estadística de diseño y modelos de elección; no son descubrimientos sociológicos originales, no se han corrido simulaciones ni comparaciones numéricas sobre microdatos humanos. La conclusión negativa es valiosa porque **evita prometer especificidad causal donde no existe** y orienta la asignación de investigación hacia observar mecanismos realmente distintos.

**Evidencia adversa que permanece íntegra:** N83 (mismo joint observado, `do(E)` 0 frente +.24); N88 (maxcard local no maximiza siempre acumuladas); N89 (reputación pública global impuesta frente a testigos); N90 (actualización de rechazo sintética con signos heterogéneos); N91 (balanceador cambia 18/18 bajo permutación de ID); N92 (snapshot 0/18 cambios de salida pero modifica formaciones de forma desigual). La existencia de aristas recíprocas no garantiza formar pareja, y match de app no es relación duradera.

**Fuentes:** SRC017 / [CEPR](https://cepr.org/publications/dp5926), SRC032 / [Wiley](https://onlinelibrary.wiley.com/doi/10.1111/iere.12631), SRC054 / [INFORMS DOI](https://doi.org/10.1287/msom.2022.1107), código v2 y reportes versionados dentro del repositorio. Relectura del texto original publicado **no** representa cohorte nueva ni licencia de dataset. Se actualizan únicamente metadatos de estas dos SOURCES existentes (SRC017, SRC032), y cualitativamente P-NOVELTY U153 y P-OPPORTUNITY U154 `NO_CHANGE_WITH_REASON`. No hay nuevos originales, ni cambios de grado/CT2/madurez, ni SSJY, datos íntimos, licencias, autores contactados, nuevas ejecuciones, CI costosa o merge main.

**AB-DECIDE FINAL: STOP_R5_EXTERNAL; A-ASSIGN NO NOVELTY GATE FAIL, SOLO INSTRUMENTO CONDICIONAL.**

