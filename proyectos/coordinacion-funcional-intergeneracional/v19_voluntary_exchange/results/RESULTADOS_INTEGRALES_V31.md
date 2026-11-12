# V31. Contratos bilaterales descentralizados con 120 individuos y cuatro profesiones

Campaña preregistrada el 12/11/2026 después de los resultados preliminares de V30 y antes de conocer el final de V30. Todos los actores de V31 se iniciaron con pesos aleatorios privados (no se transfirieron redes de V30), y aprendieron al mismo tiempo ofertas dirigidas y decisiones de ocupación. La regla institucional de liquidación mutuamente consentida permaneció disponible exógenamente, sin planificación de objetivos sociales ni recompensa de grupo.

N120, k4, anillo grado6, horizonte48, 700 actualizaciones, lote8, dos semillas por coste unitario final0,04 y0,12. Seis semillas ambientales nuevas para evaluación congelada; ocho mundos por semilla/condición para alimento y tres mundos por semilla para intervenciones de todas las personas. Los mundos no son semillas independientes de las redes neuronales.

## Resultados congelados

| Modelo | Coste | Alimento | Contratos efectivos/pers. | Cobertura | Mejor movilidad aleatoria | Ventaja | Retorno causal | Personas positivas | Oráculo físico | Fracción del excedente máximo |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v31_N120_MUTUAL_C04_s3111 | 0.04 | 0.3421 | 1.0883 | 0.3319 | 0.3316 | +0.0105 | +0.0365 | 117/120 | 0.8800 | 20.9% |
| v31_N120_MUTUAL_C04_s4111 | 0.04 | 0.3429 | 1.0905 | 0.3333 | 0.3318 | +0.0111 | +0.0355 | 118/120 | 0.8800 | 21.0% |
| v31_N120_MUTUAL_C12_s3111 | 0.12 | 0.2528 | 1.0322 | 0.3164 | 0.2401 | +0.0127 | +0.0129 | 107/120 | 0.6400 | 12.0% |
| v31_N120_MUTUAL_C12_s4111 | 0.12 | 0.2535 | 1.0406 | 0.3191 | 0.2402 | +0.0133 | +0.0119 | 103/120 | 0.6400 | 12.2% |

El oráculo supone 3 parejas contractuales útiles por persona y roles periódicos, sin movilidad ni redundancias; comida 0,88 a coste0,04 o 0,64 a coste0,12. Está programado explícitamente solo como test de posibilidad material, no como profesor ni política aprendida. La fracción del excedente máximo = (alimento−0,20)/(oráculo−0,20) cuantifica distancia al techo bajo el mismo precio.

## Transferencia al aumentar de 48 a 120 personas

| Semilla | N48 alimento | N120 alimento | Diferencia | N48 causal | N120 causal |
| --- | --- | --- | --- | --- | --- |
| 3111 | 0.3440 | 0.3421 | -0.0019 | +0.0330 | +0.0365 |
| 4111 | 0.3428 | 0.3429 | +0.0001 | +0.0346 | +0.0355 |

Las redes de N48 y N120 están entrenadas separadamente desde cero: esta es una comparación del protocolo a dos tamaños de población, no una prueba de que los mismos pesos se transfieran. La red mantiene grado6, de modo que el barrio local por persona tiene la misma cardinalidad aunque la población total aumente.

## Mecanismos y heterogeneidad

| Modelo | Circular | Sin historial | Personas permutadas | Red reconectada | Causal inmediato | Causal futuro | Causal sin historial | Causal reconectada |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v31_N120_MUTUAL_C04_s3111 | 0.3421 | 0.3388 | 0.3338 | 0.3365 | +0.0352 | +0.0012 | +0.0350 | +0.0299 |
| v31_N120_MUTUAL_C04_s4111 | 0.3429 | 0.3392 | 0.3324 | 0.3405 | +0.0342 | +0.0013 | +0.0348 | +0.0344 |
| v31_N120_MUTUAL_C12_s3111 | 0.2528 | 0.2515 | 0.2449 | 0.2467 | +0.0123 | +0.0006 | +0.0130 | +0.0080 |
| v31_N120_MUTUAL_C12_s4111 | 0.2535 | 0.2519 | 0.2411 | 0.2479 | +0.0112 | +0.0007 | +0.0112 | +0.0085 |

La contribución contractual no implica necesariamente altruismo o memoria de favores anteriores: los acuerdos simultáneos permiten pagar un bien mientras se recibe otro. Las pruebas fuera de muestra verifican beneficios materiales sin obligar a dar, y la auditoría fuerza solo una propuesta del primer turno frente a prohibirla, manteniendo libres las otras acciones. El retorno causal puede deberse principalmente a la contraprestación inmediata. Una oferta que no encuentra otra correspondiente no se liquida ni ocasiona gasto.

## Condiciones de éxito y límites

Este resultado permite explorar cooperación contractual y especialización profesional con 120 personas y cuatro oficios en dos precios, pero no acredita que la **institución contractual misma** surgiese endógenamente: sus reglas fueron diseñadas antes. Las políticas laborales aprendidas deben superar de modo sustancial controles de movilidad aleatoria y mantener estabilidad ante reconfiguración relacional para considerarse organización funcional superior. Solo dos semillas neuronales por coste y seis contextos ambientales no permiten universales ni certeza sobre todas las poblaciones.

Se conserva el objetivo general abierto. La línea V32 prueba la adopción institucional libre y V33 el aprendizaje laboral prolongado. Las conclusiones positivas V30–V31 no deben usarse para borrar los fracasos de reciprocidad unilateral V24–V29.

## Código y reproducción

Preregistro PREREG_V31_BARTER_SCALE.md, código del mercado v30_consensual.py, auditor v30_frozen_audits.py, checkpoints de las cuatro condiciones en runs/v31_N120_*, resultados crudos results/v30_holdout_v31_*.json y results/v30_causal_v31_*.json.

SHA256:
v30_consensual.py: 6cb46706df94775c6729ea1767a7aeff280e9d5e9def01afbbe0cc80def721a7
v30_frozen_audits.py: 9508fd8b690499a3aac140d313d80e74d05266e2490f3c0a7902e7c8c5f4ced9
v31_summarize.py: fe07d11a08e1c6b266eb4ec75534747068e8e539bc391d1e5b6b573d4d19577e
PREREG_V31_BARTER_SCALE.md: 13eea87225af6ca6cda9f432d4618d4e98de97ba8c32160315df44d6b70b3dee