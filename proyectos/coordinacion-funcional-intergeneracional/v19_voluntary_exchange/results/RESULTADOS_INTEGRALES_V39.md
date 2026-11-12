# V39 — Dependencia de políticas cooperativas respecto a las reglas de liquidación contractual

Campaña preregistrada 12/11/2026 sin reentrenamiento. Seis checkpoints neuronales: dos V30 de48 personas con precio0,04 y cuatro V31 de120 personas, dos a precio0,04 y dos a0,12. Todas las políticas de propuestas dirigidas y cambio de profesión se congelan. Seis semillas ambientales por checkpoint y12 u8 mundos por semilla, emparejados. En rondas1–24 las intervenciones son idénticas al control; en rondas25–32 se cambia temporalmente la regla contractual o se bloquean entregas; en rondas33–48 se restaura, salvo el comparador de unilateralidad permanente.

## Efecto de retirar la garantía contractual en rondas25–32

| Modelo | Precio | Contratos normales | Cierre del mercado | Donaciones unilaterales | Δ cierre | Δ unilateral | Excedente restaurado |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v30_MUTUAL_C04_s3111 | 0.04 | 0.3446 | 0.2000 | 0.4820 | -0.1446 | +0.1374 | 100.0% |
| v30_MUTUAL_C04_s4111 | 0.04 | 0.3445 | 0.2000 | 0.4788 | -0.1446 | +0.1343 | 100.0% |
| v31_N120_MUTUAL_C04_s3111 | 0.04 | 0.3429 | 0.2000 | 0.4819 | -0.1429 | +0.1390 | 100.0% |
| v31_N120_MUTUAL_C04_s4111 | 0.04 | 0.3437 | 0.2000 | 0.4852 | -0.1438 | +0.1415 | 100.0% |
| v31_N120_MUTUAL_C12_s3111 | 0.12 | 0.2533 | 0.2000 | 0.2475 | -0.0533 | -0.0058 | 99.9% |
| v31_N120_MUTUAL_C12_s4111 | 0.12 | 0.2543 | 0.2000 | 0.2496 | -0.0543 | -0.0047 | 100.0% |

Importante: la intervención UNILATERAL8 ejecuta **todas las propuestas** de las redes originalmente entrenadas bajo contratos. No obliga a los agentes a volver a aprender un juego de donaciones unilaterales, ni demuestra que mantendrían ese volumen de contribuciones a largo plazo ante incentivos personales negativos. El efecto de reemplazar una regla de liquidación es diferente del efecto de capacitar un actor en esa regla.

## Recuperación y transferencia de políticas congeladas

| Modelo | Comida final control | Restaurada tras cierre | Restaurada tras unilateral8 | Unilateral permanente | Entregas normales/pers. | Entregas unilaterales/pers. |
| --- | --- | --- | --- | --- | --- | --- |
| v30_MUTUAL_C04_s3111 | 0.3456 | 0.3456 | 0.3456 | 0.4808 | 1.0975 | 2.9789 |
| v30_MUTUAL_C04_s4111 | 0.3448 | 0.3448 | 0.3447 | 0.4800 | 1.0995 | 2.9797 |
| v31_N120_MUTUAL_C04_s3111 | 0.3438 | 0.3437 | 0.3438 | 0.4791 | 1.0887 | 2.9771 |
| v31_N120_MUTUAL_C04_s4111 | 0.3442 | 0.3442 | 0.3442 | 0.4845 | 1.0924 | 2.9759 |
| v31_N120_MUTUAL_C12_s3111 | 0.2539 | 0.2538 | 0.2539 | 0.2462 | 1.0357 | 2.9101 |
| v31_N120_MUTUAL_C12_s4111 | 0.2542 | 0.2542 | 0.2542 | 0.2488 | 1.0439 | 2.9158 |

Las cifras de propuestas distinguen intención de intercambio y transferencia efectivamente liquidada. En el brazo unilateral pueden ejecutarse más unidades que bajo consentimiento bilateral, elevando también el coste privado por unidad enviada; si mejora el alimento poblacional ello no implica que la estrategia sea estable o que cada donante se beneficie de su contribución marginal. La prueba de contrato y no contrato deja constantes redes, roles, costos y recompensas individuales pero altera el procedimiento de entrega.

## Falsadores preregistrados

| Hipótesis | Resultado |
| --- | --- |
| h39a | FALSADO |
| h39b | NO EVALUABLE: umbral inalcanzable para coste 0,12 |
| h39c | CUMPLIDO |

H39a predecía que quitar el consentimiento recíproco reduciría≥0,03 la alimentación durante la intervención unilateral en≥4/6 modelos y quedó falsada. H39b exigía reducir≥0,10 en6/6 modelos; sin embargo, fue **mal calibrada**: los modelos de coste0,12 solo disponían de aproximadamente0,053 de excedente sobre0,20. La caída≥0,10 es materialmente imposible al cerrar el mercado en esos dos modelos. La validez inferencial de H39b queda INVALIDADA sin alterar retrospectivamente su umbral; se mantiene el resultado numérico literal y el test mecánico de0 entregas. Véase NOTA_CALIDAD_V39_H39B.md. H39c predecía conservar≥90% al restaurar la liquidación, y se observó en6/6.

## Validez, incertidumbre y límites

Este diseño separa dependencia de política y dependencia de regla institucional, pero no reemplaza un experimento de aprendizaje endógeno sin contratos. Las seis semillas ambientales condicionadas a cada checkpoint son pares de prueba, no seis inicializaciones de entrenamiento distintas. Los intervalos bootstrap descriptivos se calculan por semilla ambiental, no por mundo ni individuo. La regla de contrato sigue programada por el diseñador.

RQ1 queda abordada para **políticas congeladas entrenadas bajo contrato**. RQ2, surgimiento de reciprocidad no contractual individualmente estable, continúa abierta. Tampoco se identifica invención de normas ni equilibrio perfecto en subjuegos. No declarar OBJETIVO COMPLETADO.

## Datos y procedencia

Preregistro PREREG_V39_CONTRACT_REMOVAL.md. Evaluador v39_contract_outage.py, tests test_v39_outage.py, por semilla y ronda results/v39_contract_outage_v30_*.json y results/v39_contract_outage_v31_*.json, CSV COMPARACION_V39.csv. Código y preregistro SHA256:
PREREG_V39_CONTRACT_REMOVAL.md: 29e51eb1fc8411e65c53abc0eef153c545ad352a9959dba7a30e08da619a38bf
v39_contract_outage.py: a32ceb48e2d30bf3729369022519045928f844797213c1845a0cbaedae6339e5
v39_summarize.py: 467ce191ddf839745d7203386b28efa4ff231e560e5556b2c7fab2513eaf81d8
test_v39_outage.py: 938d0e519767980eb86d88ae1f62059b796107841b5c3e6593cdd8e5b26aeb64
NOTA_CALIDAD_V39_H39B.md: 09a4e1bbd2d7e8eb947e95d9b4d98c1f49629f05d49c565310b9dd775ac5aefb