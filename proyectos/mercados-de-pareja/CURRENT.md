# CURRENT · Mercados de pareja · 28/10/2026, después de BRANCH6

**Proyecto:** `AB-R`, rama `research/ab-r-mercados-pareja-20261028`, independiente de `main`, no fusionado. **Pregunta:** ¿puede emerger homogamia de valor por maximización bilateral sin preferencia directa por semejanza? Antecedentes de matching estable impiden reclamar novedad genérica; todas las correlaciones del generador son **sintéticas**.

## Contabilidad histórica, campañas distintas
- `MATE10`: 10/10 cerrados, 4 documentales y 6 experimentales exploratorios.
- `BRANCH8`: 8/8 cerrados, 3 documentales y 5 experimentales; N03 inconcluso.
- **`BRANCH6`: 6/6**, 3 ciclos `EXPERIMENTAL_AB` N09–N11 y 3 `PLANNING_AB_ONLY` N12–N14. **Un intento instrumental inválido** adicional, corregido y **no contado**. 60 corridas sintéticas válidas, 5 semillas, 12 variantes clasificadas por diseño.
- **Saldo autorizado: 0.** N1 nuevos=0, N2=0, N3=0. CT2 en cierres 20→17→17; ordinal no probabilidad, [gráfica](research/ABR_BRANCH6_20261028/CT2_TRAJECTORY.svg).
- [PREREG BRANCH6](research/ABR_BRANCH6_20261028/PREREG.json), [ledger A–J](research/ABR_BRANCH6_20261028/LEDGER.json), [informe](research/ABR_BRANCH6_20261028/REPORT.md), [resultados por semilla](research/ABR_BRANCH6_20261028/RUNS.csv), [resumen](research/ABR_BRANCH6_20261028/SUMMARY.json), [QA y prerregistro del intento inválido](research/ABR_BRANCH6_20261028/QA_AND_GATES.json), [fuentes oficiales/limitaciones](research/ABR_BRANCH6_20261028/SOURCES_AND_LIMITS.md).

## Hallazgos BRANCH6
- **N09** mismo grafo ex ante: DA k60 r=.917, cobertura 98.2%; adaptativo r=.711 cobertura 80.5%; aceptación greedy r=.035 cobertura 98.6%. DA usa rankings completos, por lo que no hay paridad informativa pese a grafo idéntico.
- **N10** pools balanceados y 40 exposiciones distintas programadas: 100 agentes r=.726, 300 r=.741, 1200 r=.737; coberturas 59.9%/60.3%/59.4%. Sin gradiente monotónico sólido; corrección de interpretación fuerte previa. Gate piloto superado antes de semillas adicionales, sin retuning.
- **N11** mismo grafo planificado: simultáneo r=.633, async persistente r=.444, async caduca cinco ticks r=.396; exposiciones efectivas desiguales por salidas endógenas.
- **N12** INE ECP oficial total 49.801.559 julio 2026, pero **no** se extrajeron celdas nacionales 20–39 por sexo ni denominador de solteros activos; tabla nacional 59583 identificada. `DATA_BLOCKED`.
- **N13** tabla INE 60268 con cruce de estudios de hombre/mujer identificada, pero matriz no descargada: sin O/E ni tasas inventadas. `ANALYSIS_BLOCKED`.
- **N14** estudios de rechazo y vigilancia digital verificados; **no** identifican penalización de estatus universal por swipe.

## Ejecución y límites
`PREREG` commit `58539794`; inicial source freeze `a7eeef16`; primera corrida **INVALID** (falsa detección de pares bloqueantes por indexación errónea); reparación freeze `14059774`, SHA-256 fuente válida `6f351329c3c9fdc5aad83dcb719962dc022b8b17203b94e6661ed322ffe0b632`. Reejecución local con hashes de resultados idénticos. **Archivo completo de código local en ZIP entregado en conversación; carga al repositorio GitHub de gzip/base64 bloqueada por controles de la interfaz**. No se puede afirmar clon limpio verificado, ni fuente Python íntegra versionada en GitHub. GitHub sí conserva los registros y CSV. No ha habido replicación humana ni identificación causal externa.

## Estado J y propuesta futura
`STOP_CAMPAIGN`; bloqueadores: igualación de información DA y dinámico, recuento de oportunidades realizadas, matriz educativa española completa, evidencia de mercado activo y canal reputacional real. [Próxima propuesta, no autorizada](NEXT_6_EVIDENCE_GATED.md). **No comenzar automáticamente nuevos ciclos**.
