# Informe de campaña AB-H N93–N106 · Dependencia de oportunidades, congestión y observación

**2026-10-29 · Rama `research/ab-h-esbm-schedule-interference-20261029` · UNMERGED.** El investigador liberó el uso de las 14 plazas históricas N93–N106 para BRANCHING/PIVOT/FORCUS útil aunque el STOP_R5 de evidencia humana siga cerrado. Se asignan **14/14 a AB-H instrumental sintético**, N93–N106, NO a 14 experimentos en humanos. Ninguna afirmación humana se reabre ni se reescribe el ESBM v2 original.

## Procedencia y orden de congelación

- **Prerregistro A–J antes de outcomes:** [PREREG_AJ14.json](PREREG_AJ14.json) commit `d9ccdef6a0905c0ed69ca1afe67c6ead50d31463`.
- **Código y tests congelados antes de outcomes:** [schedule_oracle.js](schedule_oracle.js) commit `b7684b36d518445013a4b57c6f88187a0e5c01e1`.
- **Resultados efectivos inmediatamente posteriores al freeze:** [RESULTS.json](RESULTS.json) commit `921392ae88641af4f315f481384d61994944f7f2`.
- **Ledger completo A–J:** [LEDGER_AJ.json](LEDGER_AJ.json), 14 ciclos con supuesto, estimando, adversarios, falsador, medición, resolución condicional y siguiente decisión.
- **Auditoría independiente post-outcome:** [verify_fraction.py](verify_fraction.py) usa Python estándar y aritmética racional `Fraction`, ejecutada localmente sobre las distribuciones R/A/U: `P(M=0,1,2)=[1/4,1/2,1/4]`, `[1/4,3/4,0]`, `[1/4,2/3,1/12]`; comprobación PASS. No es una confirmación preregistrada ni datos externos.
- **Argumentación formal:** [THEORY_AND_FALSIFIERS.md](THEORY_AND_FALSIFIERS.md). **Demostración interactiva:** [DEMO.html](DEMO.html), fichero local autocontenido con sliders, escenarios, ronda aleatoria y referencia exacta; renderizado en navegador **no verificado**. El código original Python ESBM `esbm_dynamic.py` no ha sido alterado.

## Resultado central y control de presupuesto

Un contraste ingenuo `independent` vs `rotation` (N94) encontró E[parejas] **0.8046875 vs 1.0** con e=.5 y p(mutual|expuesto)=.5. **Esta diferencia inicial NO aísla correlación de oportunidades**: la distribución independiente tiene varianza en número de exposiciones, mientras rotación tiene dos citas fijas. El resultado N94 desencadena la corrección de diseño N95: `uniform_two` con **exactamente dos citas**, las mismas e=.5 por arista y el mismo presupuesto. Produce E[parejas] **5/6 frente a 1** de la rotación. N96 aísla el caso más estricto: dos oportunidades que comparten una persona vs dos disjuntas, ambos exactamente dos citas y exactamente los mismos marginals; el contraste da **3/4 frente a 1**.

Este efecto surge de la **regla de exclusividad del matching**. No es un efecto social externo descubierto. En N97, al variar la probabilidad condicional de sí/sí `p` sobre .1/.5/.9, la diferencia R−A satisface la identidad `p²`; por tanto, se comprende mecánicamente el contraste y el parámetro que lo origina.

## Cada ciclo, outcome y razón de la transición

| ID | Modo y objeto | Outcome real del oráculo | Razón de siguiente |
|---|---|---|---|
| **N93** | Instrumentación base, distribuciones de oportunidad | 6 regímenes normalizados, e=.5 para cada arista | N94: intervenir en correlaciones de exposición |
| **N94** | BRANCH independientes vs rotación | 0.8046875 vs 1.0 parejas esperadas | Varianza presupuestaria confunde → N95 |
| **N95** | FOCUS presupuesto exacto de 2 citas | Uniforme-dos 5/6 frente a rotación 1 | Aislar solapamiento → N96 |
| **N96** | FOCUS dos citas que comparten persona | Adyacentes .75 frente a disjuntas 1.00 | Sensibilidad p → N97 |
| **N97** | DRIFT leve de tasa condicional | Diferencia exacta `p²` para tres tasas | Buscar medición del mecanismo → N98 |
| **N98** | Distribución de exposición por actor | Misma media 1; varianza .5 vs 0; P(cero) .25 vs 0 | No basta media → N99 |
| **N99** | Distribución de parejas | P(dos parejas): rotación .25, U 1/12, adyacentes 0 | Separar media de ley → N100 |
| **N100** | Reparametrizar preferencias | Media igual .8 con p_R=.4 y p_A≈.552786; P2 difiere .16 vs 0 | Auditar institución de desempate → N101 |
| **N101** | Matching saturado y desempate fijo | 2 asignaciones máximas; misma/otra categoría 2 vs 0 | Contrastar desempate uniforme → N102 |
| **N102** | Desempate al azar | E[parejas intragrupo]=1; 2 parejas en cualquier caso | Recuperar medición de votos → N103 |
| **N103** | Asimetría de dos votos individuales | (.5,.5) vs (.25,1) dan igual sí/sí=.25 pero diferentes votos | Considerar dependencia conjunta → N104 |
| **N104** | Igual q marginal, distinto joint | Cov(00,11) rotación +.0625 vs independiente 0 | Comparar información de observaciones → N105 |
| **N105** | Valor de logs de oportunidad vs outcome | KL 2.931780966 nats vs .590738360 nats en mezclas predefinidas | QA del muestreo → N106 |
| **N106** | 30.000 eventos MC con semilla fija | Media 1.00073333 vs exacta 1.0; P2 .2511 vs exacta .25; reproducible | STOP empírico; preparar transferencia del modelo |

