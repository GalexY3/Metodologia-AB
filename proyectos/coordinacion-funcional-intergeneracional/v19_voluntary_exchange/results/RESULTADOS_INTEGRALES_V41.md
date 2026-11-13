# V41. Persistencia de cooperación unilateral tras retirar definitivamente el contrato

Ocho ramas de continuación de redes previamente entrenadas a N48/k4/anillo de seis vecinos, dos semillas neuronales por fuente institucional. Los orígenes difieren: V30/c0,04/700 actualizaciones bajo contratos; V29-L/c0,04/850 actualizaciones bajo dones unilaterales y currículo distinto. Cada fuente se bifurcó en historial social visible o suprimido. Los ocho modelos continuaron durante1000 actualizaciones a coste fijo c0,04, aprendiendo solo por alimento individual y bajo entregas unilaterales, sin liquidación bilateral, sin profesor ni recompensa grupal.

## Trayectoria y estado congelado al final de 1000 nuevas actualizaciones

| Modelo | Entrenamiento previo | Historia social | Comida u1 | u200 | u400 | u600 | u800 | u1000 | Dones u1 | Dones u1000 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v41_C_s3111_SOC | contract | sí | 0.4807 | 0.2277 | 0.2019 | 0.2008 | 0.2004 | 0.2003 | 2.9753 | 0.0037 |
| v41_C_s3111_NOSOC | contract | no | 0.4864 | 0.2087 | 0.2016 | 0.2007 | 0.2004 | 0.2003 | 2.9541 | 0.0036 |
| v41_C_s4111_SOC | contract | sí | 0.4785 | 0.2491 | 0.2021 | 0.2009 | 0.2005 | 0.2003 | 2.9762 | 0.0041 |
| v41_C_s4111_NOSOC | contract | no | 0.4831 | 0.2084 | 0.2016 | 0.2008 | 0.2004 | 0.2003 | 2.9498 | 0.0037 |
| v41_U_s3111_SOC | unilateral | sí | 0.2027 | 0.2012 | 0.2007 | 0.2004 | 0.2002 | 0.2002 | 0.0225 | 0.0031 |
| v41_U_s3111_NOSOC | unilateral | no | 0.2027 | 0.2012 | 0.2007 | 0.2004 | 0.2002 | 0.2002 | 0.0226 | 0.0031 |
| v41_U_s4111_SOC | unilateral | sí | 0.2020 | 0.2010 | 0.2006 | 0.2003 | 0.2002 | 0.2001 | 0.0182 | 0.0031 |
| v41_U_s4111_NOSOC | unilateral | no | 0.2020 | 0.2009 | 0.2006 | 0.2003 | 0.2002 | 0.2001 | 0.0182 | 0.0030 |

La población que había aprendido a contratar empezó regalando mucho más que la población acostumbrada a unilateralidad; esta conducta no se considerará cooperación robusta a menos que sostenga un retorno privado causal positivo después de reentrenarse en el nuevo régimen. Las trayectorias completas están incluidas en METRICAS_V41.json.

## Beneficio privado causal descontado y controles fuera de muestra

| Modelo | Alimento | Donaciones/pers. | Mejor rol aleatorio | Ventaja laboral | Causal total | Inmediato | Futuro | Positivos | Causal reconectado | Positivos reconectado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v41_C_s3111_SOC | 0.2003 | 0.0037 | 0.1999 | +0.0004 | -0.0406 | -0.0400 | -0.0006 | 0/48 | -0.0397 | 0/48 |
| v41_C_s3111_NOSOC | 0.2003 | 0.0036 | 0.1999 | +0.0004 | -0.0400 | -0.0400 | +0.0000 | 0/48 | -0.0398 | 0/48 |
| v41_C_s4111_SOC | 0.2003 | 0.0041 | 0.1999 | +0.0004 | -0.0401 | -0.0400 | -0.0001 | 0/48 | -0.0397 | 0/48 |
| v41_C_s4111_NOSOC | 0.2003 | 0.0037 | 0.1999 | +0.0004 | -0.0399 | -0.0400 | +0.0001 | 0/48 | -0.0399 | 0/48 |
| v41_U_s3111_SOC | 0.2002 | 0.0031 | 0.1996 | +0.0006 | -0.0400 | -0.0400 | -0.0000 | 0/48 | -0.0399 | 0/48 |
| v41_U_s3111_NOSOC | 0.2002 | 0.0031 | 0.1996 | +0.0006 | -0.0401 | -0.0400 | -0.0001 | 0/48 | -0.0399 | 0/48 |
| v41_U_s4111_SOC | 0.2001 | 0.0031 | 0.1997 | +0.0005 | -0.0406 | -0.0400 | -0.0006 | 0/48 | -0.0399 | 0/48 |
| v41_U_s4111_NOSOC | 0.2001 | 0.0030 | 0.1997 | +0.0005 | -0.0400 | -0.0400 | -0.0000 | 0/48 | -0.0401 | 0/48 |

