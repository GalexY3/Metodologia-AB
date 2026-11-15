# V178 — Rival privado competente: umbral libre sin memoria añadida

15/11/2026. Diseño motivado por resultados conocidosV173–V177. La recurrencia privada superó al MLP privado probado, pero este último puede ser un rival débil. El control sin señal social del modelo original fija el intercepto a0: χ[x+S M y_i]. Una constante libre permite una aspiración de riqueza sin observar a los pares ni reconstruirla. Esa posibilidad debe evaluarse antes de atribuir ventajas a la información colectiva o a la memoria recurrente.

## A–C. Hipótesis y antecedentes

Pregunta: ¿la restricción de representación del comparador explica una parte sustancial de la brecha de eficiencia en este modelo? Itao y Kaneko arXiv:2507.22555v2 NO afirman imposibilidad universal sin observación social: su análisisS15 describe un rango de grupos más restringido. No convertir una mejora puntual en refutación de una afirmación que los autores no hicieron. Reglas de aspiración, perceptrones con sesgo y autocontrol por riqueza son técnicas conocidas, no una arquitectura nueva ni una institución aprendida.

Selección por fitness privado, reagrupación aleatoria, mismos crecimiento, extracción, consumo, inicialización,100grupos,1000pasos,3000generaciones y fitness pasos100–999 del antecedente. Todos los brazos usan3genes inicializadosN(0,.1), herencia con mutacionesN(0,.1) de TODOS los genes; no se penalizan genes neutrales. Misma cinta de números aleatorios por semilla y tamaño, sin seleccionar mejor checkpoint.

Cinco familias explícitas:

- FULL: χ[x+g0 M y_i+g1 Σy], dos genes activos; control original de competencia.
- ORIGINAL_PRIVATE: χ[x+g0 M y_i], un gen activo; control sin señal de pares original.
- AFFINE_PRIVATE: χ[x+g0 M y_i+g1], dos genes activos; única intervención principal es intercepto libre. Solo x actual y riqueza propia actual. Sin estado mental adicional, edad, posición, acciones ajenas, riqueza colectiva o etiquetas de cooperación.
- AFFINE_FULL: χ[x+g0 M y_i+g1 Σy+g2], tres genes activos; control para separar intercepto de observación colectiva.
- PRIVATE_THRESHOLD: χ[g0−M y_i], un gen activo; ignora incluso el recurso. Rival de aspiración simple, secundario.

Etapa1: M5,8semillas178115–178122. Primario de capacidad: AFFINE_PRIVATE Q_tail≥.70 en al menos6/8semillas Y mediana pareada de AFFINE_PRIVATE−ORIGINAL_PRIVATE≥.20. Gate de física/competencia: FULL≥.70 en al menos6/8. Mostrar las40corridas y contrastes por semilla. Q_tail es promedio de últimas500generaciones; las8evoluciones son las réplicas independientes, no las500generaciones.

Etapa2 condicionada y definida ANTES de la etapa1: solo si pasan ambos gates, repetir de novo M16,8semillas nuevas178215–178222, los mismos cinco brazos. Exigir ≥6/8 AFFINE_PRIVATE≥.70 y mediana de ventaja≥.20 frente al original privado para la extensión de eficiencia a grupos mayores. Un fallo M5 detiene ESTA campaña tras registrar el negativo; no cambiar hiperparámetros ni añadir familias para rescatarla. No es confirmación externa independiente.

## D–G. Auditoría y análisis

KernelNumba independiente del entrenamientoV175. Comparar estados y parámetros aleatorios con NumPy de referencia y control FULL con código original, trazando acciones, recursos y fitness. Probar aislamiento privado alterando riquezas ajenas mientras se conservan x y riqueza propia. Limitar máximo2workers,3threads por worker, seisCPU, prioridadBelowNormal con lectura verificada.

Congelar código, protocolo y auditoría en commit remoto antes del primer entrenamiento. Conservar curvas completas, hashes, poblaciones finales, RNG y checkpoints cada500generaciones. Contrastes agregados por semilla; cualquier intervalo bootstrap será de esas semillas, sin pseudorreplicar personas o generaciones. No declarar equivalencia por una diferencia puntual pequeña. Una familia privada eficaz puede explotar renovación del recurso o la ventana de selección, que siguen programadas como en el artículo.

## H–J. Decisión

Auditoría D1 de representación en la rama ecológica. Si un rival privado sencillo logra alta eficiencia, abandonar la lectura de V175 como demostración de necesidad de memoria recurrente o riqueza colectiva. Si no, el fracaso solo corresponde a estas familias y este optimizador. No identifica imposibilidad informacional. No hay comunicación, acuerdo, monitoreo endógeno ni derecho colectivo aprendido. CT2histórico61, N2=N3=0 sin aumento; origen del juego externo y atribución preservados.
