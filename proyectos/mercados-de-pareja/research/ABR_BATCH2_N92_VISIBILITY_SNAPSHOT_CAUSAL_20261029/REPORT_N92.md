# N92 — Reparación delimitada de la invariancia frente a ID en ESBM

**Ciclo técnico sintético válido; 0/3 sociológico.** [Contrato A–J](PREREG_N92.md) y [código fuente congelado](n92_snapshot_test.py.gz) en commit PRE-ejecución `0d3260968405fd3ea070d0877f29ea04471140b3`, script SHA256 `3006583df8d3f95a8ee6a43d6ef665c44578229956e9aed8e220bf04ad484480`, fuente original SHA256 `f7e6b84000720cbdf2ee0800c2b10d136185facd00e4622756cbb5f8d8254d0b` y reutilización de N91 SHA256 `2ea5b39520f86dd35d760f6d29ddac26ff839afa1289aebbb034cf3ceeb2e791`, todo comprobado ANTES de ejecutar. El archivo fuente v2 histórico no ha sido editado: el parche se aplica exclusivamente al código compilado en memoria.

## Predicción discriminante

N91 encontró un fallo de equivarianza: renombrar a las mismas personas cambió las formaciones en **18/18** corridas `visibility_balancing`. La hipótesis concreta N92 es que `seen[j]+=1` durante el bucle de agentes y `scores += -1.4*log1p(seen[candidates])` mezcla la información de distintos remitentes en un mismo período. La alternativa `snapshot` toma `seen_tick_start=seen.copy()` al comienzo del período y usa esa copia **solo para el ranking**, conservando la actualización real de impresiones y el resto de funciones.

## 60 simulaciones reales congeladas

| Control/contraste | Resultado |
|---|---:|
| Otras dos políticas sin término `seen`: original vs patch | **12/12 coincidencias exactas** |
| Original `visibility_balancing`: relabel cambia formaciones | **18/18** |
| Variante snapshot: relabel cambia formaciones | **0/18** |
| Variante snapshot: cualquier campo de resultado cambia con relabel | **0/18** |
| Efecto snapshot−original en formaciones, seis semillas identidad | **−10,00 de media** |
| Efecto snapshot−original en Gini, seis semillas identidad | **+0,005770 de media** |

Las diferencias en parejas formadas por seed (snapshot−original) son: `101:+8`, `211:−16`, `307:−13`, `401:−30`, `503:+13`, `601:−22`. El signo no es uniforme. El cambio propuesto soluciona la dependencia de etiquetas **en estos seis seeds y permutaciones**, pero modifica los resultados y no puede sustituir silenciosamente la política original en informes históricos.

## R1–R5, A–J y actualización

A–C: inferencia de causalidad **solo dentro del programa artificial**. D–G: misma fuente verificada, shocks pareados, 60 ejecuciones con 12 shams exactos y control de inversión de todas las matrices exógenas. H: comparación deliberadamente posterior al hallazgo N91, sin réplica independiente ni evidencia humana; una reparación de software conocida no es novedad de predicción sociológica. I: `U145` P-PLATFORM-RANKING y `U146` P-OPPORTUNITY no cambian estados; **97 fuentes / 30 priors / 146 revisiones**, CT2 ordinal 7. J: N92 es ciclo técnico sintético válido 0/3, conserva STOP_R5 externo y no reivindica efecto causal de una plataforma real.

**La segunda tanda N88–N92 termina 5/5 válidos**. Se han ejecutado cinco contrastes técnicos, pero **no cinco descubrimientos originales**. Total acumulado **26/40** válidos; 14 restantes N93–N106 siguen reservados y **no liberados**, sin nuevas autorizaciones. La madurez ponderada alcanza **41.20%** exclusivamente por simulador y QA, sin subir originalidad científica (10%) ni validación externa (5%).

[Ledger A–J](LEDGER_N92.json) · [Resultados completos por semilla](RESULTS_N92.json.gz) · [Resultado compacto](RESULTS_N92_SUMMARY.json) · [CT2 completa y ampliada](CT2.svg). No se han publicado datos personales ni usado SSJY, aceptado licencias, contactado autores o fusionado main.