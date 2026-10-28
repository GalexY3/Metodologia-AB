# Informe AB-R MATE10, 28 de octubre de 2026

**Investigador:** Alejandro Panera Pascual. **Alcance:** fase de diseño discriminante y verificación exploratoria, diez ciclos AB A–J. **Contrato previo:** [PREREG.json](PREREG.json), commit `3fce00ebc059599e4244519fdfeac2ed7b935f61`. **Instrumento fijado antes de ejecución:** [experiment.py.gz.b64](experiment.py.gz.b64), commit `a5ca42159c081b6ec34ea58b7b5824cd84d9e40c`, SHA-256 Python `ca792b6c685beb075153659b862475425ed9a4ead74ad4e36e65729ceef6df7e`.

## Contabilidad y alcance
- Autorizados 10; ejecutados 10 (4 `PLANNING_AB_ONLY` de verificación documental y diseño + 6 `EXPERIMENTAL_AB` exploratorios); inválidos 0 detectados; saldo 0.
- **39 ejecuciones sintéticas**: 13 condiciones x 3 semillas (112, 223, 334); cada ejecución tiene 6.000 agentes, hasta 240 rondas y heterosexualidad binaria supuesta.
- Un conjunto adicional de 90 permutaciones de parejas emparejadas, y tres ordenaciones ideales que son límites mecánicos, no comportamientos.
- 2/3 y 3/3: NO ACREDITADOS. Ningún efecto causal real español medido. N1 concedidos: 0; prior-art sobre sorting ya existe. `CLEAN_CLONE_NOT_VERIFIED`.
- CT2 inicial: NO PUNTUADO antes de la campaña. **CT2 post hoc de esta línea: 20/100** (ordinal y no probabilidad) por antecedentes fuertes y ausencia de datos de campo. Al existir un solo punto de CT2 honesto no se crea una curva de evolución ni se inventan valores por ciclo.
- DRIFT: D0.0 dentro de esta misma línea; no hay cambios de disciplina o población humana verificables.

## Reglas implementadas
Estatus y belleza iniciales son **percentiles uniformes independientes**. No hay variables reales del INE dentro del simulador, por lo que el cálculo es un laboratorio ordinal y no una calibración social nacional. Las mujeres valoran estatus 0,60/belleza 0,40, los hombres estatus 0,40/belleza 0,60 salvo condición C06. Cada individuo parte de `q=0.90`; cada exposición sin reciprocidad rebaja q en 0,0025 y un rechazo unilateral añade 0,01 salvo ablación C05. Las parejas se forman si ambos aceptan, salen del mercado; encuentros siguientes son simultáneos y pueden repetir un candidato. El máximo temporal es T=240. En C08 se resta físicamente estatus `delta=0.002` al rechazado y la pérdida modifica su valor observado en todas las rondas siguientes.

Se calcula como estimando primario la correlación Pearson entre percentiles **de valor inicial para el sexo opuesto** de los miembros de las parejas existentes. También la cobertura de población completa (incluyendo solteros) y la distancia mediana en percentiles. La correlación entre personas emparejadas condiciona a haber conseguido pareja y puede esconder exclusión selectiva.

## C01, antecedentes y novedad (planificación documental)
Hitsch, Hortaçsu y Ariely (2010) encuentran que las preferencias pueden generar emparejamiento selectivo, usando datos de citas y una predicción de matches estables. Por tanto el enunciado general «homogamia sin gusto directo por similitud» no puede reivindicarse original sin más. Bruch y Newman (2018) observan jerarquías de deseabilidad y búsqueda aspiracional en cuatro ciudades estadounidenses. Gale y Shapley (1962) y Choo y Siow (2006) son rivales analíticos de matching estable y modelo de mercado matrimonial. **Anomalía/revisión:** la innovación específica, si existe, debe formular una predicción discriminante sobre aprendizaje, redes locales o pérdida observada de reputación frente a esos antecedentes. No se ha verificado exhaustivamente prioridad científica.

