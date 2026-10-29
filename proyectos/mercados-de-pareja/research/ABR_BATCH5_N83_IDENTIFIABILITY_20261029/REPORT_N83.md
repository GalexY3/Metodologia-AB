# Informe N83 · Contraejemplo exacto de identificabilidad de oportunidades y decisiones recíprocas

**Ciclo formal válido, negativo. No validación humana.** 29/10/2026, rama `research/ab-r-mercados-pareja-20261028`.
Prerregistro **antes de ejecutar**: [PREREG_N83.md](PREREG_N83.md), código [n83_identifiability.js](n83_identifiability.js), commit inmutable `50ed5bacab76951157ed87447d61d26737701130`, SHA256 código `e4275309e5c7e5d4b63d8ce0eb5de709d4e8b1136f437df2db5290467587463f`. Se verificó el HEAD contra dicho commit antes del primer resultado. El instrumento calculó las ocho celdas de probabilidades y diez aserciones; todas correctas. Ver [RESULTS_N83.json](RESULTS_N83.json). Contraste independiente posterior con Python `fractions.Fraction`: mismas ocho fracciones exactas y resultados de `do(E)`, no se contó como segundo ciclo. Ledger completo [LEDGER_N83.json](LEDGER_N83.json).

## A–J y explicación

A–D: condición E binaria de conjunto de oportunidades menor/mayor, dos decisiones Y_i,Y_j nativas, U no observado. **A**: U causa oportunidades y elecciones pero E no altera decisiones; **B**: E asignado al azar y se eligen probabilidades conjuntas condicionales iguales a las observadas bajo A. Distribución observada exacta:
| E | Yi | Yj | Numerador sobre 250 |
|---:|---:|---:|---:|
| 0 | 0 | 0 | 50 |
| 0 | 0 | 1 | 35 |
| 0 | 1 | 0 | 20 |
| 0 | 1 | 1 | 20 |
| 1 | 0 | 0 | 20 |
| 1 | 0 | 1 | 20 |
| 1 | 1 | 0 | 35 |
| 1 | 1 | 1 | 50 |
En cada modelo son **idénticas** las ocho probabilidades. P(E=1|U) de A toma 0.2 y 0.8, con soporte positivo; P(E=e)=0.5, todas las celdas tienen masa positiva.

E–F: resultados observados de ambos modelos: P(sí/sí|E=0)=0.16 y |E=1=0.40; contraste asociativo +0.24. **Intervención contrafáctica**:
- Modelo A: P(sí/sí|do(E=0))=P(...|do(E=1))=0.28 → efecto 0.
- Modelo B: P(sí/sí|do(E=0))=0.16 y |do(E=1)=0.40 → efecto +0.24.
A pesar de valores idénticos de toda la distribución observada, el efecto causal no queda determinado. Esto prueba la falsedad de la afirmación universal «con oportunidades E y dos yes/no basta para identificar el efecto causal del conjunto de oportunidades», pero **no prueba** que no sea identificable bajo supuestos adicionales.

G–H: rival competente es la distribución conjunta saturada de las ocho celdas, que ajusta ambos DGPs exactamente; no se ha escogido control débil. Aserciones de normalización, positividades, igualdad y diferencias causales pasan y se comprobaron de nuevo con fracciones exactas. Resultado algebraico, no ajuste a 54 personas McMaster, sin datos personales ni efectos sociales reales. La confusión no observada es un problema clásico: cero descubrimiento 2/3, N1 local nuevo 0, N2 0, N3 0. La hipótesis H-RISKSET-VETO debe etiquetar **predicción** y **causalidad** por separado.

I: registrar `U131` bajo `P-OPPORTUNITY`, **NO_CHANGE_WITH_REASON**, con prueba de límite de identificación. Mantener 97 fuentes, 30 priors, **131** revisiones. Indicadores de madurez: teoría 60→62 por límite formal explícito, QA 50→51 por instrumento precongelado y prueba exacta, global **38.25→38.65%**, redondeo **39%**: estimación de hitos, no probabilidad científica. Validación externa queda 5%, originalidad 10%.

J: dictamen **N83 válido FORMAL NEGATIVO**, no inválido ni planning; presupuesto 16→17 válidos históricos, 24→23 plazas pendientes, de las cinco N83–N87 inicialmente liberadas queda **N84–N87 (4)** y **N88–N106 (19)** reservadas. CT2 ordinal sigue **7/100**, con **punto auténtico N83=7** y gráficos [0–100 + zoom](CT2.svg). **STOP_R5 para experimentos humanos externos** sigue vigente. R1–R5 cumplidos en ámbito formal, no se confunde ausencia de datos externos con fracaso de prueba matemática. Reapertura de un test causal humano exige randomización o condiciones de ignorabilidad justificables, interferencia evaluada, competidores SRM/Pronk/Rios/Joel/Baxter y muestra externa independiente. No utilizar este resultado formal para elevar confianza en validez ESBM.

**Por qué N84–N87 no se consumen en esta respuesta:** no se ha ejecutado todavía otro instrumento nuevo y discriminante con prereg congelado y fuerte control. Más explicaciones del mismo teorema o simulaciones de supuestos ya conocidos no son nuevos ciclos. El usuario autorizó *hasta* cinco, no cinco entregables obligatorios.
