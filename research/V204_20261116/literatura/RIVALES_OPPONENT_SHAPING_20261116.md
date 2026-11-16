# Rivales adicionales y alcance de lectura

**LOLA (AAMAS 2018).** Leído el artículo original, especialmente sección 4.2 y ecuaciones 4.2–4.4: el backward original detiene el multiplicador de la corrección. V204 implementa esa ecuación; no el gradiente completo de un objetivo finito de lookahead. La sede ICLR2018 registrada por error en un ledger V203 está corregida mediante errata explícita. [Primario](https://arxiv.org/pdf/1709.04326).

**POLA (NeurIPS 2022).** Leídas motivación, sección 3 y formulación ideal/outer: ya trata la dependencia de LOLA respecto a parametrizaciones conductualmente equivalentes. Su resultado de invariancia ideal requiere unicidad del óptimo; las implementaciones prácticas son aproximaciones. La fórmula V204 depende de cómo se parametriza la historia y no supera esa contribución. No se ha implementado POLA aquí. [Primario](https://proceedings.neurips.cc/paper_files/paper/2022/file/a882dab38011264d2ca8dba3cca9faf1-Paper-Conference.pdf), [código de los autores](https://github.com/Silent-Zebra/POLA).

**SOS (ICLR 2019).** Abstract e introducción consultados; método y demostraciones todavía pendientes de auditoría. Advierte que LOLA puede impedir convergencia y propone combinar shaping y LookAhead. No afirmar que un fracaso LOLA agota rivales de actualización consciente. [Primario](https://arxiv.org/abs/1811.08469), [código](https://github.com/aletcher/stable-opponent-shaping).

**MATE (2024).** Leídos abstract, contexto y secciones 4.1–4.2, ecuaciones 3–5. El protocolo de solicitudes/respuestas y la recompensa max/min son prescritos; no equivalen a transferencias monetarias conservadas. Por ejemplo, si todos solicitan y aceptan tokens de valor x, la ecuación 5 agrega 2x a la recompensa de cada agente, sin contrapartida monetaria. Es una inferencia algebraica sobre su formulación, no un error imputado a los autores: su objetivo declarado es shaping. Sirve como rival de cooperación con reciprocidad programada, no como evidencia automática de institución inventada por aprendices que maximizan utilidad monetaria. Falta auditar y ejecutar su código. [Primario](https://doi.org/10.1007/s10458-024-09666-5).

**McAvoy et al. (PNAS 2025).** Abstract y antecedentes leídos; descubre estrategias que imponen relaciones de pagos en juegos estocásticos. Falta auditoría completa y ejecución. No reinventar alineación unilateral por relaciones lineales como si no existiera. [Primario](https://doi.org/10.1073/pnas.2319927121).

Esta revisión orienta competencia y prioridad; no acredita superioridad ni replica experimentos ajenos.
