# Mercados de pareja · N58–N66 · Un marco de ecología de selección bilateral

**Investigador:** Alejandro Panera Pascual. **Fecha:** 28/10/2026. **Rama:** research/ab-r-mercados-pareja-20261028, sin merge a main. **Autorización:** 9 plazas restantes de 20 ya concedidas; **9 ciclos válidos N58–N66 ejecutados**, cero inválidos, ninguna plaza restante. **60 corridas principales** con 10 condiciones × 6 semillas, más **6 corridas sintéticas post hoc** de equivalencia observacional con su fuente congelada *antes* de esas seis corridas; son **66 corridas, NO 66 ciclos**. N1 nuevos=0, N2=N3=0. CT2=7/100 antes y después, juicio ordinal, no probabilidad. R5: stop tras completar los nueve contrastes útiles, sin entrenamiento humano ni nueva replicación externa.

## Una tesis sociológica integrada, no una prioridad original reclamada

La distribución de parejas observadas resulta de una **ecología de selección bilateral multietapa**: condiciones demográficas y culturales determinan qué parejas son factibles; instituciones y plataformas asignan oportunidades reales de encuentro; se expresan iniciativas condicionadas por preferencias, deseabilidad, normas y atención; el otro extremo responde; la reciprocidad se transforma —o no— en una relación mediante restricciones y decisiones adicionales; las relaciones perduran o terminan en procesos diferentes. **Condicionar solo en parejas constituidas no identifica cuál de los mecanismos produjo su parecido**.

[Modelo de 12 dimensiones, hipótesis causales, definiciones y falsadores](THEORY_AND_DIMENSIONS.md). La revisión bibliográfica en N58 incorporó Kalmijn 1998 (preferencias, terceros, restricciones), Rivera et al. 2010 (assortativity/proximity/relational ties), Blossfeld 2009 (curso de vida y educación), Fuhse y Gondal 2024 (reglas culturales del campo), Wang 2026 (valores/proyectos), Lenton y Francesconi 2010 (límites cognitivos), Lundquist et al. 2024 (diversidad), Hwang et al. 2025 y estudio europeo 2026 (plataforma y sorting), Chen et al. 2023 (ensayo de campo sobre algoritmo y desigualdad), Celdir et al. 2024 (popularidad de rankings), Shi et al. 2025 (experimento de feedback). Se registraron **12 fuentes nuevas** SRC030–SRC041, con contribución exacta, acceso y límites, **11 revisiones de priors** U026–U036, y siete hipótesis nuevas. [Fuente original](../PRIORS/SOURCES.json), [juicios cualitativos](../PRIORS/PRIORS.json), [historial versionado](../PRIORS/UPDATES.json). **Nada de esto se presenta como descubrimiento propio.**

## Reproducibilidad y QA de los módulos ejecutados

Contrato [PREREG.json](PREREG.json), commit `51a387a2eaadbfb9604f0ceff9d62bb0fee32308`, fijado antes de simular. Hash SHA256 de `simulator.py` **dfe5dabc2c5c9cbd07a76471e0d855d85424a26705d1ea626b55ccb35289b279**, congelado en [SOURCE_FREEZE.json](SOURCE_FREEZE.json), commit `61c64410f58c182e1344fdc27a6c56390ee0bb08`, antes de ejecutar. Código íntegro y resultados por semilla en paquete ZIP entregado en conversación, sin datos de terceros. [Resumen auditable](RESULTS_COMPACT.json); `RUNS.json` SHA256 `72f4cadd87dc45f1edcc5ec2370ba507f58f2e337ba886239ebf2767b86c5cd6`, `SUMMARY.json` SHA256 `8cedf4fd0d59d046ee8ec0c0c1814dd971804d35fc68104e3cfd9847ce8a6ab9`. Corrida repetida con hashes iguales. **Clon limpio externo NO_VERIFICADO**.

