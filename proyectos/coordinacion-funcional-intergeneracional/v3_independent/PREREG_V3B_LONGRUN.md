# V3B-L — extensión exploratoria de presupuesto a 600 actualizaciones

**Fecha 2026-11-10. Registrado después de conocer el fracaso de estabilidad en los primeros resultados de 120 actualizaciones C1/C2.** No considerar confirmación previa ni ocultar el contraste principal V3B ya predefinido.

**Motivo**: distinguir un límite de aprendizaje temprano de una insuficiencia general del procedimiento. Las condiciones de 120 actualizaciones produjeron alta rotación y D cercana al azar IID; no han demostrado cooperación. No introducir crédito individual ni un oracle, y no modificar parámetros del optimizador.

**Diseño:** dos nuevos entrenamientos DESDE CERO con semilla 311, brazos C1 y C2, N36, red6x6, k2..4, mismos pesos iniciales, 600 actualizaciones en lugar de 120, 12 mundos por actualización, 24 turnos por mundo. Total 7200 episodios de entrenamiento por brazo. Exactamente el mismo REINFORCE global, baseline leave-one-out entre mundos del mismo k, clip por agente, hidden24, Adam .002, entropía .003, gamma .99, escala advantage 10, log cada20 actualizaciones. El primer segmento de120 se espera reproducible si configuración y código no cambian.

**Evaluación de desarrollo:** cada20 actualizaciones sobre semillas ya usadas en los pilotos anteriores, reportada como desarrollo, no prueba virgen. Se utilizarán todos los checkpoints finales de600 sin selección favorable. Si se ejecuta test adicional, reservar semillas nuevas, fijarlas antes de abrir datos y registrar si hay actualización de cualquier métrica o especificación.

**Limitaciones:** solo una cohorte de inicialización comparada por presupuesto extendido; los mundos de test anidados no equivalen a más cohortes. Aumentar episodios no garantiza resolver credit assignment. Resultado negativo permanece publicable como diagnóstico del diseño sintético, sin declarar imposibilidad de cooperación entre individuos.
