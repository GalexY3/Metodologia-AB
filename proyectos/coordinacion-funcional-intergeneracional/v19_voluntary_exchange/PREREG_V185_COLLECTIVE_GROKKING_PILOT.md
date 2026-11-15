# V185 — Piloto de generalización tardía entre agentes separados

15/11/2026. Línea exploratoria solicitada explícitamente en el objetivo ampliado. Se conocen V182–V184; no hay entrenamientos V185 previos. Dos semillas de descubrimiento185115/185116. No son una confirmación ni un hallazgo2/3.

## A–C. Definición y rivales fuertes

Grokking colectivo no significará simplemente que una curva de recompensa aumenta tarde. Pregunta: ¿pueden dos agentes con parámetros, observaciones y actualizaciones separados memorizar interacciones conocidas y, mucho después, generalizar a combinaciones nuevas? Y, si sucede, ¿depende la transición del cambio conjunto de ambos agentes o basta el grokking del receptor con un diccionario fijo?

Antecedentes que impiden reclamar novedad genérica: Power etal2022, arXiv2201.02177, sobre generalización tardía; Nanda etal2023, Progress Measures for Grokking via Mechanistic Interpretability; Chaabouni etal2020, DOI10.18653/v1/2020.acl-main.407, sobre generalización en lenguajes emergentes; Lowe etal2019, AAMAS693–701, sobre inferencias engañosas de comunicación. La búsqueda inicial no acredita que falten trabajos más cercanos. No usar ausencia de resultados de una búsqueda como prueba de prioridad.

Tarea mínima: a,b uniformes en Z31, y=(a+b)mod31. Emisor observa solo a y emite un símbolo entre31; receptor observa símbolo y b, produce y. Cada uno recibe acierto binario. El receptor además recibe la etiqueta verdadera al finalizar la interacción para aprender por entropía cruzada. Son señales de aprendizaje asimétricas declaradas. Intereses cooperativos, canal, tarea y separación de funciones están impuestos; no es cooperación surgida de intereses contrapuestos ni institución inventada.

Emisor: tabla31x31 de logits, actualización REINFORCE desde su recompensa binaria, baseline móvil por a, sin acceso a b, y, parámetros o gradientes del receptor. Receptor: embeddings separados para símbolo y b,128unidades con activación cuadrática y salida31; AdamW. Ningún gradiente cruza agentes. EmisorAdam lr=.03,sin weight decay; receptorAdamW lr=.001,weight_decay=1,betas(.9,.98). Entropía del emisor .01 durante todo el piloto. No afinar hiperparámetros mirando test.

Rival FIXED_PROTOCOL: mismo receptor con permutación biyectiva aleatoria fijada como diccionario del emisor. Es una sola red que recibe toda la información mediante un código conocido: control de grokking individual, no segundo mecanismo colectivo. Un control monolítico de esta arquitectura es equivalente a relabelar su primer embedding; no gastar ejecuciones redundantes presentándolo como evidencia independiente.

## D–F. Diseño, criterios y falsadores

Partición única congelada con semilla185000:40%de pares NO ORDENADOS de valores para entrenamiento, incorporando ambos órdenes juntos. El resto es test; ningún par aparece invertido en entrenamiento si está en test. Exigir que todos los valores marginales a,b y todas las etiquetas se vean en train. Guardar la partición íntegra. Train y test son interacciones de la misma tarea sintética, no contextos sociales externos.

Dos condiciones por semilla: FIXED_PROTOCOL e INDEPENDENT_COMM.30000actualizaciones full batch, sin parada por test. Evaluar cada100actualizaciones en modo codicioso y conservar pérdidas continuas, entropía, precisión, mensajes distintos y pesos. t_mem: primera evaluación que completa cinco evaluaciones consecutivas con train>=.99; t_gen: análogo test>=.95. Candidato a generalización tardía si finaltest>=.95, t_gen>=5*t_mem y t_gen-t_mem>=2000. Un salto de una métrica umbral no basta para hablar de transición abrupta de mecanismos.

En INDEPENDENT_COMM, guardar el primer checkpoint t_mem con RNG y optimizadores. Si existe, ejecutar desde él dos continuaciones hasta el MISMO horizonte total: FROZEN_SENDER y FROZEN_RECEIVER. Conservar también la continuación conjunta original. Si cualquiera de las congelaciones generaliza de forma comparable, no atribuir la necesidad causal a reorganización conjunta. Criterio exploratorio más exigente: ambas congelaciones finaltest<.80 mientras la conjunta>=.95, en las dos semillas. Aun pasando, no basta para originalidad o confirmación independiente y hay que descartar una explicación como mera composición de funciones entrenables.

Información: para cualquier protocolo estocástico pi(m|a) y a uniforme, la precisión Bayes óptima del receptor en el conjunto completo es `sum_m max_a pi(m|a)/31`. Para un protocolo determinista es `numero_de_mensajes_usados/31`. Calcular este techo; un cuello de capacidad del canal no es por sí mismo grokking colectivo. Registrar cross-play final entre emisores y receptores de semillas distintas y perturbaciones del mensaje que preserven su distribución marginal. Interpretar el fracaso de cross-play como dependencia de una convención, no automáticamente como especialización o generalización.

## G–J. Auditoría y decisión

Antes de entrenar, verificar partición y aislamiento de gradientes en fixtures aleatorios, cero parámetros compartidos y que cada agente recibe solo sus variables autorizadas. Publicar protocolo, código y hashes antes de entrenamientos científicos. Los datos sintéticos se generan tras congelar el código. Guardar semillas, versiones, configuración CUDA, curvas y checkpoints, incluidos negativos.

Si FIXED_PROTOCOL no aprende/generaliza, el control positivo no funciona en esta instancia: no concluir imposibilidad colectiva. Si INDEPENDENT_COMM no memoriza, no decir que se ha observado un grokking frustrado. No ampliar automáticamente semillas para rescatar la etiqueta. Un resultado prometedor requiere al menos otra campaña separada, antecedentes más cercanos y un mecanismo con predicción discriminante antes de candidatar2/3. Mantener CT2 histórico61, nueva rama sin puntuación y N2=N3=0. Un proceso GPU, dos hilos CPU, BelowNormal y seisCPU; preservar usabilidad del equipo.
