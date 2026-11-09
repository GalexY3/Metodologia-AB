# Grokking, lesiones y recuperación neuronal — laboratorio AB

## Objeto

Comparación computacional de redes que llegan al mismo nivel de precisión por trayectorias distintas y posterior respuesta a ablaciones neuronales permanentes. Proyecto experimental independiente dentro del repositorio metodológico AB.

**Estado epistemológico (09-11-2026): exploratorio, NO confirmatorio.**

La investigación pasó por pilotos semigrokking-parcial (V1–V8), una comparación de grokking de distintas latencias al 100% en suma modular (V9) y un contraste más próximo a la pregunta científica entre generalización tardía y rápida en paridad binaria (V10). No debe atribuirse causalidad al evento grokking únicamente por comparar dos condiciones que difieren en regularización L1.

## Resultado V10B (muestra de cinco semillas)

Se entrenaron cinco pares de redes MLP con 300 unidades ocultas para paridad de los tres primeros de 30 bits. Los modelos de ambas condiciones alcanzaron 100% de precisión sobre conjuntos finitos de entrenamiento, validación y prueba; las latencias de generalización difirieron. El contraste se generó con diferentes fuerzas de regularización L1, **un confusor causal directo importante**.

Se aplicaron 150 ensayos de ablación permanente, en tres dosis (30, 90, 150 neuronas), cinco máscaras emparejadas y cinco pares de redes. El grupo tardío resistió mejor las lesiones aleatorias y mostró menor déficit acumulado respecto a su control sin lesión, **pero también sufrió menor daño inmediato**. Por eso la evidencia disponible respalda una diferencia exploratoria de *robustez* entre estas condiciones, no una demostración causal de mejor *regeneración tras un daño equivalente*.

Lecciones verificadas, limitaciones, protocolos y métricas se conservan sin recalificar resultados exploratorios como confirmatorios.

## Puntos de entrada

- [CURRENT.md](CURRENT.md) — estado exacto y próximo contraste.
- [full_100/PREREG_V10B.md](full_100/PREREG_V10B.md) — diseño preespecificado antes de lesiones V10B.
- [full_100/V10_ELIGIBILITY.json](full_100/V10_ELIGIBILITY.json) — clasificación de las diez trayectorias.
- [full_100/V10_ANALYSIS.json](full_100/V10_ANALYSIS.json) — agregación y auditoría local de las 150 lesiones.
- [full_100/V10_LESION_RAW.json](full_100/V10_LESION_RAW.json) — observaciones por semilla, dosis y máscara.
- [full_100/V10_UNIT_MECHANISM.json](full_100/V10_UNIT_MECHANISM.json) — sondas de contribución funcional.
- [full_100/PREREG_V10C.md](full_100/PREREG_V10C.md) — protocolo de sensibilidad con daño igualado (ejecutado y auditado localmente; consultar REPORT_V10C.md).
- [REPORT_V7.md](REPORT_V7.md) y [full_100/V9_ANALYSIS.json](full_100/V9_ANALYSIS.json) — pilotos anteriores, incluidos resultados negativos.
- [ARCHIVE_MANIFEST.json](ARCHIVE_MANIFEST.json) — SHA-256 de archivos conservados y omitidos.

## Reproducción desde otro PC

En Windows PowerShell, tras clonar el repositorio o cambiar a la rama correspondiente, instalar Python con PyTorch y NumPy. Ejecutar desde el directorio de este proyecto:

```powershell
python -m pip install torch numpy
python full_100/classify_v10.py
python full_100/analyze_v10.py
python full_100/v10_unit_probe.py
```

Para una NUEVA semilla (por ejemplo seed 5), entrenar ambos brazos en la misma partición antes de calificar trayectorias:

```powershell
python full_100/parity_v10.py --ntrain 500 --seed 5 --l1 0.00001 --steps 8000
python full_100/parity_v10.py --ntrain 500 --seed 5 --l1 0.001 --steps 8000
```

