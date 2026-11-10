# V2-RL — Protocolo piloto, fijado antes de entrenar

Fecha: 2026-11-10. Corrige la arquitectura P0–G1: aquellos experimentos son pilotos de otro mecanismo, NO resultados de V2.

**Problema.** N agentes con colores 1..k deben aproximarse a N/k por función, con k=2,3,4 en entrenamiento. No se programa ninguna estrategia de escasez, negociación o equilibrio dentro de la política aprendida. El objetivo matemático es D=.5 sum_c |n_c/N−1/k|, con mínimo exacto 0 si N es divisible entre k. Deben aprender desde condiciones iniciales con ~70% de un mismo color.

**Red.** Piloto N=36, cuadrícula 6×6 con cuatro contactos cardinales más una diagonal por nodo emparejada en bloques 2×2. Grado interior 5 y menor en frontera. Próxima prueba N=120 en cuadrícula 10×12. Observar propio color y colores de todos los vecinos directos.

**Acciones por ronda.** Cada nodo selecciona cero o un destinatario entre sus vecinos y un color que solicitar; adjunta al mensaje su snapshot de colores locales. Cada receptor puede recibir 0..grado solicitudes, simultáneamente con su mensaje saliente. Elige rechazar todas o aceptar exactamente una; al aceptar adopta el color solicitado. Sin cambios voluntarios de color en la condición principal; cambios simultáneos al final del turno. Nadie ve colores posteriores mientras decide.

**Refuerzo.** Únicamente r_t=N(D_t−D_{t+1}), premio de equipo denso y continuo que puede ser negativo, positivo o cero; nada de bonus binario por precisión ni reglas dirigidas a rareza. El actor recibe solo su entorno y el último escalar de feedback común, no los recuentos globales. Un critic central de entrenamiento puede conocer D y recuentos. gamma=.99. Esa señal pública escalar es comunicación global limitada durante test también; es una hipótesis explícita. Primer experimento usa parámetros compartidos entre agentes con observaciones y acciones individuales; no representa aprendizaje de políticas autónomas independientes.

**Memoria** piloto: colores locales presentes más feedback del paso anterior (W1); posterior estudio W4/W8. No afirmar que W1 sea óptima.

**Criterios.** Curvas promedio de D por episodio, D final y D final mínimo, 10 ticks consecutivos con D≤.06 y churn≤.05, tasa y contenido de mensajes, rechazo, comparación con permanecer inmóvil y decisiones aleatorias. Semillas de evaluación nuevas y no usadas para entrenamiento ni tuning. Diferenciar éxito momentáneo de estabilidad. Test de necesidad de cooperación con un solo emisor activo, manteniendo las reglas de los receptores; en N36,k4, ~25 agentes en color0 frente a cuota9: un único emisor con máximo5 vecinos no puede corregir 16 excesos. Esto constituye una restricción estructural, no un éxito impuesto.

**Plan.** (1) implementar invariantes y baselines; (2) entrenamiento A2C/REINFORCE compartido con refuerzo únicamente colectivo, lotes y actualizaciones documentados; (3) bloquear hiperparámetros y test; (4) replicar en múltiples semillas y N120 solo si la fase viable. Con recompensa compartida, el problema de asignación de crédito puede impedir aprendizaje; resultados negativos son admisibles. No hay grokking colectivo confirmado, no extrapolación k>4 antes de consolidar k≤4, ni inferencia sobre sociedades humanas.
