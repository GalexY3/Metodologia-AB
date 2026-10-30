# N182–N184 · Auditoría documental adversarial · 2026-10-30

Los contratos [PREREG_D.json](PREREG_D.json) y [CODE_FREEZE_DOCUMENTARY.md](CODE_FREEZE_DOCUMENTARY.md) se registraron antes de ejecutar el barrido DOI completo y el dictamen de equivalencia de rivales. **Tres ciclos documentales negativos, cero contraste humano empírico**, sin descargar archivos de sujetos. El informe documental de 4634 bytes y SHA256 `5580ab58ce878dee5a63f61f8daaeafabe27e21f25d9f8be606cfea2f9606736` está en el ZIP de la conversación.

## N182 — Hallazgo de tres duplicados documentales

Entre 107 registros previos, 61 `canonical_url` contenían DOI, con 58 identificadores diferentes. Coincidencias exactas: `SRC003/SRC075` = `10.1126/sciadv.aap9815`; `SRC029/SRC093` = `10.1177/08902070241286254`; `SRC087/SRC107` = `10.3389/fcomp.2026.1893669`. **SRC107 ya estaba registrado como SRC087**: rectificación de la afirmación previa de novedad independiente. Conservar registros históricos, marcar alias/canonical y no interpretar fuente documental como cohorte. 46 entradas sin DOI en URL canónica: no prueba de unicidad.

## N183 — Baselines no equivalentes a rivales completos

Según `ESBM_SINGLE_DISCRIMINANT_FEEDBACK_PROTOCOL_20261029.md`, `ESBM_THESIS_REDUCTION_NOVELTY_GATE_NOCYCLE_20261029/REPORT.md` y `ABR_AUTH20_EXTERNAL_GATE_20261029/HYPOTHESIS_GATE.md`: B0 histórico exige composición/riesgo, el implementado es solo intercepto; B1 exige actor-target/SRM, se implementó edad+norma (NO equivalente); B2 histórico homofilia, implementado logistic con q artificial conocido (PARCIAL); B4 histórico ranking/fatiga/capacidad, implementado proxy de tiempo, exposición y términos cuadráticos (PARCIAL); B6 histórico dinámica flexible de historia/feedback y B6* saturado, implementado Gradient Boosting finito fijo (PARCIAL, **no es B6***); SRM histórico efectos cruzados, implementado promedio empírico Bayes sender/target de t<3 (PARCIAL). No afirmar victoria contra todas las clases históricas ni B6*.

## N184 — Nuevo documento no significa datos humanos independientes

`SRC108`: depósito de replicación Harvard Dataverse DOI `10.7910/DVN/27893` del artículo Bhargava/Fisman (2014), [texto primario](https://www.saurbhar.com/_files/ugd/4fc2f2_779eecedb95d4038b35f97be0303cea8.pdf), [catálogo NLM CC0 metadata](https://datasetcatalog.nlm.nih.gov/dataset?q=0000071358). El artículo cita explícitamente 16 sesiones Columbia 2002–04, **misma población subyacente** de Fisman et al. 2006/08, ya SRC016/SRC082. NLM indica CC0 a nivel catálogo, pero el archivo de Dataverse **no fue accesible** por URL primaria y no se verificaron licencias de archivos individuales, claves ni microdatos. Sin aceptaciones, autor contactado o filas leídas. Nuevo recurso bibliográfico/de depósito, **no** nueva cohorte independiente ni liberación R5.

No confundir `SOURCES = 108` registros con 108 estudios o muestras independientes. Los tres dictámenes son negativos válidos sobre trazabilidad/condiciones, no hallazgos empíricos sociológicos. **CT2 permanece 7/100, humano STOP_R5**.
