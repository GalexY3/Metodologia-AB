# V8 — Diagnósticos de información y reformulación colectiva V9

**Estado de investigación, 10/11/2026:** V8 no demuestra cooperación entre agentes. Los resultados corresponden a controles de solubilidad, señal/ruido y una microtarea de aprendizaje de aceptación. La interpretación científica vinculante está en **[CONTRATO_COLECTIVIDAD_V9.md](CONTRATO_COLECTIVIDAD_V9.md)**. El usuario exige que no haya una estrategia individual ganadora que sustituya la acción colectiva.

## Qué leer, por orden

1. \`CONTRATO_COLECTIVIDAD_V9.md\`: definición operacional de colectividad fuerte, límites de V8 y controles causales obligatorios.
2. \`TRASPASO_OTRO_PC.md\`: continuidad del proyecto y procedimiento para trasladarlo entre los dos PCs.
3. \`DESIGN_V8.md\`: desarrollo matemático y diagnóstico de arquitectura, observabilidad y señal pública.
4. \`RESULTS_V8_SIGNAL.json\`: 1.500 mundos por combinación N/k, con el cociente diagnóstico de señal causal a ruido por número de cambios concurrentes.
5. \`RESULTS_V8_CONTROLLER.json\`: control programado por aceptación/reversión después de observar D, con N=36/144/324.
6. \`RESULTS_V8_LEARNING_ACCEPTANCE_LR004.json\` y \`..._LR050.json\`: pilotos neuronales con ajustes de intensidad de aprendizaje realizados en exploración.
7. \`RESULTS_V8_TRANSFER.json\`, \`RESULTS_V8_COMPONENTS.json\` y \`models/*.npz\`: análisis retrospectivo y modelos congelados, entrenados solo en k=4.
8. \`TRANSFER_BUNDLE_RUNS_20261110.zip\`: 42 artefactos de V6/V7 seleccionados y verificados contra hashes SHA256 de la propia instantánea; fuente de continuidad para checkpoints ignorados por Git. No reemplaza el código de las ramas anteriores.

La instantánea no contiene una solución colectiva nueva. Mantener siempre separados: una mejora del reparto agregado, aprendizaje individual de interpretar una recompensa global y coordinación causante del resultado.

## Reproducibilidad en el equipo nuevo

Se usó Python 3.12.16 y NumPy 2.5.4. Los scripts V8 utilizan NumPy y la biblioteca estándar.

\`\`\`powershell
py -3.12 -m venv .venv
& '.\.venv\Scripts\python.exe' -m pip install -r 'proyectos\coordinacion-funcional-intergeneracional\v8_diagnostic\requirements.txt'
& '.\.venv\Scripts\python.exe' 'proyectos\coordinacion-funcional-intergeneracional\v8_diagnostic\test_v8.py'
\`\`\`

El paquete ZIP conserva los checkpoints V6/V7 bajo rutas relativas listas para restaurarse dentro de \`proyectos/coordinacion-funcional-intergeneracional/\`. Los modelos V8 son NumPy y están presentes como archivos versionados independientes.

**Siguiente investigación:** formular y probar una tarea en la que las observaciones privadas y las interacciones sean causalmente necesarias, sin dar a cada agente el cambio contrafactual de D como un oráculo. Comparar políticas individuales sin mensajes, sociedades con mensajes aprendidos, políticas clonadas, perturbaciones y generalización fuera de la distribución de entrenamiento.
