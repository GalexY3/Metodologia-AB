# SRC104 — Auditoría adversarial de votos cruzados, rondas, perfiles de contraparte y casos sin inverso

**Fecha:** 2026-10-29. **Tipo:** DATA-QUALITY FORENSICS / NONCYCLE / NO CONFIRMATORY TESTS; revisión post hoc del archivo original aportado por el investigador (sin redistribuir datos sensibles). **HEAD anterior comprobado:** `c4c2fcbb4dbce39557e2f873ec3640f8072cb195`. **Autoridad:** [auditoría de estructura previa](../ABR_SRC104_USER_XLSX_SCHEMA_QA_NOCYCLE_20261029/REPORT.md), [SRC104](../PRIORS/SOURCES.json) y archivo local recibido `rspb20181634_si_001.xlsx`, 232002 bytes, SHA-256 `91c0bb93e699cc003ad32a11c51d38da6018cf9851b613822ecb19ef5618be00`, calculado de la copia subida, NO autenticado bit a bit frente a Figshare.

**Dictamen:** los **15 conflictos** de votos originales entre dos registros reflejados siguen existiendo. El informe previo infló **solo** el desacuerdo de rondas a `32/116` al comparar datos de tipos mixtos; normalizando `Round` numérico/texto se reduce a **`26/116`**, exactamente seis falsos desacuerdos de tipo (`10` frente a `"10"`, etc.). **No se corrigió ninguna decisión**, no se reconstruyeron díadas como verdaderas sin verificación independiente, y un patrón descriptivo de anotación **no** constituye una predicción ESBM.

## 1. Reproducción y controles independientes del resultado

Se volvió a importar el XLSX local en lectura con `artifact_tool`; no se escribió hoja ni exportó copia, ni se usaron herramientas de simulación, inferencia estadística o regresión. Clave de observación: `(Group, Date, Participant ID, Dates_ID)`; cada una de las **242** claves dirigidas tiene exactamente tres registros de voz `Time segment=1,2,3`, total **726 filas**. Se comprobó que no varía entre sus tres segmentos ni identidad, `Round`, tres flags de voto ni métricas individuales relevantes. **Los 726 nombres de archivo de voz** concuerdan con `Participant ID`, `Round` y `Time segment` codificados en su propio nombre: 0 discrepancias de esos tres tokens. Los segmentos son mediciones acústicas, **no** tres decisiones románticas repetidas en el tiempo.

Para enlazar perspectivas se mantiene la clave **inversa** original por evento `(Group,Date,actor,date)` y `(Group,Date,date,actor)`, sin usar votos ni Round para elegir parejamiento. **116** díadas tienen ambas direcciones y **10** solo una, total 126 claves no ordenadas; **101/116** cruzan ambos sí/no consistentemente, **15/116** presentan contradicción; **2/116** difieren también en el indicador calculado `Chosen_both_match`. Dentro de cada uno de los **241** registros dirigidos con dos votos no ausentes, `Chosen_both_match` coincide con `Chose_date × Chosen_by_date`, lo que **no valida** el voto atribuido a la otra persona.

## 2. Hallazgo nuevo: seis desacuerdos de Round eran artefactos de tipo

`Round` contiene valores numéricos para **236/242** registros dirigidos y cadenas de caracteres numéricos para **6/242**. Una comparación sin conversión de tipos dio **32/116** pares `Round_a != Round_b`; normalizando únicamente el tipo a **valor entero exacto** (sin cambiar celdas originales), el desacuerdo de ronda es **26/116**. La corrección de seis es un ajuste **del instrumento de QA**, no una imputación. Conservamos en ledger la cifra anterior como resultado de auditoría sin normalizar, explícitamente superado.

| Doble perspectiva por pareja `actor↔date` | Díadas | Votos cruzados consistentes | Conflictos entre votos |
|---|---:|---:|---:|
| `Round` normalizado idéntico en ambas direcciones | **90** | **88** | **2** |
| `Round` normalizado distinto | **26** | **13** | **13** |
| **Total** | **116** | **101** | **15** |

**Sin test de significación:** las discrepancias se concentran descriptivamente en los pares que señalan diferentes rondas (`13/26` frente a `2/90`). Esto es una **bandera de inconsistencia o desfase de alineación**, NO prueba de que Round sea un reloj absoluto ni de que los 26 enlaces por IDs sean erróneos. Ninguna regla autoriza a cambiar `Dates_ID`, `Round` o votos sin verificar anotaciones originales de ambos participantes.

## 3. Segunda corroboración estructural: atributos de la contraparte

La hoja incluye `Dates_desirability_score` y `Dates_choosiness_score` junto con los campos homólogos del propio actor (`Desirability_score`, `Choosiness_score`). En los dos registros del mismo par se puede comprobar si **el atributo atribuido a la cita** corresponde al del participante inverso, aplicando tolerancia a redondeo de coma flotante (1e−7), sin consultar el resultado romántico ni sustituir por el valor de otro actor.

| Grupo de díadas | Alguna discrepancia de atributo de contraparte | Sin discrepancia |
|---|---:|---:|
| **90** pares con `Round` igual | **0** | 90 |
| **26** pares con `Round` distinto | **18** | 8 |

