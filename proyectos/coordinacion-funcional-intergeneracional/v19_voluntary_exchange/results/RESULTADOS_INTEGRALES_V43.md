# V43 — Horizonte incierto y reloj oculto en donaciones privadas sin contrato

Diseño factorial preregistrado 13/11/2026 con cuatro condiciones por dos inicializaciones neuronales originales. Todos los agentes N48/k4/anillo grado6 proceden de sus propios checkpoints V30 contractuales y optimizadores Adam; 1000 nuevas actualizaciones sin ejecución de contrato, con recompensas alimentarias individuales únicamente. Dos factores: horizonte fijo de48 rondas frente a supervivencia por mundo q0,98 (máximo48), y observación del avance de tiempo frente a reloj oculto. No se introduce profesor, norma de castigo ni cooperación como objetivo.

## Trayectorias completas y prueba final fuera de muestra

| Modelo | Duración | Reloj | Comida u1 | u200 | u400 | u600 | u800 | u1000 | Donaciones finales | Rondas vivas |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v43_FIX_CLOCK_s3111 | fixed | visible | 0.4807 | 0.2277 | 0.2019 | 0.2008 | 0.2004 | 0.2003 | 0.0037 | 48.0000 |
| v43_FIX_HIDDEN_s3111 | fixed | hidden | 0.4814 | 0.2083 | 0.2014 | 0.2007 | 0.2004 | 0.2003 | 0.0037 | 48.0000 |
| v43_HAZ_CLOCK_s3111 | hazard | visible | 0.4809 | 0.4389 | 0.2687 | 0.2344 | 0.2322 | 0.2278 | 0.2676 | 33.3056 |
| v43_HAZ_HIDDEN_s3111 | hazard | hidden | 0.4812 | 0.3894 | 0.2491 | 0.2301 | 0.2270 | 0.2249 | 0.2459 | 33.3056 |
| v43_FIX_CLOCK_s4111 | fixed | visible | 0.4785 | 0.2491 | 0.2021 | 0.2009 | 0.2005 | 0.2003 | 0.0041 | 48.0000 |
| v43_FIX_HIDDEN_s4111 | fixed | hidden | 0.4786 | 0.2118 | 0.2016 | 0.2008 | 0.2004 | 0.2003 | 0.0040 | 48.0000 |
| v43_HAZ_CLOCK_s4111 | hazard | visible | 0.4791 | 0.4325 | 0.2852 | 0.2338 | 0.2320 | 0.2293 | 0.2582 | 33.3056 |
| v43_HAZ_HIDDEN_s4111 | hazard | hidden | 0.4794 | 0.3851 | 0.2546 | 0.2324 | 0.2272 | 0.2242 | 0.2469 | 33.3056 |

Las métricas de alimento y donaciones en la condición HAZARD se calculan **por agente-ronda vivo**. Los mundos muertos dejan de aportar recompensas o gradientes. El valor de desarrollo se evalúa a coste0,04 con políticas congeladas y seis semillas ambientales nuevas. La longitud media observada depende de q y del truncamiento48; no compararla con48 como si fuera idéntica experiencia.

## Retorno propio descontado de una donación inicial y controles laborales

| Modelo | Comida | Causal privado | Inmediato | Futuro | Agentes positivos | Causal red reconectada | Positivos reconectados | Ventaja roles vs azar |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v43_FIX_CLOCK_s3111 | 0.2003 | -0.0406 | -0.0400 | -0.0006 | 0/48 | -0.0397 | 0/48 | +0.0004 |
| v43_FIX_HIDDEN_s3111 | 0.2003 | -0.0401 | -0.0400 | -0.0001 | 0/48 | -0.0401 | 0/48 | +0.0004 |
| v43_HAZ_CLOCK_s3111 | 0.2278 | -0.0733 | -0.0400 | -0.0333 | 0/48 | -0.0743 | 0/48 | +0.0052 |
| v43_HAZ_HIDDEN_s3111 | 0.2249 | -0.0657 | -0.0400 | -0.0257 | 0/48 | -0.0593 | 0/48 | +0.0043 |
| v43_FIX_CLOCK_s4111 | 0.2003 | -0.0401 | -0.0400 | -0.0001 | 0/48 | -0.0397 | 0/48 | +0.0004 |
| v43_FIX_HIDDEN_s4111 | 0.2003 | -0.0401 | -0.0400 | -0.0001 | 0/48 | -0.0398 | 0/48 | +0.0004 |
| v43_HAZ_CLOCK_s4111 | 0.2293 | -0.0857 | -0.0400 | -0.0457 | 0/48 | -0.0861 | 0/48 | +0.0055 |
| v43_HAZ_HIDDEN_s4111 | 0.2242 | -0.0666 | -0.0400 | -0.0266 | 0/48 | -0.0651 | 0/48 | +0.0040 |

