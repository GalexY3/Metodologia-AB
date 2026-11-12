# V24 — Límite formal de factibilidad del abastecimiento con donaciones unitarias

Documento de resultados analíticos del 12/11/2026. Demostración extraída de la función step de targeted_gifts.py (V19–V24). Se aplica a esta familia de entornos de donaciones voluntarias dirigidas, no necesariamente a modelos anteriores con otras reglas ni a sociedades humanas.

## Notación y restricción física

N personas, k especialidades y una acción binaria por donante y ronda, dirigida a un único receptor. Cada persona puede emitir **como máximo un bien por ronda**. Denotemos G la cantidad total de regalos emitidos esa ronda, q=G/N la proporción de donantes, D_i el número de clases de bienes distintos de la propia profesión efectivamente recibidas por i, y F_i el indicador de abastecimiento completo (D_i=k-1).

Cada donación puede contribuir, como máximo, a una categoría nueva recibida por el receptor, por tanto sum_i D_i ≤ G. Como una persona abastecida completamente requiere k-1 categorías, sum_i F_i ≤ sum_i D_i/(k-1) ≤ G/(k-1). Inmediatamente

media(F_i) ≤ min(1,q/(k-1)).

Para k=4 y q≤1, nunca puede haber más de un tercio de población abastecida plenamente en una ronda. Este límite persiste aunque todas las redes neuronales sean óptimas, los enlaces favorables, las profesiones estén perfectamente distribuidas y exista reciprocidad plena.

## Cota exacta de recompensa superior por capacidad

La función de alimento por ronda es

r_i = 0,20 + 0,55 D_i/(k-1) + 0,25 F_i - c g_i - m_i,

con g_i∈{0,1}, coste unitario c≥0 y m_i≥0 coste adicional de movilidad ocupacional (en V22–V24, 0,015 cuando se cambia).

Promediando sobre individuos, usando las desigualdades anteriores y media(g_i)=q,

media(r_i) ≤ 0,20 + q[0,80/(k-1) − c].

Con c=0,12 y un único regalo máximo por donante:

| Profesiones k | Cota de población plenamente abastecida (q=1) | Máximo alimento medio teórico (q=1) | Margen máximo por regalo |
| --- | --- | --- | --- |
| 2 | 100 % | 0,880 | +0,680 |
| 3 | 50 % | 0,480 | +0,280 |
| 4 | 33,3 % | 0,347 | +0,147 |
| 5 | 25 % | 0,280 | +0,080 |
| 7 | 16,7 % | 0,213 | +0,013 |
| 8 | 14,3 % | 0,194 | −0,006 |

Para k≥8, cada regalo reduce necesariamente la **cota superior** de alimento medio frente al baseline 0,20. Como el régimen sin donaciones alcanza 0,20 sin costes de movilidad, no existe estrategia de regalos que produzca alimento medio por encima de ese baseline con estas reglas, aunque los agentes coordinen perfectamente. La evaluación k≥8 con este mecanismo tendría por objetivo distinguir estructuras y normas de contribución que soportan costes netos, no identificar un régimen cooperativo positivo-suma de alimento.

## Límite adicional del grado

Si la red tiene grado d y d<k-1, ningún receptor puede obtener bienes de k-1 profesiones diferentes en una sola ronda, pues carece de suficientes vecinos. En V24 k=4, d=6, esta restricción topológica no impide el abastecimiento completo; la limitación cuantitativa proviene de la capacidad de producción de una unidad por trabajador.

## Normalización propuesta

Para k=4 conviene reportar, junto a alimento, donaciones por persona, tasa de cobertura y pleno abastecimiento, la cantidad de regalos útiles respecto de todos los emitidos. Para G>0, eficiencia de entrega = [(k-1)×media(cobertura)]/q, que queda entre 0 y 1 en el sistema unitario. Un agente puede dejar de donar por el déficit de capacidad, aunque la estructura de oficios sea óptima. El indicador normalizado no sustituye al retorno causal individual.

No se deben comparar alimentaciones absolutas k=2 y k=4 sin ajustar su frontera de factibilidad. La comparación más exigente para V24 es cuánto se aproxima el modelo a su propio techo (0,347 menos costes adicionales), bajo el coste y capacidad establecidos.

## Intervención de seguimiento V25

Se propone aumentar la capacidad a k-1 regalos independientes por donante/ronda, manteniendo receptores y regalos elegidos mediante políticas neuronales privadas. En k=4 el límite de entregas pasa de N a 3N, y se vuelve físicamente viable que todos reciban los tres bienes complementarios. El escenario óptimo constructivo requiere dos condiciones diferentes: capacidades suficientes y distribución de entrega por profesiones. Una política scriptada solo sería benchmark/oráculo y no evidencia de aprendizaje.

Con capacidad 3 y coste 0,12 por regalo, el máximo teórico de alimento medio a abastecimiento completo es 0,20+0,55+0,25−0,36=0,64. Con coste alternativo 0,04 por regalo (igual presupuesto total de contribución 0,12 que k=2) el máximo es 0,88. Es una nueva familia de entornos y deberá contrastarse explícitamente con el caso unitario; no debe confundirse con una mejora del mismo problema manteniendo recursos constantes.

## Alcance de la demostración

La cota sigue siendo cierta con políticas estocásticas, heterogeneidad individual de pesos, cambio de roles y redes arbitrarias, siempre que cada regalo aporte a lo sumo una categoría nueva a un solo receptor en esa ronda, y que ninguna otra operación genere bienes. La inclusión de almacenes intertemporales, intercambios bilaterales que creen simultáneamente dos unidades, fabricación múltiple o transferencias de inventario altera el balance y requiere un teorema diferente.
