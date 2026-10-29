# N89 — Reputación por rechazo: difusión global frente a conocimiento del testigo

**Ciclo AB-R sintético adversarial válido; resultado de mecanismo interno, 0/3 de originalidad científica.** Contrato completo A–J y código SHA256 precongelados en `8fd4a0a7b5cb5d3db57f116d4563d994a33d70ec` **antes de ejecutar resultados**. Fuente original `esbm_dynamic.py` SHA256 `f7e6b84000720cbdf2ee0800c2b10d136185facd00e4622756cbb5f8d8254d0b`, script N89 SHA256 `34e055d63b9bca17622fb0d964e804632b9fd34637c58ca6ab14869e932d1148` guardado comprimido gzip `n89_reputation_institution.py.gz` y blob Git SHA1 `41e0c40aa053a0ce39667ffac8e44fae91cb0147`. Reproducir: descomprimir y verificar SHA, ejecutar `python n89_reputation_institution.py --source esbm_dynamic.py --out RESULTS_N89.json`.

## Diseño y controles

En la fuente ESBM v2, cada rechazo disminuye `public_score[i]` del proponente; esta penalización se aplica a **todas** las respuestas posteriores, sin modelar que la información del rechazo llegase a cada receptor. N89 contrasta tres instituciones: **global** (sin modificar regla histórica), **witness** (solo j que previamente rechazó i conoce su reputación), **silent** (acumulación sin uso, control sin señal). Conservar mismas matrices de azar, propuestas, exposición, compatibilidad y matching; cada divergencia posterior de grafo de exposición forma parte del mecanismo dinámico simulado, no una comparación instantánea en el mismo grafo.

El protocolo congelado establece 4 contextos de política × 6 semillas × 3 brazos = 72 ejecuciones instrumentadas y 24 originales G +24 originales sin señal = **120 simulaciones Python reales**, no 120 muestras de personas. Cumplidos **24/24 G-sham** y **24/24 S-sham** exactamente iguales en todos los campos aplicables. Cuentan emisiones de respuesta con penalización, sin imputar información a no testigos en W. Todas las cuentas de parejas y controles pasan.

## Contraste primario: contexto aleatorio, seis semillas

| Resultado sintético (media por corrida) | Global | Solo testigo | Sin señal |
|---|---:|---:|---:|
| Uniones formadas | 209.00 | 224.00 | 226.67 |
| Uniones activas al final | 53.67 | 59.67 | 62.00 |
| Respuestas positivas | 342.50 | 405.17 | 417.83 |
| Respuestas con penalización aplicada | 1673.67 | 147.00 | 0 |

En seis corridas globales se dan **8.776 situaciones de respuesta en las que el proponente tiene mala reputación y el receptor no había rechazado antes a esa persona**. La diferencia emparejada global−testigo en uniones formadas = **−15** de media; en uniones activas = **−6**. Los seis deltas de formaciones son **[+6,−20,−10,−13,−25,−28]**: hay heterogeneidad y una inversión, no efecto uniforme por semilla. El mecanismo sin señal no tiene penalizaciones aplicadas, y la diferencia total global−sin señal es −17.67 uniones.

## Sensibilidad preregistrada: otras tres políticas de exposición

| Contexto artificial | Formadas global | Formadas testigo | Formadas sin señal | Global−testigo |
|---|---:|---:|---:|---:|
| mixed_random | 209.00 | 224.00 | 226.67 | -15.00 |
| popularity_ranking | 191.83 | 220.17 | 223.50 | -28.33 |
| institutional_segregation | 190.33 | 210.83 | 218.67 | -20.50 |
| explicit_norm_preference | 235.33 | 237.33 | 241.17 | -2.00 |

La difusión global del modelo no es una implicación lógica de los rechazos bilaterales: representa una **hipótesis institucional de circulación de información**. La intensidad cambia según la política, y no permite atribuir efectos causales sobre humanos.

## R1–R5, registro y límites

R1: el estimando son emparejamientos y respuestas de agentes sintéticos, no prestigio ni relaciones humanas. R2: rival testigo con acceso a información plausible, más placebo sin señal y dos shams byte-a-byte. R3: código A–J congelado, seis semillas reutilizadas, sin holdout humano, ninguna p confirmatoria; cuatro políticas son sensibilidades, no muestras independientes. R4: la alternativa testigo incluye solo experiencia directa, no mide redes reales de transmisión de rumores ni precisión del conocimiento. R5: **STOP_R5** para causalidad empírica externa; 0/3 nuevo.

`U139` revisa P-PUBLIC_REPUTATION sin cambiar estado `NOT_IDENTIFIED`. `U140` revisa P-FEEDBACK sin cambiar `EXPERIMENTALLY_SUPPORTED_IN_CONTEXT`: las fuentes humanas previas no demuestran degradación reputacional pública por swipe rechazado. **97 fuentes, 30 priors, 140 revisiones**. Contabilidad: **23/40 ciclos válidos, 17 disponibles** (N90–N92 tres liberados, N93–N106 catorce reservados). CT2 ordinal **7/100** sin incremento. Madurez: 40.05→**40.45 %** por simulador 59→61 y QA 59→60, sin aumento de originalidad ni validación externa.

[Datos completos por semilla, gzip JSON](RESULTS_N89.json.gz) · [Código reproducible gzip](n89_reputation_institution.py.gz) · [Ledger](LEDGER_N89.json) · [CT2 completa y zoom](CT2.svg). Fuente `RESULTS_N89.json` sin compresión SHA256 `c7ec5e5f297503c209091dd3dce1288ed36030e7082afea8247b44ab36e40354` y gzip `5332c76bcd37b49dc64ed2795d6b284bdf4bc77061bf308d350c25498e76f4c9`. No licencias, contactos, SSJY, microdatos ni fusión main.