La auditoría fuerza solo el primer regalo de un individuo frente a prohibirlo, manteniendo las demás políticas libres, seis semillas ambientales y seis mundos por semilla, intervención sobre las48 personas de cada mundo. **No se computa un contrato escondido**. Se empareja la terminación aleatoria de cada mundo por medio de un generador dedicado y semilla ambiental, con un mismo calendario de muerte dentro de cada par contrafactual; consultar AMENDMENT_V43_SURVIVAL_RNG.md. El efecto inicial equivale a−c, y el resultado futuro evalúa si las reacciones sociales compensan ese coste.

## Comparación factorial

| Diferencia | Semilla neuronal | Δ alimento | Δ retorno causal | Δ regalos | Δ rondas vivas |
| --- | --- | --- | --- | --- | --- |
| fixed_hidden_minus_visible | 3111 | +0.0000 | +0.0005 | +0.0000 | +0.0000 |
| hazard_hidden_minus_visible | 3111 | -0.0029 | +0.0076 | -0.0217 | +0.0000 |
| CLOCK_hazard_minus_fixed | 3111 | +0.0275 | -0.0327 | +0.2639 | -14.6944 |
| HIDDEN_hazard_minus_fixed | 3111 | +0.0247 | -0.0256 | +0.2422 | -14.6944 |
| fixed_hidden_minus_visible | 4111 | -0.0000 | -0.0000 | -0.0001 | +0.0000 |
| hazard_hidden_minus_visible | 4111 | -0.0051 | +0.0191 | -0.0113 | +0.0000 |
| CLOCK_hazard_minus_fixed | 4111 | +0.0290 | -0.0456 | +0.2541 | -14.6944 |
| HIDDEN_hazard_minus_fixed | 4111 | +0.0239 | -0.0265 | +0.2429 | -14.6944 |

Las comparaciones reloj visible/oculto dentro de cada tipo de horizonte son las más controladas. El contraste HAZARD vs FIX también cambia la cantidad media efectiva de experiencia por episodio y la distribución de recompensas futuras. La introducción de q afecta a toda la sociedad simultáneamente, no a la supervivencia individual, y un límite de48 rondas permanece programado.

## Hipótesis preregistradas

| Hipótesis | Resultado |
| --- | --- |
| h43a | no cumple |
| h43b | no cumple |
| h43c | no cumple |
| h43d | no aplicable |
| h43d_applicable | no cumple |

H43a exige al menos un modelo HAZARD_HIDDEN con retorno privado causal>0 y al menos24/48 personas positivas. H43b exige ventaja del reloj oculto en HAZARD≥0,025 en ambas semillas. H43c exige ventaja del reloj oculto en FIX≥0,015 en alguna semilla. H43d solo se aplica si H43a se logró: requiere transferencia a red reconectada y ventaja sobre las tres tasas de movilidad profesional aleatoria.

## Resultados válidos y límites

[Inferencia] Las diferencias entre duración y acceso a un reloj pueden modificar la exploración, el valor descontado de encuentros futuros y los incentivos aprendidos, pero conservar alimento positivo no es prueba de cooperación autoestable si la contribución forzada tiene efecto privado negativo. Se separan resultados de entrenamiento, resultados congelados fuera de muestra y retorno contrafactual individual.

Se conserva la desigualdad de relaciones potenciales entre cuatro profesiones, el vector de confianza privado heredado de versiones anteriores y un mecanismo material unilateral preprogramado; no existe evidencia de invención institucional autónoma. Solo dos semillas neuronales por brazo y seis ambientales para cada checkpoint. Esta campaña no sustituye una prueba de reproducción intergeneracional bajo juego unilateral.

## Código, enmienda y reproducción

Preregistro V43, código de entrenamiento y test de paridad FIX_CLOCK, enmienda de generador separado para supervivencia en la evaluación, código auditor v43_frozen_audits.py, test_v43_audit.py y checkpoints con pesos/Adam por cada modelo. Auditorías originales results/v43_holdout_*.json y results/v43_causal_*.json; CSV, curvas históricas y métricas resumidas.
SHA256:
PREREG_V43_RANDOM_HORIZON.md: d6c5cbda09e441e6ca9354523eab2cd758145f97ceb94feaac7595ad822fcd22
AMENDMENT_V43_SURVIVAL_RNG.md: 21d663a437639ed1ceb08d6e4bc56f8cea2261b18edbad6d42b0e341182d4775
v43_random_horizon.py: b05c09010b9b288579de3220c14d43bbb4ddb208d11908f7ab448060fa7eb0eb
v43_frozen_audits.py: 85028b9b6efac34acb79834399c0c984f566358cd60537908c4e83020ab1c4fd
v43_summarize.py: 73074854a5843eb39db4018ff1cc8d07d9e7b9ea07ff88011f8fe92707a1b306
test_v43_horizon.py: 553f032475582fa4fe363773e432912fea350043e7c69f8efa8ec42a87daa3a6
test_v43_audit.py: d0fcfbc8856fb09caf900bc7b62e200bfc002f9a000d69612199d869abf8afd2