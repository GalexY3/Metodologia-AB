# CURRENT · Mercado de pareja · 28/10/2026 (después de BRANCH8)

**Rama de trabajo:** `research/ab-r-mercados-pareja-20261028`. No fusionada a `main`. Estudio AB-R sobre homogamia de valor emergente sin preferencia explícita de semejanza; **NO** identificado causalmente para población española. No puntuar personas reales.

## Campañas
- **MATE10**, cerrado anteriormente: 10/10 (4 documentales, 6 experimentos), tres semillas, nivel científico 2/3 no acreditado. [Informe](research/ABR_MATE10_20261028/REPORT.md), [ledger](research/ABR_MATE10_20261028/LEDGER.json).
- **BRANCH8**, autorización expresa del investigador: **8/8 completados** dentro de alcance, 5 `EXPERIMENTAL_AB` sintéticos (N01–N05), 3 `PLANNING_AB_ONLY` documentales (N06–N08); 0 `INVALID` detectados, pero **N03 inconcluso**; **0 ciclos autorizados restantes**. [Informe](research/ABR_BRANCH8_20261028/REPORT.md), [ledger A–J](research/ABR_BRANCH8_20261028/LEDGER.json), [PREREG](research/ABR_BRANCH8_20261028/PREREG.json).
- Code freeze `d68c9f54`, SHA256 `39c693a8...`; 14 condiciones x 3 semillas = 42 ejecuciones sintéticas. [Fuente congelada](research/ABR_BRANCH8_20261028/experiment.py.gz.b64), [Resultados por semilla](research/ABR_BRANCH8_20261028/RUNS_COMPACT.csv), [QA](research/ABR_BRANCH8_20261028/ALT_LOCAL_AUDIT_20261028.json). Reejecución local determinista, **clon limpio no verificado**.
- **Concurrencia instrumentada:** existe además otra implementación `SOURCE_FREEZE.json` SHA256 `a4c48335...` con [RESULTS.csv](research/ABR_BRANCH8_20261028/RESULTS.csv), [HAZARDS.csv](research/ABR_BRANCH8_20261028/HAZARDS.csv), [Q_TRACK.csv](research/ABR_BRANCH8_20261028/Q_TRACK.csv). **NO** sumar como otros ocho ciclos ni combinar números sin reconciliar protocolos. [Auditoría comparativa](research/ABR_BRANCH8_20261028/AUDITORIA_CRUZADA.md).

## Resultados importantes dentro del generador
- N01: Gale-Shapley con información completa r≈.944, cobertura≈99.8%, 0 pares bloqueantes; búsqueda temporal r≈.858, cobertura≈85.7%, ~1961 pares bloqueantes. **No hay ventaja general del procedimiento adaptativo**; comparador no tiene paridad informativa todavía.
- N02: reacción al rechazo eleva cobertura de 54.3% a 71.6% y r condicional de .913 a .940 en el escenario fijado; el decil superior se empareja antes.
- N03: únicamente 1.3–1.6% emparejados, por lo que el test local es inconcluso.
- N04: asincronía/historia de likes difiere en oportunidades y cobertura; comparaciones descriptivas sin identificación pura.
- N05: difusión privada de rechazo sin efecto si rechazador no reconsidera; global reduce cobertura 60.9% →55.1% por regla impuesta.
- N06: censo ECP por sexo y edad **no mide** soltería activa ni uso de apps. 20–39 de julio fuentes secundarias pendiente cotejo con INE.
- N07: Censo 2001 educativo 69,15% mismas cinco categorías entre parejas heterosexuales, observación **histórica sin control de márgenes**; no usar como validación del modelo.
- N08: prueba externa solo **planificada, NOT_EXECUTED** por ausencia de datos/instrumentos y necesidad ética.
- N1 contados: 0, N2/N3: 0. CT2 previa 20/100 post hoc, revisión post BRANCH8 17/100, ordinal no probabilidad; [gráfica completa y ampliada](research/ABR_BRANCH8_20261028/CT2_TRAJECTORY.svg).

## Próximo bloqueo R5
Paridad de oportunidad con modelo estable; red/horario de exposición; medición social de reputación; baseline español actual con elegibilidad y matriz educativa ajustada; fuente humana ética. [Propuesta siguiente, NO AUTORIZADA: 6 ciclos BRANCHING](NEXT_6_PROPOSAL.md). No iniciar sin confirmación humana.
