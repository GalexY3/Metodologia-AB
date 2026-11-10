# Auditoría de simulador externo HTML: MARL 10→4 y curva de mejora

**Fecha 2026-11-10. Fuente suministrada por el usuario:** `simulador_marl_puro_ret_culo_3_4_3_4_y_aprendizaje_real_1m_pocas.html` (1659 líneas) y captura con curva (D_4) que desciende desde ≈0,41 hasta ≈0,17–0,19 hacia cientos de miles de episodios. Los valores de la captura SON observaciones visuales aproximadas, **no ejecución reproducida ni validación independiente**. Esta revisión NO reemplaza el experimento V5, ya evaluado por separado.

## Resultado prometedor, con alcance limitado

El archivo implementa una fórmula CORRECTA para la distancia al mejor subconjunto de cuatro estados entre diez, con 36 agentes: `D4 = 1 − [Σ_{j=1}^4 min(n_(j),9)]/36` (líneas ~589–620). Si una EMA de D4 está cerca de 0,18, representa una reducción aproximada del 56% frente a la referencia IID10 ≈0,411. Estar por debajo de 0,25 significa que no bastan solo tres colores ocupados (como máximo 3×9 de los 36 agentes podrían satisfacer cuotas), pero NO implica exactamente cuatro colores vivos ni estabilidad. La gráfica representa D al final de episodios de ENTRENAMIENTO suavizados por EMA, no evaluación sellada.

## Problemas verificados por inspección de código y ejecución directa de la función original de retículo

1. **Topología etiquetada como grado 5 es otra topología.** La función `buildSnubSquareLattice` (~426–512) construye cuatro enlaces ortogonales y una diagonal SALIENTE de cada nodo de paridad par hacia el siguiente nodo par. Cada par recibe además una diagonal ENTRANTE, y los impares no reciben ninguna. Se ejecutó la función JavaScript original en Node.js v22 (6×6): frontera toroidal = **18 nodos grado 4 y 18 grado 6**, 90 aristas; frontera abierta = **2 grado 2, 10 grado 3, 16 grado 4, 8 grado 6**, 73 aristas. No es el retículo uniforme de grado cinco declarado. La captura tiene frontera abierta, pero los cambios de modo no reinician pesos ni curva.

2. **La recompensa rotulada «Global Pura» no es uniforme.** En `Sim.creditMode==='global'` (~853–858), cada actor recibe `globalDeltaR−0.015·1[color_i cambia]`. Ese último término depende de la decisión INDIVIDUAL, por lo que no corresponde a la especificación del usuario «feedback del total, no del aporte personal». El coste es pequeño frente a NΔD, pero conceptualmente rompe la igualdad de recompensa.

3. **La observabilidad permitida se viola para mensajes ausentes.** En el bloque de comunicación (~759–790), el receptor incorpora `rolloutBeliefs[sender,c]*0.45` incluso cuando `rolloutSenderTo[sender] !== i`. `rolloutBeliefs` es estado interno del vecino, NO el color actual observado y NO fue enviado como mensaje. Por tanto, la difusión usa información que debía permanecer privada.

4. **No se aprende la estrategia de mensajería.** Cada emisor elige aleatoriamente un vecino `nbrs[Math.random()*nbrs.length]`; no hay política entrenada de destinatario ni de contenido de petición. Las creencias se mezclan automáticamente con coeficientes fijos `1.5,0.45,0.35,0.65`, repetido 1/3/5 veces por turno. Puede haber aprendizaje real de elección de color, pero parte de la coordinación provendría de un mecanismo de consenso programado (gossip/difusión), no de negociación aprendida por los agentes.

5. **Las selecciones de la interfaz no fijan la identidad del experimento.** El archivo arranca `creditMode='counterfactual'`, `gossipSteps=3`, `boundaryMode='torus'` (~627–633); la captura indica global, un mensaje y abierta. Sus manejadores de eventos (~1577–1595) no reinician la historia de entrenamiento al cambiar `creditMode`, `gossipSteps` ni `boundaryMode`. Así, un solo gráfico puede mezclar modalidades de crédito, redes y velocidades de difusión. No es posible reconstruir qué configuración generó las primeras épocas solo a partir del HTML y una captura.

