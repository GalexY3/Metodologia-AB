# V13B — sensibilidad al horizonte de recuperación cuando desaparece el 90 %

**Decisión registrada después de ver V13**, antes de ejecutar cualquier trayectoria V13B. Es un segundo experimento **exploratorio motivado por el resultado** (V13: a 90% enmascarado, recuperaron 0/20 A y 1/20 B en 500 actualizaciones). No puede presentarse como confirmación independiente de un hallazgo escogido a posteriori.

## Pregunta falsadora
¿La escasa recuperación al eliminar el 90% de unidades se debe al corto horizonte observado (500 actualizaciones), o algunas redes tampoco recuperan en 2.000 pasos bajo el mismo optimizador y regularización? **No** atribuir irreversibilidad universal a no recobrarse en el horizonte fijado.

## Cohorte y máscaras
Las cinco parejas V12 elegibles: seeds 11,12,13,14,18; misma tarea paridad 30bits/3 relevantes, mismo split20261110; checkpoints de paso10000 tras L1 común=.0001 y 100% validación, MLP 300 unidades. Se enmascaran 270/300 unidades (90%) de modo permanente.

Usar cuatro máscaras NUEVAS, con permutaciones de seeds 4201..4204, disjuntas de V13 4101..4104. Las 270 identidades retiradas por máscara son idénticas en A y B dentro de cada semilla de red. Se mantiene una cabeza de 30 unidades: el sistema *podría* recuperar la tarea mediante pesos supervivientes, pero no se le garantiza. El caso de 90% es un estrés extremo; no equiparar dosis físicas a daño funcional.

## Continuación
AdamW recién inicializado, LR=.001, WD=0; pérdida CE de los 500 ejemplos train + L1 explícita .0001 sobre todos los parámetros; máximo fijo 2000 pasos, medir cada 25 (81 mediciones). Controles intactos idénticos entrenados durante 2000 pasos; puede reutilizarse un control por red para las cuatro máscaras. Test no consultado. No extender ni acortar basándose en desenlaces.

## Resultados
- Daño inmediato valid pp y CE.
- Recuperación por dos mediciones consecutivas con >=99% valid; éxito hasta paso 500,1000,1500,2000 por grupo y red (no confundir ausencia de éxito con muerte permanente).
- Tiempo hasta evento censurado a paso2000; *restricted mean time* incluyendo censurados, agregando primero por red y después entre las cinco semillas.
- AUC de déficit valid vs control intacto entre 0 y2000, y AUC por ventana (0..500,500..1000,1000..2000), todos descriptivos.
- Interpretar pareado por semilla, máscaras anidadas; no p-values de n=20 independiente.

**Hipótesis opuestas:** 90% representa una barrera temporal que podría superarse prolongando el aprendizaje, versus 90% deja un ancho de representación tan pequeño que con estos hiperparámetros y entrenamiento muchos no vuelven a alcanzar >=99%. Las dos son falsables y ninguna garantiza efecto especial de historia grokking. Historias L1 iniciales continúan siendo confusor causal, y esta prueba no estima regeneración biológica.
