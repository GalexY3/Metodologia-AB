# V54 — Generalización de la especialización profesional de k=2 a k=12

## Alcance de la prueba

**32 entrenamientos neuronales** desde actores profesionales privados inicializados de cero (N120, exactamente igual en todos), con ocho k∈{2,3,4,5,6,8,10,12}, dos condiciones de dones preaprendidos (LOLA20 y NL) y dos semillas independientes (3111/7111 y4111/8111). Todos entrenan1400 actualizaciones, lote12, horizonte48, decisión ocupacional cada8 rondas, coste de cambio0,015 y recompensa exclusivamente alimentaria individual con REINFORCE, Adam0,003 y entropía0,01. Todos los actores ocupacionales tienen pesos diferentes por persona; **los regalos están congelados**, transferidos de los modelos V47 entrenados en 48 personas. Todos los agentes pueden elegir cualquiera de k profesiones. No existen cuotas ni recompensa por formar un grupo completo.

La topología es externa y favorable: **120/k grupos cliques Kk**, de tamaño y grado k−1. N es constante, pero la conectividad y el número de opciones cambian necesariamente con k. La MLP de ocupaciones contiene un vector de información de dimensión2k+3 y salida de k opciones; el presupuesto de parámetros neuronales no es idéntico entre k. Estos factores limitan la atribución del efecto exclusivamente al tamaño de k.

## Progreso de especialización y comida por k, inicio monolítico

| k | Donante semilla | Donante | Balance terminal | Alimento medio | Cesta completa | Ventaja sobre mejor aleatorio |
| --- | --- | --- | --- | --- | --- | --- |
| 2 | 3111 | LOLA20 | 1.0000 | 0.8768 | 0.9956 | 0.4106 |
| 2 | 4111 | LOLA20 | 1.0000 | 0.8770 | 0.9959 | 0.4108 |
| 2 | 3111 | NL | 0.9994 | 0.2010 | 0.0017 | 0.0009 |
| 2 | 4111 | NL | 0.9995 | 0.2010 | 0.0017 | 0.0009 |
| 3 | 3111 | LOLA20 | 1.0000 | 0.8758 | 0.9914 | 0.4500 |
| 3 | 4111 | LOLA20 | 1.0000 | 0.8758 | 0.9915 | 0.4528 |
| 3 | 3111 | NL | 0.8753 | 0.2005 | 0.0000 | 0.0005 |
| 3 | 4111 | NL | 0.7002 | 0.2004 | 0.0000 | 0.0004 |
| 4 | 3111 | LOLA20 | 1.0000 | 0.8743 | 0.9861 | 0.4708 |
| 4 | 4111 | LOLA20 | 1.0000 | 0.8748 | 0.9875 | 0.4695 |
| 4 | 3111 | NL | 0.3752 | 0.2004 | 0.0000 | 0.0004 |
| 4 | 4111 | NL | 0.3199 | 0.2004 | 0.0000 | 0.0004 |
| 5 | 3111 | LOLA20 | 1.0000 | 0.8733 | 0.9820 | 0.4759 |
| 5 | 4111 | LOLA20 | 1.0000 | 0.8735 | 0.9826 | 0.4764 |
| 5 | 3111 | NL | 0.0420 | 0.2004 | 0.0000 | 0.0004 |
| 5 | 4111 | NL | 0.0006 | 0.2004 | 0.0000 | 0.0004 |
| 6 | 3111 | LOLA20 | 1.0000 | 0.8720 | 0.9771 | 0.4753 |
| 6 | 4111 | LOLA20 | 1.0000 | 0.8728 | 0.9794 | 0.4754 |
| 6 | 3111 | NL | 0.0000 | 0.2004 | 0.0000 | 0.0003 |
| 6 | 4111 | NL | 0.0000 | 0.2004 | 0.0000 | 0.0003 |
| 8 | 3111 | LOLA20 | 1.0000 | 0.8701 | 0.9691 | 0.4745 |
| 8 | 4111 | LOLA20 | 1.0000 | 0.8704 | 0.9700 | 0.4747 |
| 8 | 3111 | NL | 0.0000 | 0.2003 | 0.0000 | 0.0003 |
| 8 | 4111 | NL | 0.0000 | 0.2003 | 0.0000 | 0.0003 |
| 10 | 3111 | LOLA20 | 1.0000 | 0.8682 | 0.9615 | 0.4703 |
| 10 | 4111 | LOLA20 | 0.9994 | 0.8682 | 0.9614 | 0.4706 |
| 10 | 3111 | NL | 0.0000 | 0.2003 | 0.0000 | 0.0002 |
| 10 | 4111 | NL | 0.0000 | 0.2003 | 0.0000 | 0.0003 |
| 12 | 3111 | LOLA20 | 1.0000 | 0.8656 | 0.9512 | 0.4666 |
| 12 | 4111 | LOLA20 | 0.9993 | 0.8659 | 0.9525 | 0.4668 |
| 12 | 3111 | NL | 0.0000 | 0.2003 | 0.0000 | 0.0002 |
| 12 | 4111 | NL | 0.0000 | 0.2003 | 0.0000 | 0.0003 |

### Benchmark azar y comparación material

