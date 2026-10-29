# AB-R Mercados de pareja: autorización adicional, mecanismo falsable y segunda fuente original incompleta (29/10/2026)

**GitHub parent:** `c01e5154b2b1ca038c59300cc4a496611201648b` en `research/ab-r-mercados-pareja-20261028`. Leídos del repo real AGENTS, README, AB3.2.1 y O1–O7, CURRENT, último informe/ledger/QA McMaster, SOURCES (96), PRIORS (30), UPDATES (128) y CT2. Este turno **no abre N83 ni ejecuta modelos/simulaciones/análisis de outcomes**; solamente registra autorización expresa y una ruta documental nueva. Conservar todos los negativos, priors y límites.

## Presupuesto formalmente concedido

El usuario autorizó expresamente **hasta 20 ciclos AB-R adicionales a las cuatro plazas restantes**. Nuevo total acumulado de autorización: **40** (20 anteriores +20), válidos históricos **16**, sin ejecutar **24**. Los cuatro previamente abiertos como reservados siguen **N83–N86** (NOT_STARTED); los 20 adicionales se reservan **N87–N106**, sin considerarlos abiertos ni consumidos. Ver [AUTHORIZATION.json](AUTHORIZATION.json). **No confundir 24 con ciclos nuevos realizados**, que son cero. R5 puede parar antes de cualquier máximo. No solicitar otra autorización mientras quede saldo.

## Estado empírico y necesidad científica

La auditoría original McMaster de `SRC096` fue efectivamente ejecutada antes de este turno: 116233 bytes originales SHA256 `9685dfb09a610bbf150ee2d151b05d6dceff6af18fc5b21d3ac31eecabf63eb6`, 54 actores, 2 sesiones, 357 citas con dos decisiones binarias sí/no completas, 5 registros dirigidos sin inversa; 70 sí/sí, 86 no/no, 151 sí solo hombre, 50 sí solo mujer. **Misma cohorte que SRC094, no validación independiente.** El código de su QA fue congelado ANTES de y en `5c96ba6e3b85722dcb497b58b1035ecbda283cd3`; sigue siendo auditoría descriptiva, no ventaja ESBM.

## SRC097: otra recolección humana real desde el autor original, pero no binaria ni autorizada para reutilizar aquí

