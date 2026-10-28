# Mercados de pareja · BRANCHING AB-R N41–N46

**Investigador:** Alejandro Panera Pascual. **Cierre:** 28/10/2026. **Rama:** `research/ab-r-mercados-pareja-20261028`, no fusionada con `main`. **Autorización:** seis ciclos AB-R adicionales. **Realizado:** seis ciclos A–J válidos, cero inválidos, cero de planificación, cero pendientes. Se archivaron un prerregistro antes de calcular las nuevas estimaciones, dos hashes de código antes de ejecutar, salidas de Columbia y Mixmosa, QA, fuentes, ledger, adversarial y CT2. **No se ha realizado ninguna intervención causal en personas ni se ha confirmado la teoría original de que la homogamia procede exclusivamente de maximización individual sin homofilia**.

**Contabilidad científica:** 1 hallazgo local **1/3 exploratorio**, N46, acotado a una diferencia de signo entre mercados en un estadístico de edad relativo a su control, **sin reivindicación de novedad científica** y sin acreditación 2/3; N1 histórico global no auditado. N2=0, N3=0. CT2 **17/100 →17/100**, ordinal no calibrado. DRIFT D0,4, misma pregunta social con variables de homofilia y controles por actor. R5: cerrar 6/6 y no forzar simulaciones.

