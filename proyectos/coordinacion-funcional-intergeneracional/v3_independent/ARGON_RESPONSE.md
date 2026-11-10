# Respuesta analítica a Argon — V3B

**10 de noviembre de 2026.** Evaluación de la crítica entregada como «Texto pegado(6).txt», referida al commit previo 29a3d245. Se conservan los pilotos V2 de la arquitectura anterior. Esta corrección de V3B no constituye por sí misma evidencia de aprendizaje colectivo.

## Objeciones correctas

**Aliasing en el espacio de acciones.** En el código anterior, elegir voluntariamente el color c y aceptar una petición del color c daban el mismo estado siguiente. V3B utiliza exactamente k acciones para elegir el siguiente color, incluido mantenerse. Las peticiones son información dirigida (cheap talk); se registra si coinciden con la elección, pero no se infiere obediencia causal.

**Dificultad del refuerzo colectivo puro.** El aprendizaje multiagente independiente con recompensa de equipo y políticas que cambian simultáneamente tiene problemas documentados de no estacionariedad y atribución de crédito. Las condiciones C1 y C2 utilizan REINFORCE con la misma recompensa colectiva. Una línea base leave-one-out por tiempo y k, formada con los retornos de otros mundos, reduce varianza sin introducir premio por agente, y los gradientes se recortan por individuo.

**Escalabilidad de cerebros individuales.** No es legítimo trasladar directamente una cohorte de 36 políticas individuales a 960 nodos sin definir un mecanismo de nacimiento o transferencia. La comparación entre tamaños necesita nuevas poblaciones, reclutamiento o transmisión explícitos.

**Controles C1/C2/C3.** C1 cambia voluntariamente sin mensajes; C2 añade peticiones y snapshots dirigidos con idéntico reward global; C3 elimina mensajes durante evaluación de C2, conservando la capacidad de cambiar de color. C3 identifica dependencia del canal en una política entrenada y también introduce cambio de distribución. No prueba que toda cooperación necesite mensajes.

## Objeciones plausibles, pero no demostradas

**Memorización estática.** Es un riesgo auténtico para políticas por identidad. Sin embargo, renombrar aleatoriamente los colores iniciales NO descarta un convenio fijo en el que cada agente adopta una etiqueta absoluta, porque el objetivo es simétrico a las etiquetas. La nueva política puntúa cada candidato con un scorador único DENTRO de cada agente: es exactamente equivariante ante permutar colores; un test explícito lo confirma. Todavía podría emerger una convención espacial o dependiente de identidad, por lo que se necesitan permutaciones de identidades y perturbaciones.

**Fracaso garantizado al aumentar N.** La no estacionariedad y la varianza de la señal común dificultan aprender, pero no implican que la varianza sea siempre proporcional a N ni una imposibilidad universal. La frase «cada red recibe 1/N muestras» depende de cómo se asigne el presupuesto de entrenamiento; con B mundos paralelos todos los agentes reciben B trayectorias de decisiones cada actualización.

**Supuesto cherry-picking deliberado.** La presentación temprana del 8/8 de la cohorte 221 de N960 fue selectiva y exageró la robustez; las otras cohortes 222 y 223 desmintieron la supuesta generalización sólida. El texto crítico no demuestra intención de ocultar datos. La práctica correcta es presentar conjuntamente todas las cohortes predefinidas, incluyendo resultados negativos.

**Solo tirar dados y congelarse.** Las tasas reducidas de aceptación de V2 son compatibles con esa explicación, pero no la identifican de forma única. La tasa de agentes que acepta peticiones por turno tampoco es literalmente la tasa de mensajes rechazados. Hay que estudiar aceptación condicionada, identidad del emisor, mensajes y respuesta a shocks.

**Resolución local de 1/9.** Ver una muestra local de nueve colores no establece una barrera formal de precisión de la organización mundial. Puede haber información acumulada, mensajes de varios vecinos y feedback de equipo repetido. No puede tratarse 1/9 como un límite matemático de equilibrio.

## Métricas

La distancia D=0,5·Σ_c|n_c/N−1/k| debe compararse con su esperanza EXACTA bajo asignación IID uniforme E[D_IID]. El cociente D/E[D_IID] se denominará «desequilibrio relativo al azar», no «hiperuniformidad». Valores menores que uno describen menos desajuste que una referencia IID; tampoco demuestran cooperación mediada por mensajes. La verdadera hiperuniformidad requiere fluctuaciones espaciales en múltiples ventanas. El óptimo matemático puede ser D=0 si N es divisible por k; E[D_IID] no es un mínimo de error.

## Estado implementado

- environment_v3.py: cambio voluntario a cualquiera de los k colores legales, incluso sin mensajes; mensajes salientes opcionales, recepción múltiple y actualizaciones síncronas.
- individual_agents.py: N políticas con pesos propios, scorador equivariante de opciones de color dentro de cada persona; las observaciones incluyen solo vecinos directos, peticiones dirigidas y feedback previo.
- train_independent.py: retorno de equipo compartido, baseline leave-one-out formado por otros mundos del mismo k, sin crédito causal por agente, sin crítico global, clipping y momentos de Adam separados por bloque de agente.
- test_individual.py: 10 pruebas automáticas aprobadas; incluyen aislamiento de gradientes, equivariancia exacta, self-change sin mensajes, mensajes múltiples y no filtración de mensajes no entregados.
- Solo se ejecutaron pruebas de arranque de DOS actualizaciones de entrenamiento por C1 y C2. **No hay resultados V3B que acrediten aún cooperación aprendida.**

## Referencias contrastadas

Foerster et al. (2018), Counterfactual Multi-Agent Policy Gradients, AAAI, https://doi.org/10.1609/aaai.v32i1.11794.

Investigation of independent reinforcement learning algorithms in multi-agent environments (2022), https://pmc.ncbi.nlm.nih.gov/articles/PMC9530713/.

Torquato y Stillinger (2003), Local Density Fluctuations, Hyperuniformity, and Order Metrics, https://doi.org/10.1103/PhysRevE.68.041113.

## Conclusión metodológica

Es necesario experimentar C1 vs C2 con cohortes independientes, semillas apareadas, baselines aleatorios de parada y pruebas de perturbación. Un C2 mejor que C1, seguido de C3 con degradación, apoyaría un papel funcional de los mensajes para políticas concretas bajo este simulador. No se debe anticipar un resultado positivo ni interpretar un simple nivel bajo de churn como prueba de consenso colectivo.
