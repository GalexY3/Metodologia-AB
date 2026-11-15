# Fe de erratas V197: ley de desempate de los evaluadores V195–V196 de votación

15/11/2026. Auditoría posterior; ningún nuevo entrenamiento. Los originales se conservan íntegros. No afecta V195 neuronal `WITHDRAW_COUNTERFACTUAL`, que utiliza argmax sin ese jitter y tiene su propia auditoría.

Los entrenadores de votación eligen `argmax(Q + U[0,1e-12])` con un ruido independiente por acción. Los evaluadores V195A/V196 trataban todo margen de magnitud<=1e−12como un empate de probabilidad1/2. Para un margen d=(Q_yes−Q_no)/1e−12la probabilidad continua correcta es0si d<=−1; `(1+d)^2/2` si −1<d<0; `1−(1−d)^2/2` si0<=d<1;1si d>=1. Por ejemplo d=.5produce.875, no.5. La derivación es la CDF de la diferencia de dos uniformes, no una nueva ley científica.

Se revisaron72arrays de políticas guardadas,645120entradas de estado contadas entre arrays, incluyendo controles repetidos.30arrays presentan discrepancias numéricas en alguna entrada. No son645120réplicas. La diferencia de probabilidad por acción puede acercarse a.5, pero la corrección máxima del bienestar medio entre las72políticas es 0.0001011664. Se reconstruye la evaluación antigua con error máximo1.11e-16. La fórmula continua no pretende reproducir cada redondeo de coma flotante del generador.

| k | Regla | Valor inicial corregido | Final sin pulso epsilon.08 | Retención corregida |
|---:|---|---:|---:|---:|
|4|UNANIMITY|0.22257500|0.04971500|22.336%|
|4|MAJORITY|0.26727250|0.19616750|73.396%|
|8|UNANIMITY|0.18041309|0.00535076|2.966%|
|8|MAJORITY|0.40066649|0.25423566|63.453%|
|12|UNANIMITY|0.14029699|0.00035398|0.252%|
|12|MAJORITY|0.44651890|0.29588100|66.264%|

La conclusión principal V196 permanece:0/6alcanza75%de retención. Los seis intervalos bootstrap pareados del beneficio de mantener el pulso siguen siendo positivos al recalcularlos con32mundos y10000remuestreos. Son nuevos remuestreos, por lo que sus últimos decimales no tienen por qué coincidir con los previos. Los puntos intermedios de V196 no se recalculan: las Q de esos instantes no quedaron guardadas. Se corrigen los extremos para los que sí existen pesos. La expresión anterior «valor exacto» debe entenderse respecto a la aproximación de empate usada; esta fe de erratas la reemplaza para esos extremos.

El efecto pequeño no excusa mantener una ley de selección incorrecta. Tampoco acredita originalidad, confirmación externa o aumento de61. Fuentes, Q, JSON y reporte previos permanecen como historial; la referencia corregida es `V197_TIE_POLICY_AUDIT.json`.