## Fuentes realmente inspeccionadas y antecedentes
1. **Columbia**: Parquet aportado por el investigador, SHA256 `a0fe55d6172d01f81d6c7e2546330828cb98d1f631b2598fec4d4f4660eaa37d`, versión limpiada. Los 8.368 registros dirigidos corresponden a 4.184 citas únicas (21 waves), 551 individuos. Los atributos propios `age` y `field_cd` se cruzaron con ID de contraparte; las decisiones `dec` se tomaron de la propia fila. No se sumaron dos veces las citas en la comparación de populares entre parejas; sí se conservó una fila por decisión de actor en el análisis de gustos. Eventos speed dating norteamericanos de unos cuatro minutos en 2002–2004.
2. **Mixmosa**: [repositorio público](https://github.com/dankras/mixmosa-anonymized-data), CSV originales `interactions.csv` Git blob `c4aba45888dc07573b6bd12554f73fb57ebb0479`, `user_features.csv` Git blob `99679f0e33b55099a4a0705810dd9771019554d0`; 1.895 encuentros completos de ocho minutos y 30 eventos. Se extrajo la edad de ambos agentes **en memoria**, sin rehostear filas individuales; 1.888 encuentros tenían edad válida de ambos.
3. Antecedentes **Fisman et al. (2006)**, [*Gender Differences in Mate Selection*](https://doi.org/10.1162/qjec.2006.121.2.673), y **Fisman et al. (2008)**, [*Racial Preferences in Dating*](https://doi.org/10.1111/j.1467-937X.2007.00465.x): ya estudian diferencias de atributos y preferencias en el experimento original de Columbia. Este proyecto **no declara descubrir de nuevo** esos efectos.

## N41 · Contrato de datos y calidad
Columbia: 8.368 decisiones dirigidas, sin duplicados de (wave, actor, contraparte), espejos de `dec`, `dec_o`, `match` previamente validados, 4.184 citas; edad de ambos completa en **8.180/8.368 decisiones**, campo académico de ambas personas completo en **8.204/8.368**, 18 categorías `field_cd`. La edad y campo del mismo ID no cambiaron entre sus fechas observadas y no se observaron edades fuera de 16–90. Popularidad del candidato: proporción de aprobaciones recibidas en **otras citas**, excluyendo la decisión focal; 8.368 filas tienen proxy tras el criterio de cuatro exposiciones totales. Datos faltantes excluidos solo del correspondiente contraste.

**Límites:** `field_cd` es disciplina de estudio, no nivel educativo ni posición de clase; Columbia es un archivo limpiado que omite diez filas frente a versiones ampliamente difundidas. Mixmosa tiene otras covariables sociales, sin `field_cd` equivalente; evitar trasladar directamente ese estimando.

## N42 · Proximidad de edad y control de oportunidades por persona

**Estimando:** media de `|edad_candidato−edad_actor|` entre decisiones positivas menos media de todas las citas disponibles para los mismos actores. **Nulo competente:** 1.000 permutaciones de decisiones **dentro de cada actor y evento**, conservando cuántos sí dio cada persona y la oferta de citas realmente vista. El resultado **observado menos media nula** es:

| Actor que decide | Columbia, decisiones con edad | Distancia aceptada menos disponible | Media nula del contraste | Exceso frente a nulo |
|---|---:|---:|---:|---:|
| Mujeres eligiendo hombres | 4.090 | −0,055 años | +0,101 | **−0,156 años** |
| Hombres eligiendo mujeres | 4.090 | −0,187 años | +0,015 | **−0,202 años** |

En ambas se encontró un exceso de cercanía en el sentido predeterminado por el control (cola inferior de permutación ≈.001 por 1.000 repeticiones). Este **no es un coeficiente causal**: los eventos, edades y personas asistentes no se asignan al azar; además múltiples contrastes fueron explorados en el mismo fichero.

## N43 · Homofilia de campo académico

`same_field=1` cuando la disciplina académica codificada de actor y candidato es igual, únicamente con ambos campos presentes. Contraste idéntico actor×evento de 1.000 permutaciones de etiquetas sí:

| Actor | N decisiones | Diferencia en proporción de misma disciplina entre sí y oportunidades | Media nula | Exceso |
|---|---:|---:|---:|---:|
| Mujeres | 4.102 | +1,249 p. p. | −0,302 p. p. | **+1,551 p. p.** |
| Hombres | 4.102 | +2,197 p. p. | +1,089 p. p. | **+1,108 p. p.** |

Colas superiores exploratorias de ≈.007 y .010. Son efectos **pequeños y específicos de disciplina**; pertenecer a la misma disciplina puede señalar contexto educativo, redes, normas compartidas o intereses, no necesariamente preferencia consciente por semejanza. Ninguna inferencia sobre homogamia matrimonial española es legítima.

## N44 · Calidad consensuada frente a semejanza en el mismo decisor

Se ajustaron tres modelos de probabilidad lineal con efecto fijo por **actor que decide**, idénticas observaciones completas, predictores estandarizados y errores estándar robustos agrupados por actor: (a) popularidad del candidato estimada en otras citas; (b) distancia de edad, edad con signo y mismo campo; (c) ambos. No se emplea validación prospectiva; es **R² interno sobre el mismo conjunto**:

| Decisiones | N | R² popularidad | R² semejanza | R² combinado |
|---|---:|---:|---:|---:|
| Mujeres eligiendo | 4.071 | **0,1391** | 0,0055 | **0,1424** |
| Hombres eligiendo | 4.071 | **0,1627** | 0,0107 | **0,1678** |

En combinado, coeficiente de popularidad por una desviación típica: mujeres **+0,1693**, hombres **+0,1876** en probabilidad lineal de sí. Igual campo contribuye ≈**+0,024** por desviación típica en ambos, mientras distancia absoluta de edad tiene coeficiente mujeres −0,0120 (SE .0094), hombres −0,0254 (SE .0078). Las diferencias firmadas de edad no aportaron efecto parcial estable. Todas las variables están estimadas desde los mismos eventos de interacción; la popularidad del candidato, aunque excluye la decisión focal, se calcula con votos contemporáneos de **otras** personas y puede actuar como un proxy endógeno de gusto compartido. Los errores agrupados por actor no cubren completamente dependencia por candidato y evento. No inferir que el 60/40 del simulador está calibrado; tampoco declarar causalmente independiente a la homofilia.

**Conclusión local:** frente a una semejanza sencilla de edad y disciplina, el proxy de popularidad refleja mayor asociación descriptiva con las decisiones, **pero añadir semejanza no tiene efecto estrictamente cero**. La coexistencia de mecanismos es más compatible que el monopolio de uno solo.

## N45 · Heterogeneidad por eventos

Entre las 21 sesiones Columbia, 18 tuvieron al menos diez citas de interés mutuo y permitieron correlación de popularidad de las dos personas: **14 positivas y cuatro negativas**, valores entre **−0,412 y +0,704**; las estimaciones con pocas citas son particularmente ruidosas. La correlación global de `r=+0,1244` permanece positiva al retirar cada sesión una por una: rango **+0,0963 a +0,1631**. La primera mitad de waves tiene r≈+0,115 y la segunda mitad ≈+0,140. No hay un evento único que explique toda la correlación global, pero tampoco uniformidad individual o transportabilidad.

## N46 · Replicación aproximada de la proximidad de edad en Mixmosa

Se ejecutó [`mixmosa_age.js`](mixmosa_age.js) sobre las tablas originales de Mixmosa, con semilla 20261028 y 1.000 permutaciones de decisiones por **actor×evento**. Solo se emitieron salidas agregadas y se repitió la misma ejecución con resultado idéntico. 1.888/1.895 citas tenían ambos registros de edad, generando 1.888 decisiones observadas por sexo.

| Actor | Columbia, exceso proximidad vs nulo | Mixmosa, exceso proximidad vs nulo |
|---|---:|---:|
| Mujeres | **−0,156 años** | **−0,210 años** |
| Hombres | **−0,202 años** | **+0,117 años** |

En Mixmosa, las mujeres seleccionaron candidatos más próximos que el control (cola inferior ≈.003), pero los hombres tuvieron una proximidad menor que la esperada bajo sus propias tasas de sí (cola superior ≈.018). La comparación de signo **no equivale a una diferencia causal entre sexos ni entre plataformas**, y por las múltiples pruebas debe leerse exploratoriamente. El control preserva las oportunidades realmente observadas; no preserva diferencias de edad preferida direccional ni características de interlocutores no medidas.

**Registro 1/3 local:** una observación reproducible y concreta de que la preferencia aparente por proximidad de edad de hombres, **medida como desviación respecto a la permutación por decisor y evento**, cambia de signo entre estos dos mercados de citas rápidas. Identificador `MATE-N46-AGEGAP-REVERSAL`; el estudio original y la literatura ya han mostrado heterogeneidad contextual general, **por tanto no se declara novedad científica**. N42 no genera una segunda unidad 1/3 para la misma idea. Contraste falsador futuro: reproducir en cohortes/mercados prospectivos predefinidos con modelos de edad firmada y oportunidad equivalente; la reversión podría desaparecer bajo comparación causal ajustada.

## Auditoría adversarial, validez y decisión J
- **Interna:** Parquet recuperado, scripts congelados por SHA antes de resultados, Columbia repetido dos veces con mismo SHA256 de salida `968da0ea68e35a36c898a2bfe790fa93a52c1931cef76ebe63077b4cf88f72a4`, Mixmosa repetido con resultados agregados idénticos; zero inconsistencias de edades/campo dentro de ID. **No** clon limpio externo.
- **Causalidad:** ninguna. La sesión de citas es estructurada y los participantes repetidos, ambos lados se influyen, atractivo no medido en estos modelos y popularidad no prospectiva.
- **Generalización:** dos muestras de speed dating extranjero, no población española, no aplicación de citas, no relaciones estables.
- **Novedad:** literatura Fisman 2006 y 2008 ya analiza preferencias por atributos, restricciones de oferta y género. El control actor×evento reduce algunas confusiones; no se reivindica hallazgo novedoso de nivel 2/3.
- **Ética:** no se publicaron datos identificables ni filas originales en el repo AB; fuentes brutas permanecen en adjunto/Google GitHub original.
- **DRIFT D0,4**, mismo dominio con distinción entre semejanza en rasgos y popularidad, no cambio de disciplina.
- **CT2 17/100 →17/100** después de cada ciclo, escala ordinal (no probabilidad). Un hallazgo **1/3 local**, N2=N3=0. N1 acumulado histórico `NOT_AUDITED`.

**AB-DECIDE = STOP_R5** con seis ciclos válidos y **saldo 0**. Las siguientes pruebas con mayor valor requerirían observables prospectivos de preferencias personales, edad y redes de oportunidad equilibradas, un baseline de elección condicional multinivel con efectos por candidato/actor y un holdout externo. No aumentar simulaciones sintéticas para mejorar r ni atribuir a rechazo una pérdida social pública que nunca medimos.

**Solicitud de nueva autorización conforme O6:** para contrastar sistemas de preferencias individuales heterogéneas, modelos de exposición con paridad y tercera fuente observacional, propongo **20 ciclos BRANCHING AB-R** condicionados a instrumentos reales y R5, nunca un objetivo de consumo automático. **SOLICITO BRANCHING 20 CICLOS**.
