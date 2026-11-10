# V12 — Agrupación con números variables de profesiones y grupos

**Fecha: 11/11/2026. Estado: batería exploratoria ejecutada.** Todas las métricas proceden de scripts, configuraciones y checkpoints versionados en el directorio. No constituye una prueba confirmatoria; las condiciones nuevas se consultaron durante el desarrollo del programa. No se ha demostrado cooperación comunicativa.

## 1. Problema

Hay N habitantes que pueden escoger libremente entre M profesiones equivalentes. El óptimo económico es ocupar exactamente k profesiones cualesquiera, con N/k habitantes por profesión. El alimento individual de quien trabaja en una profesión j con n_j trabajadores es:

    r_i = min(n_j/(N/k), (N/k)/n_j).

Los individuos NO conocen M como parámetro explícito, k, la cuota, D_k ni el reparto ocupacional completo; sí pueden observar las profesiones candidatas, la suya y las presentes en sus vecinos. La puntuación de cada profesión utiliza la misma función neuronal DENTRO de cada agente, con **pesos diferentes entre personas**. El programa admite de 2 a 80 profesiones y k entre 2 y M, siempre con N divisible por k.

## 2. Anatomía del agente y señales

La arquitectura V12 contiene **128 parámetros entrenables por persona**, 80 para escoger profesión y 48 para comunicar una intención. Sin el canal de anuncios, los 48 parámetros de señalización no se utilizan para actuar ni se actualizan. Cada persona dispone de observaciones de su profesión, distribución de profesiones entre cinco vecinos, memoria temporal de esa distribución, alimento individual y su cambio.

En las condiciones C1, los actores anuncian voluntariamente una profesión a sus vecinos antes de decidir simultáneamente su trabajo. Es una petición/intención, no una orden, y el significado básico de la etiqueta está definido por el experimento; no es un lenguaje emergente de significado libre.

Con el tratamiento público se añaden el alimento medio real de la aldea y su variación temporal. Con alpha=0.1 el retorno de aprendizaje es 90 % alimento individual y 10 % alimento medio global realizado. Se deben separar epistemológicamente: los modelos C0-public de la batería usan AMBOS tratamientos a la vez y no permiten distinguir sus efectos causales por separado. Los otros modelos C0 y C1 de N60 reciben recompensa 100 % individual.

El entrenador utiliza REINFORCE con ventajas normalizadas respecto a otros mundos del mismo individuo, no crítico centralizado ni recompensa marginal contrafáctica. El indicador D_k solo se calcula para auditoría.

## 3. Batería efectuada

Los entrenamientos mezclaron cuatro tareas con M en {10,20} y k en {2,4}, alternando una por actualización. Ningún otro k ni M apareció en una actualización de parámetros. Los mundos de desarrollo incluyeron M30/k3 y M30/k5, por lo que su evaluación posterior NO constituye un holdout sellado.

Se completaron seis entrenamientos cortos de 180 actualizaciones, tres sobre N60 y tres sobre N120, comparando ausencia de mensajes, mensajes de intención y mensajes con bienestar público/alpha .1. Todos los brazos cortos quedaron cerca del azar.

Entrenamientos prolongados: N60 C0 sin anuncios, recompensa individual hasta 500 actualizaciones y continuación hasta 1000; N60 C1 con anuncios y recompensa individual hasta 500. N120 C0 con bienestar público y recompensa 90/10 hasta 600 y continuación hasta 1100; N120 C1 con ambas facilidades hasta 600. Un control sin visión vecinal se entrenó desde cero con los mismos 1000 pasos de N60, y otro con 1100 pasos de N120. Son doce inicializaciones de entrenamiento entre ambos tamaños, más dos continuaciones de checkpoints existentes, NO doce semillas de replicación por condición.

Todos los archivos de evaluación y checkpoints originales están en los subdirectorios runs. Los pesos de GPU del sobremesa y los de CPU del portátil se fusionaron explícitamente a una rama GitHub común, conservando los estados de optimizador.

## 4. Cambios observados durante el entrenamiento

La N60 C0 individual pasó, en desarrollo, de ~0,23 raciones en M10/k2 a 0,706 en la actualización 400 y 0,591 en la 1000. Para la prueba M30/k5 pasó de ~0,25 a ~0,694; k5 y M30 no se usaron durante actualizaciones. En k2 hubo repartos exactos aislados, pero las curvas son inestables.

La N120 C0-public y alpha .1 pasó de ~0,21 en M10/k2 a 0,602 en la actualización 600 y 0,598 en la 1100. En M30/k5 alcanzó 0,715. La variante comunicativa C1 no demostró mejora superior de manera consistente.

## 5. Transferencia comprobada con políticas congeladas

Estrés de 70 turnos, dos nuevas semillas, 64 sociedades por semilla: **128 mundos por condición**. Las políticas se congelaron, y se compararon contra agentes aleatorios e imitación local. El alimento máximo teórico es 1.

