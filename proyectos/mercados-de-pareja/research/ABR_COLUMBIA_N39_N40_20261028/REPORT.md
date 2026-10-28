# Mercados de pareja · AB-R N39–N40 · Columbia vs Mixmosa

**Programa:** Alejandro Panera Pascual · **Fecha:** 28/10/2026 · **Rama:** `research/ab-r-mercados-pareja-20261028`. **Estatus:** análisis observacional exploratorio con dos fuentes de citas rápidas; no se ha validado el mecanismo de pérdida de estatus por rechazo ni comportamiento español de Tinder.

## Procedencia y ejecución
- [Prerregistro N39–N40](PREREG.json), commit `c1382f77113bce9e0bf2e275a77ccb2403f5c053`; se fijó después de validar formato y correspondencia de filas, **antes de estimar correlaciones de popularidad y construir nulos**.
- Archivo adjunto por el usuario: `speed_dating_clean.parquet`, **297.736 bytes, SHA256 `a0fe55d6172d01f81d6c7e2546330828cb98d1f631b2598fec4d4f4660eaa37d`**, versión limpia publicada en [ZharlieSineFine/Speed-Dating-Reciprocal-Recommender-System](https://github.com/ZharlieSineFine/Speed-Dating-Reciprocal-Recommender-System), Git blob `c873e1466f9594f3b709b0da70d7dc4a2739b1cd`. **No se republica el dataset de participantes en este proyecto**.
- El entorno carecía de `pyarrow` y no tenía acceso de red para instalarlo. Se implementó un lector local de Parquet mediante metadatos Thrift Compact y descompresión `libsnappy`, que leyó las columnas necesarias. Fuente congelada con SHA256 en [SOURCE_FREEZE.json](SOURCE_FREEZE.json), commit `9d9bcf9a6a11b44102b3dbd0dac1c71b10fb4af6`. El código reproducible se proporciona al investigador como ZIP en la conversación (no archivado todavía íntegramente en el repositorio; **CLEAN_CLONE_NOT_VERIFIED**).
- Se ejecutó dos veces la corrida principal con semilla 20261028, 1.000 permutaciones por cada nulo y 1.000 réplicas de bootstrap por evento; el archivo agregado fue idéntico byte a byte (SHA256 `f43e9deae3366229707b79ce5324c4a42e24410cb44fd7cd6637b15eba98704d`). [Salida agregada](AGGREGATES.json), sin registros individuales.

## N39 · Auditoría y resultado real
El Parquet contiene **8.368 filas dirigidas y 121 columnas**. Cada encuentro aparece dos veces, una por persona, perfectamente reflejado. El fichero depurado contiene **4.184 citas únicas**, 21 sesiones (`wave`), 551 personas (274 mujeres y 277 hombres). Se comprobó que no faltaban filas espejo, que `dec` de una fila coincidía con `dec_o` de su inversa y que `match = dec × dec_o` se cumplía **sin excepciones**. El archivo es una muestra limpiada de la versión mayor de Columbia que suele citar 8.378 filas; **no recuperar las diez filas omitidas sin evidencia del preprocesamiento**.

Decisiones: mujeres **1.529/4.184 = 36,54 %**, hombres **1.986/4.184 = 47,47 %**, y **690/4.184 = 16,49 %** encuentros con interés mutuo. No representan 690 parejas exclusivas: una persona puede aceptar a varias.

Se calculó **popularidad como proporción de respuestas positivas recibidas en otras citas**, excluyendo la díada focal de ambos miembros y requiriendo al menos tres exposiciones restantes. Las 4.184 citas cumplen el criterio y las 690 mutuas están distribuidas entre las 21 sesiones.

| Estimando | Resultado |
|---|---:|
| `r(popularidad_h,popularidad_m)` entre 690 aceptaciones mutuas | **+0,1244** |
| `r` entre todas las 4.184 citas observadas | −0,0441 |
| `r` entre las mutuas, centrando por sesión | +0,1934 |
| Nulo: permutar etiquetas mutuas dentro de cada sesión (conservar n.º de mutuas) | media −0,0386, cuantiles 95 % [−0,1022; +0,0283], p cola superior exploratoria 0,001 |
| Bootstrap por 21 sesiones, r de mutuas | cuantiles 95 % [+0,0376; +0,2516] |

La asociación positiva es **modesta**, no la diagonal casi perfecta de algunas simulaciones anteriores. La permutación por eventos no conserva las propensiones individuales de ambos participantes. Las inferencias dependen de sesgos de invitación/selección, perfiles repetidos, estructura del evento, medición de popularidad por otros encuentros del **mismo evento** y la naturaleza de citas rápidas presenciales.

### Reciprocidad frente a tres controles
Las 690 citas con interés mutuo se compararon con 1.000 permutaciones cada una:
- Reordenar decisiones femeninas dentro de cada evento: media **710,21** mutuas [683; 739], cola inferior p≈0,089.
- Reordenar decisiones de cada mujer entre sus propias citas en ese evento, preservando sus sí: **673,46** [651; 697], cola superior p≈0,087.
- Reordenar independientemente decisiones de cada persona entre sus propias citas, preservando ambos grados de aceptación: **708,80** [679; 738], cola inferior p≈0,104.

**No se identifica un exceso robusto e inequívoco de mutualidad**, y elegir un único nulo alteraría la interpretación. Los p son diagnósticos de permutación exploratoria, no pruebas causales de población.

### Sensibilidad posterior a observar resultados, explícitamente NO confirmatoria
Se diseñó después del principal un control alternativo: permutar decisiones por persona y evento, recalcular las popularidades que se reciben en otras citas y el conjunto de aceptaciones mutuas. En 1.000 repeticiones dio `r` media **−0,1743** (cuantiles [−0,2503; −0,0949]), frente a `+0,1244` observado; los matches nulos promediaron 709,4. El contraste altera conjuntamente red efectiva de matches y popularidades, de modo que **no es el mismo estimando condicionado** que el nulo principal; fue elegido **post hoc** y no prueba mecanismo original. [Registro separado](POSTHOC_SENSITIVITY.json).

## N40 · Réplica externa y dictamen adversarial

[Mixmosa, muestra anterior](../ABR_REALDATA13_20261028/N33_N35_EXTRA_RESULTS.json): 1.895 citas presenciales de ocho minutos, 30 eventos, 410 participantes y **259** aceptaciones mutuas. Popularidad estimada excluyendo fecha focal: `r=−0,0159` entre mutuos, con control de permutación por evento media `−0,0545`, cuantiles [−0,1644; +0,0685]; el valor observado estaba dentro del nulo. Columbia: 4.184 fechas únicas, 21 eventos, 551 personas, 690 mutuas, `r=+0,1244` entre mutuos y resultado por encima de su control por evento.

**Resultado comparativo:** una asociación débil positiva aparece en Columbia pero no en Mixmosa. Es una **réplica de protocolo operacional aproximada en otra muestra observada**, no replicación positiva de un hallazgo uniforme ni confirmación del mecanismo causal del simulador. Columbia realiza citas rápidas de aproximadamente cuatro minutos, Mixmosa de ocho, en poblaciones/contextos y tiempos distintos. Incluso el constructo popularidad, aunque operacionalmente similar, depende de las oportunidades y composición observadas. No hay un control idéntico de propensiones participantes, asignación aleatoria real o modelo de preferencias homofílicas frente a ranking compartido.

**Consecuencia epistemológica:** sostener «las parejas reales se ordenan en un valor único con r≈0,9 sin homofilia» sería incompatible con estos indicadores y con la complejidad de la literatura de matching. La prueba confirma que se puede **medir** un fenómeno de ordenación por popularidad en un mercado observado, pero que su dirección y magnitud dependen del contexto. La presencia de `r>0` no distingue preferencias por semejanza, rankings convergentes, segmentación ni aprendizaje de rechazos. La variable postulada «pérdida objetiva de estatus tras un rechazo» no es observable ni en Columbia ni en Mixmosa.

## Contabilidad y R5
- **N39**: ciclo válido `EMPIRICAL_AB`; fuente, QA, nulos y resultado negativo frente a homogeneidad fuerte ejecutados.
- **N40**: ciclo válido `COMPARATIVE_AB`; resultados Columbia y Mixmosa cotejados, autocrítica, dictamen R5, sin modelo de causalidad estimado.
- Autorización EVIDENCE20: **20/20 ciclos válidos documentados**, sin saldo. Un intento instrumental inválido histórico N32 fue reparado y **no** contado como otro ciclo.
- **N1 nuevos por novedad científica no acreditada: 0; N2=N3=0**. CT2 se mantiene en **17/100**, juicio ordinal no probabilidad, porque el segundo conjunto de datos aporta heterogeneidad observada pero no confirma la tesis causal. **No asignar nivel 2/3 a resultados descriptivos publicados que podrían tener antecedentes.**
- **AB-DECIDE: STOP_R5** a nuevas simulaciones por selección adaptativa. Propuesta para un nuevo presupuesto solo si se ofrece hipótesis discriminante con base bibliográfica, propensity-matched nulls y validación independiente prospectiva; auditar efecto por edad/sector/género y preferencias explícitas si se autoriza.