Los entrenamientos originales generaron checkpoints `.pt`; se incluyen los finales para las diez redes V10B, seis V9 y seis V7. Se excluyen miles de snapshots intermedios, reproducibles desde el código y las semillas. La instantánea contiene todas las curvas CSV disponibles y los resultados JSON de ensayos de lesión, además de los protocolos y análisis.

**Nota**: la arquitectura de paridad comparte la capa oculta de 300 unidades entre ambos grupos; las unidades no deben interpretarse como neuronas biológicas. La generalización 100% fue comprobada únicamente sobre muestras finitas, no en las 2^30 entradas posibles.

## Gobernanza

La carpeta original del sobremesa permanece intacta en `C:\Programación\grokking_lesion_20261109`; esta copia se ubicó de forma aislada en `proyectos/grokking-lesion-recovery` sin modificar los demás proyectos de AB. No se ha adoptado un nuevo hallazgo confirmado, ni se ha demostrado superioridad del protocolo AB o la originalidad científica de la hipótesis.

## Nuevo resultado V10C: reparación tras igualar la gravedad inicial de la lesión

El estudio [V10C](full_100/REPORT_V10C.md) ya está completo. Se seleccionaron cinco máscaras nuevas por cada uno de los cinco pares de redes **antes** de entrenar la recuperación, obligando a que ambas redes perdieran entre 10 y 40 puntos de precisión y difiriesen <=5 puntos porcentuales en daño inicial. En 50 trayectorias de reconstrucción, la caída media inicial de validación fue A 23,808pp frente a B 23,768pp; la diferencia media de área de déficit A−B fue −8,614 en cinco unidades de replicación, con A favorable en 4 de 5 semillas. Se recuperaron al menos hasta el umbral de 99% 22/25 ensayos A y 17/25 B. Sigue siendo un resultado **exploratorio condicionado por la selección de daño**, con regularización L1 distinta entre grupos y baja coincidencia de ejemplos dañados (Jaccard promedio 0,183). No demuestra causalidad del grokking.

Archivos: [protocolo](full_100/PREREG_V10C.md), [informe](full_100/REPORT_V10C.md), [selección de máscaras](full_100/V10C_MASK_SCAN.json), [resultados individuales](full_100/V10C_MATCHED_RAW.json), [auditoría/análisis](full_100/V10C_MATCHED_ANALYSIS.json), [código de selección](full_100/v10c_scan.py), [código de reconstrucción](full_100/v10c_repair.py) y [análisis](full_100/analyze_v10c.py).

Para verificar los resultados guardados desde otro PC:

```powershell
python full_100/analyze_v10c.py
```

## V11 — control adversarial de la historia de grokking

[Informe V11](full_100/REPORT_V11.md), [protocolo](full_100/PREREG_V11.md), [robustez V11](full_100/V11_ROBUSTNESS.json) y [reparación V11C](full_100/V11C_ANALYSIS.json).

Tras 4.000 actualizaciones de entrenamiento **con el mismo λ L1=0.0001** y rendimiento 100% en ambas historias, la ventaja de resistencia inicial (A−B=−11.16pp) se redujo casi a cero (−0.48pp) ante 90/300 neuronas eliminadas. En reconstrucción manteniendo la misma L1, las cinco parejas no mostraron una ventaja reproducible: 2 semillas favorecen a A, 3 a B; diferencia media de AUC A−B=−3.48, prueba exploratoria de inversión de signos p=0.6875. La evidencia disponible no acredita que el grokking, separadamente de la regularización, mejore la reparación. Las máscaras no son replicaciones independientes de entrenamiento.

Se incluyen 10 checkpoints iniciales V10 paso5000 y los checkpoints V11 5000/7000/9000, así como las 200 curvas completas de reparación V11B/V11C. Los anteriores resultados positivos V10 permanecen documentados para comparación. No se ha demostrado equivalencia estadística ni una ausencia universal de dependencia de trayectoria.

## V12 — réplica en GALEXY_TRAVEL

