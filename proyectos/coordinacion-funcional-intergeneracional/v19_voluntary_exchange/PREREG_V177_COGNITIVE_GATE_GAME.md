# V177 — Juego restringido de activación de recurrencia

15/11/2026. V176 ya es conocido: en RNN_FULL apagar toda recurrencia mejora Q .4753→.8125 y .4988→.9066; en RNN_RESOURCE la misma lesión reduce .4577→.01547 y .5237→aproximadamente0. La hipótesis de una trampa cognitiva colectiva es POSTERIOR a esa observación. Se congela esta prueba antes de enumerar sus incentivos individuales; no es una confirmación independiente de V176.

## A–C. Estimando y rivales

¿La mejora grupal de apagar recurrencia requiere una decisión colectiva contraria al incentivo individual? Alternativa fuerte: una política particular mal optimizada mejora también por una lesión unilateral. Otra alternativa: unas personas ganan y otras pierden, sin mejora de Pareto. Ninguna de ellas requiere una institución emergente.

Schmid, Hilbe, Chatterjee y Nowak2022, PLoSComputBiol18:e1010149, DOI10.1371/journal.pcbi.1010149, ya demuestran dominancia de espacios de estrategia menores y dilemas sociales entre capacidades de memoria. Alqithami2026, arXiv:2604.11733v2, ya formula perjuicios de mayor recuerdo en juegos de rutas. Los contextos y definiciones son distintos; NO reivindicar novedad general de memoria perjudicial ni redescubrimiento de estos resultados.

Sin reentrenar, usar las dos poblaciones finales de RNN_FULL y RNN_RESOURCE, con LINEAR_FULL como control neutro. Nuevos lotes177115–177118,128grupos de5 por lote y1000pasos; fitness individual pasos100–999. Todos los32perfiles de activación se evalúan con idénticos genotipos y riqueza inicial. Bit i=1 conserva recurrencia, bit i=0 pone a0 los16pesos recurrentes SOLO de esa persona. La red restante y sus sensores siguen iguales. Es una intervención experimental; los agentes NO aprendieron esta elección binaria ni un derecho de decidirla.

## D–G. Enumeración y falsadores

Reutilizar el kernel auditadoV176 sin modificarlo; comprobar que poner a0 todos los pesos recurrentes produce exactamente el mismo fitness que RESET. En LINEAR_FULL las32máscaras deben ser idénticas. Conservar matriz completa de512grupos×32perfiles×5pagos por condición y semilla.

Un equilibrio puro RESTRINGIDO a esta elección cumple u_i(a)≥u_i(a xor2^i)−1e−10 para todas las personas. No es un equilibrio sobre todas las políticas o acciones posibles. Calcular arrepentimiento máximo, frecuencia de equilibrio de todos activos y de todos apagados, y proporción de grupos sin equilibrio puro restringido. No confundir esta última con inexistencia de equilibrio mixto.

Mejora de Pareto al apagar todos: ninguna persona pierde más de1e−10 y al menos una gana más de1e−10. Trampa fuerte especificada ahora: ≥50% de los grupos deben tener simultáneamente todos-activos como equilibrio restringido y todos-apagados como mejora de Pareto, en AMBAS poblacionesRNN_FULL. Si falla, rechazar ESTA caracterización como explicación general de esas poblaciones.

Mostrar también ventaja media de apagar unilateralmente la persona0 cuando todas las demás conservan memoria y ventaja de apagar frente a activar para cada número0…4de otras personas activas, promediando las combinaciones. Solo generaliza a poblaciones congeladas y esta familia binaria de desviaciones. No p-valores con generaciones o personas como réplicas de evolución (n=2).

## H–J. Decisión

Auditoría causalD1, no un nuevo mecanismo aprendido. Si apagar unilateralmente ya beneficia al individuo, el principal cuello de botella de estas redes es representación/selección, no gobernanza para coordinar apagado. No ampliar automáticamente arquitecturas. Si hay trampa, contrastarla con el antecedente de Schmid y un competidor de aprendizaje competente antes de alegar avance. CT2 histórico61 y N2=N3=0 permanecen. Guardar criterios fallados y todos los perfiles.
