# En cola — coordinación funcional distribuida y transmisión intergeneracional

**Orden de ejecución acordado:** DESPUÉS del estudio de grokking, destrucción y recuperación de neuronas (V13 y sus controles). Este documento preserva el diseño, las decisiones del usuario y los problemas metodológicos detectados. **No se ha ejecutado ni validado esta simulación.**

**Origen de la idea:** texto adjunto a la conversación de ChatGPT de 9/11/2026, titulado `Texto pegado(4).txt`, que incorpora una propuesta del usuario y respuestas anteriores. El texto menciona `Proyecto_Simulacion_Intergeneracional_Version_Conceptual_Rigurosa.pdf`, `.docx` y `Traspaso intergeneracional simulación (1).docx`, pero sus contenidos binarios **no están entre los archivos verificados de esta copia**. No presumir que se han leído o reproducido esos documentos. Si se facilitan en otro chat, prevalece su contenido sobre cualquier interpretación nuestra.

## Núcleo de la propuesta del usuario

Una población de N agentes debe coordinarse y mantener aproximadamente **1/k** de sus miembros desempeñando cada una de k funciones. El número de funciones **k es variable**. El usuario propuso entrenamiento con k=1..4 (k=1 es un control trivial) y pruebas con k>4 hasta un n escogido, sin asumir que una regla aprendida con cuatro funciones extrapole automáticamente a ocho. Inicialmente mencionó 8 estados posibles por agente solo como ejemplo, luego lo generalizó a k. Se quiere una tarea **colectiva genuina**, donde ningún individuo controle la solución global.

Los agentes disponen de información local y saben su propio estado y el k vigente. La idea de comunicación es **un vecino por turno**, intercambiando estado propio y quizá resumen del entorno; cada agente puede conservar o cambiar su función, y aprende estrategias por experiencia local. No usar la distribución global real como observación individual ni como señal de recompensa individual en el modelo principal: sería filtración de la solución.

La topología inicial puede ser una malla regular o grafo de proximidad; un diagrama de Voronoi es una partición geométrica y **no** una topología óptima universal de comunicación. Después comparar con mundo pequeño y, en una fase separada, enlaces endógenos aprendidos. La adaptación simultánea de enlaces y funciones desde el principio crea una fuente adicional de confusión.

El fenómeno de estabilidad requiere **equilibrio global**, **accesibilidad/diversidad local**, **pocos cambios innecesarios** y **duración durante varios turnos**. Evitar éxitos triviales por inicialización aleatoria cerca del equilibrio; introducir distribuciones iniciales deliberadamente desequilibradas (por ejemplo 60/20/15/5 % para k=4). El umbral debe admitir que N/k no sea entero: el objetivo óptimo para cada grupo es floor(N/k) o ceil(N/k).

El examen central es la **generalización a k inéditos**, por ejemplo k=5..8, sin reciclar durante selección la información del test. Después sustituir una parte de los agentes por recién llegados con estrategias/recuerdos iniciales: medir cuánto equilibrio se pierde inmediatamente y cuánto tarda en restablecerse (relevo generacional). Variar fracción de reemplazo, quién desaparece, comunicación y topología, con controles por dificultad funcional y composición de la red. Una idea secundaria es estudiar transiciones tardías análogas al grokking si aparecen espontáneamente y si importan para la recuperación posterior.

## Reproducibilidad: lo que es posible y lo que todavía no se sabe

**Es implementable** como simulación determinista-condicionada-por-semillas en NetLogo o Python. No necesita modelos generativos ni redes neuronales para cada individuo. Las trayectorias del modelo serán reproducibles con versión fijada, parámetros completos, RNG por corrida, reglas locales claras y artefactos de salida.

**No está demostrado** que un aprendizaje local sencillo produzca equilibrio global robusto, que extrapole a k>4, ni que aparezca un fenómeno de grokking. Esas son hipótesis falsables, no requisitos garantizados. Una heurística manual que simplemente elige el color menos frecuente local o global puede constituir un **baseline programado**; no se le debe llamar descubrimiento emergente de una estrategia si el investigador la incorporó explícitamente.

**Punto técnico indispensable:** si una política aprende únicamente sobre cuatro IDs de estado fijos, quizá no pueda producir acciones en un quinto color. Por ello la política debe disponer de un **conjunto de acciones variable de 1..k** y de representaciones invariantes a la permutación de etiquetas, o un generador abierto de estados; comparar frente a una política que memorice IDs 1..4. Los agentes conocen k y el listado de funciones legalmente disponibles, pero no su distribución poblacional exacta.

