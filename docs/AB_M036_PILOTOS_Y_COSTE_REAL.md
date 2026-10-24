# AB-M036 — Presupuesto efectivo y reutilización de observaciones de piloto (24-10-2026)

**Estado: PROPUESTA OPERATIVA**, no nueva norma ni demostración de superioridad general de AB. Procede de LARP Q07–Q24, rama research/ab30-composition-pilot-20261024, PR #16; resultados completos en ZIP SHA256 82b5f789a06a501079415c0d98f7d118b3562837c69e0482a29b908f11177011.

## Riesgo diagnosticado
Un diseño adaptativo puede parecer mejor que otro diseño adaptativo (shrinkage mejora a un piloto bruto en seis fuentes) y, pese a ello, ser peor que un muestreo sin piloto bajo idéntico presupuesto total de etiquetas. El piloto consume seis etiquetas; si se excluyen de la estimación final, el comparador puede ser deliberadamente débil. Una auditoría posterior que reutiliza las seis etiquetas también obtuvo peores MSE descriptivos en las seis fuentes examinadas, pero no testea diseños multiwave óptimos.

## Propuesta de checklist antes de un experimento con adquisiciones secuenciales
1. Declarar explícitamente el presupuesto de **observaciones únicas compradas**, el número de consultas repetidas, el coste diferencial y qué se hace con las etiquetas de cada fase.
2. Ofrecer al menos un **estimador competente que utilice todas las observaciones disponibles** cuando el objetivo sea medir riesgo poblacional, conservando la propiedad de insesgamiento bajo el diseño o declarando claramente su ausencia.
3. Comparar al menos un **método de una fase con presupuesto total**, además del competidor adaptativo del mismo tipo.
4. Evitar que las simulaciones repetidas de etiquetas se interpreten como fuentes externas independientes; analizar la reutilización del test y la selección adaptativa.
5. Si un método parece superior solo a un piloto ineficiente, adjudicar 0/3 nuevo o, como máximo, 1/3 técnico estrictamente condicionado; nunca afirmar superioridad general ni originalidad 2/3.
6. En nuevos ciclos, aplicar AB-R2 y O2; esta propuesta los operacionaliza, **no** los sustituye ni acredita eficacia del método AB.

**Falsador/abrogación:** si el objetivo exige de verdad etiquetas desechables (p. ej. calibración irreversible), reutilizarlas podría ser incorrecto; no imponer este checklist fuera de su estimando. Descartar la propuesta si no modifica las decisiones frente a aplicar R2/O2 convencionales.

**Antecedentes:** JSS 2025 *optimall*, BLS 2026 *Bayesian optimal sample design for surveys with heteroscedasticity*. El principio de costes reales y comparadores competentes no es original.