**Modelo realmente simulado:** 320 agentes ficticios (160 L y 160 R, compatibilidad binaria heterosexual simplificada), cuatro grupos de campo sintéticos, calidad escalar Q independiente de grupo/edad, edades ficticias 18–45, k=12 oportunidades para ambos lados bajo grafos bipartitos 12-regulares y decisiones binarias estocásticas. NO se simularon orientaciones diversas, valores ideacionales medidos, familias/terceros, estatus público visible ante rechazos, aprendizaje longitudinal o duración real. El submodelo sirve para probar mecanismos parciales, no puede explicar *todos* los mercados humanos. Los parámetros numéricos son **estipulados y no calibrados**.

La función de consentimiento unilateral en una oportunidad existente es:

```
Pr(i acepta j) = sigmoid(-0.35 + 2*wQ*(Qj-.5)
                          + wH*1(campo_i=campo_j)
                          - 0.7*lambda*(Qi-.5))
```

`wQ` calidad del candidato, `wH` homofilia explícita, `lambda` umbral creciente con Q propio, **supuesto de software, no hallazgo psicológico**. Reciprocidad = 2 consentimientos sobre la arista; pareja final = matching bipartito de **cardinalidad máxima**, NO emparejamiento estable/óptimo de bienestar. Todos los modelos de una misma semilla comparten calidad, campos, edades y los **uniformes potenciales de aceptación por díada**, lo que reduce ruido al comparar mecanismos. 12 aristas por integrante de L; grado de R también 12 en grafos regulares, **no** en exposición sesgada por popularidad. QA confirma 60/60 corridas principales, cardinalidad ≤reciprocidad, unicidad y grados según modo; seis semillas distintas, no estimación estadística de una población humana.

## Tabla central: medias de seis semillas para diez condiciones

| Condición | % agentes emparejados | r(Q_L,Q_R) parejas | % parejas mismo grupo | % oportunidades mismo grupo | Gini visibilidad R |
|---|---:|---:|---:|---:|---:|
| Nulo sin preferencias por Q/grupo | 80,52 | +0,020 | 24,83 | 24,97 | 0 |
| Calidad consensual sin exigencia endógena | 79,58 | **−0,059** | 26,93 | 24,97 | 0 |
| Calidad consensual + umbral propio creciente | 76,98 | +0,084 | 24,61 | 24,97 | 0 |
| Preferencia explícita mismo grupo | 91,04 | −0,052 | **49,69** | 24,97 | 0 |
| Calidad+umbral+preferencia grupo | 90,73 | +0,115 | **48,26** | 24,97 | 0 |
| Exposición segregada, SIN homofilia | 80,73 | −0,091 | **88,87** | 89,07 | 0 |
| Ranking popularidad (R recibe exposición desigual) | 67,92 | −0,166 | 24,15 | 24,97 | **0,435** |
| Calidad+umbral, k=6 | 58,02 | +0,082 | 26,48 | 26,23 | 0 |
| Calidad+umbral, k=24 | 97,08 | +0,157 | 24,22 | 24,81 | 0 |
| Nulo con exposición segregada | 82,60 | −0,016 | **88,21** | 89,07 | 0 |

Cada r corresponde a correlación entre personas que quedaron emparejadas; las fracciones son proporciones de personas o aristas indicadas, NO matrimonios o swipes reales. Los modelos tienen diferentes números de parejas; interpretar r aislado induce selección de denominador. Nulos y tamaños están en [RESULTS_COMPACT.json](RESULTS_COMPACT.json). **Seis semillas son pocas para afirmar estabilidad universal**. En particular el contraste pareado `common_quality → common_with_reservation` de r tuvo signos [+,+,+,−,+,+] y no es uniformemente positivo.

