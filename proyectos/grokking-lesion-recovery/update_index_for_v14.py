"""Update portable index without altering historical experimental evidence."""
from pathlib import Path
ROOT=Path(__file__).resolve().parent
README=ROOT/"README.md"
raw=README.read_text(encoding="utf-8")
marker="## V13–V14B — Dosis y control del estado del optimizador"
if marker not in raw:
 raw += """
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
"""
 README.write_text(raw.replace("\r\n","\n"),encoding="utf-8")
print("README_UPDATED",len(raw),flush=True)
