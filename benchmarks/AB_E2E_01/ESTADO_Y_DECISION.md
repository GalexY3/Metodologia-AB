# AB-DECIDE — AB-E2E-01

**2026-10-21. Estado:** DISEÑADO / INSTRUMENTADO / TESTS DE INFRAESTRUCTURA SUPERADOS. **Sin ejecuciones independientes de agentes. Sin resultados de efectividad.**

Se creó un protocolo de comparación pareada AB frente a baseline competente en BixBench, con evaluación ciega y 60 cápsulas como unidad independiente. Se diseñó transferencia a DiscoveryBench sin mezclarla con el estimando primario.

El harness fue probado únicamente con datos ficticios, verificando selección determinista, emparejamiento, cegamiento del grader y fallo explícito ante calificaciones ausentes. Esas pruebas no aportan evidencia a favor ni en contra de AB.

**BARRERA:** este chat no dispone de una interfaz para ejecutar múltiples instancias independientes de un mismo modelo con herramientas y presupuestos idénticos. Tampoco se han descargado ni evaluado las 60 cápsulas BixBench ni obtenido calificaciones oficiales. No simular dos agentes en el mismo contexto y llamarlo experimento.

**A01 sigue vigente:** la superioridad empírica end-to-end de AB frente a un investigador competente no está demostrada.

**AB-DECIDE: WAIT / PIVOT A EJECUCIÓN EXTERNA CONTROLADA.** Para cambiar el estado: acceder a tareas reales, congelar versión y hashes, ejecutar brazos en contextos independientes, registrar costes, obtener evaluación ciega, auditar y analizar con el código congelado. Si no se cumplen las condiciones, informar la barrera, no inventar puntuaciones.
