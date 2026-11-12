# V23 — Aprendizaje conjunto desde cero de reciprocidad y movilidad ocupacional

Fecha de preregistro: 12 de noviembre de 2026, antes de generar las ejecuciones V23. Procedencia: V21–V22, commit 18d617c677e4b21c22969bee339566a85a0f7391.

## Cuestión de investigación

V22 mostró decisiones ocupacionales aprendidas desde poblaciones inicialmente monolíticas, pero se apoyaba en un actor de donaciones preentrenado y congelado. V23 examina si dos decisiones privadas —donar de manera dirigida y cambiar de ocupación— pueden aprenderse al mismo tiempo, con ambos conjuntos de pesos inicialmente aleatorios, solo por recompensa individual de alimento. No se incluye imitación, reparto programado, recompensa social agregada ni política donante preentrenada.

## Mecanismo de investigación

24 actores individuales privados, cada cual con red neuronal propia de donación dirigida y red propia de movilidad, sin parámetros compartidos. Horizonte de 48 rondas; movimiento entre dos ocupaciones cada 8 rondas, coste 0,015 al moverse; dar una donación cuesta al donante 0,12 en evaluación. El grafo de referencia es anillo de grado dos, sin alterar durante aprendizaje; población inicial dividida entre mundos totalmente monolíticos y mundos con ocupación Bernoulli independiente. Se observan únicamente estados locales, incluidos rol de vecinos, histórico propio y señales de donantes vecinos. Las redes donantes tienen la misma arquitectura que V20 y las ocupacionales la misma que V22. Cada gradiente REINFORCE usa solo el retorno propio descontado, con comparación contra otros mundos para el mismo individuo (baseline, no recompensa grupal).

## Diseño

Cuatro semillas neuronales independientes (3111, 4111, 5111, 6111). Tratamiento principal: coste de donación crece 0,01→0,12 en primeras 800 actualizaciones; el resto a coste 0,12. Total 1.400 actualizaciones por semilla. Arquitectura de donante 20 neuronas ocultas, init_scale 8; actor de movilidad 20 neuronas ocultas, sesgo inicial -1; batch 20, horizonte 48, gamma 0,995, learning rate donante 0,002 y rol 0,003, entropy donante 0,015 y rol 0,01. Inicializaciones ajenas al preentrenamiento V21 y V22 (solo arquitectura y algoritmo).

Dos controles negativos preregistrados: donación de coste alto desde el principio, en dos semillas; y privación de historial social para donaciones con el mismo plan gradual de coste en dos semillas. El tratamiento de coste alto y el de privación social se evaluarán con la misma intervención de largo plazo. La selección de modelos se hace por semilla y no por prueba final.

## Resultados y falsadores

En la prueba congelada fuera de muestra, informar media de alimentación en toda la trayectoria, donación media, enlaces ocupacionales complementarios al final y proporción de sociedades con reparto 12/12 desde una distribución inicial monolítica. Contrastar con red de movilidad aleatoria y ausencia de cambios, e intervenir en la donación inicial para cada persona con un auditor contrafactual si surge retorno positivo. Comparar anillo original, anillo de grado 4 y grafo reconectado.

H1. El conjunto frío alcanza una ventaja alimentaria superior al mejor control aleatorio de movilidad, sin donante preentrenado.

H2. Al menos algunos actores contribuyen de manera individualmente rentable desde el inicio aleatorio en su sociedad aprendida, y el beneficio se debilita al eliminar señales sociales. Un aumento en donaciones no basta.

H3. Los mecanismos de reciprocidad y movilidad tienen interacciones de realimentación: la estructura de roles emergentes puede generar un entorno que recompensa futuros regalos voluntarios.

Se reportarán fracasos, colapsos y heterogeneidad. Un éxito localizado no prueba escalamiento a N=120 ni k=4, y no justifica la expresión «OBJETIVO COMPLETADO» sin robustez y auditoría. Los modelos V21–V22 son referencia histórica, nunca cargados en el entrenamiento frío.

## Trazabilidad

Archivos de configuración, log de rondas/épocas, checkpoints, pruebas de invariantes y auditorías de distribución fuera de muestra. Dos equipos disponibles; PC con GPU para entrenamiento y PC de viaje para pruebas de reproducción. Documentación, hipótesis y definiciones en Markdown del repositorio, incorporando controles negativos y resultados que contradigan hipótesis.
