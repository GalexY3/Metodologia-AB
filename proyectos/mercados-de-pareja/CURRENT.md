# CURRENT · Mercado de pareja · 28/10/2026, después de EVIDENCE6

**Proyecto:** investigación AB-R sobre homogamia de valor emergente sin preferencia explícita por semejanza. Rama `research/ab-r-mercados-pareja-20261028`, no fusionada a main. **No hay inferencias causales humanas ni un modelo calibrado a usuarios españoles.**

## Campañas cerradas
- MATE10: **10/10** (6 experimentales sintéticos + 4 documentales).
- BRANCH8: **8/8** (5 experimentales sintéticos + 3 documentales); N03 inconcluso.
- BRANCH6: **6/6** (3 experimentales + 3 documentales/planning); 1 intento de código inválido, reparado y no contado.
- EVIDENCE6: **6/6 autorizados y completados en alcance**, N15/N16/N19 documentales, N17/N18 experimentales sintéticos, N20 planning. 45 ejecuciones sintéticas (9 condiciones x 5 semillas) distintas de los 6 ciclos; 0 intentos inválidos. **Saldo 0.**

## Resultados y límites EVIDENCE6
- N15: INE ECP 59583 identificado; acceso directo a descarga y API bloqueado. Sin suma oficial verificada 20–39 por sexo al 1/7/2026; no usar total de residentes como personas elegibles para mercado Tinder.
- N16: INE matrimonios 60268 identificado; matriz educativa real no descargada; **NO** calculado O/E ni control por márgenes, ni validación con parejas 2026.
- N17: N240, k20 mismo grafo: Gale-Shapley r≈0.9085, cobertura≈96.17%, 0 pares bloqueantes; greedy r≈0.0172, cobertura≈97%; adaptive r≈0.4121, cobertura≈41.33%. Información de grafo compartida ex ante, no paridad de política temporal. No novedad fuerte ni supremacía del umbral adaptativo.
- N18: grafo idéntico y sin salida durante fase de vistas. q fijo: sincrónico y asíncrono persistente **exactamente idénticos** en cinco semillas (r≈0.4774, cobertura≈11.5%); identidad bajo reglas fijas, no hallazgo social. TTL de 5 posiciones reduce cobertura; r inestable por pocos matches. Fatiga/percepción temporal generan diferencias internas.
- N19: rechazo en apps mayormente no señal pública a terceros por defecto; literatura sobre autoestima, unmatching y awareness cues **no** estima δ universal de pérdida reputacional ante terceros.
- N20: prueba confirmatoria futura formalizada, **NO EJECUTADA** por falta de datos humanos y necesidad ética.
- Validación: código [experiment.py](research/ABR_EVIDENCE6_20261028/experiment.py) íntegro versionado, [freeze](research/ABR_EVIDENCE6_20261028/SOURCE_FREEZE.json), [per-seed RUNS](research/ABR_EVIDENCE6_20261028/RUNS.csv), [SUMMARY](research/ABR_EVIDENCE6_20261028/SUMMARY.csv), [QA](research/ABR_EVIDENCE6_20261028/QA_AND_ERRATA.json), [ledger A–J](research/ABR_EVIDENCE6_20261028/LEDGER.json), [informe](research/ABR_EVIDENCE6_20261028/REPORT.md).
- Fuente SHA256 congelada 2028d687102c211a2bc31994a80985d643aaf48752a5da21b3bf5ae0e1072dc3. La ficha de freeze anotó tamaño equivocado 6909; tamaño real 6972, errata QA. Archivo remoto byte-equivalente verificado por FNV-32. Corrida local reproducida byte a byte, **CLEAN_CLONE_NOT_VERIFIED**, sin réplica externa.
- CT2 por rama: **20 (MATE10 post hoc) →17 (BRANCH8)→17 (BRANCH6)→17 (EVIDENCE6)**, ordinal y no probabilidad. N1 nuevos=0, N2=0, N3=0, N1 histórico portfolio NO_AUDITED. Gráfica completa y ampliada [CT2](research/ABR_EVIDENCE6_20261028/CT2_TRAJECTORY.svg). DRIFT D0.0.
- R5: **STOP_CAMPAIGN**, siguiente evidencia de más valor es acceso efectivo a datos y baseline ético con preferencias/actualizaciones observables. Ampliar semillas o millones de agentes no repara denominador ni reputación.

**NO ejecutar más ciclos automáticamente.** Solicitud siguiente en informe: BRANCHING 20 condicionados a datos externos nuevos, no autorizada, y detener bajo R5 si continúa el bloqueo.