[Prochazkova et al., Nature Human Behaviour (2022), DOI 10.1038/s41562-021-01197-3](https://doi.org/10.1038/s41562-021-01197-3), [preprint 2019 original](https://doi.org/10.1101/748707) y [repositorio GitHub del equipo](https://github.com/Eprochazkova/Physio_Synchrony), commit fuente **`666f4d05d60a5ce2fa745c7e621182cb2eb7a334`**. El propio preprint indica Github como repositorio de los originales; artículo final cita DataverseNL DOI `10.34894/RFUGGD`. **Un artículo/dos rutas del mismo corpus: NO dos muestras independientes**.

Se verificó mediante **conector GitHub** la presencia de originales separados por `Dyad...` en `3.Raw_data/`, documentación, `5.Processed data/1.behavior_long_format.sav` y `3.Centered.sav`, scripts SPSS de atracción y análisis fisiológico. En concreto el script fuente `Code_SPSS_Express_Attraction.sps` especifica `TARGET=Attraction`, `DISTRIBUTION=NORMAL LINK=IDENTITY`: la inferencia publicada se refiere a **atracción** y no constituye prueba de decisiones reales binarias de ambos individuos. El artículo describe correlación observacional de sincronía fisiológica (frecuencia cardiaca y conductancia) con atracción; **no identifica causalidad** ni una predicción nueva ESBM. Es un rival fuerte para cualquier afirmación trivial de sincronía.

El repositorio original no exhibe fichero `LICENSE` en el listado raíz inspeccionado. No se leyó ningún archivo SPSS binario o fisiología personal ni se descargaron bytes: **licencia de datos, SHA256 original y sí/no bilateral permanecen desconocidos**. GitHub público y acceso a código no equivalen a permiso de re-publicación de datos sensibles. No se visitó DataverseNL ni se intentaron los accesos previamente fallidos OSF/Essex/Stanford/Gist; no se contactaron autores.

SRC097 es por tanto una **cohorte original distinta a McMaster a nivel documental**, pero **no es un holdout apto** para el outcome sí/sí. No equivale a N83, no sube CT2. Es mejor descartar con base en variables/resultados que procesar sin permisos registros de salud y fisiología sensibles.

## Predicción ESBM candidata y prueba adversarial

Se documenta [HYPOTHESIS_GATE.md](HYPOTHESIS_GATE.md): separar **estructura de oportunidades**, **umbrales individuales de aceptación** y **consentimiento mutuo**. La mera ecuación sí/sí (veto bilateral) no es un descubrimiento. Comparar (M0) dos modelos individuales calibrados con actor/target/evento y producto de probabilidades; (M1) modelos SRM relacionales y de señales con controles fuertes; (M2) interacción **riesgo de exposición × selectividad × veto** con predicción propia del cambio de calibración del match cuando cambia el conjunto elegible de posibles encuentros entre sedes. Evaluar log-loss/Brier y robustez por eventos/cohortes con mismas covariables y presupuesto.

**Nivel científico:** `PROPOSED_UNVALIDATED` porque Joel/Baxter, Pronk, Rios y otros ya estudiaron partes sustanciales; no se ha establecido originalidad de esta interacción específica ni se ha escrito o probado código M2. McMaster ya expuso resultados, no puede servir como holdout virgen; ninguna segunda cohorte original de decisiones binarias legalmente utilizable y no contaminada fue confirmada. El éxito solo sería reivindicable tras una **nueva fuente original**, prerregistro formal A–J y código SHA antes de outcomes, rivales más fuertes que modelos triviales, auditoría de contaminación y holdout independiente. Si se trata de otro reempaquetado Columbia o un estudio con escalas de atracción, descartar. Ningún experimento esta revisión.

## R1–R5 / O1–O7

- **R1:** estimando sí/sí *condicionado a oportunidad real y riesgo de elegibilidad*; no confundir deseo, matches, intercambio de contacto o duración.
- **R2:** comparador competente paridad informativa con SRM actor-partner-relación, Pronk selección/orden, Rios optimización, Baxter longitudinal, Ogushi 2026, Matz lenguaje, Chang movimiento y Zhao permutaciones.
- **R3:** hipótesis documental actual no es prerregistro; congelar A–J y SHA al conocer esquemas y antes de examinar outcomes futuros. Corregir multiplicidad por afirmaciones efectivamente confirmatorias y adaptaciones.
- **R4:** comparar ablaciones de riesgo/visibilidad, popularidad, secuencia, umbrales/costos y censura; no confundir cambio codificado de ofertas con descubrimiento causal.
- **R5:** falta *otra* cohorte de oportunidades reales con licencia de archivo y dos binarias, SHA original, y reserva confirmatoria externa. STOP_R5. Sin ejecución de ciclos y sin gastar crédito.

O6 requiere CT2 completo 0–100 + zoom, [SVG histórico](../ABR_SSJY_STAGE_N82_20261029/CT2.svg) y [puntos](../ABR_SSJY_STAGE_N82_20261029/CT2_TRAJECTORY.json). CT2 **7/100 ordinal** permanece, último ciclo verdadero N82, sin N83. O7: se registra dependencia de nuevo holdout y novedad de H-RISKSET-VETO, modo BRANCHING AB-R sin nuevo branch D0.7 relativo a línea ESBM, como nodo propuesto/bloqueado; no consumir ciclo planning. No N1/N2/N3 nuevo.

## Registros al cierre

Fuente **SRC097**, revisiones **U129** (P-INTERACTION-EXPRESSIVE) y **U130** (P-DYADIC_ACCESS), ambas **NO_CHANGE_WITH_REASON**. **97 fuentes, 30 priors, 130 revisiones**; autorización 40 total, 16 válidos, 24 sin iniciar; nueva ejecución 0 válidos / 0 inválidos / 0 planning, auditoría documental 1; CT2 7/100 y **STOP_R5**. No se publican filas ni fisiología, se respetan permisos y no hay merge a main. Todo queda en rama privada.

**Siguiente paso:** una fuente efectivamente nueva con datos de encuentro y doble elección 0/1, términos públicos explícitos y original SHA256; si se consigue, congelar instrumento, competidores M0/M1 y M2 bajo A–J antes de outcomes; evaluar en cohorte totalmente independiente. Los 24 ciclos están autorizados y son techo, **no objetivo de consumo**. No solicitar otros.
