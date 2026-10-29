# AB-R N88 — Influencia institucional del emparejamiento centralizado en ESBM

**Ciclo válido computacional sintético, 0/3 originalidad.** Primera prueba de la nueva tanda N88–N92. Documentación A–J y SHA256 del código original congelados ANTES de resultados en commit `c4b9442c9ffdcc1f792987df4171a2ca79e752cc`. [Preprerregistro](PREEXEC_AJ_N88.md), [manifiesto](CODE_FREEZE_MANIFEST.json), [código original sin alterar comprimido Brotli](n88_assignment_audit.py.br), [ledger](LEDGER_N88.json), [resultados detallados por escenario](RESULTS_N88_SUMMARY.json). SHA256 de código descomprimido `0218886d3d52c4557cf8a54066cd931e349a74114c80ee687f72fd67d0ae98af` (idéntico al manifiesto previo), archivo Brotli SHA256 `002c8d25205db82e4b1389d2507eb0f9328247239c0c4a8995aa9a4a005682a3`. Para reproducir, descomprimir con biblioteca Python `brotli`, verificar SHA256 y ejecutar `python n88_assignment_audit.py --original esbm_dynamic.py --output results.json`.

## Prueba realmente ejecutada

Original v2 Python SHA256 `undefined`; 6 semillas ×10 escenarios ×4 brazos = **240 simulaciones reales de Python**: original, control instrumental central idéntico, greedy por los mismos pesos de arista y greedy por orden de actor. Los 60 controles centrales repiten **exactamente cada campo del original**; se restauró operador NetworkX en `finally`. Dentro de cada brazo, en cada tick, la alternativa central cardinalmente domina a ambas greedy sobre el MISMO grafo de consentimientos. Entre brazos cambia la disponibilidad futura: no confundir maximización instantánea con máximo acumulado. En cada brazo se conserva formado − disuelto = activo. Sin datos de personas.

## Estimandos principales: central menos alternativa, media emparejada sobre 60 corridas

| Resultado | Greedy por peso | Greedy por orden de actor |

|---|---:|---:|

| Relaciones formadas acumuladas | +9.5167 | +7.7000 |

| Relaciones activas al final | +2.1167 | +0.7667 |

Central formó una media de **227.8** relaciones por simulación y terminó con **60.6667** activas: la brecha +9.5167 supone **4.18%** de la media central, **por debajo del umbral descriptivo 5% fijado para el agregado**. Con los dos tipos de greedy, la diferencia aparece en 680 y 595 grafos de tick respectivamente. No se calcularon p-valores confirmatorios ni se afirmó superioridad humana.

## Heterogeneidad y resultado adversarial

| Escenario | Δ formadas vs greedy peso | Δ activas vs greedy peso | Δ formadas vs greedy actor | Δ activas vs greedy actor |

|---|---:|---:|---:|---:|

| mixed_random | 3.67 | 3.00 | 8.50 | 0.00 |

| heterosexual_restricted | -1.00 | 1.83 | -3.67 | 1.83 |

| institutional_segregation | 6.50 | 2.83 | 7.50 | 0.83 |

| explicit_norm_preference | 9.50 | 2.50 | 2.67 | 2.50 |

| popularity_ranking | 5.00 | 4.67 | 4.17 | 1.83 |

| visibility_balancing | 13.00 | -1.17 | 16.17 | -1.33 |

| private_rejection_learning | 15.67 | 2.83 | 11.17 | 1.33 |

| public_rejection_signal | 13.67 | 3.33 | 7.50 | 1.33 |

| longer_partnerships | 5.83 | -0.33 | 3.33 | -0.50 |

| shorter_partnerships | 23.33 | 1.67 | 19.67 | -0.17 |

En el escenario `heterosexual_restricted` el operador central tuvo **menos formaciones acumuladas** que las dos alternativas (−1 y −3.67), pese a que en el mismo grafo de cada período maximiza cardinalidad. El signo también cambia para la cantidad activa en determinados escenarios. No es un fallo lógico: los emparejamientos cambian a quién queda disponible después. Con ello se **acota** una conclusión de ESBM: sus resultados no proceden solo de decisiones bilaterales, sino de la regla institucional de asignación y la realimentación temporal. Esto es sensibilidad estructural, no descubrimiento causal social.

## R1–R5, registros y alcance

R1: encuentros y uniones artificiales; no relaciones observadas. R2: dos baselines descentralizados competentes, uno con los mismos pesos/semillas y otro con prioridad institucional distinta, más sham central exacto; no modelo empírico humano. R3: A–J y SHA congelados antes de ejecución; sin outcome externo no hay confirmación. R4: cambio algorítmico produce redes futuras diferentes, efecto de política interna del modelo, sin transportabilidad. R5: **STOP_R5** permanece para predicción empírica nueva. 
U137 P-ACTION-SEMANTICS y U138 P-OPPORTUNITY sin cambios de estado; 97 fuentes, 30 priors, 138 revisiones. CT2 ordinal 7/100 no aumenta. Madurez ponderada **40.05%**, aumenta solo simulador y QA; novedad 10% y validez externa 5% no cambian. 22/40 ciclos válidos, 18 restantes: N89–N92 cuatro disponibles, N93–N106 catorce reservados; ningún ciclo abierto adicional. No hubo SSJY, licencias, autores, OSF/Essex/Stanford/Gist, microdatos ni fusión a main.

Fuente original, script completo congelado (Brotli) y outputs agregados son verificables; JSON íntegro de los 60 pares en runtime: SHA256 `051df4293751846c532f1d720b84b40d89ac8471f2763391e320734ec50264df`. No confundir code SHA en GitHub con publicación del repositorio privado.