## N60 · Nulo y sanidad del instrumento
Sin calidad ni similitud explícitas, el grupo compartido en exposición y parejas es ≈25% por cuatro grupos y la correlación Q de emparejados ≈+0,020. No aparece un fuerte sorting sistemático en seis semillas; este control no prueba que el programa sea universalmente válido ni que la distribución de Q coincida con una población real. El matching de cardinalidad máxima sobre respuestas aleatorias produce alta cobertura por construcción.

## N61 · Oportunidades bastan para crear homogamia social

Al reorganizar exactamente 12 contactos por integrante de ambos lados para favorecer proximidad de grupo, la exposición mismo grupo aumenta de 25% a 89% **sin añadir preferencia individual por compartir grupo**. Las parejas resultan 89% del mismo grupo. Un nulo segregado con ningún término de calidad ni homofilia obtiene también ≈88%. El patrón proviene de la composición del grafo, no de la utilidad psicológica. Es ejemplo sintético del mecanismo ya discutido por Kalmijn/Blossfeld y Belot–Francesconi, no prioridad original.

**Demostración post hoc explícitamente adaptativa**: se congeló [EQUIVALENCE_SOURCE_FREEZE.json](EQUIVALENCE_SOURCE_FREEZE.json), commit `c150a122c9bb1e3eb333a34bce1b45c907be2684`, antes de ejecutar un anexo de seis semillas que reconfigura el grado-12 para ≈50% exposición mismo grupo. Target **elegido después de observar** que preferencia explícita había dado ≈49,7% parejas mismo grupo; por tanto es **construcción ilustrativa**, no prueba confirmatoria. Los resultados fueron:
- Preferencia homofílica individual en oportunidades aleatorias: exposición mismo grupo 24,974%, parejas mismo grupo 49,691%, cobertura 91,04%.
- Oportunidades segregadas deliberadamente en 50,017% con `wH=0`: parejas mismo grupo 49,988%, cobertura 81,46%.
- **Mismo observable final ≈50%** pese a mecanismos incompatibles, con **distintas oportunidades y coberturas** observables que permiten distinguirlos. [Registro agregado post hoc](EQUIVALENCE_COMPACT.json). El código adicional y salidas originales están en el ZIP de reproducción.

## N62 · Popularidad, umbrales propios y semejanza explícita
Un consenso por calidad **sin umbral propio** NO garantiza asociación positiva entre Q de emparejados aquí: r≈−0,059. Al fijar umbral que aumenta en calidad propia, r sube a ≈+0,084, con cobertura inferior y dispersión por semilla, con un seed de contraste pareado negativo. `wH=1.1` conduce en cambio a ≈50% de coincidencia de grupo con exposición aleatoria 25%; cuando se combinan ambos mecanismos, rQ≈+0,115 y 48% parejas de mismo grupo. Es un argumento de que múltiples microreglas pueden coexistir y conducir a resultados que no se resumen con una única correlación; **las magnitudes dependen directamente de parámetros elegidos**.

## N63 · Intermediario algorítmico y desigualdad de visibilidad
La política `popularity_imbalanced` muestra a cada persona L doce candidatos, pero concentra las visualizaciones sobre personas R de Q alto: correlación Q-visibilidad recibida ≈+0,885, Gini de visibilidad ≈0,435, y en seis semillas una media de **2,33 personas R de 160 nunca vistas**; no es igualdad de exposición por candidato. Con este algoritmo simplificado y las mismas probabilidades de respuesta, la cobertura baja a 67,92% frente a 79,58% con oportunidades k-regulares aleatorias. **No atribuir este resultado a plataformas reales**: es consecuencia del algoritmo y paridad unilateral impuestos, diferente capacidad de oferta y distribución de la oportunidad. Referencia de campo pertinente: Chen et al. 2023 sobre desigualdad y matching bilateral.