Fuentes: [Hitsch et al. AER 2010](https://doi.org/10.1257/aer.100.1.130), [Bruch y Newman 2018](https://doi.org/10.1126/sciadv.aap9815), [Gale-Shapley 1962](https://doi.org/10.1080/00029890.1962.11989827), [Choo-Siow 2006](https://doi.org/10.1086/498585).

## C02, denominador real (planificación documental)
Según la [ECP del INE](https://ine.es/dyngs/INEbase/operacion.htm?c=Estadistica_C&cid=1254736177095&idp=1254735572981), España tenía 49.801.559 habitantes el 1 de julio de 2026 (24.462.607 hombres, 25.338.952 mujeres). Esta distribución **no equivale** a la distribución de hombres y mujeres solteros, heterosexuales, disponibles y usuarios de aplicaciones de citas de 18–40 años. Se localizó el acceso oficial a tablas por sexo y edad, pero **no se descargaron ni verificaron microdatos/contajes de usuarios elegibles**. Pendiente construir cohortes locales y límites de observabilidad. Los ratios `0.491/0.509` de C10 son intervención sintética, no calibración válida.

## C03, estatus y heterogeneidad social (planificación documental)
El Gini de renta de la ECV y los atributos de estatus sociológico son constructos diferentes. Cuando se transforman los valores a percentiles, la forma de la lognormal inicial puede desaparecer de las decisiones; por ello usar el Gini 0,308 como «realismo» es insuficiente. El [INE ECV 2025](https://www.ine.es/dyngs/Prensa/ECV2025.htm) aporta indicadores de renta y privación. La investigación en España de López-Rodríguez y Gutiérrez (2023) utiliza microdatos EPA sobre homogamia educativa. Se seleccionan como sectores prioritarios: edad, área urbano/rural, educación, situación laboral, cohortes y migración. **No existe aquí una muestra multivariada calibrada ni un archivo EPA procesado**.

## C04, outcome y validez (planificación documental)
Una correspondencia online no equivale a una relación consolidada, convivencia o matrimonio. La [investigación española publicada por el Banco de España en 2026](https://www.bde.es/wbe/es/publicaciones/analisis-economico-investigacion/documentos-trabajo/assortative-mating-inequality-and-rising-educational-mobility-in-spain.html) documenta asociaciones entre emparejamiento educativo y movilidad, pero no valida el modelo Tinder. Se define un futuro estimando empírico por sector y tipo de relación: tasa de reciprocidad, tiempo a primer match, probabilidad de transición a vínculo, y matrices de pareja observadas ajustadas por composición de elegibles. **No se ejecutó aún ese análisis externo.**

## C05–C10, pruebas computacionales
| Ciclo | Comparación | Correlación de valor (media de 3 semillas) | Cobertura total |
|---|---|---:|---:|
| C05 | Fatiga sola, β=0 | 0,9564 | 67,12 % |
| C05 | + rechazo, β=0,01 | 0,9673 | 89,56 % |
| C06 | Ponderación simétrica 50/50 | 0,9674 | 89,80 % |
| C06 | Ponderación cruzada 60/40 | 0,9673 | 89,56 % |
| C07 | Pools de 100 | 0,8331 | 72,36 % |
| C07 | Pools de 600 | 0,9090 | 77,11 % |
| C07 | Pool de 6000 | 0,9673 | 89,56 % |
| C08 | Sin pérdida efectiva de estatus | 0,9673 | 89,56 % |
| C08 | Pérdida de 0,002 por rechazo | 0,9584 | 83,11 % |
| C09 | Sin ruido perceptivo | 0,9673 | 89,56 % |
| C09 | Mezcla 20 % ruido por evaluación | 0,9420 | 99,07 % |
| C10 | Sexo 50/50 | 0,9673 | 89,56 % |
| C10 | Sexo 49,1/50,9 | 0,9623 | 80,01 % |

**C05:** el feedback hace aumentar la cobertura, pero la correlación condicionada varía poco; no concluye que aprender del rechazo sea la causa principal de sorting. **C06:** `r` total es casi idéntica aunque las correlaciones atributo-a-atributo cambian; hay una diferencia en composición del valor, no en su gradiente principal. **C07:** la segmentación aleatoria disminuye r y cobertura, pero mezcla dos tratamientos (tamaño del mercado + diferencias aleatorias de composición sexual local). Requiere pools con conteos balanceados y redes de exposición medibles. **C08:** la pérdida efectiva, bajo las normas supuestas, reduce simultáneamente cobertura y r inicial; no demuestra que el rechazo dañe el estatus de personas reales. Además es globalmente visible por construcción: investigar redes donde un rechazo privado no sea público. **C09:** el ruido idiosincrático baja r y eleva cobertura; debe distinguirse gusto estable de ruido blanco por ronda. **C10:** leve desbalance sexual amplifica exclusión en esta implementación; hace falta separar composición, horizontes y fallos de oportunidad por sexo. Rechazar un match nunca asigna castigo por similitud.

En C10, manteniendo los mismos emparejados, 90 permutaciones produjeron `r≈0,0015` y distancia mediana `≈0,268`. Una ordenación ideal ex post dio `r≈1`; solo sirve como límite algebraico, no como comparador conductual competente. Los tamaños muestrales individuales son altos pero las observaciones dependen de las mismas reglas.

## Auditoría F e interpretación I
**Invariantes inspeccionados:** no hay parejas duplicadas simultáneamente; estatus se actualiza después del rechazo unilateral; estado de pareja es irreversible; seeds y N/T fijados; se conserva `coverage_m/coverage_w`. **NO ejecutados:** prueba de regresión independiente del código, validación en clon limpio, baseline Gale-Shapley/Choo-Siow, exposición realista asíncrona, comparación con usuarios reales y modelo con edad/elegibilidad real. Por tanto la auditoría es interna, no certificación independiente.

**Riesgos principales**: (1) un único score agregado puede reificar jerarquías; (2) porcentaje entre emparejados es selectivo; (3) sexo/género binarios y preferencias 60/40 son restricciones experimentales, no generalizaciones; (4) estática vs cambio real del estatus; (5) fuentes España no aportan datos directos de belleza, swipes o rechazo; (6) grupos locales aleatorios distorsionan composición, y el mismo candidato puede volver a aparecer; (7) la comparación inicial 1:100 de 49,8 M en conversaciones pasadas mezclaba censo con elegibilidad.

**Grados (O4)**: todos los contrastes son 0/3 o indicios exploratorios condicionados al generador en espera de auditoría de novedad y reejecución independiente. N1 nuevo contado: **0**; N2=N3=0. Publicar correlaciones como observaciones humanas sería incorrecto.

## Actualización H y decisión J
La hipótesis de homogamia de valor sin preferencia homofílica **permanece compatible dentro de este generador**, con amplia dependencia de reglas y antecedentes científicos. La pretensión de novedad de esta formulación genérica se reduce. Priorizar tres líneas de falsación: (i) modelo de matching estable competente con las mismas preferencias y restricciones; (ii) pools balanceados y redes de exposición con historia de swipes; (iii) estatus observable por redes y evidencia plausible de difusión de reputación. La siguiente intervención útil requiere un nuevo tipo de evidencia española y auditoría externa del código, antes de ampliar el tamaño de agentes.

**CT2 20/100 post hoc, ordinal**, no extrapolable a población real y sin trayectoria previa auténtica. Bajo R5, se detiene la campaña de diez; ninguna extensión comienza sin autorización.

**Solicitud excepcional conforme al encargo del investigador:** 8 ciclos nuevos en `BRANCHING AB-R`, con cuatro ciclos de validación/pools y cuatro de inferencia y controles contra datos españoles; autorizar expresamente antes de ejecutarlos. `SOLICITO BRANCHING 8 CICLOS`.
