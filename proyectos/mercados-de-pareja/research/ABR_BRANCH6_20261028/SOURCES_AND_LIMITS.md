# N12–N14: verificación documental y límites (28/10/2026)

**Regla de integridad:** los tres ciclos son `PLANNING_AB_ONLY` / `DOCUMENTARY_RESEARCH`. No se ejecutó contrastación sobre personas, no se extrajo una matriz completa de matrimonios y no se midió reputación individual. Fuente y consulta quedan documentadas sin deducir números no observados.

## N12. España, población elegible: dato oficial y bloqueo
[INE ECP 1 de julio de 2026](https://www.ine.es/dyngs/INEbase/operacion.htm?c=Estadistica_C&cid=1254736177095&idp=1254735572981): total de residentes **49.801.559**, hombres **24.462.607**, mujeres **25.338.952**, provisional (nota publicada el 6/8/2026). El portal INE muestra la [tabla nacional 59583, Población residente por fecha, sexo y edad](https://www.ine.es/jaxiT3/Tabla.htm?t=59583); no devuelve una selección numérica de edades en el acceso disponible (`Total: 0 series y 0 datos`). Se probó el CSV nacional `https://www.ine.es/jaxiT3/files/t/csv_bdsc/59583.csv` sin respuesta accesible; la descarga HTTP desde el entorno de ejecución falló por DNS. La tabla `59662` sí presenta CSV pero es de **islas**, NO debe agregarse como total nacional por error. La cifra 20–39 de julio reproducida de fuentes secundarias en BRANCH8 (**5.969.215 hombres; 5.677.941 mujeres**) **NO FUE CORROBORADA DIRECTAMENTE** en esta campaña y no se promueve a dato oficial verificado. El parámetro de fracción masculina nacional no es apropiado para el conjunto específico de solteros heterosexuales que buscan citas. 

En la [ampliación del Censo Anual de Población](https://www.ine.es/dyngs/Prensa/CensoVariables2025.htm) se informa de estado civil, pero **soltería legal** no equivale a **ausencia de pareja** ni a participación activa en apps; no se encontró aquí una tabla que cruce de forma suficientemente fina todos los criterios de elegibilidad. `N12=DOCUMENTARY_SOURCE_VERIFIED + AGE_SEX_2026_EXACT_BLOCKED + ACTIVE_MARKET_BLOCKED`.

## N13. Homogamia educativa contemporánea, bloqueo documentado
El INE publica [tabla 60268](https://www.ine.es/jaxiT3/Tabla.htm?t=60268), «Matrimonios por nivel de estudios de los cónyuges», unidad **matrimonios de diferente sexo**, provincia/total, estudios de mujer y hombre (14 categorías por dimensión) y periodos **2016–2023 visibles** en la vista recuperada. Está confirmada su **estructura de doble clasificación**. La página pública obtenida devolvió `Total: 0 series y 0 datos` sin selección; los intentos de recuperar `csv_bdsc/60268.csv`, `csv_bd/60268.csv` y `px/60268.px` no proporcionaron datos accesibles verificables. **NO se creó ni imputó matriz de cruces.** 

Una vez obtenida la matriz legítima `n_ij` (por año y grupos de edad, con `No consta` identificado aparte), definir:
`D_observada = sum_i n_ii / n`;
`D_independencia = sum_i (n_i+ / n)*(n_+i / n)`;
`indice_relativo = D_observada / D_independencia`;
el estimando compara **matrimonios**, no matches, y se necesita adecuación de clasificaciones y cohortes. No se pueden usar porcentajes del Censo 2001 para completar celdas 2023. `N13=DOCUMENTARY_SCHEMA_VERIFIED + ANALYSIS_BLOCKED`.

## N14. Difusión reputacional observada: literatura
- Campaioli, Zamperini y Cecchinato, «‘Now you’re home’: Awareness cues, rejection and post-digital safety on mobile dating apps», *New Media & Society* (en línea desde **19/5/2025**), DOI [10.1177/14614448251336437](https://doi.org/10.1177/14614448251336437). **Estudio de diario durante un mes, ocho participantes** con diversidad de identidades; describe pistas de actividad, incertidumbre tras rechazo, vigilancia y riesgos de seguridad. No cuantifica caída objetiva de estatus social por swipe. Datos anunciados en [CORA](https://doi.org/10.34810/data2183), no descargados aquí.
- Van der Zanden y Schokkenbroek, «Multiple Facets of Rejections in Online Dating: Exploring Types, Reasons, and Impact», 2024, DOI [10.1089/cyber.2023.0751](https://doi.org/10.1089/cyber.2023.0751), PMID 38963768. Se verificó su resumen: dos estudios transversales de encuesta, primero **n=177**, orientados a tipos, motivos y dolor del rechazo. No establecen que terceros vean rechazados ni una penalización de reputación cuantificable.

### Grafo causal propuesto, no empíricamente identificado
`Rechazo privado R_i,j -> señal al rechazado E_i -> decisiones futuras de i`; 
`R_i,j -> información observable por tercero Z_k` **solo si hay canal de difusión verificable**;
`Z_k -> reputación percibida P_ki -> decisión de k -> resultado de matching`.
La propuesta de «estatus que se pierde» necesita distinguir estatus material, señal reputacional y valoración subjetiva. Una cadena causal de rechazo privado a reputación universal **no viene respaldada** por los estudios localizados. La rama local/social queda como hipótesis futura contrastable, con privacidad, consentimiento y controles contra daño. La publicación de perfiles individuales de puntuación social no forma parte del proyecto.

### Estado de confirmación externa
`NOT_EXECUTED`; ni la ECP ni la estadística de matrimonios ni los diarios sobre rechazo verifican por sí mismos las ecuaciones Tinder del generador.
