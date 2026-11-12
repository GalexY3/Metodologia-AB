# V34. Escasez de socios y formación de especialidades en redes de cuatro vecinos

Ensayo preregistrado el 12/11/2026 tras V30. Dos inicializaciones neuronales N48/k4 por tratamiento topológico. Ambas redes de oferta contractual dirigida y ocupación comenzaron con pesos aleatorios privados por individuo. Misma economía institucional de contratos recíprocos voluntarios V30, coste final0,04 y 700 actualizaciones. Intervención única: anillo de grado4 en entrenamiento en vez de grado6. No hay quotas profesionales ni objetivos sociales agregados.

## Evaluación congelada fuera de muestra

| Modelo | Alimento grado4 | Alimento grado6 | Azar roles grado4 | Ventaja roles g4 | Ventaja roles g6 | Mejora de ventaja | Potencial roles g4 | Potencial azar g4 | Causal oferta | Agentes positivos |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v34_N48_D4_MUTUAL_s3111 | 0.3731 | 0.3440 | 0.3389 | +0.0342 | +0.0113 | +0.0229 | 0.9035 | 0.6803 | +0.0388 | 48/48 |
| v34_N48_D4_MUTUAL_s4111 | 0.3726 | 0.3428 | 0.3418 | +0.0308 | +0.0110 | +0.0199 | 0.8934 | 0.6803 | +0.0403 | 48/48 |

La condición de éxito ocupacional preregistrada requería superar en ambas semillas al mejor control aleatorio por ≥0,05 de alimento. El control aleatorio se selecciona por mayor comida entre tres tasas prefijadas. Aunque se usa una red con menos contactos, el proceso de aprendizaje privado y la institucionalidad contractual permanecen constantes. Los dos grados tienen asignaciones de roles aleatorias suficientemente diversas para abastecer materialmente si se consigue coordinación. Seis semillas ambientales y doce mundos por semilla controlan el efecto condicional, sin multiplicar las inicializaciones neuronales independientes.

## Transferencia, controles y auditoría de consentimientos

| Modelo | Normal | Sin ofertas | Personas reasignadas | Red reconectada | Causal anillo | Causal reconectada | Oráculo |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v34_N48_D4_MUTUAL_s3111 | 0.3731 | 0.1998 | 0.3423 | 0.3528 | +0.0388 | +0.0284 | 0.8800 |
| v34_N48_D4_MUTUAL_s4111 | 0.3726 | 0.1997 | 0.3592 | 0.3547 | +0.0403 | +0.0299 | 0.8800 |

La auditoría obliga a un individuo por vez a emitir o no una oferta contractual inicial, manteniendo libres otros dos slots y todos los turnos siguientes. Su retorno puede reflejar la contraprestación inmediata del acuerdo. El oráculo de grado4 logra plena cobertura material mediante socios bilaterales a ±1 y parejas alternadas a distancia2; se utiliza solo para demostrar factibilidad matemática, no como política de entrenamiento.

## Interpretación y límites

[Inferencia] Una mayor escasez local de contactos complementarios puede elevar la importancia funcional de aprender posiciones ocupacionales. La comparación debe separar esa mejora de la simple variación de capacidad de contratación por número de vecinos. Una organización profesional significativamente mejor que la aleatoria con red fija todavía puede quedar ligada a posiciones particulares; por ello se midió cambio de personas y red reconectada.

Criterios pendientes para el objetivo general: 120 individuos con ventaja ocupacional robusta, varias inicializaciones, cambios de vecinos, adaptabilidad después de pérdidas y sustituciones, y distinción entre regla contractual exógena y estructuras emergentes endógenas.

## Procedencia y hashes

Preregistro PREREG_V34_NEIGHBOR_SCARCITY.md; entrenador v34_contract_degree4.py, evaluador v34_frozen_audits.py, resultados de todos los individuos y mundos en results/v30_{holdout,causal}_v34_*.json, checkpoints runs/v34_N48_D4_*, comparadores V30 congelados.
v34_contract_degree4.py: d9292f3563169100e731232a70f2cb5e02f832beafca3f423aee4db34e0f7c8a
v34_frozen_audits.py: e40a431a5b473337e4fed296565b7a83baeb80d927ff35399ef79286a4f49c6a
v34_summarize.py: 6fdaa884e3cb293352e76755fdacbd40cc6254e432d56c4113684f0b40d7dc82
PREREG_V34_NEIGHBOR_SCARCITY.md: ffb178214b4b1f65fcbf47320f94e0fd9adf88e2422c4b56760dc05ca241ec68