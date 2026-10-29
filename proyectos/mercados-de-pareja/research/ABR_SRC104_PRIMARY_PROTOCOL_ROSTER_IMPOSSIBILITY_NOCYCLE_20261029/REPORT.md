# SRC104 — Control adversarial de documentación primaria y contabilidad de encuentros sin modificar votos

**Fecha:** 2026-10-29 · **Tipo:** AUDIT_POSTHOC_NO_AB_CYCLE / DATA_QUALITY_ONLY / NO_CONFIRMATORY_TEST. **Commit de partida comprobado:** `1816ea2360de729f7682e76b2d06ba07eeb35bae`. **Fuente de filas:** XLSX recibido `rspb20181634_si_001.xlsx`, SHA-256 de esta copia `91c0bb93e699cc003ad32a11c51d38da6018cf9851b613822ecb19ef5618be00` (**no** hash original de Figshare). **Fuente independiente del procedimiento, NO independencia de la cohorte ni de observaciones:** [Pisanski et al., *Proceedings of the Royal Society B* (2018), DOI 10.1098/rspb.2018.1634](https://doi.org/10.1098/rspb.2018.1634); [PMC6304053](https://pmc.ncbi.nlm.nih.gov/articles/PMC6304053/), **Material and Methods §§2(a)–(d)** y **Data accessibility**; [depósito suplementario original CC BY4](https://doi.org/10.6084/m9.figshare.7410575.v1).

**Resultado central:** el libro posee una **cobertura de pares de IDs aparentemente completa** entre personas grabadas, pero su grafo de claves del segundo evento **excede** el máximo de encuentros distintos compatible con la asignación de una cita por hombre y ronda registrada. Es un **control de coherencia lógico condicionado** a la interpretación física de `Round` descrita en el artículo; NO evidencia de nuevas relaciones, ni reconstrucción de los votos, ni una demostración independiente de qué campo original está errado. A ello se suman 15 contradicciones entre perspectivas ya observadas. Sigue `STOP_R5_EXTERNAL`.

## 1. Qué documenta realmente el artículo original

Los autores documentan **dos eventos presenciales**, en dos grupos de edades, con **30 personas estudiadas** en total, citas de **seis minutos**, participantes con etiqueta y un cuadernillo personalizado; tras cada cita **ambas personas** indicaban `yes/no` **junto al ID de aquella cita**. Los hombres se desplazaban a la mesa contigua entre rondas. Las preferencias se notificaban como *match* por email si había dos sí y daban lugar a intercambio de contacto, NO automáticamente a una unión duradera. Los autores dividieron posteriormente cada grabación de voz en **tres segmentos** por cita y participante. Fuente: §2(a)–(c) del artículo original, no una inferencia de la distribución de votos en nuestro Excel.

El artículo **NO proporciona** (en los métodos comprobados) un diccionario explícito de los campos informáticos `Group`, `Date`, `Round`, `Dates_ID`, `Chose_date`, `Chosen_by_date` del XLSX, un plano de mesas o cuadernillos originales por persona. Aunque su procedimiento implica rondas comunes de citas, **no queda demostrado que el campo `Round` de la hoja reproduzca sin errores el reloj físico del evento** ni que `Dates_ID` esté correctamente transcrito en cada fila. Las definiciones conceptuales de dos elecciones nativas sí están respaldadas; la codificación **fila a fila** no.

La ficha Figshare identifica el suplemento de autores como *raw data* y licencia **CC BY 4.0 del depósito**, no un certificado de exactitud de cada transcripción. No se descargó un archivo canónico nuevo ni se obtuvieron anotaciones originales adicionales. **No se contactó a participantes/autores, no se aceptaron licencias y no se ejecutaron simulaciones ni pruebas de hipótesis.**

## 2. Unidad de análisis y control de relojes

Auditoría en memoria del XLSX original aportado, con `artifact_tool`, **lectura sin modificaciones**: 726 filas de voz `=242` claves dirigidas `(Group, Date, Participant ID, Dates_ID)` × **3 segmentos**; cada persona presenta **un único registro dirigido por cada valor normalizado `Round`** dentro de su evento. La cadena textual del nombre de audio coincide con `Participant ID`, `Round` y `Time segment` en las **726** filas, pero es **otra anotación del mismo fichero**, NO una grabación audio externa o reloj independiente. `Round` tiene seis valores numéricos representados como texto para 6 registros dirigidos; la normalización entero solo existe en QA en memoria.

| Evento codificado en XLSX | Personas grabadas | Distribución de sexo en hoja | Rondas distintas | Registros dirigidos por ronda | Pares de ID distintos entre personas grabadas |
|---|---:|---|---:|---|---:|
| `Group=2` | **19** | 11 hombres y 8 mujeres | **11** | 8 hombres + 8 mujeres en **cada una** de las 11 rondas | **88/88 = 11×8** |
| `Group=3` | **11** | 6 hombres y 5 mujeres | **6** | 6 hombres + 5 mujeres en **cada una** de las 6 rondas | **30/30 = 6×5** |
| Ambos grupos | **30** | 17 hombres y 13 mujeres | 11+6 rondas en eventos separados | Sin cruces de evento | **118/118 pares posibles entre personas grabadas** |

**Importante:** `118/118` representa **cobertura del grafo de etiquetas de ID**, NO prueba de que las 118 díadas sean correctamente atribuidas en cada ronda ni votaciones perfectamente recíprocas. En `Group=2`, las 88 claves están representadas por dos perspectivas; en `Group=3`, las 30 parejas de dos personas grabadas están representadas en al menos un sentido, pero **28 tienen ambas perspectivas y 2 solo una**. El grupo 3 contiene además **8 claves** que asocian a un hombre con **uno de dos IDs de mujer sin grabación propia** (6+2 referencias), total **38 claves de pareja distintas** en esa sesión.

## 3. Contradicción formal condicionada a la interpretación de ronda física

En `Group=3` hay **6 hombres grabados × 6 valores de ronda**, con exactamente **una** anotación dirigida por hombre y valor; por tanto el número de encuentros distintos que estos seis hombres pueden tener en seis rondas *si cada ronda es una franja física simultánea y cada hombre está en una sola cita por ronda* es **a lo sumo 36**. No hay observación duplicada de encuentro de un mismo hombre dentro de una misma ronda, con independencia de voz.

Sin embargo el **grafo de parejas derivado de la unión de las anotaciones de hombres y mujeres** incluye **38 claves distintas**: 30 parejas entre grabados (`6×5`) y 8 etiquetas adicionales a las dos contrapartes sin audio. Para que las 38 fueran 38 citas **distintas y correctas** celebradas **por estos seis hombres dentro de esas seis rondas** sería necesario **38 ≤ 36**, lo que es falso.

Este contraejemplo lógico (diferencia de **al menos 2 claves por encima de la capacidad registrada**) no necesita ningún contraste estadístico. **Conclusión limitada:** todas estas condiciones no pueden ser simultáneamente verdaderas: (i) `Round` marca el turno físico común, (ii) cada hombre tiene una cita por turno, (iii) las 38 claves identifican encuentros únicos de ese evento y (iv) las anotaciones correspondientes no omitieron ni desplazaron eventos. En consecuencia, el conjunto actual de claves **no certifica** 38 díadas físicas independientes ni permite usar `Dates_ID` como verdad completa del emparejamiento. **No demuestra exactamente dos filas erróneas**, no identifica sus IDs, ni permite borrar dos encuentros a voluntad: el problema puede implicar más anotaciones incorrectas o diferencias de definiciones/observación.

La presencia de las **8** contrapartes sin audio **no** significa que esas personas no participasen, no votasen o rechazasen citas: solo que carecen de una perspectiva acústica en esta hoja. Tampoco contradice necesariamente el número de 30 personas estudiadas que informa el artículo si hubo otros asistentes no grabados; el paper no ofrece en estos métodos una lista completa de invitados versus grabados. Si `Round` fuera un contador **individual** y no un turno físico común, la prueba de 36 **no sería aplicable** sin un horario externo.

## 4. Control adversarial de votos y atributos sin reparar los originales

Se conservan los controles directamente verificados en el informe precedente, [auditoría de round/mirror](../ABR_SRC104_MIRROR_ROUND_ADVERSARIAL_QA_NOCYCLE_20261029/REPORT.md), sin ningún nuevo test estadístico ni cambio de filas:
- **116** parejas con dos anotaciones dirigidas por `(Group,Date,actor,date)` inversas: **101** votos cruzados coherentes y **15** discrepancias.
- `Round` diferente **26/116** tras normalización entera, frente a un artefacto `32/116` sin normalización. **90** tienen ronda igual; **2** de esas 90 todavía difieren en votos. Entre las 26 de distinto valor, **13** difieren en votos y **18** tienen discrepancias de atributos repetidos de la pareja.
- Los scores `Desirability_score`, `Choosiness_score` y sus duplicados de la contraparte **se calculan a partir de votos del propio evento** (§2d de autores), por lo que sus concordancias no son un criterio externo independiente para decidir cuál `Dates_ID` es correcto, ni covariables predictores independientes de `yes/no`. Hay **riesgo explícito de fuga de información**.
- **10** claves unilaterales: 8 contrapartes sin grabación propia, 2 con grabación pero sin fila de encuentro inversa; **1** de esas perspectivas carece de ambos votos. Un `NA` o ausencia de contraparte no equivale a `NO`.

No se ha utilizado `Round` para reemplazar ni eliminar `Dates_ID`, ni el producto `Chosen_both_match` como voto adicional independiente, ni las puntuaciones retrospectivas para derivar consentimiento. **No publicar archivos de voz, nombres, códigos de participantes, filas ni resultados individuales en GitHub**.

## 5. Compatibilidad científica y puerta AB-R

Esta documentación primaria confirma la **semántica de los cuestionarios** y el calendario general de encuentros; la auditoría aritmética encuentra un obstáculo adicional de consistencia, pero **no identifica cuál de las columnas es errónea** y no permite fabricar un dataset confirmatorio. Contra B0 (composición y denominadores), B1/SRM (actor/target), B2 (homofilia), B4 (orden y capacidad) y B6 (historia flexible), ESBM v2 **sigue sin predicción diferencial ex ante** ni evaluación equitativa. Las 3 por cita son segmentos de voz, no decisiones secuenciales; tampoco observamos un algoritmo de recomendación exógenamente modificado, y los dos eventos no otorgan poder para una prueba por mercados independientes.

La **única** reconciliación fiable de `Round`/ `Dates_ID`/votos exigiría una fuente primaria de *agenda física original, correspondencia mesa/ID/ronda o cuadernillos binarios originales*. La publicación consultada no facilita esos instrumentos. **No contactar autores o participantes sin permiso**. Un documento matemático que identifica inconsistencias no sustituye esa fuente.

**R5 sigue cerrado:** no se abrieron N93–N106, no se consumieron ciclos AB-R y el permiso del usuario de ejecutarlos sin otra autorización **no sustituye A–J ni el SHA congelado antes de outcomes**. No corregir retrospectivamente filas y declarar `holdout` virgen. Este informe es `NONCYCLE`, sin nuevos hallazgos 1/3, 2/3 o 3/3.

## 6. Registro de trazabilidad

Una sola fuente primaria `SRC104` (artículo original + suplemento), **sin nuevo SOURCE**. Actualizaciones `U163` (`P-DYADIC_ACCESS`) y `U164` (`P-OPPORTUNITY`), ambas `NO_CHANGE_WITH_REASON`: añadimos cobertura estructural y la incompatibilidad condicional del calendario, **no** mejora de identificación ni confianza externa. Cambian contadores de revisión documental **104 SOURCES, 30 PRIORS, 164 UPDATES**. **Estado inalterado:** 26/40 ciclos válidos históricos, 14 N93–N106 reservados y 0 abiertos; STOP_R5_EXTERNAL; CT2 ordinal 7/100; madurez 41.20%. Sin accesos a microdatos nuevos, nuevos outcomes ni simulaciones. El código de ESBM v2 y su teoría deben permanecer sin cambios.

