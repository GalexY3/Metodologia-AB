# V3B — contraste prospectivo C1/C2 con recompensa exclusivamente colectiva

**Registrado: 10/11/2026, antes del entrenamiento completo de C1/C2.** Se habían ejecutado solamente tests de 10 invariantes y *smoke tests* de dos actualizaciones con seed341. Esas pruebas no son resultados científicos. El objetivo es saber si la comunicación dirigida aporta ventaja a agentes que disponen de capacidad autónoma de cambiar de color.

## Fijación del experimento

- **Tres inicializaciones independientes** de redes neuronales, semillas de entrenamiento **311, 312, 313**. Dos brazos por semilla, con los MISMOS pesos iniciales por agente, 36 agentes en rejilla 6×6 (cinco vecinos interiores), red no periódica. Se entrenará C1 (sin peticiones, con cambio voluntario) y C2 (con peticiones + cambio voluntario), seis políticas poblacionales en total.
- En ambos casos cada individuo posee matrices y estados de optimizador Adam propios (organizados en tensores disjuntos). Sin entrenamiento de un crítico mundial ni reparto de recompensa entre agentes. **Recompensa colectiva única** `r=N[D(t)-D(t+1)]`, con D distancia de variación total respecto a cuotas N/k. Feedback público del turno anterior idéntico para todos; cada política solo observa color propio, vecinos, mensajes efectivamente recibidos y k.
- Los colores iniciales se distribuyen aproximadamente 70% mayoritario, nombre mayoritario aleatorizado por mundo. Color-equivariancia neuronal comprobada por invariantes, aunque no se presupone ausencia de roles fijos ligados a posición/identidad.
- **Presupuesto fijado:** 120 actualizaciones por brazo y semilla; minibatch de 12 mundos paralelos (cuatro con cada k2,3,4), 24 turnos por mundo y actualización, 1440 episodios de aprendizaje por brazo/semilla, 8640 episodios totales. `hidden=24`, `lr=.002`, `gamma=.99`, `entropy_beta=.003`, `adv_scale=10`, clipping L2 por agente=10. No se seleccionará retrospectivamente el mejor checkpoint. Todos se evaluarán en el peso final de actualización120.
- REINFORCE: cada agente recibe el MISMO retorno descontado de equipo por mundo; baseline **leave-one-out de los demás mundos del mismo k**, idéntico para todos los agentes de ese mundo. Los parámetros i se actualizan solo con acciones logπ_i, sin mérito marginal individual ni gradientes de otros agentes.
- Se registran curvas de entrenamiento de TV y churn, logs de pérdidas, norma de gradiente, resultados de desarrollo cada 20 actualizaciones, pesos finales y configuración. El desarrollo **no determina** selección de checkpoints.

## Evaluación reservada

Una vez guardados los seis pesos finales, registrar un lock SHA256 de todo código y pesos **antes de abrir los resultados de evaluación**. Evaluar k2,3,4 sobre **100 sociedades nuevas por semilla y k**, horizon **120 turnos**. Seeds del generador de mundos `990000+10000*train_seed+100*k`, iguales para los dos brazos y el C3 de cada cohorte. Políticas estocásticas como durante entrenamiento, sin gradientes. No escoger la semilla de entrenamiento que mejor funcione: presentar las tres por separado y agregado descriptivo.

- C1 sin mensajes.
- C2 con mensajes.
- C3 pesos de C2 con mensajes bloqueados durante **ejecución** (capacidad de cambio autónomo intacta); es dependencia de C2 en ese canal, pero con cambio de distribución de entrada.
- Controles sin aprendizaje, sin trucos de acceso al censo mundial: R1 colores elegidos uniformemente al azar cada ronda, con petición dirigida aleatoria permitida; R2 mismos movimientos aleatorios T=24 y después mantener el color indefinidamente; R3 quedarse inmóvil. En los tres los cambios voluntarios siguen siendo físicamente posibles. Los resultados R1/R2 se calculan sobre las mismas inicializaciones que C1/C2; el aleatorio con reloj T24 es un control programado, no aprendizaje.

**Métricas primarias continuas:** media de D(t) al último turno, D media últimos10, D/E[D_IID(N,k)] exacta en la distribución binomial y área del desequilibrio en 120 turnos. **Métrica de resultado operacional secundaria:** D≤0,06 y churn≤0,05 durante los últimos diez turnos. Además D=0 exactamente, máximo acercamiento temporal, comunicaciones emitidas, coincidencia entre peticiones y decisión propia, variabilidad entre tres aprendizajes. Diferencias entre C2-C1 comparadas por semilla de entrenamiento y k: n independiente=3 para inferencia sobre optimización de políticas, NO 300 mundos independientes. No usar 'hiperuniformidad' para el cociente D/IID.

## Interpretación y fallos admisibles

Un C2 mejor que C1 y peor con C3 es **evidencia interna al simulador** de utilidad funcional de mensajes bajo esa configuración, no prueba general de consenso o instituciones sociales. Las peticiones no garantizan por sí mismas cooperación: si C1 es igual o mejor, la información directa del vecindario y el cambio propio pueden bastar. El refuerzo por mejora de equipo no asegura estabilidad ni convergencia. Registrar resultados negativos sin ajustar post hoc. No reutilizar k5 ni afirmar extrapolación a nuevos k; la arquitectura de esta primera versión admite k≤4.

## Validez y auditoría

Comprobar antes de ejecutar invariantes de parámetros por agente, equivariancia exacta bajo permutación de colores, acción de cambio voluntario sin mensajes y recepción de múltiples solicitudes. Los seis brazos compartirán parámetros iniciales apareados por seed y distinta intervención comunicativa; no hay recompensa individual. Un objeto Adam con parámetros apilados mantiene momentos por elemento y un recorte de gradiente por cada fila, sin cross-agent clipping. La ablation de quitar mensajes no prueba por sí sola que no exista otra política sin comunicación capaz de llegar al objetivo. Diferencia de N/k divisible (36/2, /3, /4) significa D_min=0, pero la esperanza de IID no es límite físico de alcanzabilidad.