La auditoría fuerza una propuesta unilateral adicional frente a impedirla para cada uno de los48 individuos, con seis semillas ambientales independientes de los entrenamientos y políticas congeladas. El coste inmediato de forzar el regalo es -0,04 para quien contribuye. Solo una mejora posterior mayor que0,04 puede producir retorno privado total positivo. Los controles de profesiones aleatorias evalúan la misma política de donar y tres tasas predefinidas; en las ramas entrenadas sin historial social se usa evaluación sin esa información.

## Comparaciones pareadas por fuente, semilla y observación

| Diferencia | Semilla | Factor mantenido | Δ comida | Δ causal | Δ regalos |
| --- | --- | --- | --- | --- | --- |
| contract_history_minus_unilateral_history | 3111 | SOC | +0.0001 | -0.0006 | +0.0006 |
| contract_history_minus_unilateral_history | 3111 | NOSOC | +0.0001 | +0.0001 | +0.0005 |
| social_history_minus_no_social | 3111 | C | +0.0000 | -0.0006 | +0.0001 |
| social_history_minus_no_social | 3111 | U | +0.0000 | +0.0001 | +0.0000 |
| contract_history_minus_unilateral_history | 4111 | SOC | +0.0002 | +0.0005 | +0.0010 |
| contract_history_minus_unilateral_history | 4111 | NOSOC | +0.0001 | +0.0001 | +0.0007 |
| social_history_minus_no_social | 4111 | C | +0.0000 | -0.0002 | +0.0004 |
| social_history_minus_no_social | 4111 | U | +0.0000 | -0.0005 | +0.0000 |

No es un factorial plenamente identificado de formación institucional: el checkpoint unilateral V29 acumuló150 pasos más que V30 y siguió un currículo de costes diferente. Las comparaciones entre fuentes son exploratorias; las bifurcaciones de observación sí parten de los mismos pesos y estados originales de Adam. El cumplimiento literal de H41c solo depende del signo de diferencias de retorno minúsculas (entre aproximadamente -0,00060 y +0,00051) cuando los ocho modelos ya convergieron cerca de -0,040. **H41c es nominalmente positiva pero no refleja una mejora individualmente relevante ni cooperación estable.**

## Hipótesis preregistradas

| Hipótesis | Resultado |
| --- | --- |
| h41a_any_contract_24_of48_positive | no cumple |
| h41b_social_history_causal_gain_0025 | no cumple |
| h41c_contract_history_improves_in_2_of_4 | cumple |
| h41d_all_positive_models_transfer | no aplicable |
| h41d_applicable | no cumple |

H41d solo es aplicable si se alcanzó H41a; si no hay ningún modelo con retorno causal positivo para≥24 personas, informar «no aplicable», no interpretar una verdad vacía de programación como éxito experimental.

## Interpretación

[Inferencia] El entrenamiento continuo después de retirar las garantías contractuales permite examinar si las estrategias heredadas de una institución formal pueden adaptarse a relaciones de reciprocidad diferida sin liquidación automática. La alimentación social, por sí misma, no demuestra que contribuir sea una mejor respuesta privada; los controles causales son necesarios. La historia social puede modular la extinción de regalos sin resolver necesariamente su coste privado.

La evaluación no demuestra aparición autónoma de nuevas instituciones, ni constitución cultural de normas, ni cooperación en una población abierta: todas las políticas se aprendieron previamente dentro de una ecología simulada y solo se probaron dos semillas por fuente.

## Reproducción

Preregistro, entrenador v41_unilateral_adaptation.py, ocho optimizadores y checkpoints finales runs/v41_*, evaluaciones congeladas results/v30_holdout_v41_*.json y results/v30_causal_v41_*.json, CSV de modelos, CSV de contrastes, métricas e histogramas de individuos en METRICAS_V41.json.
SHA256:
PREREG_V41_POSTCONTRACT_RECIPROCITY.md: a972b055758e61228097d9c7abc740a87dd742049e6bf7523185de83be38c91c
v41_unilateral_adaptation.py: f5093c4eb1a47617cc468e09b9f73fc127dfd884f39c9b532216b78821b37d1b
v41_frozen_audits.py: b4595e13e484ad3161c038e870044aec0fc09ada6c978be66b77b2154f800b6d
v41_summarize.py: 8eb0d9f2b4940909ed8a30c62faa6da4f22bc18623bdcfde511959cf66d16c9e