**Dificultad sociológica esencial:** definir qué feedback es localmente observable para atribuir un resultado a la elección de estrategia, sin introducir un evaluador global que instruya constantemente a los agentes. La recompensa global puede medirse externamente por el investigador; recompensas individuales deben derivarse de señales locales verificables (diversidad o disponibilidad de funciones en vecinos, cambios observados tras interacciones, estabilidad) y controles que detecten conflictos local-global.

**Dificultad de la generalización:** separar reutilizar una política fija en k nunca visto de continuar aprendiendo durante el episodio de test. Si los agentes actualizan sus parámetros con experiencias de k=6 durante evaluación, eso constituye adaptación online a un régimen nuevo y debe reportarse separadamente de generalización zero-shot. Definir explícitamente qué se conserva entre episodios y generaciones: estados, enlaces, creencias, reglas de estrategia, pesos de aprendizaje y memoria comunicativa.

## Protocolo escalonado propuesto (no ejecutado)

**Estudio de factibilidad.** Población N≈100 o120 (parámetro variable); grafo fijo toroidal o de grado pequeño; cuatro funciones de ejemplo, k variable; comunicación con un vecino por turno; reglas de decisión mínimas y memoria local acotada. Probar primero que un optimizador-oráculo global puede alcanzar la cuota, para verificar que la tarea es alcanzable. Luego comparar con baselines sin aprendizaje (no cambio, elección uniforme, copia de vecino, heurística local). Usar múltiples semillas y parámetros de desbalance inicial.

**Aprendizaje**. Elegir un mecanismo simple y auditable, como selección de estrategias con valores Q tabulares o bandit contextual y recompensa local postinteracción. Los agentes no deben recibir el estado global como señal supervisada. Registrar también consumo de mensajes, churn, fallos persistentes, heterogeneidad de estrategia y diversidad local. Medir objetivos múltiples, no solo cuota global.

**Generalización extrapolativa.** Entrenar en k=2..4; reservar k=5..8 en evaluación, con perturbaciones de estado inicial y de topología. El objetivo externo `D_global = sum_s abs(n_s - N/k)/N` es fácil de reproducir, pero no debe imponerse como recompensa local. Éxito: mantener D_global bajo un umbral **predefinido compatible con cotas discretas**, diversidad local y cambio reducido durante H pasos. Comparar zero-shot vs adaptación online. Fijar test seeds antes de explorar políticas.

**Transmisión intergeneracional.** Reemplazar porcentaje r de individuos después de alcanzar y mantener criterio de estabilidad; variantes de selección aleatoria versus centralidad; nuevos agentes comienzan sin política/recuerdos adquiridos (especificar si retienen función/vecinos existentes). Medir caída inicial, tiempo hasta recuperación estable, área de déficit funcional, supervivencia de estrategias y variación relacional. Debe compararse bajo **misma competencia inicial** y daño inicial equivalente cuando se investigue recuperabilidad, a la luz de V10–V13.

**Hipótesis de grokking colectivo.** Requiere rendimiento alto en configuraciones conocidas, rendimiento de evaluación bajo por periodo prolongado, transición tardía reproducible en k inéditos y auditoría de fugas. Una explosión de difusión de una estrategia y un cambio de composición generacional pueden imitar la curva sin que se haya aprendido una regla más general. Registrar mecanismos para distinguirlos. No forzar una curva tardía mediante cambios manuales en evaluación y presentarla como emergente.

**Topologías**. Empezar por rejilla/torus y mundo pequeño de tamaño/grado medio comparables; no etiquetar Voronoi como óptima. Opcional extensión posterior de rewiring social aprendido.

## Cómo continuar desde otro chat

Primero terminar el programa de lesiones (V13); luego leer este `QUEUE.md` y, si se han aportado, los documentos PDF/DOCX originales. Diseñar un modelo mínimo ejecutable con tests de invariantes (N constante, todos estados legalmente en 1..k, número de mensajes por turno, no fuga global, reproducibilidad por semilla), ejecutar baselines, barrido de hiperparámetros y controles de emergencia. Documentar resultados negativos y mantener datos en una carpeta propia independiente del proyecto de grokking. El modelo puede implementarse y verificarse técnicamente; **la generalización y el grokking colectivo son resultados empíricos desconocidos hasta ejecutarlo**.
