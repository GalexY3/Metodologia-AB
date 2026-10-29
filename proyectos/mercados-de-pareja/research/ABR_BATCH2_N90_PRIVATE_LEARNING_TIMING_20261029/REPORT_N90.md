# N90 — Rechazo y aprendizaje privado: actualización inmediata frente a diferida

**Ciclo AB-R sintético válido, grado científico 0/3.** Congelación A–J y código antes de resultados: commit `5f59462e03fb5af198c7824bafdaf37a3512ac3d`, [PREREG_N90.md](PREREG_N90.md), [código gzip](n90_private_timing.py.gz), SHA256 código `0dd721ea30a5e89b465fd2e22234dcb8af94835eb537e51ffe4c1223bddecb33`. Fuente original SHA256 `f7e6b84000720cbdf2ee0800c2b10d136185facd00e4622756cbb5f8d8254d0b`. Se ejecutó script Python realmente en sistema local, no reconstrucción de resultados.

### Qué distingue
ESBM v2 aumenta `private_bias[i]` en +0.08 (máximo .80) **inmediatamente tras un rechazo**, dentro del bucle secuencial de propuestas de un mismo período. La variante `next_tick` conserva exactamente las mismas señales y monto por rechazo, pero las acumula y solo cambia la propensión en el período siguiente. La variante `silent` acumula sesgo sin modificar conducta, control igual a `private=False`. Son tres estructuras temporales y no tres mediciones de personas reales.

Se ejecutaron **120 simulaciones**: 4 contextos ×6 semillas×3 versiones, más 24 originales con aprendizaje y 24 sin aprendizaje. Los dos bloques de 24 controles `sham` resultaron **exactamente iguales** al original; todos los contadores e invariantes pasaron. La instrumentación detectó **14.053 ocasiones** en las seis corridas principales en que decisiones de proposición posteriores de un mismo período usaron un `private_bias` ya incrementado por rechazo. Esto es una oportunidad potencial de efecto, no 14.053 cambios de decisión demostrados.

### Principal: política aleatoria y seis semillas

| Media sintética | Inmediato original | Aplicado al siguiente período | Sin señal |
|---|---:|---:|---:|
| Relaciones formadas | 247.00 | 243.33 | 226.67 |
| Relaciones activas final | 66.17 | 63.50 | 62.00 |
| Propuestas emitidas | 2020.67 | 2001.00 | 1646.83 |
| Respuestas positivas | 509.67 | 501.17 | 417.83 |

Diferencia emparejada I−L en formadas = **+3.67** media, pero seis deltas **[−11,+11,+9,−12,+18,+7]**: no hay una ganancia universal por semilla. Diferencia inmediata−sin señal de relaciones formadas = +20.33; *no interpretar como psicología real*.

### Sensibilidad por contexto, controles predefinidos

| Contexto artificial | Formadas inmediato | Formadas próximo tick | Formadas sin señal | Δ inmediato−siguiente |
|---|---:|---:|---:|---:|
| mixed_random | 247.00 | 243.33 | 226.67 | 3.67 |
| popularity_ranking | 239.50 | 236.50 | 223.50 | 3.00 |
| institutional_segregation | 231.00 | 226.00 | 218.67 | 5.00 |
| explicit_norm_preference | 247.67 | 242.67 | 241.17 | 5.00 |

### A–J, R1–R5 y decisión

A–C: contraste de calendario de feedback, no cambio real de umbrales de pareja en humanos. D/E: código original SHA-verificado, fuente exacta congelada antes de la ejecución, 120 corridas de misma población sintética. F/G: 48 controles idénticos y 14.053 oportunidades de procesamiento intraperíodo, diferencias de resultados heterogéneas. H: variación posterior en pares disponibles y rechazos; no identificación causal humana ni tests externos, cinco contextos no representan poblaciones. I: `U141` y `U142` actualizan cualitativamente P-BOUNDED y P-FEEDBACK, **sin cambiar sus estados** ni atribuir novedad: estudios externos sobre feedback se refieren a condiciones distintas. J: **N90 válido sintético 0/3**, sin crecimiento CT2 ni originalidad/validación.

[JSON completo por corrida y contexto](RESULTS_N90.json.gz), [ledger N90](LEDGER_N90.json), [CT2 completa y ampliada](CT2.svg). SHA256 del JSON descomprimido `6ad62ca776f6dc5e91247b05ea2fa680f76950b4f652b6e8aac85e4a18a88cc8`, gzip `547ba73fdf48676bfc12fa9684da8e67b2f9510e80f34f7120f05f5ebbcf70ad`.

Saldo: **24/40 ciclos válidos, 16 pendientes**, de ellos **N91–N92 dos liberados**, N93–N106 14 reservados. Fuentes 97, priors 30, revisiones 142. CT2 7 ordinal, `STOP_R5` externo. Madurez ponderada 40.70% por cambios técnicos de simulador y QA, sin afirmar descubrimiento humano. No licencias, contacto de autores, SSJY ni merge main.