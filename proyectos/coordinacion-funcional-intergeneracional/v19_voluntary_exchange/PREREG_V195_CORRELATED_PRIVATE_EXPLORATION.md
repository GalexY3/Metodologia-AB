# PREREG V195 — Exploración correlacionada de convenciones sin recompensa de grupo

15 de noviembre de 2026. Se registra después de ver V194/V194A; todas las hipótesis y configuraciones de V195 se fijan antes de ejecutar sus entrenamientos. Problema: la mayoría de los agentes V194 aprenden rechazo casi total bajo unanimidad; algunos también tienen razones reales por su pérdida privada L_i. Pregunta de identificación: ¿es posible enseñar al sistema la **existencia de una convención mutuamente rentable** mediante exploración ocasional de políticas conjuntas, sin dar etiquetas del estado, transferir recompensa de grupo ni compartir Q, de tal modo que, una vez eliminada toda coordinación externa, los agentes mantengan esas políticas por su recompensa PRIVADA? Esta coordinación de exploración es PROGRAMADA POR EL EXPERIMENTADOR, nunca presentada como institución inventada por los agentes.

Antecedentes explícitos: joint intrinsic motivation / coordinated exploration (Toquebiau et al AAMAS 2024, https://aamas.csc.liv.ac.uk/Proceedings/aamas2024/pdfs/p2522.pdf), cooperative Stag Hunt and relative over-generalization (Claus & Boutilier 1998, revisiones MARL), Basak, Deb & Kuvalekar AER 2026 sobre similitud informativa. No atribuir novedad a correlación, coordinación o aprendizaje independiente.

## Entorno
Reutiliza solo las funciones material y de inicialización de V194, ya auditadas; no sus resultados ni Q. Grupos fijos m=k−1 votantes, k∈{4,8,12}, Nmundos=32 y 20 grupos/mundo; coste privado L_i∈{1,7}, constante por persona; estado GOOD Pr=.6, señal individual exactitud .8 e independencia CONDICIONAL en el estado. No se ofrece canal público: el canal es INDEPENDENT fijo en todos los brazos, aislando la coordinación de exploración. Ratificación UNANIMITY o MAJORITY, impuestas externamente. Acuerdo GOOD=+1 individual, BAD=−L_i individual, rechazo=0. Ningún agente observa estado real, señales ajenas, utilidad de otros ni los Q de sus compañeros.

## Algoritmo
Todos tienen Q propia de 2 señales×2 decisiones VOTE YES/NO, inicializada cero. Solo actualizan la acción REALIZADA con su recompensa privada; alpha=.10; 8000 oportunidades de entrenamiento con epsilon-greedy de .30 a .08 en paso 6000, 2000 nuevas oportunidades en evaluación congelada epsilon=0. Las Q no se comparten. Test sin pulsos: **cualquier resultado cooperativo debe mantenerse por la política aprendida sin intervención externa**. Estados y señales ambientales emparejados exactamente por brazo con RNG de entorno separado de RNG de decisiones. Cada mundo representa una réplica computacional de sus agentes y 20 grupos anidados, sin confundir repeticiones con evidencia externa.

## Intervenciones preregistradas
- STANDARD_PRIVATE: voto independiente epsilon-greedy, sin intervención.
- IID_SIGNAL_PULSE_10: cada persona con probabilidad .10, independientemente de los demás, ejecuta VOTE=SEÑAL PROPIA en esa reunión, sin seleccionar la acción de su Q; recompensa recibida actualiza su Q de acción ejecutada. En el 90% restante vota por epsilon-greedy. La tasa marginal de intervención es10% por individuo.
- JOINT_SIGNAL_PULSE_10: con probabilidad .10 por grupo, TODOS los individuos usan VOTE=SEÑAL PROPIA en esa reunión; cada Q se actualiza en su propia recompensa real. Tasa marginal individual igual al brazo anterior. El experimento **no entrega señales ajenas** y no modifica consecuencias económicas.
- JOINT_RANDOM_PULSE_10: con probabilidad .10 por grupo, TODOS usan el MISMO voto aleatorio YES/NO (50%); a igualdad de frecuencia de pulso, separa sincronización de política con contenido informativo.
- JOINT_SIGNAL_PULSE_02: como JOINT_SIGNAL, pero .02 de oportunidades. Examina costo de encuentros exploratorios, preespecificado antes de test.
- SIGNAL_FOLLOW_CONTROL: conducta impuesta, nunca aprendida; entrega la cota de rendimiento de la política focal.
- ORACLE_STATE: control de información perfecta, no un agente aprendible.

El uso de presión exploratoria adicional bajo pulse NO mantiene idéntica la tasa de cambio respecto a STANDARD_PRIVATE, pero la comparación JOINT_SIGNAL_PULSE_10 vs IID_SIGNAL_PULSE_10 iguala la frecuencia de oportunidad individual y distingue correlación; el contraste con JOINT_RANDOM_PULSE_10 distingue información en la convención conjunta.

## Hipótesis y falsadores
H1. Bajo UNANIMITY, la tasa de aprobación de acuerdos favorables tras congelar las políticas JOINT_SIGNAL_PULSE_10 supera a IID_SIGNAL_PULSE_10, al menos en un k, pero no se presupone que supere al baseline signal-follow no aprendido.
H2. La mejora debe persistir en las 2000 reuniones de evaluación SIN pulso ni mayores tasas exploratorias; si desaparece, se trata de cooperación impuesta temporalmente y NO aprendida.
H3. JOINT_RANDOM_PULSE_10 puede fallar pese a la misma sincronización, si lo esencial es explorar una política conjuntamente coherente con la información; si tiene igual efecto, la explicación “exploración de convención” queda debilitada.
H4. La ganancia puede desaparecer para votantes de L=7, cuyo beneficio de aprobar bajo una sola señal pública positiva puede ser negativo; el canal sigue siendo independiente, con inferencia del respaldo ajeno a través de ser pivotal.
H5. Con mayoría, el mecanismo de aprendizaje y la necesidad de exploración conjunta son diferentes; no transportar resultados de unanimidad sin prueba.

Primaria exploratoria: bienestar privado medio por mundo de JOINT_SIGNAL_PULSE_10 − IID_SIGNAL_PULSE_10 congelado; diferencia de grupo funcional (GOOD y acuerdo) y valoración por tipo individual L. IC bootstrap pareado 10000 remuestras de32 mundos, 20 grupos dentro de mundo. Secundaria: Q de YES bajo señales positiva/negativa, voto, fracción de grupos sin ratificar acuerdo GOOD, mínimo de desviaciones adicionales, períodos de entrenamiento por ventanas de1000 para evidencia de transición. Registrar resultados de todas las seis celdas, no seleccionar la que funcione para afirmación global.

## Auditoría y criterios
Paridad de recompensa contra motor V194 en500 perfiles, independencia RNG, congelación real de pulso y actualización, conteo de frecuencia de pulsos durante entrenamiento para garantizar igualdad nominal y empírica, todos los resultados negativos e intervención realmente ejecutada; código/hashes. No elevar N2 por esta adaptación sin rivales de exploración coordinada, grupos endógenos, roles y contratos materiales, validación fuera de este juego y novedad identificada en literatura. CT2=61,N2=0,N3=0. No inventar logros con escenarios donde el entrenamiento no haya terminado.
