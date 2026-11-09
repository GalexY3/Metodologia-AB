# Protocolo exploratorio predefinido - lesión neuronal y generalización tardía (09-11-2026)

**Pregunta:** a igual precisión de generalización y, en la medida de lo posible, igual precisión de entrenamiento, ¿la trayectoria semigrokking frente a gradual predice diferente robustez inmediata y reaprendizaje tras inutilizar 10% de una capa oculta?

**Fase 0:** buscar dos modelos comparables, sin etiquetar a posteriori cualquier subida como semigrokking. Unidad experimental: entrenamiento independiente; los ejemplos test no son réplicas.

**Modelo piloto:** suma modular p=31, train/test estratificados por combinación de operandos mediante la misma permutación, red MLP con embeddings por operando, ReLU y exactamente 300 neuronas ocultas, 31 salidas. El estudio NO pretende probar que las neuronas sean equivalentes a neuronas biológicas.

**Definiciones prospectivas de elegibilidad:** precisión test en [0.55,0.65] durante al menos 5 observaciones consecutivas, amplitud máxima <=0.04; precisión train >=0.99 durante la meseta; semigrokking exige >=5 evaluaciones de estancamiento previo tras train>=.99 con test<=.20 y luego aumento de >=.30 en test; control gradual exige un incremento distribuido entre >=4 intervalos sucesivos, sin salto individual >.15, y que los datos no exhiban una meseta prolongada de fracaso seguida de salto. Si ningún entrenamiento cumple, registrar **SIN PAR ELEGIBLE**, nunca fabricar la comparación. Las condiciones están sujetas a estudio de viabilidad; futuras revisiones se versionan antes de nuevas corridas.

**Intervenciones sobre el 10% (30/300):** ablación funcional permanente con máscara post-ReLU, misma magnitud de lesión, mismos números de máscaras predefinidos entre grupos, estado del optimizador conservado; brazo control sin lesión y brazo reinicialización de 30 neuronas (exploratorio). Múltiples selecciones aleatorias por red; se calcula la distribución dentro de red y después entre semillas, sin pseudorreplicación.

**Resultados:** daño inmediato en precisión de test y train, pérdida, actualizaciones para restituir >=95% del rendimiento prelesión, área de déficit respecto al control sin lesión en el mismo horizonte, derivada de recuperación. Comparar tanto diferencia relativa como absoluta; la normalización puede inducir artefactos cuando el daño inicial es pequeño. Si no existe daño apreciable (p.ej. <2 pp), tiempo de recuperación=0 y no interpretar como gran plasticidad.

**Control de confusores:** mismo conjunto de entrenamiento y test, capacidad arquitectónica, número de neuronas, distribución de máscaras, evaluación sobre el MISMO test fijado y sin seleccionarlo por su resultado. Registrar semilla, decay, tasa de aprendizaje, pasos, norma de pesos, train loss, test loss y diferencias en estado del optimizador. Igualar accuracy no iguala margen ni representaciones ni tiempo de entrenamiento. Selección de entrenamientos y umbrales es exploratoria, exige réplica con semillas reservadas para evaluación confirmatoria.

**Restricciones de inferencia:** ningún resultado de este piloto sería automáticamente evidencia de emergencia ni de mayor resiliencia social. Revisión bibliográfica: Varma et al. (2023), semigrokking; Salah & Yevick (2026), robustez ante dropout. No atribuir originalidad sin evaluación adversarial de prior art.

**Directorio:** aislado del repositorio principal Grokking y no modifica sus checkpoints ni experimentos.
