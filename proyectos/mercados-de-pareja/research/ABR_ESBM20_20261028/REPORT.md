# Mercados de pareja · ESBM v2 · N67–N75 · Informe de campaña

**Fecha:** 28 de octubre de 2026. **Rama:** `research/ab-r-mercados-pareja-20261028`; no merge a `main`. **Investigador:** Alejandro Panera Pascual. **Autorización:** 20 ciclos BRANCHING AB-R nuevos, como presupuesto máximo, no cuota. **Trabajo efectivamente ejecutado:** 9 ciclos A–J N67–N75 (documentales N67 y N74, teórico N68, analíticos N69–N73, adversarial N75). **11 plazas no ejecutadas por R5**, ningún ciclo inválido registrado, no nuevas muestras humanas analizadas y ningún descubrimiento nuevo 1/3, 2/3 o 3/3. CT2 se mantiene en **7/100, valoración ordinal NO probabilidad**. DRIFT D1 respecto a modelo ESBM v1, expansión hacia compatibilidad y tiempo sin abandonar pregunta original.

## 1. Registro de evidencia y preregistro

[PREREG](PREREG.json) en commit `026cc12b5136e60034c71c2f794d01a453bdf5bd` y [SOURCE_FREEZE](SOURCE_FREEZE.json) en commit `7f196409bc1ba5b5af6d8caad39c173a38a99405`, ambos **anteriores a cualquier cálculo del nuevo simulador**. [Código fuente íntegro](esbm_dynamic.py), SHA256 `f7e6b84000720cbdf2ee0800c2b10d136185facd00e4622756cbb5f8d8254d0b`, 11.913 bytes. [60 recorridos sintéticos por semilla](RUNS.json.gz.b64) comprimidos en gzip/Base64, [resúmenes](SUMMARY.json), [diferencias pareadas](PAIRED_CONTRASTS.json), [QA](QA.json) y ZIP reproducible entregado en la conversación. Todas las corridas se **ejecutaron por segunda vez y los outputs fueron idénticos byte a byte**:
- `RUNS.json` SHA256 `ae6ea50be7bd36d1a4aa5b637f4048205742ea6ae228654ef759332a07bd4c67`.
- `SUMMARY.json` SHA256 `e0f04f702fec3ea58f029eb8b056949d039272c120aea38a1b3c8ca895b8c197`.

Esto verifica reproducibilidad **local**, no validación de tercero o clon limpio por equipo independiente. No se generaron participantes humanos ni se descargaron registros de parejas durante estas corridas.

## 2. Modelo ampliado: qué se ejecutó realmente

[Especificación teórica y límites](THEORY_V2.md). N=144 agentes ficticios, 16 períodos, 6 semillas (101, 211, 307, 401, 503, 601), 10 políticas. Etiquetas de género inventadas F=60, M=60, X=24; ámbitos de compatibilidad inventados all=72, same=36 y other=36. Una relación potencial exige que **ambas** personas acepten la categoría de la otra. No describe identidad u orientación humana ni porcentajes reales de LGBTQ+. El escenario de restricción F/M es un control de exclusión **para mostrar el efecto de definir un universo de riesgo más estrecho**, no política recomendada.

Cada individuo libre recibe hasta siete impresiones dirigidas por período; emitir un sí abre la posibilidad de que el receptor conteste sí. Solo las reciprocidades generan aristas de un matching no solapado de cardinalidad máxima con desempate fijo; los vínculos pueden disolverse por una función de riesgo estipulada, y las personas vuelven a estar disponibles. La dinámica incluye estados de selectividad privada y reputación hipotéticamente pública, con mecanismos **deliberadamente distintos**. Las condiciones mantienen población y shocks aleatorios comunes por seed, pero el número de disponibles y el total de impresiones **divergen como consecuencia del escenario**, por lo que no hay paridad en exposiciones acumuladas. Un emparejamiento sintético no equivale a pareja de la vida real, relación duradera ni bienestar.

### Medias de seis semillas sobre 144 agentes y 16 períodos

