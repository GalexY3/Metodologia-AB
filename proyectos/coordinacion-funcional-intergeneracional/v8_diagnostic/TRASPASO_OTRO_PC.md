# Traspaso de investigación entre ordenadores — 10 de noviembre de 2026

## Prioridad máxima y no negociable

El investigador ha precisado: **«es importante para mí que la solución sea colectiva, que no haya una strat ganadora que puedas hacer tu solo»**.

Se conserva literalmente este criterio en el diseño. Ver \`CONTRATO_COLECTIVIDAD_V9.md\`; su especificación prevalece frente a cualquier interpretación de V8 como prueba de cooperación. **No** promocionar el control V8 de propuesta/reversión basada en el cambio del D global a método principal. Es una microtarea que una política aislada puede aprender sin comunicación. V9 debe buscar coordinación genuinamente interdependiente, con evidencias causales y controles sin mensajes.

## Repositorio GitHub

- Repositorio: \`https://github.com/GalexY3/Metodologia-AB\`
- Rama de trabajo V8 y contrato V9: \`research/marl-v8-signal-observability-20261110\`.
- Rama V7 anterior: \`research/cooperacion-v7-pilotos-20261110\`, commit \`f56388ee\`.
- Rama V6 anterior: \`research/marl-million-144-20261110\`.
- Carpeta de análisis: \`proyectos/coordinacion-funcional-intergeneracional/v8_diagnostic\`.

Para clonar en el otro ordenador, en PowerShell:

\`\`\`powershell
New-Item -ItemType Directory -Force -Path 'C:\Programación' | Out-Null
git clone --branch research/marl-v8-signal-observability-20261110 https://github.com/GalexY3/Metodologia-AB.git 'C:\Programación\Metodologia-AB'
Set-Location 'C:\Programación\Metodologia-AB'
git status
\`\`\`

Si el repositorio ya existe en el otro equipo:

\`\`\`powershell
Set-Location 'C:\Programación\Metodologia-AB'
git fetch origin
git switch research/marl-v8-signal-observability-20261110
git pull --ff-only
\`\`\`

ADVERTENCIA: si el directorio del otro ordenador tiene cambios locales, revisarlos antes de cambiar de rama; no sobrescribir trabajos sin examinar.

## Entorno de ejecución

Los experimentos de V8 \`information_bottleneck.py\`, \`feedback_controller.py\`, \`learn_acceptance.py\`, \`transfer.py\` y \`audit_components.py\` necesitan Python >= 3.10 y NumPy. Están separados del entorno PyTorch de V6/V7. Se ejecutaron en el entorno local de DESKTOP-I4SULKD:

\`C:\Programación\MARL-million-144-20261110\.venv\Scripts\python.exe\`.

En el otro ordenador, preparar un entorno virtual propio:

\`\`\`powershell
Set-Location 'C:\Programación\Metodologia-AB'
py -3.12 -m venv .venv
& '.\.venv\Scripts\python.exe' -m pip install numpy
& '.\.venv\Scripts\python.exe' 'proyectos\coordinacion-funcional-intergeneracional\v8_diagnostic\test_v8.py'
\`\`\`

Si \`py -3.12\` no está disponible, utilizar el intérprete Python existente compatible, sin instalar herramientas innecesarias.

## Interpretación de resultados V8

La comparación original V7 con 36 agentes y políticas individuales independientes no consiguió una ventaja consistente respecto a azar, ni estabilidad. V6 con 324 agentes se detuvo en el episodio 518.400/1.000.000; su prueba sellada final no se abrió. Conservar el resultado negativo.

V8 produjo cuatro hallazgos de diseño y diagnóstico, **ninguno equivalente a coordinación fuerte**.

1. La mejora de una modificación focal deja de distinguirse estadísticamente de los cambios aleatorios concurrentes al aumentar el número de agentes activos (\`RESULTS_V8_SIGNAL.json\`).
2. Un control **programado**, con propuestas aleatorias y aceptación exclusivamente si mejora el D global, se aproxima mucho más al equilibrio cuando los agentes actúan de uno en uno (\`RESULTS_V8_CONTROLLER.json\`).
3. Políticas logísticas independientes aprendieron a aceptar propuestas tras observar el cambio provisional de D. El ensayo a learning rate 0.5 dio error final D_4≈0.05 para N=324, frente a ≈0.535 inicial (tres semillas; \`RESULTS_V8_LEARNING_ACCEPTANCE_LR050.json\`). Esto es aprendizaje de una **regla individual con oracle-feedback**, no de una cooperación comunicativa.
4. Congelando las políticas entrenadas solo con k=4, su regla de aceptación tuvo ventaja sobre la versión inicial en k=2,3,4,6,9. Es transferencia exploratoria de un discriminador que recibe un feedback global provisional, **no** generalización de coordinación distribuida (\`RESULTS_V8_TRANSFER.json\`, \`RESULTS_V8_COMPONENTS.json\`). Los resultados fueron inspeccionados después de ver otros pilotos; no califican como prueba sellada.

El código de V8 y tres modelos NumPy están en \`v8_diagnostic\`. Los modelos guardados son \`models/acceptance_n324_k4_rep{0,1,2}.npz\`; \`transfer.py\` documenta sus semillas, y el JSON contiene hashes SHA256. \`audit_components.py\` reconstruye el rendimiento de esos modelos y valida distancias contra los JSON de transferencia.

## Recuperación de checkpoints de V6/V7

Se ha preparado una instantánea de los artefactos experimentales locales en \`v8_diagnostic/TRANSFER_BUNDLE_RUNS_20261110.zip\` para facilitar el traslado. **Este ZIP no sustituye a Git**: el código está versionado en las carpetas originales; la instantánea contiene archivos de ejecución antes ignorados por .gitignore, concretamente el checkpoint V6, estado/curva de entrenamiento y replays, además de los principales checkpoints, estados y resultados de los pilotos V7.

Después de clonar, abrir el ZIP y extraer sus carpetas \`v6_million\` y \`v7_pilots\` dentro de \`proyectos/coordinacion-funcional-intergeneracional/\` respetando la estructura del paquete. Para evitar duplicaciones si el otro PC ya tiene artefactos, comparar rutas, timestamps y hashes antes de sobrescribir.

El código V6/V7 puede requerir PyTorch CPU o CUDA y dependencias propias. La instantánea conserva pesos y estado del optimizador; el nuevo dispositivo puede mapearlos a CPU mediante \`torch.load(..., map_location='cpu')\`. No dar por hecho que el nuevo ordenador tiene CUDA.

## Avance lógico para la siguiente conversación

1. Leer \`CONTRATO_COLECTIVIDAD_V9.md\` y \`DESIGN_V8.md\`, preservando la rectificación del investigador.
2. Auditar y confirmar qué canal de información pública tienen realmente los actores del simulador. Separar recompensa colectiva **de entrenamiento** de información global **accesible al decidir**.
3. Predefinir una versión V9 donde exista una ventaja medible de intercambiar información y actuar conjuntamente, sin imponer por construcción el acto de negociar como condición obligatoria para cambiar.
4. Contrastar C1 sin comunicación vs C2 con comunicación, variación de topología, perturbaciones, controles clonados, aleatorios y de oracle-feedback. Analizar interdependencia causal, no solo D final.
5. Fijar evaluaciones selladas y presupuestos antes de entrenar; empezar por grupos pequeños y replicaciones de semillas. Los resultados V8 son exploratorios y no deben utilizarse como un test sellado.

**No se debe lanzar automáticamente otro millón de episodios**: diseñar antes una tarea donde el éxito individualmente alcanzable o la regla de «aceptar si mejora D» no sustituyan la coordinación que se quiere estudiar.
