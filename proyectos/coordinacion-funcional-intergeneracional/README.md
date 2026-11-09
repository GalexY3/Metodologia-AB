# Coordinación funcional distribuida y transmisión intergeneracional

**Estudio de simulación social artificial, no prueba causal de fenómenos humanos.** Código reproducible en Python 3.14 con NumPy. Proyecto derivado de una propuesta del usuario sobre N agentes que deben repartir k funciones aproximadamente en proporciones 1/k, con comunicación local, extrapolación a valores nuevos de k y relevo generacional. Contexto original en [QUEUE.md](QUEUE.md).

## Qué hay verificado

- **P0:** 10 pruebas automáticas aprobadas; población de 120 agentes, anillo de grado4, a lo sumo una conversación por agente/tick; formación de roles por observación de vecinos, no por censo global. Los agentes reciben funciones inicialmente desbalanceadas (70% en la misma). La heurística minoritaria manual consiguió equilibrio en k=2,3,4; la política entrenada con REINFORCE no estabilizó k=4 ni generalizó a k5..8. Ver [informe P0/P1](REPORT_P0_P1.md).
- **P1:** cambiar únicamente la representación de escasez local de `−frecuencia` a `−k×frecuencia` permitió que una política con ponderaciones aprendidas exclusivamente en k2..4 se transfiriera a k5: 10/10, k6: 6/10, k7: 3/10 y k8: 1/10 en un conjunto nuevo de diez semillas por k. El control P0 entrenado con la misma cohorte obtuvo 0/10 en los cuatro. **No se ha replicado aún entre distintas cohortes entrenadas**. La representación de escasez fue diseñada por nosotros, no descubierta espontáneamente.
- **G0:** desde comunidades ya estables, sustituir el 25/50/75% de individuos y comparar herencia inmediata de una regla explícita, ausencia de enseñanza y aprendizaje de esa regla por contacto. A k4 y sustitución de 50/75%, el control sin enseñanza recuperó 0/20, mientras la enseñanza local recuperó 20/20; con k5 y sustitución 50%, 0/17 frente a 11/17. Ver [informe G0](REPORT_G0.md). Esta etapa usa una **heurística programada**, no una estrategia aprendida autónomamente.

Los gráficos son originales y se generan a partir de los JSON auditados. No se han incorporado datos empíricos de personas. No se ha demostrado grokking colectivo.

## Ejecutar y verificar

Desde este directorio, con Python 3.14 y NumPy:

```powershell
py -3.14 -m unittest -v test_model.py
py -3.14 pilot_known.py
py -3.14 heldout_k.py
py -3.14 experiment_p1.py
py -3.14 turnover_v0.py
py -3.14 report_p1.py
py -3.14 report_turnover.py
```

**Importante:** los scripts de test virgen P0/P1 y G0 no sobrescriben una salida existente. Para reproducir íntegramente sin destruir datos históricos, ejecutar en una copia limpia del proyecto o usar un directorio temporal de experimento, conservando las mismas versiones. No borrar ni sustituir los archivos de evidencia existentes para «repetir» con los mismos nombres. Los datos están en `results_p0`, `results_p1`, `results_g0`; los test-locks registran hashes de código y políticas.

## Metodología y términos

La estabilidad requiere TV≤0,06, churn≤0,05 durante diez turnos al final del episodio. La población global se mide solo por el **evaluador**, no por los agentes; conocer k y observar un estado de vecino por contacto es suficiente para definir la acción local. El test zero-shot congela pesos, pero permite la actualización de memoria de observaciones. Las intervenciones de transmisión G0 conservan choque y población inicial exactamente iguales entre condiciones.

**Siguiente investigación:** replicar P1 con varias semillas independientes de entrenamiento y datos nuevos; después, implementar transmisión intergeneracional de una **política genuinamente aprendida** en vez de la heurística G0. Mantener separadas la comparación con grokking neuronal y la búsqueda aún no demostrada de transición tardía social. Estado detallado en [CURRENT.md](CURRENT.md).
