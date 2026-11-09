# V14 — control factorial de regularización final frente a historia de aprendizaje

**9 de noviembre de 2026. Fase exploratoria registrada antes de ejecutar el V14.** Motivación observada en V11–V12: la brecha de robustez entre el grupo tardío y el rápido desapareció casi totalmente después de compartir 4.000 pasos finales de L1=0,0001. Ese contraste puede confundirse con el mero hecho de entrenar 4.000 pasos adicionales. V14 divide exactamente **los mismos checkpoints iniciales** en varias continuaciones, controlando el tiempo.

## Cohorte
Cinco parejas preseleccionadas por los gates originales de V12, semillas 11,12,13,14,18; misma tarea de paridad de 3/30 bits y misma partición train500 / val1000; MLP 300 neuronas. Punto de partida: checkpoint step=6000 de A (historia inicial lambda=1e-5, grokking tardío) y B (historia inicial lambda=.001, aprendizaje rápido), ambos train/val=100%. NO seleccionar por efecto de lesión V13.

## Experimento factorial 2 x 3
Cada checkpoint de cada historia se **copia** y continúa durante 4.000 actualizaciones bajo una de tres lambda L1 finales:
- lambda_final = 1e-5, igual a la historia original del brazo A
- lambda_final = 1e-4, régimen común utilizado en V12
- lambda_final = 1e-3, igual a la historia original del brazo B

En total 5 semillas × 2 historias × 3 lambda finales = 30 modelos terminales. Cada continuación empieza desde el mismo modelo por semilla/historia con un **optimizador nuevo AdamW lr=.001, wd=0** y pérdida CE + lambda_final sum abs parámetros de todos los pesos y sesgos. Misma cuenta de 4.000 actualizaciones y log train/validación cada500, checkpoint final step10000. Las tres intervenciones son contrastables dentro de la **misma red inicial** y, por tanto, identifican dentro de este simulador el efecto del régimen final elegido, no del grokking como evento aislado.

**Gate de comparación funcional**: train/val=100% en las últimas tres evaluaciones de la rama final. Si no se cumple, conservar datos, marcar no elegible para el contraste de robustez al100%; no aumentar pasos adaptativamente. Medir fallos de generalización como resultado relevante de cambiar L1.

## Robustez bajo tratamientos finales
Para cada rama final elegible medir daño inmediato por **100 máscaras nuevas** semillas 4301..4400 que retiran 90/300 unidades pos-ReLU (30%). Mismos índices para los tres tratamientos finales y para los dos grupos dentro de cada semilla. Medir precisión y CE de validación, contribución efectiva de neuronas, y comparar medias por semilla (no por máscara).

Estimar dentro de cada historia el contraste de cambiar lambda_final: daño medio L1 fina bajo (1e-5) vs media (1e-4) vs alta (.001), con 4.000 pasos fijos. Comparar A/B con **la misma lambda_final** para evaluar persistencia de su diferencia histórica, y con lambda cruzada (A recibe .001, B recibe 1e-5) como control adversarial de que las representaciones siguen directamente la L1 actual. No interpretar «más robusto» como «más capaz de reparar»; V14 no entrena tras lesiones.

## Hipótesis falsables
- H_reg: la resistencia responde al régimen final incluso dentro de un mismo checkpoint histórico, y la diferencia A/B bajo lambda común es pequeña; una lambda alta produce estructura diferente y afecta a la robustez.
- H_hist: aún a igual lambda final, A/B presentan una ventaja robusta consistente con su historia, no explicada por tiempo ni λ final.
- H_tiempo: 4.000 pasos extra con **λ original sin cambios** bastan para eliminar brecha, lo que debilita que sea necesaria la homogeneización de L1.
Las hipótesis no son mutuamente excluyentes y no requieren un signo fijado: una regularización alta también puede reducir precisión final e invalidar el contraste.

## Garantías metodológicas
No consultar test para seleccionar ni medir V14; las pruebas de test V12 ya se abrieron en un paso anterior para esa cohorte, por lo que V14 sigue siendo exploratorio. Conservar todos los outcomes, incluidos los fallos y cambios de signo. Unidad de réplica: cinco pares de redes iniciales, aun cuando se generan 30 contrafactuales de optimización. Mascarillas anidadas por red. No hay randomización de un «estado grokking» aislado; la historia A/B fue provocada por L1 inicial diferente, que sigue siendo una variable de confusión en el contraste histórico. Los contrastes de **L1 final** sí son intervenciones controladas sobre un checkpoint fijo.

Archivos de este diseño y scripts en la misma rama de trabajo GalexY3/Metodologia-AB, carpeta proyectos/grokking-lesion-recovery, preservando V10–V13 y la simulación intergeneracional en cola.
