# V13 — curva de dosis y reconstrucción postablación
Fecha 2026-11-09. Protocolo EXPLORATORIO registrado antes de ejecutar ninguna lesión V13.

**Pregunta concreta:** ¿varía la capacidad de recuperar función en función de la proporción de unidades eliminadas, cuando comparamos dos modelos que alcanzaron 100 % en validación después de historias de aprendizaje distintas y 4000 pasos con igual regularización final?

## Cohorte fija y estimando
Se usarán EXCLUSIVAMENTE las cinco parejas de redes ya declaradas elegibles en V12 (semillas 11,12,13,14,18), entrenadas sobre la misma partición 20261110 y evaluadas al checkpoint step=10000 tras 4000 pasos L1 final común=0.0001. Modelos con 300 neuronas ReLU y paridad de 3 de 30 bits. Brazo A: historia grokking tardío bajo L1 inicial 1e-5; B: aprendizaje rápido bajo L1 inicial .001; ambas historias **confundidas por L1 inicial**. No seleccionar modelos por respuesta a lesión.

## Dosis fijadas, máscaras y criterios
Porcentaje fijo de neuronas de la capa oculta enmascaradas de forma permanente: 10%, 20%, 30%, 40%, 50%, 60%, 70%, 80% y 90% = 30,60,90,120,150,180,210,240,270 de 300. Para cada pareja de redes usar exactamente cuatro semillas de máscara 4101,4102,4103,4104; una permutación aleatoria de 300 índices por semilla, prefijos anidados para dosis crecientes. Los índices serán idénticos dentro de la pareja y para cada dosis. Así se obtiene una curva de ablación bajo aumento monotónico de dosis nominal; la **precisión no tiene por qué descender monótonamente** en una red multicapas al retirar más neuronas.

9 dosis × 4 máscaras × 5 pares × 2 brazos = 360 ramas lesionadas, más controles intactos. Las máscaras son repeticiones anidadas dentro de cada red; n=5 pares independientes, NO n=180 por brazo. Las cuatro máscaras son un piloto de precisión limitada, suficiente para estimar factibilidad/umbrales pero no para asegurar una función dosis-respuesta universal.

## Protocolo de reparación
Desactivar permanentemente el vector mask después de ReLU; la máscara queda en 0 para neuronas destruidas durante toda la recuperación. La función superviviente y sus pesos sí pueden actualizarse (no se regeneran neuronas). Cada modelo: control intacto desde step10000; y lesión desde checkpoint idéntico. Inicializar **un AdamW nuevo con LR=.001 WD=0** en ambos, aplicar CE de 500 ejemplos + penalización L1 explícita .0001 para las 500 actualizaciones de seguimiento, entrenando exclusivamente en split train. Evaluar train/val cada 10 pasos. No consultar test durante selección, lesión ni análisis de V13. No cambian la tasa, las condiciones finales ni el horizonte por causa del resultado observado.

## Resultados principales
1. Robustez inmediata = precisión de validación perdida al paso0 en puntos porcentuales y aumento de CE val.
2. Recuperabilidad = tiempo hasta dos mediciones consecutivas con validación >=99% (evento censurado al paso500, no asignar falsamente un tiempo observado de 510). Tasas de éxito y **tiempo restringido a horizonte 500** también cuentan los censurados.
3. AUC en paso0..500 de déficit validación = accuracy de control intacto menos de lesionado, integral trapezoidal; menor AUC mejor, pero mezcla magnitud de daño y reparación.
4. Sensibilidad solo entre lesiones con daño inicial >2 pp en ambos brazos: comparar AUC normalizada por daño inicial, sin usar selección condicional como estimando primario.
5. Interacción historia×dosis: diferencias A−B del daño, probabilidad de alcanzar recuperación, AUC y tiempos; resumir primero dentro de semilla y luego sobre cinco pares, mostrar **todas** las curvas incluyendo casos negativos, y si hay inversión de signo por dosis.
6. Indicador de fallo fuerte: no recuperación en 500 pasos bajo la configuración fijada; esto NO significa irrecuperabilidad universal.

## Auditoría y límites
Identidades de índices y número de neuronas enmascaradas verificables en JSON. Mascarilla persistente (los pesos de neurona dañada pueden conservar gradiente nulo para fc hidden pero optimizador puede modificar salidas en parte; multiplicación pos-ReLU inhibe toda contribución funcional). Código preservado y hashes. Evaluar comparabilidad antes de ejecutar. No usar resultados para escoger una dosis favorable. No atribuir diferencia a *grokking* separadamente de L1 inicial, arquitectura o representaciones.

Conservar como hipótesis rival que un grupo más robusto a daños nominales resulte menos capaz de reparar daños de severidad funcional igualada, o a la inversa. Un resultado global mixto es admisible. Test V12 ya fue abierto para auditoría final después de congelar análisis V12, pero V13 no debe utilizarlo para calibrar nada. Aun así, V13 es **posthoc respecto a toda la historia V10–V12**, aunque este barrido esté registrado antes de correr.

Fase siguiente, una vez cerrado V13: evaluar en nueva cohorte y tarea distinta, y ensayar un diseño que varíe independientemente el mecanismo de regularización y el calendario de adquisición; V13 no se confundirá con causalidad.
