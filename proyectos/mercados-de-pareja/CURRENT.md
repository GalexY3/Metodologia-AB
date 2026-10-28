# CURRENT · Mercados de pareja · 28/10/2026, cierre parcial EVIDENCE20

**Programa:** AB-R, investigación sobre homogamia de valor sin preferencia por similitud. **Rama:** `research/ab-r-mercados-pareja-20261028`; `main` intacta. **Investigador:** Alejandro Panera Pascual. **No hay** validación causal sobre mercado de parejas real ni calibración de personas españolas disponibles para citas.

## Presupuesto y evidencias
- MATE10: 10/10; BRANCH8: 8/8; BRANCH6: 6/6 (un intento instrumental inválido reparado fuera del contador de válidos); EVIDENCE6: 6/6.
- **EVIDENCE20: 20 autorizados; 7 cerrados válidos N21–N27; 0 inválidos en este bloque; 13 autorizados NO INICIADOS**. R5: `STOP_CAMPAIGN` hasta acceder a una fuente externa discriminante. No contar el saldo como ciclos.
- EVIDENCE20: 3 DOCUMENTARY_AB N21/N22/N26, 1 FORMAL_AB N23, 1 EXPERIMENTAL_AB sintético N24, 1 REANALYSIS_AB N25 y 1 PLANNING_AB_ONLY N27. **No afirmar que los siete son experimentos**.
- [Prerregistro EVIDENCE20](research/ABR_EVIDENCE20_20261028/PREREG.json) commit `89490770`, [fuente congelada audit.py](research/ABR_EVIDENCE20_20261028/audit.py) SHA-256 `30417b2a58368f2e3df952d567923d5fb8c435c1d3b15e89d82ec62f053a6f45`, [freeze](research/ABR_EVIDENCE20_20261028/SOURCE_FREEZE.json) commit `f7e8e2d6`, [RESULTADOS por semilla](research/ABR_EVIDENCE20_20261028/SEGMENT_NULLS.csv), [QA](research/ABR_EVIDENCE20_20261028/QA_RESULTS.json), [ledger](research/ABR_EVIDENCE20_20261028/LEDGER.json), [informe](research/ABR_EVIDENCE20_20261028/REPORT.md).

## Hallazgos y límites actuales
1. **N21 nueva ancla social real:** Funcas diciembre 2025 (ESS 2024 ronda 11; convivientes 25–50 años) documenta que 53 % de mujeres españolas universitarias convivientes tiene pareja universitaria, frente a 76 % de hombres universitarios españoles convivientes. **Porcentajes condicionales distintos; no inferir causas ni tasas de Tinder**.
2. **N22 registros:** Universidad de Essex (Ortega 2018) declara Excel anonimizado CC BY y experimento ético; archivo no descargable desde este entorno, contenido no inspeccionado. SwipeStats muestra resúmenes voluntarios por perfil sin acceso procesado; no hay muestra diádica procesada.
3. **N23 teorema:** con rankings completamente alineados y todos aceptables, el único matching estable asocia a los rangos iguales; prueba por inducción y exhaustiva n2..6. Matemática conocida, no novedad 2/3.
4. **N24 control de segmentación sintético:** 4 submercados de emparejamiento aleatorio interno, r global ≈.920, r intragrupo ≈0, permuta global ≈0, permuta por sector ≈.920. **El nulo por permutación global es insuficiente para atribuir sorting a preferencias, si hay grupos distintos**. No implica que la realidad social siga estos cuatro grupos artificiales.
5. **N25 sesgo selección:** N17 previo DA r=.9085 cobertura 96.17%; adaptativo r=.4121 cobertura 41.33%; utilidad media de quienes casan mayor en adaptativo pero no compara bienestar de solteros; reanálisis sin nueva ejecución de modelos.
6. **N26 rechazo:** fuentes sobre autoestima y vigilancia digital no identifican pérdida cuantitativa automática de status externo tras swipe privado.
7. **N27 R5:** no matriz INE 60268 descargada ni fichero de 59583 recuperado ni microdatos ESS ni logs de interacciones diádicas verificables; por tanto STOP antes de gastar 13 ciclos adicionales.

## Posición metodológica
CT2 = **17/100** al inicio y cierre EVIDENCE20, trayectoria histórica 20→17→17→17→17. Escala ordinal (NO probabilidad), [gráfico escala completa y zoom](research/ABR_EVIDENCE20_20261028/CT2_TRAJECTORY.svg). N1 nuevos =0; N2=N3=0; N1 portfolio no auditado. DRIFT D0.0. `CLEAN_CLONE_NOT_VERIFIED`, ejecución local determinista comprobada; hipótesis humana `NOT_CONFIRMED`.

## Próxima acción con valor de evidencia
**Obtener el archivo público `AnonymizedData.xlsx` desde https://researchdata.essex.ac.uk/85/ y examinar sus columnas**, o microdatos ESS/INE realmente accesibles. No se debe asumir que el Excel contiene suficientes observaciones diádicas: verificarlo antes de gastar los 13 ciclos. Una nueva consulta sin fuente diferente no rompe R5. No ejecutar ciclos automáticamente desde la rama.