## N64 · Las etapas y el condicionamiento cambian el signo de correlaciones
En el escenario de calidad con umbral propio (media por seis semillas), el `r_Q` de exposición es ≈+0,007; en reciprocidad ≈+0,099; en parejas exclusivas ≈+0,084. En el escenario de calidad sin umbral, la correlación en aristas de reciprocidad ≈+0,017 pero en parejas finales ≈−0,059: la etapa de matching cambia la muestra de parejas, aun usando el mismo grafo. El grafo de pares observados es **selección por consentimiento de dos extremos y congestión**, no prueba de parecido deseado en sí mismo. No hay desenlace longitudinal simulado (aún no implementado), así que no fingir persistencia de parejas.

## N65 · Densidad del mercado y límites de representación

En `quality+reservation`, variar **k=6,12,24** conduce respectivamente a cobertura **58,0%, 77,0%, 97,1%**, con rQ de parejas ≈+0,082, +0,084, +0,157. Esto es un **experimento con presupuestos de oportunidades distintos**: no adjudicar el cambio a personalidad, estabilidad o causalidad humana. La simulación es heterosexual/binaria, monógama bajo matching exclusivo, no representa uniones LGBTQ+, consentimiento no binario, relaciones poliamorosas, movilidad geográfica real, religión, etnia, historia familiar, capacidad material, preferencias de fertilidad, información, discriminación, sexo, salud mental o bienestar. El marco teórico sí identifica esas dimensiones e instrumentos, pero **NO son módulos ejecutados**. Describir un futuro módulo no cuenta como corrida ni ciclo empírico.

## N66 · Síntesis adversarial y plan de falsación
A. La idea «homogamia emergente sin homofilia» **tiene prioridad externa firme** (Topinkova-Diviak 2025, Hitsch 2010, economía de matching y Kalmijn 1998). El principal mérito local es un **contraejemplo didáctico de no-identificación multietapa**, no un hallazgo novel 2/3. B. El simulador no ajusta valores de status/belleza desde personas y elegir parámetros apropiados para obtener una correlación favorable es **imponer**, no contrastar, un mecanismo. C. Preferencias exclusivas vs oportunidades segregadas producen 50% de misma categoría con distintas tasas de parejas; añadir un solo indicador de homogamia final no identifica motivaciones. D. La intervención no incluye rechazo público, consecuencias de status, aprendizaje social, visibilidad por cohortes, duración o bienestar, así que ese mecanismo queda **sin prueba**. E. El modelo de maximum cardinality no equivale a Gale–Shapley, régimen de libre elección ni preferencias reveladas; compararlo con emparejamiento estable requiere igualdad de oportunidades y criterios temporales. F. Cualquier comparación con Columbia, Mixmosa o el estudio checo 2025 debe respetar unidades, fechas, edad, exposición y derecho de uso; no extrapolar valores de r synthetic a personas.

**Falsador ambicioso pero concreto:** con un dataset independiente que registre realmente perfiles mostrados, decisiones dirigidas, respuestas, tiempos, resultados longitudinales y covariables comparables, estimar por etapa cuánto sorting atribuible a oportunidades, a preferencias explícitas, a umbrales, a ranking y a colas de reciprocidad, usando holdout por usuarios/períodos. Nuestro ESBM solo merecería prioridad científica si hace **predicciones nuevas, prerregistradas y mejores fuera de muestra que Kalmijn/Belot/Topinkova/Chen y competidores formales**. Si los baselines explican lo mismo, abandonar reivindicación de novedad.

**Dictamen AB:** nueve ciclos A–J N58–N66 ejecutados, 66 corridas sintéticas (60 principales + seis adaptativas post hoc), documentación y priors actualizados, **cero descubrimientos 1/3 nuevos** y cero 2/3 o 3/3; **CT2 permanece 7/100**, valoración ordinal de trayectoria a novedad. **AB-DECIDE STOP_R5**, presupuesto de 20 agotado tras los anteriores 11 y estos nueve. No solicitar más simulaciones del mismo generador para mejorar métricas; siguiente vía exige datos de exposición real o experimento autorizado y diseño prospectivo.
