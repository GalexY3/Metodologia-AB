# Mercados de pareja ESBM -- alcance cientifico, puntuacion y primera tanda N83-N87
Fecha 2026-10-29. Parent repo GitHub branch `research/ab-r-mercados-pareja-20261028` HEAD comprobado `dc5a5726f93c2fc94b9a3338a4e158eb96d6a702`.
**Auditoria de alcance, NO ciclo AB-R.** El usuario ha delimitado a una tanda inicial de **5 intentos posibles N83–N87**, procedente de los 24 ya aprobados. Los **19 N88–N106** permanecen concedidos en presupuesto historico pero **no liberados para ejecucion en esta tanda**. Los 16 ciclos validos acumulados no cambian. R1-R5, O1-O7 y STOP_R5 conservan fuerza: si bloquea la muestra externa, se puede progresar en otra linea cientifica del mismo proyecto, siempre con A-J y tests utiles.

## Definicion de un 100 % verificable (alcance ESBM fase 1)

Un **primer paquete de investigacion cientificamente defendible** que (a) formaliza las oportunidades y elecciones bilaterales, selectividad, instituciones/plataformas y dinamica en un modelo reproducible; (b) confronta las explicaciones fuertes ya publicadas; (c) emplea licencias y mediciones reales adecuadas; (d) propone una prediccion discriminante precongelada; (e) la contrasta fuera de la cohorte usada para construirla y resiste controles y ablaciones; (f) publica documentacion cientifica y codigo reejecutable sin violar privacidad. Esto **no es** "explicar mejor que todos" ni cubrir ya toda poblacion/orientacion/pais, ni garantizar un descubrimiento. Pueden quedar resultados negativos que exijan cambiar la tesis aunque la infraestructura alcance madurez.

## Rubrica ponderada estimativa -- 38 % (38,25 % exacto)

**ATENCION:** este porcentaje es una estimacion de madurez por hitos, no un porcentaje estadistico medido ni probabilidad de exito de la teoria, ni CT2; margen de juicio +/-10 puntos no CI. No se deduce de 16/40 ciclos (40 % por casualidad numerica distinta). La base se fija ahora para evitar mover el baremo despues de resultados. Formula: `avance = SUM(peso * porcentaje_de_area / 100)`.

| Area | Peso | Avance estimado | Contribucion a total |
|---|---:|---:|---:|
| Marco teórico y mecanismos | 15 % | 60 % | 9.00 puntos |
| Estado del arte | 10 % | 75 % | 7.50 puntos |
| Simulador ESBM | 15 % | 55 % | 8.25 puntos |
| Controles técnicos y reproducibilidad | 10 % | 50 % | 5.00 puntos |
| Datos reales y preparación empírica | 15 % | 40 % | 6.00 puntos |
| Originalidad científica y baselines competentes | 15 % | 10 % | 1.50 puntos |
| Validación externa independiente | 15 % | 5 % | 0.75 puntos |
| Producto científico final | 5 % | 5 % | 0.25 puntos |
| **TOTAL** | **100 %** | -- | **38.25 puntos = 38 % redondeado** |

**Motivacion y hitos por area (auditados desde archivos del repo):**
- **Marco teórico y mecanismos 60%**: THEORY_V2.md defines actual implemented mutual compatibility scopes, staged accept/response, 16 periods, algorithmic exposure, private/public feedback and stipulated exits; parameters not calibrated. **Hito para llegar a 100%:** Rival-specific equations, identifiable estimands, population scope, norms/institutions, alternatives and formal falsifiers linked to observable data.
- **Estado del arte 75%**: 97 versioned original source records and 30 explicit priors, strong adverse Joel/Baxter/Pronk/Rios/Chang/Ogushi/Matz/Zhao, deduped author GitHub source SRC096 and SRC094. **Hito para llegar a 100%:** Systematic search protocol, inclusion/exclusion and study overlap audit, strongest competing outcomes and qualified literature synthesis ready for manuscript.
- **Simulador ESBM 55%**: Executable esbm_dynamic.py, frozen 6x10 scenarios, N144 synthetic agents, 16 ticks, dynamic eligibility/platforms/dissolution; simplistic matching, exogenous hazards, arbitrary weights and identities. **Hito para llegar a 100%:** Modular mechanisms and independent measurable observables, stateful event chronology, time-to-event censoring handled, negative controls and realistic constraints without forced outcomes.
- **Controles técnicos y reproducibilidad 50%**: Pre-outcome source freezes, A-J and R1-R5 gate, SHA256 McMaster original and QA code, 60 synthetic scenario QA and byte-identical repeat on same machine; no independent clean clone. **Hito para llegar a 100%:** Fresh clean-room deterministic replay, unit+property testing, code/data provenance, exposure-preserving strong nulls, CI validation and ready-to-run reproduction package.
- **Datos reales y preparación empírica 40%**: Columbia, Mixmosa and McMaster original observational samples studied; McMaster 54 actors, two sessions, 357 native bilateral complete dates and SHA256. Original source rights for some other data unknown; no universal harmonized cross-site risk-set dictionary. **Hito para llegar a 100%:** Licensed complete original datasets from distinct cohorts, harmonized native yes/no and exposure identifiers with missingness and timing, versioned SHA256 and secure controlled access.
- **Originalidad científica y baselines competentes 10%**: Only one scoped 1/3 finding with subsequent attenuation, 2/3 not established. Risk-set-veto hypothesis PROPOSED_UNVALIDATED; strong existing prior-art SRM, assortments and sequence effects. No strong independent model comparison. **Hito para llegar a 100%:** Prospectively pre-registered original discriminating prediction surviving matched strong baselines and ablations; adverse results retained with no 2/3 if failed.
- **Validación externa independiente 5%**: No virgin held-out independently collected original yes/no reciprocal dataset with legal rights, no ESBM heldout model test; within-source actors/2 McMaster sessions insufficient. **Hito para llegar a 100%:** External other-cohort untouched test, valid intervals/clustering and transport/negative results across populations and settings; no posthoc tuning.
- **Producto científico final 5%**: Numerous internal reports/ledgers and transparent code, but no finished reproducible journal-style manuscript with defensible central claim and external validation. **Hito para llegar a 100%:** Complete methods, preregistration, data provenance and tables, independent reproduction, limitations, polished paper and supplement fit for scientific peer review.

