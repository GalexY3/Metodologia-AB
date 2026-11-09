# CURRENT — Coordinación funcional distribuida

**Fecha inicial:** 9/11/2026. **Máquina principal:** DESKTOP-I4SULKD. **Rama:** research/intergenerational-k-coordination-20261109. **Worktree local:** C:\Programación\AB-coordinacion-intergeneracional-20261109. **Repositorio:** GalexY3/Metodologia-AB. El laboratorio de grokking y lesiones V10–V15 está cerrado en la rama research/grokking-lesion-v12-travel-20261109, commit base ac897748f0fdfb9630f967ebf08a41f5858bcee8.

## Contrato del usuario y prioridades

Proyecto posterior a V15 de regeneración neuronal, planteado por el usuario en texto adjunto: N agentes deben distribuirse de manera estable entre k funciones en proporción 1/k; comunicación con un vecino por turno; entrenamiento k=1..4 y evaluación k>4; investigar aprendizaje/generación y después sustitución intergeneracional. El texto mencionaba DOCX/PDF que no se han inspeccionado como archivos binarios. No asumir su contenido; QUEUE.md recoge el texto fuente disponible y cautelas.

## P0 realizado

Modelo `model.py`, parámetros en PROTOCOL_V0.md: N120, anillo grado4, matching sobre aristas (cada agente ≤1 conversación/tick), memoria local descontada, θ_i con tres pesos privados sobre rareza local, persistencia, imitación; REINFORCE con recompensa de complementariedad calculada solo con información local. División conocida k2..4 y evaluación inédita k5..8. Se probaron 10 invariantes. La heurística manual de función menos observada resuelve 12/12 en cuatro semillas por k2..4; el agente REINFORCE P0 k4 0/4 y test k5..8 0/10 en cada k. La recompensa de escasez y las features son ingeniería previa, no solución autónoma no guiada.

## P1 realizado

PROTOCOL_P1_SCALE.md fijado después de observar P0 y antes de nueva cohorte/test. Cambia UNA característica: `−freq_local(c)` → `−k×freq_local(c)`. Entrenamiento de P0 y P1 desde cero en la MISMA cohorte seed20261110, 8 episodios por k2..4, 120 pasos cada; validación conocida nueva semillas 7000+100k+s (s0..3); test nuevo 10000+100k+s (s0..9) k5..8, parámetros congelados, 140 ticks. Resultados test P0 vs P1: k5 0/10 vs10/10; k6 0 vs6; k7 0 vs3; k8 0 vs1. La heurística manual k5 9, k6 5, k7 0, k8 0 para esas semillas. Informes REPORT_P0_P1.md, código model_p1.py y experiment_p1.py, JSON results_p1/P1_RESULTS.json y archivo results_p1/TEST_LOCK.json. **Una cohorte independiente por tratamiento**: no hablar de prueba universal.

## G0 realizado

PROTOCOL_TURNOVER_V0.md: regla de minoría manual, comunidades estables en k4 o k5 (intentos 20 por k, elegibles k4=20 y k5=17). Reemplazar 25,50,75% de agentes, con idéntico vector posshock y nodos sustituidos entre tres intervenciones: herencia de regla, no enseñar, enseñanza por contacto con p=.25/turno (contacto limitado y efecto desde tick siguiente). Horizonte 150. Con k4 y 50/75%: heredada20/20, sin enseñar0/20, contacto20/20. Con k5 y50%: heredada17/17, sin enseñar0/17, contacto11/17; con 75%: heredada17, sin0, contacto5. Reporte REPORT_G0.md, auditoría RESULTS_G0_AUDIT.json PASS para333 ramas. Esta etapa no representa política aprendida por REINFORCE ni emergencia de grokking social.

## Resultado de conjunto

La coordinación local es técnicamente factible; un agente puede usar conocimiento parcial para promover equilibrio global. La extrapolación de la política aprendida es sensible a la escala de rasgos, y el éxito se reduce al aumentar k. La pérdida y transmisión de una regla ya programada afectan fuertemente la reconstrucción intergeneracional bajo shocks emparejados. NO se ha demostrado un mecanismo de grokking colectivo, originalidad científica, ni un fenómeno causal en sociedades reales.

## Próximos pasos concretos

1. Replicar P1 vs P0 **entre varias semillas de entrenamiento independientes**, no solo episodios test de la misma cohorte. Reservar nuevas semillas de evaluación y quizá k9..12 para no reutilizar k5..8 ya inspeccionados. Mantener escala/recompensas fijas y controlar mensajes/tasa de actualización. Usar ambos PCs si conviene.
2. G1: comparar desde idéntico vector posshock la recuperación de agentes que han aprendido θ_i, frente a recién llegados con θ inicial y controles con θ heredados. Antes garantizar que el sistema aprendido establece estabilidad. Cuidado con distinguir reset de θ, reset de memoria y reemplazo de colores.
3. Un diseño para analogía grokking requiere series temporales de rendimiento conocido y desconocido sin entrenar con test, transición tardía real y comparación con aprendizaje gradual a competencia equivalente. Actualmente no se ha observado.
4. Gráficos y memoria reproducible en informes/JSON, no reciclar test vistos como virgen.