| Escenario artificial | Con pareja al terminar | Relaciones iniciadas acumuladas | Disoluciones acumuladas | Gini de impresiones recibidas | Parejas nuevas mismo grupo |
|---|---:|---:|---:|---:|---:|
| Aleatorio general | **86,1%** | 226,7 | 164,7 | 0,316 | 31,9% |
| Compatibilidad solo F/M | 72,0% | 194,2 | 142,3 | 0,388 | 36,2% |
| Exposiciones segregadas por norma | 86,8% | 218,7 | 156,2 | 0,332 | **65,9%** |
| Preferencia explícita misma norma | 96,5% | 241,2 | 171,7 | 0,316 | **68,3%** |
| Ranking hacia calidad alta | 85,4% | 223,5 | 162,0 | **0,414** | 35,6% |
| Balance histórico de visibilidad | 81,7% | **240,5** | 181,7 | **0,216** | 31,1% |
| Aprendizaje privado tras rechazo | **91,9%** | 247,0 | 180,8 | 0,311 | 32,1% |
| Penalización públicamente observada | **74,5%** | 209,0 | 155,3 | 0,325 | 30,4% |
| Relaciones de menor riesgo de ruptura | **90,0%** | 142,8 | 78,0 | 0,394 | 33,4% |
| Relaciones de mayor riesgo de ruptura | **77,5%** | **334,5** | 278,7 | 0,270 | 33,0% |

Cada relación cuenta una vez cuando se forma; pueden formarse varias en distintos períodos con la misma persona. `relaciones iniciadas - disoluciones = vínculos activos al final` en todas las 60 corridas. **Las magnitudes proceden de tasas inventadas**; estas medias NO son estimaciones de población española ni internacional. La media de duraciones completadas (solo vínculos disueltos) está censurada a derecha: excluir vínculos todavía activos sesga la estimación de duración media. Reportar stock y flujo separadamente.

## 3. N69 · Redes de compatibilidad y contraejemplo de exclusión

El grafo general contiene ~5.837 aristas compatibles no dirigidas de media entre las 144 personas, y nadie carece inicialmente de posibles parejas bajo la asignación artificial. Restringir a contactos F/M reduce las aristas posibles a 3.600, deja **24 agentes X con grado 0 por construcción** y reduce la ocupación final de 86,1% a 72,0%. El efecto agregado pareado fue −14,12 puntos porcentuales con signo negativo en **6/6** semillas. No se demuestra ninguna desventaja observada real para identidades particulares: es consecuencia algebraica de la restricción de diseño. Para diversidad real se necesitan muestras y consentimiento, no parámetros demográficos inventados.

## 4. N70 · Instituciones que segmentan frente a homofilia explícita

El modelo aleatorio expone a grupos iguales ~33,2% de las veces y termina con 31,9% de vínculos nuevos entre miembros del mismo grupo. Segregación institucional, **sin término de preferencia por grupo**, incrementa exposición entre semejantes a ~63,5% y pareja de mismo grupo a ~65,9%. La preferencia explícita favorece el mismo grupo **sin cambiar deliberadamente la exposición aleatoria**, y da ~68,3% de parejas de ese grupo. Este es otro caso de **equivalencia parcial del resultado final sin equivalencia causal del mecanismo**. Diferencias de cobertura, costes y redes permiten distinguirlos. La proximidad cultural por grupo se impuso, no se midió.

## 5. N71 · Intermediarios y objetivos incompatibles

En las mismas semillas, elegir destinatarios de Q alto aumenta el Gini de impresiones de 0,316 a 0,414, **+0,098** pareados, signo positivo en 6/6 semillas, mientras la presencia final de pareja cambia poco de 86,1% a 85,4% (3 semillas suben, 3 bajan). Balancear la visibilidad por histórico disminuye Gini a 0,216, **−0,100** en 6/6 semillas; el número de relaciones iniciadas sube de 226,7 a 240,5, pero personas en pareja al final baja de 86,1% a 81,7% (**−4,4 puntos**, 6/6). **No decir que optimizar visibilidad siempre reduce éxito humano**: el algoritmo de balance es una regla local artificial, los flujos cambian el conjunto de disponibles y no se garantizó la misma exposición total. El experimento real de Chen et al. 2023 ofrece un comparador fuerte de política bilateral, NO replicado aquí.

## 6. N72 · Rechazo privado no es reputación pública

