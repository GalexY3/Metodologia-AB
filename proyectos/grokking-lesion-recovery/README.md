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