El [informe científico V12](full_100/REPORT_V12.md) contiene dos gráficos, resultados completos y limitaciones. Se entrenaron diez pares nuevos sobre una partición independiente; cinco cumplieron todos los criterios de historia y capacidad antes de ser lesionados. La diferencia de robustez A−B disminuyó de −10,38 a −0,96 puntos porcentuales tras 4.000 actualizaciones finales con la misma L1=0,0001. La comparación posterior de reconstrucción con cien lesiones nuevas NO encontró una ventaja consistente del grupo tardío: dos de cinco semillas favorecieron a A y tres a B. Ni este resultado ni los pilotos previos identifican causalmente un efecto exclusivo del grokking.

Evidencias: [selección](full_100/V12_GATES.json), [robustez](full_100/V12_ROBUSTNESS.json), [reparación](full_100/V12B_ANALYSIS.json), [test reservado](full_100/V12_TEST_AUDIT.json), [prerregistro V12](full_100/PREREG_V12.md) y [prerregistro de lesiones](full_100/PREREG_V12B.md). La carpeta V12 mantiene los checkpoints y curvas para reproducir los análisis.

Para recomputar el análisis desde Windows, con Python y PyTorch/NumPy instalados, ejecutar full_100/v12_robustness.py, full_100/v12b_analysis.py y full_100/v12_make_report.py. Se puede verificar el manifiesto mediante SHA-256 byte a byte.

## V13–V14B — Dosis y control del estado del optimizador

La pregunta sigue siendo si dos redes que ya alcanzaron 100% accuracy en
datos evaluados, una con generalización tardía y otra más rápida, toleran
y compensan de modo distinto la pérdida permanente de neuronas. Los resultados
V10–V14B son **exploratorios** y no identifican causalidad aislada del grokking.

El [informe V13](full_100/REPORT_V13.md) compara 9 dosis (10–90%) y conserva
360 trayectorias de reparación en 5 parejas independientes de modelos. Al
destruir 80%, recuperan 5/20 A y 4/20 B; al destruir 90%, 0/20 A y 1/20 B
en 500 pasos. En la sensibilidad de [2.000 pasos V13B](full_100/REPORT_V13B.md),
con máscaras nuevas del 90%, recuperan 3/20 A y 4/20 B. Son resultados de
recuperabilidad **dentro de las condiciones y horizontes fijados**, no pruebas
de irreversibilidad absoluta.

El [informe V14/V14B](full_100/REPORT_V14.md) realiza controles adversariales
de mecanismo. Continuar 4.000 pasos después de alcanzar 100% con un nuevo
AdamW reduce la brecha de resistencia entre grupos desde -10,40 hasta aprox.
-1,18 pp **incluso conservando la misma L1 histórica**, con efectos parecidos
al igualarla o cruzarla. En cambio, **conservar los momentos originales de
AdamW** durante esa continuación mantiene una brecha de -8,76 pp. Las
correcciones metodológicas son centrales: no atribuir esa convergencia al
grokking, a cambiar L1 ni simplemente al tiempo de entrenamiento. El estado
del optimizador es una intervención crucial y falsable.

[PREREG_V15_OPTIMIZER_REPAIR.md](full_100/PREREG_V15_OPTIMIZER_REPAIR.md)
establece el experimento siguiente para comparar recuperaciones con exactamente
los mismos pesos y máscaras, conservando vs reiniciando AdamW. **En el momento
de esta actualización aún no está ejecutado.**

Evidencias V13: [auditoría y resultados](full_100/V13_ANALYSIS.json),
[protocolo](full_100/PREREG_V13_DOSE.md), datos en full_100/v13_dose_runs.
Evidencias V14:
[factorial](full_100/V14_ANALYSIS.json),
[continuidad temporal](full_100/V14_TEMPORAL_CONTROL.json),
[optimizador conservado](full_100/V14B_ANALYSIS.json).
El estado actualizado para otro PC está en [CURRENT.md](CURRENT.md).

La próxima simulación de coordinación funcional e intercambio de generaciones
se mantiene **en cola**, bajo
[coordinacion-funcional-intergeneracional/QUEUE.md](../coordinacion-funcional-intergeneracional/QUEUE.md).
No confundir la simulación propuesta con resultados ejecutados.
