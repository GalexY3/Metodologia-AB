# Auditoría de acceso independiente · AEA E218862V1 y Stanford HCMST · 28/10/2026

**Alcance:** comprobación documental de fuentes oficiales, interfaces, términos y preguntas de investigación. **NO se han descargado ni inspeccionado bytes de microdatos**, variables de fichero real ni código de replicación de E218862V1; no se ha estimado efecto alguno de esas muestras. Esta auditoría no es replicación de AEA ni de HCMST.

## N76 · AEA/OpenICPSR: acceso legal y adecuación del estimando

**Fuente oficial verificada:** [AEA Data and Code Repository: E218862V1](https://www.openicpsr.org/openicpsr/project/218862/version/V1/view), autores Berkeren Buyukeren, Alexey Makarin y Heyu Xiong, citado 2026-03-05. V1 lista expresamente `Code/`, `Data/`, `Exhibits/`, `Temp/`, y `README.pdf` de 256,1 KB. **Los nombres de carpetas son metadatos de la interfaz; no se conocen sus archivos internos por inspección propia.** Enlace oficial [DOI de depósito](https://doi.org/10.3886/E218862V1); [artículo](https://doi.org/10.1257/app.20240455), *AEJ: Applied Economics* 18(2), 61–106, abril 2026.

**Unidad del estudio según la ficha editorial (no fichero):** encuesta de **más de 1,1 millones de respuestas de estudiantes universitarios** de EE. UU., período 2008-09 a 2019-06, con estrategia de diferencias en diferencias de exposición a la introducción de Tinder según presencia en fraternidades/hermandades; outcomes de actividad sexual, relaciones duraderas, calidad, desigualdad y otros. **Una encuesta individual sobre resultados no es un log de perfiles mostrados, likes, correspondencias o respuestas bilaterales.** No hay evidencia positiva de que la carpeta `Data` contenga aristas de exposición a candidatos ni datos de rechazo público. La gran N no subsana esa diferencia de estimando.

**Acceso intentado (no se sortearon permisos):**
1. La página del depósito se abrió por web y se leyó inventario de primer nivel y ficha. Click en `Data/` y `README.pdf` devolvió cache miss/no hubo bytes. El DOI acortado y el ZIP [AEA 24788](https://www.aeaweb.org/articles/materials/24788) no se recuperaron por navegador. El [apéndice AEA 24787](https://www.aeaweb.org/articles/materials/24787) ofreció texto indexado de tablas/definiciones, pero el PDF remoto no se pudo capturar para verificación visual; no se utilizó para extracción cuantitativa nueva.
2. Intentos Python requests en contenedor contra `www.openicpsr.org`, `www.aeaweb.org`, `data.stanford.edu`, `stacks.stanford.edu` fallaron en resolución DNS. No se abrió ninguna respuesta de bytes, cabecera de licencia del paquete o microdatos. Una búsqueda web de rutas migradas no proporcionó una URL de fichero verificada.
3. [ICPSR informa una transición de openICPSR](https://www.icpsr.umich.edu/sites/icpsr/posts/shared/openicpsr-in-transition), con DOIs preservados según FAQ. El cambio de plataforma podría explicar problemas del enlace antiguo, pero **no lo demostramos** y no debe atribuirse el fallo exclusivamente a la migración.
4. [AEA Data Editor, guía sobre licencias](https://aeadataeditor.github.io/aea-de-guidance/preparing-for-data-deposit.html): licencia CC BY 4.0 por defecto de depósito a menos que el depositante la cambie con LICENSE.txt. **No se ha inspeccionado LICENSE.txt de E218862V1**, por tanto no afirmar que se puedan republicar esos datos.

**Gate N76:** `META_VERIFIED_FILES_NOT_DOWNLOADED`, `UNIT_MISMATCH_FOR_EXPOSURE_DYADS`, `NON_DYADIC_LONG_TERM_OUTCOMES_RELEVANT`, `LICENSE_SPECIFIC_NOT_VERIFIED`. Puede servir para un **baseline macro** del efecto de plataformas en outcomes de estudiantes, pero no para estimar la probabilidad de aceptación entre candidatos bajo el ESBM. Ni su trabajo publicado ni nuestra lectura identifican por sí mismos aceptación reciproca a nivel de perfil. **No se ejecuta diferencia en diferencias propia.**

## N77 · Stanford HCMST 2017–2022: fuente longitudinal independiente pero de otra unidad

[Stanford Libraries](https://data.stanford.edu/hcmst2017) y [registro ICPSR 38873](https://doi.org/10.3886/ICPSR38873.v1), autores Michael Rosenfeld, Reuben Thomas y Sonia Hausen. Muestra base de **3.510 adultos** en 2017, seguidos 2020 **2.107** y 2022 **1.722**. Panel de personas —**no 3 muestras nuevas**—, sin solapamiento de sujetos con la muestra HCMST 2009 (también de Stanford). Contiene preguntas de cómo/cuándo se conocieron las parejas, apps móviles, contexto social, satisfacción y continuidad. Según Stanford, la cohorte tiene una sobrerrepresentación muestral de adultos que se identifican como lesbianas, gais y bisexuales (LGB) y pesos de encuesta específicos.

**Inspección de esquema documental:** registro ICPSR indica datos individuales, no una matriz de contactos/potenciales, cobertura EE. UU. y cortes 2017/2020/2022. La ficha [Data Use Agreement de Stanford](https://data.stanford.edu/hcmst2017) exige: (i) no identificar a individuos, (ii) no cobrar por redistribución, (iii) informar a la persona de contacto del trabajo realizado con esos datos, (iv) cita correcta. No se considera que aquí se hayan cumplido automáticamente obligaciones de estudio con datos: **no se ha descargado ni utilizado la tabla**. ICPSR declara acceso de datos a miembros institucionales y términos del archivo; usar la descarga pública de Stanford no equivale a tener permiso para descargar cualquier versión restringida de ICPSR.

**Archivos anunciados en la fuente primaria:** Stata/SPSS/Rdata v2.2, guía v2.3 y codebook de la combinación 2017–2022; los enlaces de descargas directas de Stanford `stacks.stanford.edu` fallaron en este entorno (cache/robots y resolución DNS). **No se ha abierto el codebook íntegro ni las filas**. La versión 2009 original posee indicadores `w2_broke_up`, `w3_broke_up`, `relationship_quality` y `how_long_relationship` documentados en su [guía Stanford de 2015](https://web.stanford.edu/~mrosenfe/how_meet_public/HCMST_brief_user_guide_v5_June_16_2015.htm), pero **no trasladar automáticamente esos nombres al archivo 2017–2022** sin inspeccionar su codebook.

**Decisión de identificación:** HCMST responde potencialmente a «¿qué tipos de relaciones se mantienen o disuelven?» y permite evaluar de modo descriptivo vínculo entre cómo se conoció la pareja y continuidad, aplicando pesos de panel y reglas de censura, **pero no mide el universo de perfiles mostrados, candidatos disponibles, rechazo a perfiles ni estatus previo**. No puede confirmar nuestro mecanismo de reputación por rechazos, ni el algoritmo de recomendaciones, ni preferencias entre todas las oportunidades no realizadas.

**Riesgos obligatorios de una futura ejecución:** considerar selección en tener pareja en 2017, selección y atrición al seguir en 2020/2022, ajuste de pesos LGB y de seguimiento, censura, ruptura vs pérdida de contacto, confusión entre canal de encuentro y cohortes de relación (uniones online más jóvenes), cambios pandémicos, correlaciones entre miembros de pareja, definición de parejas que existían antes de línea base, y tamaño efectivo de subgrupos. Un contraste base sería comparar modelos de supervivencia ponderados de relación por modo de encuentro (online vs offline) con edad de la unión, características de las dos personas y cohorte de formación, seguido por baseline de supervivencia sin modo de encuentro. **No ejecutar** hasta verificar archivos, definiciones, periodos y derechos. Resultados no causales sin identificación adicional.

## Verificaciones y candados

| Requisito | E218862V1 | HCMST 2017–22 |
|---|---|---|
| Identidad oficial de fuente/versión | Verificada | Verificada |
| Metadatos y unidad | Encuesta individual de estudiantes | Panel individual de adultos |
| README/codebook original leído | No | No |
| Archivo de microdatos descargado/verificado | **No** | **No** |
| Derechos del fichero comprobados plenamente | No, licencia específica no inspeccionada | Condiciones públicas Stanford leídas; obligaciones aún no activadas con microdatos |
| Exposiciones de perfiles no elegidos | No documentado | No |
| Decisiones por candidato y respuestas bilaterales | No documentado | No |
| Información de relación a largo plazo | Sí, según publicación | Sí, según ficha de estudio |
| Simulación calibrada o réplica propia | **No** | **No** |

**AB R5:** dos auditorías reales N76 y N77, **cero nuevas ejecuciones de análisis de datos humanos, cero simulaciones repetitivas y nueve plazas no iniciadas N78–N86**. Hay una ruta de medición longitudinal distinta que merece quedar registrada; no permite aún una nueva prueba confirmatoria. Reintentar descargas con un navegador autorizado de usuario o recibir archivos originales con su licencia, sin usar espejos no autorizados, es siguiente dependencia. No presentar política de descarga implícita ni simular efectos.
