# V52 — Coaprendizaje de donaciones privadas y diferenciación profesional

Ocho sociedades formadas por48 actores,12 equipos K4 exógenos,4 profesiones libremente seleccionadas y3 vínculos simultáneos por persona. Cada individuo optimizó únicamente su propia comida mediante REINFORCE durante1500 actualizaciones; se aprendieron simultáneamente donaciones (5 logits privados) y elección de profesión (MLP privada). El brazo SCRATCH arranca con ambos componentes aleatorios. El brazo PRIOR inicializa solo la política de regalo con una estrategia cooperativa LOLA20 aprendida previamente en V47, y **permite que siga actualizándose**. Sin cuotas, contratos, castigos programados ni recompensa grupal. El juego material corresponde a V51.

## Evaluación final preregistrada con seis semillas nuevas

| Modelo | Estado inicial | Comida | Equipos 4 oficios al final | Donaciones por vínculo | Recibe 3 tipos | Efecto causal regalar | Personas positivas | Comida respecto V51 congelado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v52_SCRATCH_D3111_R7111 | monolith | 0.2632 | 0.9988 | 0.1451 | 0.0042 | -0.0223 | 7/48 | — |
| v52_SCRATCH_D3111_R7111 | random | 0.2636 | 0.9994 | 0.1460 | 0.0041 | -0.0261 | 4/48 | — |
| v52_SCRATCH_D3111_R8111 | monolith | 0.2625 | 0.9994 | 0.1435 | 0.0041 | -0.0205 | 5/48 | — |
| v52_SCRATCH_D3111_R8111 | random | 0.2629 | 0.9994 | 0.1446 | 0.0039 | -0.0234 | 3/48 | — |
| v52_SCRATCH_D4111_R7111 | monolith | 0.2627 | 0.9983 | 0.1440 | 0.0041 | -0.0218 | 5/48 | — |
| v52_SCRATCH_D4111_R7111 | random | 0.2631 | 0.9988 | 0.1449 | 0.0040 | -0.0261 | 5/48 | — |
| v52_SCRATCH_D4111_R8111 | monolith | 0.2625 | 0.9983 | 0.1436 | 0.0040 | -0.0204 | 5/48 | — |
| v52_SCRATCH_D4111_R8111 | random | 0.2628 | 0.9994 | 0.1444 | 0.0039 | -0.0232 | 3/48 | — |
| v52_PRIOR_D3111_R7111 | monolith | 0.8794 | 1.0000 | 0.9997 | 0.9990 | 0.3596 | 48/48 | 0.0046 |
| v52_PRIOR_D3111_R7111 | random | 0.8792 | 1.0000 | 0.9996 | 0.9986 | 0.3722 | 48/48 | 0.0047 |
| v52_PRIOR_D3111_R8111 | monolith | 0.8794 | 1.0000 | 0.9997 | 0.9992 | 0.3458 | 48/48 | 0.0046 |
| v52_PRIOR_D3111_R8111 | random | 0.8793 | 1.0000 | 0.9996 | 0.9988 | 0.3794 | 48/48 | 0.0048 |
| v52_PRIOR_D4111_R7111 | monolith | 0.8794 | 1.0000 | 0.9997 | 0.9991 | 0.3556 | 48/48 | 0.0046 |
| v52_PRIOR_D4111_R7111 | random | 0.8792 | 1.0000 | 0.9996 | 0.9986 | 0.3774 | 48/48 | 0.0046 |
| v52_PRIOR_D4111_R8111 | monolith | 0.8794 | 1.0000 | 0.9997 | 0.9991 | 0.3650 | 48/48 | 0.0045 |
| v52_PRIOR_D4111_R8111 | random | 0.8793 | 1.0000 | 0.9996 | 0.9989 | 0.3790 | 48/48 | 0.0048 |

La condición SCRATCH aprende una estructura ocupacional complementaria, pero la tasa de donación colapsa durante el entrenamiento hasta ~14–15% por vínculo y el incentivo causal de regalar suele ser negativo. **En este modelo el balance ocupacional terminal no es evidencia suficiente de cooperación materialmente sostenible.** Las cuatro condiciones PRIOR conservan cooperación y especialización casi completas y un incentivo causal positivo en48/48 individuos; ello depende de un donante entrenado antes con inferencia exacta del aprendizaje de la contraparte.

## Hipótesis registradas antes de entrenar

| Criterio | Resultado |
| --- | --- |
| h52a_any_scratch_joint_emergence | no cumple |
| h52b_prior_stability_at_least_3of4 | cumple |
| h52c_prior_vs_v51_frozen_within_0_05 | cumple |
| h52d_causal_positive_if_any_cooperation | cumple |

H52a exige que alguna de cuatro sociedades SCRATCH alcance simultáneamente alimento≥0,55,≥50% de equipos completos al final y≥0,50 donaciones por enlace. H52b exige los mismos umbrales en3/4 PRIOR. H52c compara alimento con las políticas de rol V51 congelando los regalos, con tolerancia−0,05 en al menos3/4 pares. H52d comprueba retorno causal positivo de regalar en al menos24/48 personas si hay una sociedad que cumpla los umbrales cooperativos.

## Interpretación sociológica

[Inferencia] La especialización de tareas aparece más fácilmente que la cooperación que permite obtener de ella beneficios materiales; la adaptación individual simultánea erosiona el intercambio cuando no existe un mecanismo de anticipación estratégica. Las primeras contribuciones pueden facilitar la aparición de una distribución laboral que luego persiste incluso cuando se reduce el intercambio. La diferencia PRIOR–SCRATCH indica dependencia de la historia de aprendizaje (trayectoria), no una prueba de que la cooperación solo pueda surgir mediante LOLA.

Las cliques de cuatro, los roles de especialidad y las recompensas fueron establecidos por el diseñador. No se ha probado apertura demográfica, cambio de compañero en V52, institución pública emergente ni existencia de una población autoorganizada de120 personas.

## Reproducción

Preregistro V52, motor conjunto, auditor frozen y test de intervención privada,8 checkpoints de pesos/Adam, histories y evaluaciones causales por semilla, CSV/JSON final y SHA256:
PREREG_V52_JOINT_ENDOGENOUS.md: c98295e0906fc082d2e517dcb46e6df2a83c051f808becead625e174a8619fb1
v52_joint_roles_gifts.py: d45e4703a90c8a702cd03e246e46a3cd2c6f74ef5d599a89e22c75ad822cbb1b
v52_frozen_audits.py: d65b8e0bfaab59d7d8e56811253dc019bb919bee302acd1d288c47676a89eccc
test_v52_joint_roles_gifts.py: 3e24c94b8d2488aaff0d24ca526f2578ff3781263496447781e51c072bd13c77
test_v52_frozen_audits.py: 873ea0c12377f41e4c49c109ad110f196dc719f1a88de2740295d1631d0e4f11
v52_summarize.py: d03e4fafa18fac2124f972e9f95daee14ce905cc423c9b295bcdd7151ce80e66