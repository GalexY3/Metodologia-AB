# V191 — Identificación de aprendizaje entre dos redes

15/11/2026. El turno anterior produjo evidencia y una decisión: V187–V190 terminó, se publicó y se retiró el emisor tabular como vía para identificar grokking entre varios cerebros. No se reinicia esa campaña. El objetivo global sigue activo.

## Incertidumbre que cambia

Un receptor neuronal que generaliza tras recibir un código adecuado no establece reorganización de varios aprendices. Tampoco el fracaso de un emisor REINFORCE demuestra que aprender con información privada sea inviable. Se necesita un juego con dos redes, cada una con entradas locales de test nunca vistas, y una comparación que distinga el ruido de asignación de crédito del propio objetivo.

El nuevo juego tiene dos participantes con observaciones privadas x_i=(a_i,b_i). Cada uno elige u_i en Z31. El entorno concede a ambos r=1 si u_A+u_B=f(x_A)+f(x_B) mod31, con f(a,b)=a+b mod31. El agente no recibe f(x_i), la observación del otro ni sus gradientes. La evaluación combina de forma independiente los conjuntos locales retenidos de ambos participantes. Los agentes no son un emisor y un receptor de mensajes; ambos deciden y ambos deben generalizar.

Los intereses comunes, el juego y el feedback están diseñados. Una solución con desfases g y −g sería una convención aprendida dentro de ese diseño, no una institución material inventada ni cooperación surgida de intereses enfrentados. Hay antecedentes de sincronización por aprendizaje mutuo: Klein et al., NIPS2004, y Kinzel/Kanter2002. No se reclama como nueva la coordinación entre redes en general.

## La comparación correcta de feedback

Cada participante estima sus pagos Q_i(x_i,u_i) mediante una red cuadrática. La política es epsilon-greedy con epsilon=.1. Un feedback rico entrega el vector de pagos de todas sus acciones, manteniendo fija la acción realizada del interlocutor. En este juego el vector tiene un único1. Esa información es un oráculo contrafactual suministrado externamente: no se describe como institución aprendida ni como información gratuita. El feedback pobre solo entrega el pago de la acción elegida.

La pérdida con información completa es L_F=(1/P) sum_u (Q_u−R_u)^2. Si la acción elegida U se extrae de q, la pérdida bandit es L_B=(Q_U−r)^2/(P*q_U). El denominador se trata como constante durante la actualización. Condicionado a la observación y acción del interlocutor, E[L_B]=L_F y E[grad L_B]=grad L_F. La probabilidad q_U>=epsilon/P evita denominadores cero. Son identidades clásicas de muestreo por importancia y marginalización, no una contribución algorítmica original.

Esta igualdad no implica trayectorias iguales con Adam, ni elimina diferencias de información o coste. Se igualan inicialización, episodios y actualizaciones; la condición rica observa31pagos contrafactuales por cada pago observado en la condición bandit. No se atribuirá una eventual ventaja a un nuevo algoritmo ni a mayor eficiencia de consultas. La hipótesis local se refiere a cómo información y varianza afectan un juego privado de aprendizaje de funciones.

COMA ya usa contrafactuales para asignar crédito mediante un crítico centralizado. Expected Policy Gradients ya estudia la reducción de varianza por integración de acciones. Aquí no se ejecutan esos algoritmos ni se afirma superarlos: son antecedentes que restringen la interpretación.

## Un error de diseño evitado antes de entrenar

No sería equivalente sustituir REINFORCE por entropía cruzada sobre la acción contrafactual correcta. Cambiaría el objetivo. Además, si la política muestreara directamente de probabilidades calibradas con log-loss, la exploración uniforme puede diluir la convención. Bajo cobertura cartesiana y mejor respuesta probabilística exacta, sean h_A,h_B las distribuciones de error u_i−f(x_i) y M la inversión g->−g. Las respuestas calibradas satisfacen h_A=M((1−epsilon)h_B+epsilon*U) y simétricamente para B. Sustituyendo, h_A=(1−epsilon)^2 h_A+(1−(1−epsilon)^2)U: la solución de estas ecuaciones es uniforme. Esto es una deducción condicional de un candidato descartado, no un resultado de entrenamiento ni una imposibilidad de aprendizaje privado. No se aplica a toda regla de entropía cruzada ni a una política epsilon-greedy sobre argmax.

## Métricas que evitan un falso negativo causal

Sea h_i(g) la fracción de entradas cuyo error de despliegue es g. Sobre productos cartesianos independientes, la precisión conjunta es sum_g h_A(g)h_B(−g). La identidad se comprobará frente a enumeración independiente. El desfase para medir cada función local se elige usando entrenamiento, nunca maximizando test. Se reportan precisión conjunta codiciosa, precisiones locales bajo esa convención y precisión del comportamiento exploratorio por separado.

Congelar una red que aún falla en sus entradas locales de test puede limitar por construcción la precisión conjunta del sistema. Por tanto, una prueba posterior de necesidad de coadaptación debe examinar también la generalización del aprendiz que sigue activo y mantener la exploración del compañero. No basta con observar que el par congelado no alcanza95%.

## Decisión experimental

Primero se ejecutarán fixtures de gradientes, feedback, aislamiento y datos, sin entrenamiento científico. La campaña V192 se registrará después: un control con interlocutores oráculo debe demostrar que esta pérdida y arquitectura pueden generalizar antes de gastar recursos en sus dos condiciones privadas. Si el control falla su criterio, las condiciones privadas quedarán canceladas, no contabilizadas como negativos ejecutados. Si funciona, se ejecutarán sin ajustar parámetros tras ver resultados. Un candidato tardío requerirá seguimiento causal registrado y confirmación científica independiente; ninguna de estas comprobaciones técnicas concede AB2/3.

Fuentes primarias consultadas: https://papers.neurips.cc/paper_files/paper/2004/hash/5a45828dead8c065099cb653a2185df1-Abstract.html ; https://ojs.aaai.org/index.php/AAAI/article/view/11794 ; https://arxiv.org/abs/1801.03326. Revisión de resúmenes y métodos pertinentes, no revisión sistemática ni ejecución de sus programas.