## Dos ejes independientes que NO deben sumarse

1. **Madurez de infraestructura y capacidad de investigar**: teoria, simulador, fuentes y QA relativamente adelantados (aprox. 50-75% segun cada modulo).
2. **Fuerza empirica de la explicacion original**: muy incipiente. Un unico 1/3 historico de alcance local y posteriormente debilitado, cero 2/3 confirmados, cero validacion externa independiente de una tesis ESBM y CT2 7/100 ordinal. No deben presentarse la corrida de 60 escenarios ni las 357 citas McMaster como validacion causal.
3. **Presupuesto**: 16 validos / 40 autorizados = 40% usado del techo, NO porcentaje cientifico. Quedan 24, solo primeros cinco N83-N87 liberados para intentar ahora, 19 no liberados; ninguna plaza consumida hoy.

## 5 pistas para la tanda inicial (NO ciclos ya abiertos)

La distribucion siguiente es **ruta propuesta**, flexible ante pruebas nuevas, no un A-J prereg ni autorizacion de ejecutar sin evidencias; un ciclo se abre solo al congelar pregunta, rivales, contrato A-J, script/hash, datos y control y ejecutar/verificar el procedimiento completo. Documentar invalidaciones y negativos, y no producir cinco ciclos ficticios a cambio de cinco informes.

- **N83 / T1: Originalidad adversarial**. Comparar mapa ESBM `H-RISKSET-VETO` vs modelo de actor/target/relacion (Joel/Baxter), sobrecarga y orden (Pronk), optimizacion de assortments (Rios), comportamiento (Chang/Ogushi), lenguaje (Matz) y nulos Zhao. Salida admisible: prediccion no trivial con falsador claro o registro de que NO es novedosa. Si solo se releen los mismos articulos sin hallazgo nuevo: NO gastar plaza.
- **N84 / T2: Identificabilidad formal**. Pregunta si la estructura de oportunidades realmente observada permite distinguir un efecto de conjunto elegible de mera seleccion y heterogeneidad individual. Probar formalmente identificacion o contraejemplo con estimandos y rivales; no simular para repetir un supuesto por construccion. Controles de riesgos, codificacion de oportunidades, no-meet, reciprocidad.
- **N85 / T3: Dinamica temporal ESBM**. Separar exposicion, solicitud, respuesta bilateral, formacion, supervivencia/censura; evaluar si las duraciones y la reputacion actual son resultados artificialmente inducidos por codigo. Reingenieria o experimento solo con contraste congelado, test de invariantes y mecanismo falsable.
- **N86 / T4: Baselines y reproducibilidad**. Auditoria de `esbm_dynamic.py` frente a nulos que respeten grafo de elegibilidad/exposicion, Gale-Shapley u optimizacion donde sean comparadores pertinentes, prueba de clon limpio, controles de filtracion y paridad informativa y computacional. Solo si hay control efectivamente ejecutado y contrastable.
- **N87 / T5: Datos externos y convergencia**. Priorizar una segunda cohorte con decisiones 0/1 de ambas personas, licencia de archivo, bytes SHA256, evento y riesgo real, reserva de outcomes en holdout. Si bloqueo legal o instrumental persiste, redirigir a un contraste independiente dentro de T1-T4 que pueda ejecutarse rigurosamente, SIN disfrazar el cambio de validacion externa.

**Regla de pivot entre pistas:** STOP_R5 significa NO a una pretension empirica sin datos, no "paralisis de todo el proyecto". Se permite ejecutar pruebas teoricas, formales, QA, computacionales y negativas independientes **si** distinguen mecanismos de alternativas competentes, quedan precongeladas y se mantienen honestamente en nivel exploratorio. No conceder 2/3 por pruebas artificiales. Maximo cinco A-J en esta tanda, y cero si no aparece trabajo con capacidad real de cambiar la conclusion.

## Indicadores de avance y guardarrailes

- KPI 1 `maturity_score`: rubrica fija de ocho areas con pesos, corte e incertidumbre; subir solo con artefacto, test o fuente nuevo y calidad documentada; no sube por ciclos gastados.
- KPI 2 `scientific_claim_grade`: N1=exploratorio local no generalizable, N2 requiere originalidad/control y replica externa independiente, N3 sin evidencia; del ledger original N1 hay un hallazgo debilitado por estimando mas fuerte. Es la medida de resultado, no el 38%.
- KPI 3 `confirmatory_external_studies`: hoy **0** para prediccion ESBM; no contar varias publicaciones de misma cohorte, distintos seeds o splits internos como replicaciones externas.
- Guardarrailes: `CT2 7/100 ordinal`; `clean-clone NOT_VERIFIED`; limites de licencia/datos personales; prereg/codigo SHA anterior a outcomes; conteo A-J valido/invalid/planning real; evaluacion por bloques, y reportar consecuencias de controles adversariales desfavorables.

No hay nuevas fuentes originales ni nuevos resultados en la presente delimitacion: **SOURCES=97, PRIORS=30, UPDATES=130** sin revisiones inventadas. Ningun ciclo N83-N87 abierto, CT2 N82 permanece ultimo punto. Sin merge main, sin copias de microdatos, ni contacto de autores o aceptacion de licencias.