| Población y condición | M | k | Alimento de red | Alimento azar | Alimento imitación |
|---|---:|---:|---:|---:|---:|
| N60, individual, C0 | 30 | 3 | 0,6710 | 0,1498 | 0,5786 |
| N60, individual, C0 | 30 | 5 | 0,6946 | 0,2497 | 0,4150 |
| N60, individual, C0 | 50 | 6 | 0,6821 | 0,2176 | 0,3630 |
| N60, individual, C0 | 50 | 10 | 0,6264 | 0,3627 | 0,2394 |
| N60, individual, C0 | 80 | 12 | 0,5989 | 0,3465 | 0,2065 |
| N60, individual, C0 | 80 | 15 | 0,5262 | 0,4290 | 0,1688 |
| N120, público + alpha .1, C0 | 30 | 3 | 0,6830 | 0,1241 | 0,6687 |
| N120, público + alpha .1, C0 | 30 | 5 | 0,7115 | 0,2068 | 0,6237 |
| N120, público + alpha .1, C0 | 50 | 6 | 0,7238 | 0,1693 | 0,5789 |
| N120, público + alpha .1, C0 | 50 | 10 | 0,6827 | 0,2821 | 0,4209 |
| N120, público + alpha .1, C0 | 80 | 8 | 0,6981 | 0,1652 | 0,4914 |
| N120, público + alpha .1, C0 | 80 | 12 | 0,6709 | 0,2478 | 0,3715 |
| N120, público + alpha .1, C0 | 80 | 15 | 0,6491 | 0,3097 | 0,3113 |

Ninguno de estos objetivos NUEVOS de k3/5/6/8/10/12/15 consiguió un reparto exacto en el ensayo de 128 sociedades por condición, aunque mejoraron marcadamente sus recompensas. En M30/k2, con M inédito pero k entrenado, hubo 4/128 exactos con N60 y 2/128 con N120. No interpretar estos resultados como una solución universal.

**Cautela:** algunas reglas simples de imitación también logran rendimientos elevados y en ocasiones comparables. Lo que generaliza es la capacidad parcial de regulación de poblaciones, sin que deba atribuirse todavía a especialización funcional entre roles.

## 6. Equilibrios exactos y persistencia temporal

El script stability_v12.py congeló pesos y ejecutó 128 sociedades por condición durante 100 turnos; buscó D_k=0 y también cinco turnos consecutivos exactos.

| Condición | Escenario | Exactos alguna vez | Exactos 5 turnos seguidos |
|---|---|---:|---:|
| N60, C0 individual | M10/k2 conocido | 17/128 | 9/128 |
| N120, C0 público y alpha .1 | M10/k2 conocido | 15/128 | 3/128 |
| N60 y N120 | M30/k5 nuevo | 0/128 cada uno | 0/128 cada uno |
| N60 y N120 | M20/k4 iniciado en trampa | 0/128 cada uno | 0/128 cada uno |

Por tanto, existe un pequeño subconjunto de sociedades con equilibrio exacto y estable durante al menos cinco turnos, pero no una estrategia de generalización exacta a k desconocidos. El criterio es temporalmente limitado; no prueba estabilidad indefinida ni resiliencia a perturbaciones graves.

## 7. Observaciones sociales y anuncios

Al entrenar desde cero el control blind que no ve las profesiones vecinas, N60 obtuvo ~0,232 de alimento de desarrollo en M10/k2, frente a ~0,591 con vecinos. En N120, con bienestar público y alpha .1, el control sin vecinos obtuvo ~0,213 frente a ~0,598. En otras sociedades nuevas, las políticas estocásticas de los controles blind dieron ~0,231 y ~0,215, respectivamente.

Esto respalda, bajo esta arquitectura y protocolo, una ventaja de disponer de observaciones sociales. No significa que ninguna estrategia individual pueda resolver el reparto: hay controles deterministas blind cuyo resultado supera al estocástico, y una estrategia de imitación simple puede alcanzar distribuciones productivas.

En las políticas C1 con mensajes de intención, bloquear o permutar los anuncios en evaluación produjo resultados mixtos, sin ventaja causal sistemática. La manipulación no conserva estrictamente cada fuente de ruido de muestreo. Se requiere una ablación emparejada más rigurosa antes de afirmar negociación aprendida.

## 8. Trampas de coordinación y límites

La evaluación con estados iniciales de monocultura para k2 o dos grupos sobrepoblados para k4 muestra que los agentes entrenados desde estados aleatorios no aprenden todavía a formar coaliciones para escapar de estas situaciones. En k4, los modelos C0 estabilizaron alimento medio ~0,5 y no alcanzaron equilibrio exacto.

El trabajo demuestra aprendizaje parcial de reglas distributivas con información local y transferencia entre distintos M/k, no división funcional del trabajo entre profesiones materialmente complementarias. Las profesiones siguen siendo alternativas simétricas con producción dependiente del tamaño del grupo.

No se ha demostrado grokking clásico, cooperación comunicativa irreducible, solución para k arbitrarios o un procedimiento que garantice convergencia. Las políticas C0 no necesitan mensajes y parte del resultado puede describirse como autoorganización a través de interacciones e imitación.

## 9. Archivos y reproducibilidad

- v12.py, test_v12.py: motor y diez pruebas de integridad, todas superadas en los dos PCs.
- evaluate_v12.py: evaluación de pesos congelados en metas nuevas, controles y bloqueos de mensajes.
- stress_v12.py: pruebas M30, M50, M80 y k2/3/5/6/8/10/12/15.
- stability_v12.py: auditoría de estabilidad durante 100 turnos.
- make_panel.py y PANEL_ALDEA_VARIABLE.html: panel HTML autocontenido, con curvas, ocupaciones y fotogramas de ejecuciones reales.
- runs/: 14 directorios de ejecuciones, con todos los checkpoints, configuraciones, estados e historiales.
- Resultados numéricos de transferencia, estabilidad y estrés en JSON con las semillas y protocolos.

Repositorio privado: GalexY3/Metodologia-AB, rama research/aldea-v12-variable-mk-20261111.

**Conclusión:** el número de profesiones no tiene que estar codificado en el cerebro, y se ha observado transferencia parcial a nuevos k incluso desde entrenamiento con solamente k2 y k4. Falta descubrir cómo emergen acuerdos y migraciones coordinadas que hagan exactos y robustos esos repartos.
