# V20. Preinscripción metodológica — trayectoria del coste de donación (11-11-2026)

**Pregunta**. ¿Pueden agentes con parámetros privados, aprendizaje por recompensa propia y donación dirigida voluntaria mantener una convención de contribución cuando el coste de ayudar a otros aumenta?

**Hipótesis contrastable**. A igualdad de actualizaciones e inicialización neuronal, una progresión de costes (0,01 → 0,12) conserva mayor cooperación bajo coste final 0,12 que entrenar desde el comienzo al coste alto. Si no existe ventaja, se rechaza para las condiciones examinadas.

**Mecanismo excluido**. No se impone cooperación, no se bonifica directamente el acto de donar, no hay imitación, parámetros compartidos ni recompensa colectiva.

**Tratamientos**. Coste constante alto, transición gradual y transición brusca, con misma arquitectura, número de actualizaciones, gamma, señales sociales y topología. Inicializaciones 3111 y 4111 como primera réplica; nuevas semillas para verificación posterior. El coste de evaluación es siempre 0,12. Además se mide la respuesta de las políticas congeladas a suprimir o permutar la información social y a obligar temporalmente a donar a un actor.

**Variables**. Media alimentaria final por sociedad, porcentaje de donaciones, cobertura, beneficio causal de donar una vez sobre el retorno propio descontado, generalización a grado/topología/k y variabilidad entre semillas. Se comparan acciones de donar siempre, al azar, nunca y reciprocidad explícita.

**Criterio exigente**. Una alta tasa de donaciones es insuficiente para reclamar cooperación aprendida. Se exige evidencia de beneficio intertemporal propio de donar, dependencia específica de quién colaboró, replicación entre semillas y resistencia a intervenir la información sin sesgos de evaluación. Ninguna condición aislada acredita un resultado universal.

**Fuentes**. Código del modelo previo de donación dirigida en targeted_gifts.py y función de entrenamiento REINFORCE en train_targeted.py, reutilizados sin modificar. Nueva implementación v20_curriculum.py. Las evaluaciones de entrenamiento no sustituyen las pruebas independientes y congeladas.