De los **13** conflictos de voto con `Round` distinto, **10** también tienen un atributo de contraparte inconsistente; **3** no. Entre los 13 pares que tienen votos coherentes pese a `Round` distinto, **8** presentan discrepancia de esos atributos. Es un diagnóstico de **anotaciones repetidas dentro de la misma fuente**, no una comprobación externa independiente de identidad: los scores proceden de preferencias y pueden compartir errores de transcripción o calcularse de los propios votos. No usarlos como covariables *pre-outcome* para predecir los mismos sí/no, porque habría leakage.

Los **2 conflictos restantes con `Round` igual** y atributos de contraparte coherentes **no se explican por el desajuste de ronda**. Persisten como contradicciones en la representación cruzada de las decisiones originales. No forzar reconciliación, invertir etiquetas por conveniencia ni atribuir error psicológico a participantes.

## 4. Diez claves de una perspectiva: cobertura del registro, no diez rechazos

Las **10** claves con una sola perspectiva están **todas en la segunda sesión (Group=3)**. En **8**, la contraparte pertenece a **dos IDs distintos** que **nunca** aparecen como `Participant ID` de personas con voz; esas dos contrapartes reciben seis y dos referencias respectivamente. Que no se haya registrado su voz **no demuestra ausencia del encuentro ni del voto**: solo demuestra que no hay segunda perspectiva en **esta hoja**. En las otras **2**, ambas personas sí tienen voz grabada en algún registro, pero **falta la fila recíproca para esa díada**. **Una** de las diez perspectivas, referente a una persona sin fila de voz, no tiene valores nativos en `Chose_date`, `Chosen_by_date` ni `Chosen_both_match`; las otras nueve sí. Quedan **8/10** pares asociados a contrapartes sin audio y **2/10** con audio pero sin registro inverso; ninguna votación silenciosa se recodifica como NO.

Desglose por sesión: Group=2 contiene **88 pares** con las dos direcciones registradas, **80** de votos consistentes y **8** discordantes; Group=3 contiene **28 pares** con doble perspectiva, **21** consistentes, **7** discordantes y **10** con una sola perspectiva. No convertir estos grupos en clusters independientes suficientes para inferencia causal de política.

## 5. Regla de conservación, alcance ESBM y salida R5

**Conservar todas las filas de origen intactas** y mantener por separado las banderas de QA `round_type_only_discordance`, `round_value_discordance`, `counterpart_score_discordance`, `cross_vote_discordance`, `match_label_discordance`, `missing_inverse_record`, `counterpart_not_recorded`, `native_vote_missing`. Esas banderas son **diagnósticos no observaciones nuevas**. Si se pretendiese analizar después, habría que fijar por adelantado una regla de exclusión o sensibilidad respetuosa con incertidumbre, y obtener los originales auténticos de las respuestas si es posible. No «reparar» por mayoría, por match derivado, por ranking de score ni por ronda presumida correcta.

**B0** (elegibilidad/estructura) necesita un universo de participantes y encuentros completos; **B1/SRM** requiere que cada voto sea atribuible a actor, target y díada genuinos; **B2** no recupera preferencias causales desde un grafo de citas y homofilia; **B4** depende de orden/capacidad si la ronda se puede interpretar y alinear verdaderamente; **B6** historial causal temporal no se identifica con tres segmentos de voz ni con rondas de participantes contradictorias. Se desconocen reglas exógenas de asignación y no se ha derivado ninguna **predicción original diferencial** de ESBM. La coherencia de 88 pares con misma ronda no crea una muestra confirmatoria automáticamente: sería una selección de calidad a posteriori con variables potencialmente relacionadas con el outcome.

**CONCLUSIÓN:** QA revela un problema **más preciso** que «15 votos contradictorios» y una corrección reproducible de `32` a `26` diferencias de ronda, pero no demuestra todavía si los errores son de `Dates_ID`, `Round`, campos `Chosen_by_date` o transcripción. El consentimiento/atribución CC BY4 del depósito SRC104 no elimina obligaciones de privacidad sobre datos sensibles. La copia aportada sigue sin cotejo de SHA editorial. No se ejecutaron simulaciones, estimaciones de efecto, validación humana de ESBM, ni ciclos AB-R A–J.

**CONTABILIDAD:** 104 SOURCES / 30 PRIORS / 162 UPDATES (`U161` P-DYADIC_ACCESS, `U162` P-OPPORTUNITY, ambos `NO_CHANGE_WITH_REASON`); **26/40** ciclos válidos históricos; **0** ciclos válidos/inválidos/planning nuevos; N93–N106 **14 reservados**, 0 abiertos; `STOP_R5_EXTERNAL` sigue activo; CT2 **ordinal 7/100**, madurez ponderada **41.20%** inalterados; sin 1/3, 2/3 o 3/3 nuevos. El usuario ha aclarado que las plazas autorizadas pueden utilizarse sin pedir otra autorización, **pero sigue siendo obligatorio** el contrato A–J, el SHA congelado antes de outcomes, controles adversariales y la liberación R5 científica; esta auditoría es post hoc y no puede contarse como ciclo.

