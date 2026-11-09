# PROTOCOLO V3 — corrección sustantiva solicitada por el investigador (09-11-2026)

**Estado:** diseño para siguiente fase. NO es una reinterpretación de los resultados previos ni altera el prerregistro previo. Los resultados ya producidos siguen siendo exploratorios.

## Estimando y contraste correcto

La pregunta principal es si dos sistemas **con la misma competencia funcional al momento de una lesión** se recuperan de forma diferente en función de su *historia de adquisición*, una con **semigrokking tardío** y la otra con **adquisición gradual sin grokking**. La capacidad objetivo puede ser cualquier nivel intermedio (60% era meramente ilustrativo). No comparar como contraste primario el mismo sistema *antes frente a después* del grokking, pues ello confundiría trayectoria con competencia alcanzada.

## Emparejamiento PRELESIÓN

Misma tarea, mismo conjunto de evaluación externo fijado, mismas condiciones de test, misma arquitectura y capacidad (300 neuronas ocultas), mismo tipo/intensidad de lesión 30/300. Buscar modelos que tengan precisión test en banda de +-1 punto porcentual (tolerancia exploratoria ampliable de forma documentada a +-2 pp), y **meseta durable** verificada en ventanas posteriores y en una prolongación sin lesión. No forzar un 60%. Requerir entrenamiento cercano a 100% en ambos si es empíricamente viable. Registrar y evaluar comparabilidad de pérdida de test, márgenes de confianza, calibración, distribución por clases y superposición del conjunto de aciertos sobre los MISMOS casos. Utilizar estos indicadores para análisis de sensibilidad, y comparar pares con balance más estricto como resultado secundario. NO ajustarlos indiscriminadamente: parte de las diferencias de representación, márgenes y pérdida podría mediar el efecto de la trayectoria de adquisición sobre la recuperación. Distintos aciertos al mismo porcentaje NO significan igual competencia granular.

El emparejamiento debe producirse sobre un conjunto *de selección/validación* independiente del test final reservado; el test final de análisis y sus etiquetas no se utilizan para escoger pares, hiperparámetros o puntos temporales. La definición de meseta usa validación; el test final se consulta después de congelar el par.

## Clasificación longitudinal prospectiva

Grupo A: primero alcanza ajuste completo de entrenamiento; mantiene un tramo prolongado de generalización baja; posteriormente experimenta transición tardía sustancial y entra en meseta de generalización parcial duradera (semigrokking). Detectar latencia, aumento, cambio de pendiente y durabilidad mediante curvas de accuracy y loss, no solo precisión final.

Grupo B: alcanza la misma meseta parcial mediante generalización que progresa en paralelo al aprendizaje inicial o de forma suficientemente continua, sin intervalo prolongado de train-fit / test-failure seguido de una transición tardía. **Una pendiente suave de generalización tardía tras memorizar también podría constituir grokking**: está PROHIBIDO etiquetarla automáticamente como control «sin grokking». La clasificación se verifica ANTES de abrir resultados de lesión. Se conserva una variable continua de latencia/concentración de ganancia y análisis alternativos por umbral.

Las trayectorias son la exposición/variable explicativa de interés, pero los tratamientos de entrenamiento necesarios para producirlas (regularización, inicialización, curriculum, velocidad, tiempo acumulado) también son tratamientos con efectos directos potenciales sobre robustez. Por tanto, matching de accuracy NO identifica causalidad automáticamente; reportar estimación descriptiva/condicional y emplear replicación, balance de tratamientos, contrafactuales y pruebas negativas.

## Intervención y resultados

Ablación **permanente** de 30 de 300 unidades ocultas (máscaras aleatorias iguales en índices para cada pareja). Perturbar ambas redes en el mismo momento *relativo a meseta estabilizada*, no igualar forzosamente los pasos históricos. Registrar robustez sin reentrenamiento, deterioro de accuracy/loss de train y test, recuperación al 95% del nivel anterior **y** distancia respecto al control intacto que continúa entrenándose, área integrada del déficit, número de actualizaciones y muestras para recuperar, y viabilidad de reconstrucción dentro de horizonte predefinido. Además reinicialización del 10% como un estimando distinto, nunca mezclado con ablación permanente.

Normalizar el daño inicial o estratificar por nivel de daño; si un modelo resiste y no pierde casi accuracy, esto indica **robustez**, no una reparación rápida. Repetir sobre muchas máscaras anidadas en múltiples redes y semillas independientes, sin pseudorreplicar las máscaras como si fueran entrenamientos independientes. Control negativo sin lesión. Control de estado del optimizador: continuidad idéntica dentro de cada modelo, registrar diferencias entre modelos.

## Puertas de decisión

1. **Viabilidad de historias:** establecer al menos una trayectoria A y una B genuinas.
2. **Pareamiento válido:** mismo rendimiento estable en un intervalo elegido por validación, sin selección por el test final.
3. **Intervención:** cegar etiquetas A/B al análisis de recuperación cuando sea practicable.
4. **Confirmación:** replicar con semillas/particiones reservadas, un modelo jerárquico de redes y máscaras, y comprobación adversarial de explicaciones rivales. Si no existe par válido, publicar resultado de factibilidad negativo y NO atribuir efectos al grokking.

## Estado actual específico

Los checkpoints de aprox. 60% usados en el primer piloto NO son grupos A y B: ambos tenían generalización retrasada y todavía ascendente. La observación de 60% en una ventana de 0.37 train fraction tampoco es semigrokking persistente: terminó con 75.08% en el paso 45,000. 16 entrenamientos exploratorios, 15 lesiones; cero comparaciones A-vs-B elegibles, al corte de esta versión. **No se obtuvo todavía el resultado científico principal.**