6. **Entrenamiento y tablero visual representan procesos diferentes.** `trainOneRealEpisode()` corre 20 turnos, usa softmax con temperatura decreciente y muestreo; `stepVisualEpisodeOneTurn()` utiliza argmax con ruido añadido y el reproductor avanza 24 turnos (~1040–1077). El gráfico histórico sí proviene de entrenamiento (EMA), pero la configuración visual puede transmitir una estabilidad que no se está midiendo en rollouts entrenados.

7. **La política utiliza un gradiente aproximado mal rotulado como exacto.** Se muestrea con logits `rawLogit/temp` (~814–835) pero `mlpBackwardStep` no incluye el factor de cadena `1/temp` para derivar respecto de pesos (~559–583). Al ser temperatura común, altera principalmente la escala del estimador por episodio, pero no es el gradiente exacto anunciado. El valor de descuento realmente fijado es `gamma=0.80` (~889), pese a otro comentario. La línea base móvil se actualiza con retornos del propio episodio mientras se itera hacia atrás, de modo que algunas líneas base posteriores están correlacionadas con acciones anteriores; ello compromete la interpretación de estimación de gradiente sin sesgo.

8. **No hay test independiente ni artefactos de reproducción de la captura.** El código usa `Math.random` sin seed persistida, no exporta pesos ni datos de curva, y no existe partición de evaluación independiente. El enfriamiento de temperatura `max(0.35, 0.85 − (epoch/250000)*0.45)` también puede producir reducciones en la distancia sin cambios de pesos; se requiere control de políticas iniciales congeladas bajo idéntico calendario.

## Pruebas recomendadas sin cambiar el objetivo social

- Experimento controlado del modo GLOBAL estricto: `r_i(t)=N[D_t−D_{t+1}]` IDÉNTICO para todos, sin incentivos por acción individual; no cambiar el reward a mitad de curva.
- Definir un verdadero grafo grado cinco, o aceptar/documentar el grafo grado 4/6 usado. Inicializar todas las condiciones con semillas y topologías explícitas iguales; sin cambios en marcha.
- Restringir la difusión a información efectivamente enviada; sustituir los coeficientes de gossip preprogramados por mensajes locales elegidos por las políticas, o declararlos explícitamente como condición de «canal de información preprogramado», distinta de comunicación aprendida.
- Congelar pesos al final de 50k/200k/400k episodios con export y SHA256. Comparar modelos sin entrenar, entrenados, congelados con temperatura decreciente, sin mensajes, con mensajes, y con mensajería aleatoria. Reportar D, EXACTOS, estados vivos, churn y estabilidad sostenida en nuevas semillas/condiciones iniciales, con 100–1000 sociedades por escenario (réplicas de mundo, no de entrenamiento).
- Replicar 5–10 inicializaciones de pesos θ con presupuestos similares antes de concluir ventaja del aprendizaje global. Medir la evolución por episodio y la evaluación reservada por separado.

## Relación con nuestra V5

V5 mide aprendizaje descentralizado de color Y decisión de destinatario/petición, con parámetros independientes, recompensa global idéntica y acceso estricto a mensajes; el HTML mide elección de colores bajo una difusión con coeficientes fijos y acceso a creencias de vecinos sin mensaje. Las curvas de ambos NO son directamente comparables. La evaluación reservada V5 con W1/W8 y H64/H128 tras 150 actualizaciones dio 0 soluciones exactas y 0 sociedades estables por condición entre 100 tests de k2/3/4. Ese fracaso NO contradice una mejora de D en el HTML; son problemas/algoritmos/presupuestos diferentes.

**Juicio:** la caída visual es una pista experimental prometedora, NO una prueba verificable de cooperación local aprendida bajo las restricciones acordadas. Priorizar aislar el mecanismo de la mejora sobre replicar la curva sin auditoría.
