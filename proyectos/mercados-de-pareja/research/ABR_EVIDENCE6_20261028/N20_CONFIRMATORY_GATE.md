# N20 · Contraste confirmatorio futuro: contrato de información y transporte empírico

**Estado en esta campaña:** `PLANNING_AB_ONLY`, `CONFIRMATORY_NOT_EXECUTED`. No existe dataset individual verificado con atributos, preferencias, secuencia de exposición y resultados de reciprocidad; el simulador no es holdout y no justifica causalidad social.

## Punto de partida: rival explicativo competente
- H0 `STATIC_PREF`: una estructura de preferencias compartidas y oportunidades bipartitas observables genera assortative matching; no precisa adaptación de q ni sanción reputacional.
- H1 `DYNAMIC_SELECTION`: con el MISMO conjunto de oportunidades, preferencias y exposición ex ante, la actualización temporal de q tiene efectos incrementales sobre cobertura y distribución de valor entre parejas.
- H2 `VISIBLE_REPUTATION`: sólo si terceros reciben señales efectivamente observables de rechazo, éstas modifican evaluaciones y elecciones futuras, además del historial de opciones y preferencias.
- H3 `SELECTION_ARTIFACT`: correlación condicionada a tener pareja aumenta mientras cobertura cae; el mecanismo agregado no mejora bienestar ni reproduce distribuciones humanas.

## Estimandos diferenciados
Primario I: `Δcoverage` entre estrategias a igual presupuesto de oportunidades efectivas y entorno, por deciles de valor prefijados ex ante. Primario II: `Δgini-gap` o distancia absoluta mediana de valor entre emparejados, acompañada siempre por cobertura y composición de no emparejados. Descriptivo separado: `corr(V_h,V_m | pareja)` y null con mismos emparejados reordenados respetando márgenes. Reputación sólo si existe observabilidad humana de terceros: `Δterceros_juzgan_i` con diseño no lesivo y consentimiento.

## Puertas antes de la ejecución
1. Dataset original de preferencias y ratings independientes, con definición de "valor" ex ante que no dependa tautológicamente del mismo outcome que queremos explicar.
2. Acceso legal/consentimiento, privacidad, aprobación ética cuando corresponda, desidentificación y plan para no crear daños reputacionales artificiales.
3. Exposiciones bilaterales reales observables y denominador personas solteras voluntariamente participantes; no sustituir por total INE.
4. Comparador matching estable y asignación secuencial con **mismo grafo y presupuesto de información efectiva**, no equiparar una política de ranking completo al aprendizaje en tiempo real.
5. Umbral de efecto mínimo de interés y potencia especificados desde datos piloto externos al confirmatorio, después sellar código, protocolo, unidades de análisis, control multiplicidad, ventana temporal y resultados nulos aceptables.
6. Auditoría de implementación y reproducción de un tercero, además de prereg DOI/OSF cuando sean posibles; no reutilizar exploración MATE10/BRANCH8/BRANCH6/EVIDENCE6 como set de test confirmatorio.

## Predicciones falsadoras
- Si DA y una estrategia de decisión secuencial con información equiparada producen el mismo sorting y coverage dentro de límites predefinidos, no hay evidencia de contribución adicional de adaptación de q.
- Si una señal de rechazo observable no cambia valoraciones de terceros en una prueba ética suficientemente potente, se rechaza/estrecha la hipótesis `VISIBLE_REPUTATION`.
- Si mejora la correlación entre parejas pero la cobertura cae hasta excluir sistemáticamente estratos, la tesis debe reportarse como sorting condicionado y no como eficiencia de emparejamiento.
- Si una matriz educativa española ponderada no presenta exceso de homogamia respecto al nulo de composición, falla la generalización educativa específica. Aun un resultado positivo no validaría automáticamente el mecanismo Tinder.

## Decisión
`STOP_LOCAL/STOP_CAMPAIGN` respecto a confirmación hasta obtener las fuentes y la estrategia de acceso. Se permite seguir mejorando instrumentos de forma limitada, pero más simulaciones sobre la misma distribución inventada no convierten la tesis en evidencia empírica.

**Bloqueadores:** `DATA_ACCESS_BLOCKED` (INE csv), `TINDER_EXPOSURE_DATA_UNAVAILABLE`, `THIRD_PARTY_REPUTATION_SIGNAL_NOT_OBSERVED`, `EXTERNAL_CONFIRMATION_NOT_RUN`.
