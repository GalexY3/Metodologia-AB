# G1 — traspaso intergeneracional de una política verdaderamente entrenada

**Protocolo exploratorio registrado después de P1 y G0, antes de ejecutar G1.** A diferencia de G0, que transmitía una heurística de rareza programada, G1 utiliza θ_i efectivamente aprendido por REINFORCE en la cohorte P1 (seed20261110), entrenada solo con k2..4, con rasgo de escasez escalado por k. El rasgo y recompensa local siguen diseñados por nosotros; no hay emergencia no guiada ni prueba de grokking.

## Población, condiciones previas y red

N=120, anillo no dirigido grado4; como máximo un intercambio bilateral por agente/tick, comunicando su estado funcional. k=4 (conocido) y k=5 (inédito respecto al entrenamiento), 12 comunidades iniciales por k con semillas base **30000+100k+s**, s=0..11, completamente nuevas respecto a P0/P1/G0. Inicializar θ_i a los pesos P1 congelados del archivo results_p1/P1_k_scaled_theta.npz; cada comunidad debe alcanzar estabilidad TV≤0,06 y churn≤0,05 en el final de 140 ticks SIN actualizar θ. Las comunidades que no lleguen a estabilidad se registran como no elegibles. **No buscar ni añadir semillas que den resultados favorables**.

## Choque emparejado

Para cada comunidad estable se reemplazan **25%,50% y75%** de individuos. Selección de nodos y nuevos colores quedan fijados por una semilla determinista (dependiente del id base y r, no del tratamiento), con 70% de los nuevos colores en0 y el resto uniformemente en otras funciones. Memorias de los nuevos individuos se reinician a prior uniforme; todos los demás conservan funciones, memoria, red y pesos aprendidos. Las cuatro condiciones comienzan desde el MISMO vector de colores, grafo, nodos reemplazados y memorias. Se evalúan **150 ticks** posteriores con congelación/aprendizaje según condición.

## Cuatro tratamientos de conocimiento
1. **Herencia exacta**: el nuevo miembro recibe el θ entrenado del predecesor que ocupaba su nodo, sin entrenarlo más durante recuperación.
2. **Novato congelado**: el recién llegado obtiene θ inicial sin entrenamiento (idéntico vector y jitter controlado entre los tratamientos de novatos), sin permiso de actualizarlo.
3. **Aprendizaje local**: el novato comienza con el MISMO θ inicial que el control congelado y puede modificarlo por REINFORCE exclusivamente con recompensa local tras contactos, mientras los veteranos permanecen congelados.
4. **Enseñanza vecinal**: el novato comienza con el MISMO θ inicial, no recibe gradientes de aprendizaje; si conversa con un portador de θ entrenado (veterano o previamente enseñado), con probabilidad fija **p=0,25** copia exactamente su vector θ; esa copia solo cambia su política desde el tick siguiente. Cada conversación sigue siendo entre un único par/tick y no se comparte el resultado global de la comunidad.

El tratamiento de aprendizaje local implica entrenamiento online de novatos después del choque y debe distinguirse de la prueba zero-shot P1. La herencia exacta constituye una condición idealizada de altísima fidelidad. La enseñanza por copia θ también es un mecanismo cultural postulado.

## Variables y análisis

Equilibrio final estable (TV≤.06 y churn≤.05 durante últimos10), tiempo hasta 10 ticks estables (censura a150), TV inmediatamente después del relevo, AUC del desequilibrio TV en 150 ticks (menor mejor), riqueza local de funciones, fracción de θ entrenados por copia/herencia, número de transmisiones. Comparar primero por cohorte inicial/r, después agregando sobre las 12 comunidades iniciales; no tratar cuatro condiciones, 150 ticks o pares como unidades independientes.

**Hipótesis**: herencia preserva capacidad de recuperación mejor que novatos congelados; enseñanza por contacto y aprendizaje local pueden compensar, con eficacia dependiente de r y k. El signo y magnitud comparada entre ambos mecanismos de transmisión es desconocido y no se forzará. Puede ocurrir que una política aprendida transfiera peor que la regla manual G0, y eso también es resultado importante.

## Auditoría

Bloquear los parámetros y semillas antes de ejecutar. Verificar mediante hashes idénticos los colores posshock y los nodos sustituidos de cada cuarteto; para los tres grupos de novatos, vector θ inicial idéntico en cada nodo nuevo. Máximo una conversación por agente/tick, transmisión θ solo por aristas en el siguiente paso, ausencia de censo global en elecciones, estabilidad y recuperación bajo mismos criterios de P1, datos íntegros de casos excluidos.

**Límites:** una sola cohorte de políticas θ_i entrenada en P1; G1 permite comparación causal *dentro de ese simulador* del modo de transferencia, no identificar efectos sociales reales ni grokking. P2 intenta replicar P1 entre seis entrenamientos independientes en una rama separada y no debe contaminar la interpretación de G1 hasta traer sus datos verificados.