El módulo de **aprendizaje privado** incrementa la disposición a enviar sí después de recibir rechazo, hasta un tope prefijado; aumento medio final de sesgo privado ≈+0,602 (escala logit), y presencia de pareja 91,9% (+5,8 pp frente a base, 6/6 semillas). El módulo de **señal pública** presupone explícitamente que *terceros pueden ver* la historia de rechazo y penalizan futuras valoraciones del candidato; penalización logit media ≈−0,823, y presencia de pareja 74,5% (−11,6 pp, 6/6). El código **crea por definición** este efecto social externo: no demuestra que Tinder o sociedades reales difundan rechazos privados, ni que el estatus intrínseco disminuya. Las dos intervenciones cambian variables y mecanismos diferentes; no comparar sus efectos como si fueran estimaciones del mismo tratamiento.

## 7. N73 · Duración, rotación y stock

Reducir riesgo de disolución sintético a 0,40× genera 142,8 formaciones, 78 disoluciones y 90% en pareja al final. Aumentarlo a 1,75× genera 334,5 formaciones, 278,7 disoluciones y 77,5% al final. Por tanto **más relaciones iniciadas no implica más personas emparejadas en un corte temporal**, ni mayor bienestar o duración. La muestra de vínculos todavía activos está censurada y no debe usarse para proclamar esperanza de duración real.

## 8. N67 y N74 · Evidencia externa y R5

[Auditoría documentada](EXTERNAL_VALIDATION_AUDIT.md): Fong 2024 estudia aleatoriamente información de mercado y selectividad; Hu y Markowitz 2026 ofrecen dos experimentos preregistrados de cantidad de perfiles y compatibilidad; Büyükeren, Makarin y Xiong 2026 asocian expansión de Tinder en campus con más actividad sexual pero cambios pequeños en relaciones duraderas, diferenciando flujos de bienestar y calidad; Jung y Lusher 2026 estudian matrimonio y disolución; Lee y Niederle 2025 prueban señales escasas de preferencia. Se añadieron **6 registros SRC042–SRC047**, **8 actualizaciones U037–U044**, y **3 nuevos priors**, ahora [47 fuentes](../PRIORS/SOURCES.json), [24 priors](../PRIORS/PRIORS.json), [44 actualizaciones](../PRIORS/UPDATES.json). Cada fuente declara lo que aporta y lo que no prueba. **No hubo una nueva muestra humana de impresiones, decisiones bilaterales y tiempos descargada**; el paquete de réplica de AEA `E218862V1` fue localizado pero no abierto, y el ZIP de AEA no se pudo descargar. No inventar una réplica en datos reales.

## 9. N75 · Dictamen metodológico

Esta versión **aumenta la expresividad del simulador**, no la validez externa. Principales límites:
1. Población, compatible scopes, parámetros de utilidad, penalizaciones y hazards son completamente inventados.
2. El procedimiento de matching puede cambiar resultados aunque preferencias sean iguales; no se comparó con Gale–Shapley bajo información igualada ni con satisfacción de parejas.
3. Realimentación pública de rechazo presupone información disponible a terceros; en datos humanos no está demostrada y puede ser ética o legalmente sensible.
4. El modelo no estima resultados para minorías sexuales, estructuras familiares diversas, contexto español, atención real, redes geográficas, normas vividas, bienestar, consentimiento continuado o violencia.
5. Las oportunidades acumuladas cambian endógenamente con las parejas activas; no hay igualdad universal de presupuesto total entre condiciones.
6. Seis semillas cuantifican una mínima sensibilidad interna, no incertidumbre de población real.
7. Estudios externos no sirven para «calibrar» nuestros parámetros sin microdatos, definiciones y estimandos comunes.
8. Hay **fuerte prior art** para oportunidades, reciprocidad, información de mercado y algoritmos; no hay nuevo aporte científicamente original de nivel 2/3.

**AB-DECIDE: STOP_R5** tras N67–N75, **9 ciclos A–J válidos**, ninguno inválido, **11 plazas autorizadas no iniciadas**, **CT2 7/100 sin cambios** (ordinal, no probabilidad), nuevos 1/3=0, 2/3=0, 3/3=0. La nueva puerta para continuar exige observaciones temporales humanas o experimento ético que permita contrastar exposición, respuesta bilateral y continuidad de relaciones, o una predicción prerregistrada diferente y falsable frente a las investigaciones publicadas. Mantener saldo, no solicitar autorización nueva ni ajustar el código simplemente para obtener cifras más favorables.
