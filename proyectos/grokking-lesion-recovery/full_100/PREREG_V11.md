# V11 — contraste adversarial del confusor L1 y persistencia de la robustez
Fecha de bloqueo: 2026-11-09, antes de ejecutar la continuación común.

## Problema
V10B mostró resistencia superior de redes que generalizaron después de una meseta larga; V10C, tras selección de daño en validación, mostró una mejora modesta y heterogénea de recuperación. Pero la condición "grokking tardío" se produjo con lambdaL1=1e-5 y la condición "rápida" con lambdaL1=.001, diferencia que por sí misma puede explicar distintos patrones de redundancia, entropía y concentración de contribuciones neuronales. El aprendizaje rápido puede seguir siendo parcialmente grokking de transición breve: no afirmar una categoría ontológica sin grokking.

## Pregunta V11
Una vez ambos grupos han aprendido la misma tarea al 100%, ¿persiste la diferencia estructural de resistencia al daño cuando ambos continúan bajo el **mismo régimen de regularización y optimización**? ¿Se atenúa o invierte, y cómo depende de la duración común?

Este análisis es un **control adversarial exploratorio**, no identifica aisladamente causalidad histórica, pues las trayectorias previas tienen distinta regularización, y continuaciones pueden producir cambios estructurales nuevos. Tratar como evidencia de persistencia o convergencia condicionada, no "efecto puro del grokking".

## Diseño congelado
* Tarea: 30 bits, XOR de los tres primeros, 500 ejemplos de entrenamiento y 1000 de validación, 2000 de test. Arquitectura MLP ReLU 300 unidades, idénticas entradas y semillas entre pares. Bloque de semillas 0..4 heredado y ya exploratorio.
* Partir de checkpoints **step5000** de V10, donde las cinco semillas de ambos brazos ya deben haber alcanzado 100% train/val (verificar si falla).
* Dos continuaciones para cada checkpoint: una con L1 común lambda=.0001 y otra lambda=0 (control no regularizado), ambas con AdamW lr=.001 y weight_decay=0 y **estado del optimizador reestablecido idéntico (nuevo)**. Independientes, no encadenarlas entre ellas. 4000 pasos. Registros en pasos absolutos 5000,6000,7000,8000,9000, y checkpoints steps 5000,6000,7000,9000. La comparación primary de V11: checkpoint común a paso 9000 (4000 de exposición común); p.ej. tras formación V10B con distinta L1, ver si las representaciones convergen bajo una norma común.
* Un control secundario bajo lambda=0 tras step5000 indaga si la propia persistencia de regularización sigue manteniendo patrones; el objetivo sigue siendo estudiar continuidad de historia, no mecanismos causales aislados.
* Solo son elegibles para lesión los pares 100% train/val (o confirmar y declarar fallo).
* Medida de robustez **sin reparación**: para cada uno de 5 pares y cada régimen común, aplicar 100 nuevas máscaras idénticas de 90/300, máscara seeds 2001..2100, sobre ambos modelos, mismos checkpoints. Calcular daño inmediato de accuracy valid y CE, media primero por red y después por semilla. No elegir máscaras ni redes a partir de recuperación y no contar máscaras como unidades independientes.
* Predecimos dos resultados rivales: (H1) la resistencia inicial sigue favoreciendo a la historia tardía tras ambos pasar por regularización común; (H0) la diferencia se reduce/converge al aumentar la exposición compartida. La diferencia entre ambos resultados aún admite explicaciones por geometría distinta heredada de lambda histórico.
* Medida funcional de mecanismos: participación efectiva de neuronas por contribución activación-media × norma peso salida, proporción top-5 y top-10, pérdida de precisión causada por eliminar una unidad. Registrar val CE, norma pesos y ambos niveles.
* Se preservan controles sin lesión (los propios checkpoints), ventanas de tiempo y curvas. Por ahora V11 **no realizará 400 pasos de reconstrucción**: primero buscar y auditar si la comparación estructural después de un entrenamiento común es consistente.

## Datos y vulnerabilidades
* El registro original V10 contenía métricas de test durante entrenamiento; ese test no se considera prueba externa sellada.
* N real es cinco pares de redes, independientemente del número de máscaras.
* El resultado sería específico de una tarea artificial y 300 neuronas MLP.
* Las réplicas confirmatorias deberán usar nuevas particiones (test realmente reservado), y separar efectos de L1, historia, intensidad y tipos de lesión mediante factorial. Las máscaras 2001..2100 se predefinen aquí, y no pueden seleccionarse a posteriori por su efecto.

## Entrada
Fuente en `C:\Programación\grokking_lesion_20261109\full_100\parity_runs`; GitHub portátil `GalexY3/Metodologia-AB`, branch `research/grokking-lesion-v10-portable-20261109`, en `proyectos/grokking-lesion-recovery`. Actualizar al cerrar con auditores, código y datos reproducibles, conservando el estado verdadero del hallazgo y todo resultado negativo.