| k | Equipos perfectos por azar i.i.d. | Aprendida elástica | Oráculo roles | FIXED3 comida | FIXED3 cesta completa | Coste 0,04 por vínculo comida |
| --- | --- | --- | --- | --- | --- | --- |
| 2 | 50.000000% | 0.8769 | 0.8768 | 0.9566 | 0.9957 | 0.9566 |
| 3 | 22.222222% | 0.8758 | 0.8758 | 0.9156 | 0.9914 | 0.9156 |
| 4 | 9.375000% | 0.8746 | 0.8745 | 0.8746 | 0.9868 | 0.8746 |
| 5 | 3.840000% | 0.8734 | 0.8737 | 0.4815 | 0.0764 | 0.8336 |
| 6 | 1.543210% | 0.8724 | 0.8727 | 0.3875 | 0.0070 | 0.7928 |
| 8 | 0.240326% | 0.8702 | 0.8703 | 0.3027 | 0.0001 | 0.7109 |
| 10 | 0.036288% | 0.8682 | 0.8683 | 0.2567 | 0.0000 | 0.6292 |
| 12 | 0.005372% | 0.8657 | 0.8663 | 0.2270 | 0.0000 | 0.5471 |

La probabilidad de equilibrio casual para k personas y k profesiones elegidas independientemente con probabilidad uniforme es k!/k^k. El benchmark ORACLE_ROLES fija externamente una asignación perfecta y únicamente se usa al evaluar para comparar el alimento: nunca participa en los gradientes ni crea el aprendizaje.

La tecnología de entrenamiento **ELASTIC** incrementa la capacidad potencial de ofrecer regalos con k, pero normaliza el coste total de regalar a todos los k−1 vecinos a0,12. Recompensa=0,20+0,55×tipos recibidos/(k−1)+0,25×I(cesta completa)−0,12/(k−1)×regalos entregados−0,015×cambio de oficio. Máximo de intercambio universal 0,88 para todos los k. Con k4 el pago coincide con la fórmula de V25/V51.

Se evaluaron las mismas políticas profesionales y donantes congelados con dos alternativas tecnológicas. **FIXED3** solo admite tres entregas por trabajador y ronda, pagando0,04 por unidad; cuando k≥5 no pueden recibir todos una cesta completa simultáneamente, aunque algunos sí, con cota de cobertura plena≤3/(k−1). **PER_LINK04** permite k−1 regalos pero cada uno cuesta0,04, lo que hace crecer el coste total al aumentar k. Son contrafactuales fuera de distribución; las redes NO fueron reentrenadas para ellos.

## Contrastes preregistrados

| Hipótesis | Resultado |
| --- | --- |
| h54a_six_of_eight_k_both_seeds_high_balance_food | cumple |
| h54b_at_least_one_k_ge8_below_80_percent | falsada |
| h54c_six_of_eight_k_both_seeds_gain_10pct | cumple |
| h54d_all_nl_food_below_0_30 | cumple |
| h54e_fixed3_conservation_bound_valid | cumple |

H54a exige al menos6 de8 valores k con ambas semillas LOLA20 con≥80% grupos profesionales completos y alimento≥0,65. H54b predecía una frontera de fracaso para al menos un k≥8: si no se observa se reporta falsada, sin ajustar los criterios. H54c pide ventaja alimentaria≥0,10 frente al mejor cambio ocupacional aleatorio en al menos6 k y ambas semillas. H54d pide alimento≤0,30 para todos los controles NL. H54e comprueba conservación de capacidad3, no ausencia absoluta de cestas completas.

## Interpretación de mecanismos y reservas

[Inferencia] La existencia de una política privada que dona a sus vecinos con probabilidad elevada hace que ocupar una especialidad faltante proporcione beneficio propio, lo cual genera incentivos para la diferenciación laboral. El número k por sí solo puede alargar el período de descubrimiento y reducir la probabilidad de configuración óptima accidental, sin volverla inaccesible bajo determinadas tecnologías y horizontes.

El actor profesional observa la distribución de ocupaciones de sus vecinos y conoce su propia comida. Los modelos generaron las especialidades desde ocupaciones monolíticas y aleatorias. Sin embargo, los vecinos ya están organizados en cliques del tamaño exacto k y se heredan las estrategias de cooperación LOLA20; no se ha demostrado una elección espontánea del tamaño de los grupos, creación de vínculos, cooperación desde cero ni una población abierta que decida cuántas profesiones necesita realmente.

## Protocolo de evaluación y reproducibilidad

El checkpoint final u1400 se evaluó con seis semillas ambientales reservadas999201/207/209/221/231/237,24 mundos por semilla, dos estados iniciales (monolito,aleatorio), tres tecnologías y seis políticas de movilidad de oficios (aprendida, inmóvil,3 aleatorias y oráculo). No se seleccionaron los checkpoints de rendimiento máximo durante entrenamiento. Se conservan los historiales u1,200,400,600,800,1000,1200,1400, especificaciones por modelo, pesos y Adam, resultados completos por semilla y escena, CSV y JSON.

El experimento responde a escalado de k dentro de una clase de economías, no a una ley universal de formación de profesiones. La diferencia entre política neuronal aprendida y mejor respuesta exacta también deberá estudiarse por separado, como hace el control mecanístico V54B.

## Código e integridad
PREREG_V54_K_SCALING.md: 2e1b54e19e6d22e2af0167f114360ed4d6f9efd99ec1193ad0bc76ac37fdbe40
v54_k_scaling.py: 36c5c5363eeb7e1cc2fe5f7947a4c33c83fdf537b9d1fe90ffc2472c02a0a517
v54_frozen_audits.py: 320fb2352a352ba24d5649dc55409b83e13bbe9b7204e1ace0e702da0928e26d
v54_summarize.py: 3b98c897969337a46897152c2460ac899fbb9bb22c4cbd1b83b7b1415b111d3d
test_v54_k_scaling.py: 6b167d817e8a51c8ed004252171fe7d7d51999a75af0904d8d92de897c0f5eba
test_v54_frozen_audits.py: d8f13d04757c3b946c0a0045dbe293be967101b353ae84a86ebbb6742b6168e1