# P1 — Validación de un mecanismo de fracaso de generalización: escala de rareza local

**Declaración exploratoria hecha tras el P0 y antes de abrir la nueva cohorte de evaluación P1.** P0 se entrenó con k=2,3,4 y falló en 40/40 tareas nuevas k=5..8, aunque una heurística manual sí fue parcialmente eficaz. Se observó θ promedio P0≈[3,29,2,97,-1,21]. Como las frecuencias locales por color disminuyen mecánicamente con k, puede surgir una **interacción de escala** entre la característica de rareza y la preferencia por conservar el propio estado. Esta explicación aún es una hipótesis.

## Intervención

Mantener n=120, grafo de anillo grado4, emparejamiento uno-a-uno por tick, memoria local descontada, recompensa complementaria local, REINFORCE θ_i, tasa de aprendizaje, coste de cambios, distribución inicial 70/30 y umbral de equilibrio exactamente como P0. Alterar **una característica de política**:

P0 original: feature_rare(c) = -freq_local(c).

P1 escalado: feature_rare(c) = -k * freq_local(c).

El resto de las características del candidato (permanecer, imitar vecino), la recompensa local 1−freq_local−coste_cambio, la temperatura y los presupuestos permanecen inalterados. Esta escala impone explícitamente un sesgo inductivo k-consciente. NO se presenta como estrategia descubierta completamente por agentes.

## Emparejamiento experimental y prueba nueva

Entrenar en la misma cohorte de entrenamiento seed=20261110, 8 episodios por cada k=2,3,4 (24 en total), 120 ticks por episodio, los modelos P0 y P1 desde θ idénticos y generadores de números aleatorios controlados. Evaluación conocida separada k=2,3,4, semillas 7000+100*k+s, s=0..3, 140 ticks (desarrollo diagnóstico, no para modificar k>4).

**Test nuevo P1**, sin modificar reglas después de ver conocido: k=5,6,7,8, 10 semillas POR k = 10000+100*k+s con s=0..9 (distintas del P0). Políticas de evaluación con θ congelado (se permite actualización de observaciones locales, no de pesos). P1 y P0 entrenadas con la misma semilla y los mismos episodios; comparar tasas de estabilidad y distancias TV contra la población de referencia, no tratar ticks como réplicas independientes. Se reserva k=9..12 para un test ulterior no abierto en P1.

## Criterios, incertidumbre y conclusión aceptable

Se conserva éxito fuerte TV≤.06 + churn≤.05 durante últimos diez ticks (sistema mantenido, no éxito transitorio). Se observa si P1 supera P0 en k>4 y si hay efectos adversos en k2..4. El tratamiento de escala controla un único mecanismo en el **simulador**; no verifica una ley sociológica. Un solo entrenamiento por condición exige replicación con varias semillas de cohorte antes de hacer inferencia estable.

En los informes, distinguir fracaso de la política aprendida de incapacidad de la población para coordinar: la heurística manual de rareza local es una prueba constructiva de factibilidad al menos parcialmente para k>4. Si P1 fracasa, conservar el resultado y explorar después mecanismos alternativos (difusión de regla por interacción, aprendizaje cultural, más observaciones) sobre un test independiente nuevo, sin reutilizar k5..8 de P0/P1 como test intacto.