Los **14 outcomes PASS** proceden del **mismo universo matemático**; no son 14 predicciones científicas independientes ni replicaciones externas. El diseño es una secuencia de condiciones instrumentales preregistradas, no una batería descubierta ex post. Cada resultado se guardó con su sucesor condicionado; no se abrieron revisiones de datos reales.

## Aporte a una explicación sociológica

La misma población con la misma disposición hacia los encuentros puede producir distinta cantidad y composición de parejas si las instituciones imponen simultaneidad, exclusividad y arreglos de oportunidades. La evidencia de un `match` final mezcla al menos cuatro operaciones: **apertura de oportunidad → consentimiento bilateral → resolución del conflicto de asignación → supervivencia en el tiempo**. Las primeras tres están representadas parcialmente por este oráculo; la cuarta queda fuera y ESBM v2 ya incluye un hazard artificial no calibrado.

Esto refuerza una distinción sociológica: no equiparar una regularidad agregada de vínculos con una preferencia individual latente. Aun el control por oportunidades marginales puede ser insuficiente: importa **su distribución conjunta** y la política de selección cuando hay más de una opción mutua. No inventar costes sociales, motivaciones personales, dinámicas de género ni bienestar: las normas aquí no son preferencias observadas, sino reglas de capacidad y calendario. Antecedentes directos de oportunidades y matching ya figuran en fuentes SRC017, SRC054 y SRC098; la tesis general no se reivindica como descubrimiento original.

## Priors y estado científico tras campaña

- Nuevo prior cualitativo **P-SCHEDULE-CORRELATION**, estado `SYNTHETIC_MATHEMATICAL_ONLY_NOT_HUMAN_VERIFIED`, justificado por demostraciones exactas. No es un prior probabilístico de comportamiento humano.
- Revisiones append-only **U167** nuevo prior, **U168** P-OPPORTUNITY sin cambio empírico, **U169** P-NOVELTY sin cambio por antecedentes y falta de evidencia humana. **106 SOURCES**, **31 PRIORS** y **169 UPDATES**, sin registrar como externas las pruebas propias.
- **Ciclos originales AB-R con humanos/simulaciones históricas:** 26 válidos hasta N92. **Bloque ahora transferido explícitamente a AB-H:** 14/14 tests internos válidos N93–N106, 0 inválidos, 0 planning y 0 nuevos tests AB-R empíricos. El cupo 14 queda usado en AB-H, sin cambiar retroactivamente el significado de 26/40 AB-R históricos.
- **CT2 originalidad ESBM: 7/100 ordinal, no calibrado, sin subida.** Madurez científica ponderada vigente **41.20 % subjetiva**, sin recálculo automático: el paquete nuevo todavía no se integra en Python ESBM ni resuelve la validación externa. N1 nuevos=0, N2=N3=0, grado científico nuevo **0/3**.
- **STOP_R5_EXTERNAL** permanece. SRC104 conserva anomalías, no se editó ningún voto ni ID; no se accedió a rutas humanas bloqueadas, ni se aceptaron licencias, ni se contactó con personas, ni se hizo merge a main.

## Reparos y puertas futuras

El estimando del modelo es `E[# de parejas exclusivas simultáneas]`, no éxito romántico, relación duradera, utilidad ni efecto causal humano. Las desigualdades matemáticas son transportables solo si los supuestos también lo son, extremo no demostrado. La probabilidad `p` corresponde a un consentimiento **mutuo agregado** condicionado a una cita, y no reemplaza dos decisiones nativas observadas; N103 advierte precisamente de la diferencia. Las reglas de desempate del oráculo son una política artificial (orden descendente de máscara binaria), no un principio de igualdad o racionalidad humana.

El siguiente trabajo ejecutable, sin inventar humanidad, es **integrar módulos de oportunidad conjunta en el Python ESBM v2 con comparación de invariantes al oráculo y reportes por periodo**. Los cambios de política requerirán nuevos contratos A–J, seed freeze, paridad y controles sham; no se podrá usar ninguno de estos 14 resultados como holdout nuevo. Para el avance científico hacia 2/3 aún hacen falta nuevos datos humanos utilizables legalmente, dos votos nativos, exposiciones reales, reglas de matching observadas, comparadores fuertes y una predicción original externa al generador.

**AB-DECIDE:** `AB-H BRANCH_COMPLETE` y `AB-R STOP_R5_EXTERNAL`. Se usaron los 14 créditos libres autorizados para una intervención sintética de una clase nueva; no existe saldo pendiente en ese lote. No hubo hallazgos humanos nuevos ni subida CT2 por volumen de pruebas.
