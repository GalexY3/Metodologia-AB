# Decisión científica: de la distribución ocupacional a la cooperación demostrable

**Fecha:** 11 de noviembre de 2026. **Estado:** evaluación conceptual; propuesta para V14, NO ejecutada. La investigación V12/V13 continúa siendo exploratoria. El resultado de MHU como regeneración ~20 % más rápida citado por el investigador NO se ha verificado en los documentos consultados de LARP; no inferir de resistencia a dropout un tiempo de reparación.

## 1. Fuentes específicas leídas

- LARP, [README principal](https://github.com/GalexY3/proyecto-LARP/blob/main/README.md): declara no confirmada una ventaja computacional específica de MHU.
- [Dictamen BR12](https://github.com/GalexY3/proyecto-LARP/blob/main/docs/06_BR12_DICTAMEN.md), [dropout de sensores](https://github.com/GalexY3/proyecto-LARP/blob/main/data/BR12/dropout_4096.json), [script](https://github.com/GalexY3/proyecto-LARP/blob/main/src/BR12/dropout_4096.py): en un ensayo f1,k16 y 12 mundos sintéticos, con eliminación de 60 % de sensores, error de reconstrucción MHU=0.474236; CVT refinados 0.497803–0.499583 y LOCAL=0.531066. Es un error estático tras eliminar sensores, NO un tiempo de regeneración. La mejora relativa en MSE de MHU frente a la media de tres CVT es aproximadamente 4.9 %, frente a LOCAL 10.7 %. No hay generadores MHU independientes en esta comparación y no certifica causalidad específica.
- [LARP native neighborhood, 09-10-2026](https://github.com/GalexY3/proyecto-LARP/blob/main/legacy/local_lab_20261022/LARP_NATIVE_NEIGHBORHOOD_AND_TRADEOFF_RESULTS.md): 18 ciclos de tres marcas admitidos y tres endpoints que no pueden alcanzarse mediante **dos intercambios admisibles** desde el estado nativo. La imposibilidad queda restringida a esas dos operaciones y reglas; no excluye trayectorias más largas ni demuestra aprendizaje neuronal. **Analogía útil**: movimientos colectivos admisibles que carecen de descomposición sencilla en movimientos individuales admisibles.
- [Avian Patterns Lab](https://github.com/GalexY3/avian-patterns-lab): controles geométricos reproducibles de empaquetamiento y supresión espectral finita; no es simulador de agentes cooperativos ni prueba asintótica de MHU.
- [Leibo et al. (2017), Sequential Social Dilemmas](https://discovery.ucl.ac.uk/id/eprint/10069053/): cooperatividad como propiedad de políticas secuenciales; no basta la elección o distribución final.

## 2. Diagnóstico de la aldea V12/V13

La función actual r_i=min(n_j/q,q/n_j), q=N/k, crea un óptimo colectivo de k roles de cuota q. Los agentes con parámetros independientes han mostrado transferencia parcial y, en algunos casos, repartos exactos. Esto demuestra **adaptación distributiva**, no por sí solo cooperación irreducible. Las redes sociales pueden facilitar una estrategia de imitación individual de vecinos que conduce a un buen macrorresultado.

Más pesos privados entre personas no prueban cooperación. Una mejor distribución de roles tampoco prueba dependencia causal de interacción: puede ser el agregado de políticas individuales independientes condicionadas por el mismo entorno. La MHU es otra propiedad (orden espacial multicomponente) y no debe reemplazar el test principal.

La aldea resulta aprovechable como **plataforma y calibrador**, pero su entrenamiento actual desde distribuciones aleatorias es poco identificador. Se recomienda cambiar a un protocolo centrado en **reparación de una trampa de coordinación**. No aumentar M, k, número de vecinos y complejidad neuronal simultáneamente en la prueba principal.

## 3. Ejemplo matemático de necesidad de acción colectiva

Para N=120, k=4, q=30, M≥4, iniciar dos profesiones con 60 trabajadores cada una. Todos reciben 0.5.

- Ningún habitante puede mejorar unilateralmente su ración en un paso manteniendo fijas las decisiones de los demás: pasar al grupo de 60 reduce la ración a 30/61; pasar a un grupo vacío produce 1/30.
- Una coalición de p trabajadores del mismo grupo que se traslade **simultáneamente a la misma profesión vacía** obtiene p/30 mientras p≤30, y quienes permanecen en el origen reciben 30/(60−p) si p≤30.
- Para que cada migrante mejore *estrictamente* su ración frente a 0.5: p/30>0.5, de donde **p≥16**. Con p=16, el origen queda con 44 trabajadores (ración 30/44≈0.682), la profesión naciente con 16 (ración 16/30≈0.533), y el otro grupo con 60 (ración 0.5). Todos los habitantes se mantienen o mejoran; los migrantes y quienes permanecen en el origen mejoran estrictamente.
- p=15 da a migrantes 0.5 (indiferencia) y mejora a quienes permanecen en origen. Es una mejora de Pareto **débil**, pero no una mejora estricta para todos los participantes. Declarar explícito el umbral utilizado en el protocolo.
- Estas desigualdades certifican el escenario **unilateralmente estable** en un paso y una intervención colectiva estrictamente beneficiosa para sus participantes. NO certifican que una política solitaria no pueda provocar respuestas futuras de terceros, ni que los agentes aprendan coaliciones espontáneamente.

Esta geometría de incentivos proporciona un criterio preexperimental y falsable. Elegir profesiones distintas para la migración impide crear un nuevo grupo viable: además de decidir emigrar, deben converger sobre un destino común sin conocer una etiqueta ganadora predefinida.

## 4. Propuesta de nuevo experimento principal, V14: «Rescate de una aldea atrapada»

Mantener la economía de la aldea, pesos neuronales separados, identidad de profesiones permutada entre mundos y decisiones simultáneas. Cambiar la distribución inicial: al menos una familia de condiciones con el estado 60/60 (N120,k4), y controles con estados más o menos alejados. Los individuos perciben únicamente alimento propio, vecinos y, si el tratamiento lo permite, señales voluntarias anteriores al movimiento. No introducir un coordinador que nombre profesión ni un oráculo con el destino correcto. Permitir memoria limitada y un canal de intención que no ejecuta ni impone acuerdos.

Medir recuperación material y coordinación, no solamente reparto final. Variable principal sugerida: probabilidad de formar una nueva profesión viable (al menos 16 migrantes de origen común, misma profesión y turno, con ración superior a la anterior) **sin empeorar a nadie**, y probabilidad de llegar después a cuatro profesiones de 30 trabajadores manteniendo ese estado durante 10 turnos. Una métrica secundaria es el área acumulada bajo la curva de alimento desde el choque; registrar reparto de beneficios y costes temporales de primeros migrantes.

Intervenciones necesarias:
1. Actores entrenados juntos con comunicación real.
2. Misma arquitectura y entrenamiento sin comunicación.
3. Mensajes emparejados pero rotos mediante replay, permutación o retardo, conservando frecuencias, costos y semillas donde sea posible.
4. Contrafactual «solo un actor puede cambiar» con compañeros inmóviles: verifica experimentalmente el límite unilateral de la tarea, no constituye por sí solo evidencia de aprendizaje.
5. Equipos recompuestos con compañeros desconocidos/políticas mezcladas y etiquetas de profesiones relabeladas.
6. Una política individual programada de imitación/gradiente de ración y políticas independientes sin acceso contingente a otros como controles fuertes. Comparar contra un planificador ORACLE únicamente como cota superior, nunca dotar de su información a los actores.

Informar probabilidades, intervalos sobre **semillas de entrenamiento**, variación de mundos y de grafo, y si las mejoras se conservan al quitar mensajes. El protocolo debe congelar endpoints, semillas y presupuesto y reservar un holdout NO inspeccionado para confirmación.

## 5. Criterio de cooperación frente a simple autoorganización

No llamar cooperación demostrada solo porque D_k cae, el bienestar aumenta o la influencia social sea estadísticamente significativa.

Se exige combinar una condición estructural (el estado inicial admite mejora mediante acciones conjuntas, pero no mediante desviación unilateral instantánea) con evidencia causal **en la política aprendida**: aparición sistemática de migraciones complementarias, dependencia del comportamiento real de compañeros frente a intervenciones de información y persistencia del beneficio sin una etiqueta universal ganadora.

En particular, abolir comunicación puede deteriorar una estrategia individual que imita vecinos; por ello la ablación de mensajes sola NO prueba cooperación fuerte. Se necesitan análisis contrafácticos de la contingencia: que un agente cambie sus decisiones según compromisos de otros, que esos otros ejecuten decisiones complementarias, y que la combinación de acciones aumente el bienestar cuando esas acciones aisladas fracasarían.

**Definición operativa propuesta**: «coordinación cooperativa aprendida» es la resolución repetida de trampas unilateralmente estables mediante decisiones simultáneas complementarias, contingentes a la interacción local, con mejoras sostenidas respecto a baselines independientes de igual información y recursos.

## 6. MHU de LARP como hipótesis secundaria de resiliencia

No entrenar con premio espectral en la primera prueba. Conservar como resultado secundario el espectro parcial por profesión y la varianza de recuentos en ventanas con baseline de barajado condicionado a ocupaciones. La necesidad de equipos por barrio podría aumentar segregación y producir un signo contrario a MHU.

Solo después de demostrar reparación cooperativa, diseñar un factorial espacial que compare configuraciones con **ocupaciones, red social, cobertura y costos emparejados**: distribución de marcas MHU construida, local-homogénea y barajada. Aplicar perturbaciones (por ejemplo incapacidad temporal del 20 % de los miembros o desconexión de parte de los enlaces) y medir tiempo y pérdida integral de comida hasta recuperación. MHU puede mejorar resiliencia por redundancia local, pero no debe asumirse un +20 % sin medirlo ni atribuir a aprendizaje de la propia sociedad una geometría generada externamente.

## 7. Decisión

**Mantener el simulador de aldea como plataforma; no usar el objetivo V13 de agrupación desde azar como prueba principal de cooperación.** Convertir el ensayo de migración colectiva desde trampas en el experimento principal y relegar la MHU a un eje secundario de resiliencia espacial. Éxito principal: coordinaciones causalmente necesarias, generalizables y medidas, con posibilidad explícita de resultado nulo.

En este documento **no se ejecutó V14 ni se verificó una ventaja temporal de recuperación del 20 % en LARP**.
