

## Desviación de registro V195 y comprobación posterior

Los dos prefijos que cambian a BANDIT en1100no registraron la evaluación1200durante ejecución, aunque sí guardaron sus pesos, momentos y RNG alineados. Se han reconstruido esas dos evaluaciones con un forward NumPy posterior: 192116: train=1.00000000, test=0.03164639; 192117: train=1.00000000, test=0.03325334. Es una reconstrucción retrospectiva, no una observación registrada a tiempo ni una nueva réplica. No cambia el criterio final, la parada ni los parámetros; se conserva como desviación del plan de logging cada100pasos. El resto de curvas publicadas conserva sus registros originales. Fuente: V195_V198_DOCUMENT_QA.json.
