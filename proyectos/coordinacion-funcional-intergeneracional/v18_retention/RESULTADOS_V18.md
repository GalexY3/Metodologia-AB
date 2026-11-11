# V18 — Estabilidad de la organización durante aprendizaje individual

Informe derivado de evaluaciones congeladas; ninguna página web generada.

El aprendizaje de refuerzo utiliza exclusivamente la ración individual como recompensa. El término de regularización utiliza una política de coordinación aprendida por imitación de un profesor programado y debe distinguirse de cooperación descubierta autónomamente.

## Métricas fuera de muestra

| Política | Comunicación | Casos | Sociedades | Comida | Exactos | Porcentaje exacto |
|---|---|---:|---:|---:|---:|---:|
| teacher_v17_DISTILL_LATTICE_R8_s3111_fix | normal | 12 | 1152 | 0.9254 | 232 | 20.14% |
| teacher_v17_DISTILL_LATTICE_R8_s3111_fix | scrambled_senders | 12 | 1152 | 0.7602 | 87 | 7.55% |
| teacher_v17_DISTILL_LATTICE_R8_s3111_fix | no_messages | 12 | 1152 | 0.5349 | 0 | 0.00% |
| teacher_v17_DISTILL_LATTICE_R8_s4111_fix | normal | 12 | 1152 | 0.9248 | 234 | 20.31% |
| teacher_v17_DISTILL_LATTICE_R8_s4111_fix | scrambled_senders | 12 | 1152 | 0.7544 | 73 | 6.34% |
| teacher_v17_DISTILL_LATTICE_R8_s4111_fix | no_messages | 12 | 1152 | 0.5358 | 0 | 0.00% |
| v17_RL_BC_005_s5111 | normal | 12 | 1152 | 0.8110 | 0 | 0.00% |
| v17_RL_BC_005_s5111 | scrambled_senders | 12 | 1152 | 0.7993 | 1 | 0.09% |
| v17_RL_BC_005_s5111 | no_messages | 12 | 1152 | 0.5353 | 0 | 0.00% |
| v17_RL_BC_020_s5111 | normal | 12 | 1152 | 0.8395 | 6 | 0.52% |
| v17_RL_BC_020_s5111 | scrambled_senders | 12 | 1152 | 0.8246 | 1 | 0.09% |
| v17_RL_BC_020_s5111 | no_messages | 12 | 1152 | 0.5355 | 0 | 0.00% |
| v17_RL_BC_080_s5111 | normal | 12 | 1152 | 0.9221 | 174 | 15.10% |
| v17_RL_BC_080_s5111 | scrambled_senders | 12 | 1152 | 0.8799 | 86 | 7.47% |
| v17_RL_BC_080_s5111 | no_messages | 12 | 1152 | 0.5357 | 0 | 0.00% |
| v18_BC08_s6111 | normal | 12 | 1152 | 0.9279 | 201 | 17.45% |
| v18_BC08_s6111 | scrambled_senders | 12 | 1152 | 0.8824 | 93 | 8.07% |
| v18_BC08_s6111 | no_messages | 12 | 1152 | 0.5360 | 0 | 0.00% |
| v18_BC08_s7111 | normal | 12 | 1152 | 0.9263 | 186 | 16.15% |
| v18_BC08_s7111 | scrambled_senders | 12 | 1152 | 0.8823 | 101 | 8.77% |
| v18_BC08_s7111 | no_messages | 12 | 1152 | 0.5367 | 0 | 0.00% |
| v18_BC0_s6111 | normal | 12 | 1152 | 0.8066 | 1 | 0.09% |
| v18_BC0_s6111 | scrambled_senders | 12 | 1152 | 0.7941 | 0 | 0.00% |
| v18_BC0_s6111 | no_messages | 12 | 1152 | 0.5319 | 0 | 0.00% |
| v18_BC0_s7111 | normal | 12 | 1152 | 0.8071 | 0 | 0.00% |
| v18_BC0_s7111 | scrambled_senders | 12 | 1152 | 0.7952 | 0 | 0.00% |
| v18_BC0_s7111 | no_messages | 12 | 1152 | 0.5312 | 0 | 0.00% |
| v18_BC3_s6111 | normal | 12 | 1152 | 0.9454 | 301 | 26.13% |
| v18_BC3_s6111 | scrambled_senders | 12 | 1152 | 0.8961 | 184 | 15.97% |
| v18_BC3_s6111 | no_messages | 12 | 1152 | 0.5361 | 0 | 0.00% |
| v18_BC3_s7111 | normal | 12 | 1152 | 0.9487 | 309 | 26.82% |
| v18_BC3_s7111 | scrambled_senders | 12 | 1152 | 0.8987 | 188 | 16.32% |
| v18_BC3_s7111 | no_messages | 12 | 1152 | 0.5351 | 0 | 0.00% |

## Contrastes pareados (primer modelo menos segundo)

Intervalos por bootstrap de 5.000 remuestreos de escenarios completos. Son descriptivos y no cubren la incertidumbre entre muchas nuevas inicializaciones de redes.

| Contraste | Diferencia de comida | IC 95 % por escenario | Diferencia en reparto exacto | IC 95 % | Casos favorables |
|---|---:|---|---:|---|---:|
| v18_BC08_s6111 − v18_BC0_s6111 | +0.1213 | [+0.0908, +0.1564] | +17.36 pp | [+8.07, +28.91] pp | 12/12 |
| v18_BC08_s6111 − teacher_v17_DISTILL_LATTICE_R8_s3111_fix | +0.0024 | [-0.0156, +0.0223] | -2.69 pp | [-12.85, +7.73] pp | 5/12 |
| v18_BC3_s6111 − v18_BC0_s6111 | +0.1388 | [+0.1044, +0.1760] | +26.04 pp | [+16.84, +36.55] pp | 12/12 |
| v18_BC3_s6111 − teacher_v17_DISTILL_LATTICE_R8_s3111_fix | +0.0200 | [+0.0072, +0.0358] | +5.99 pp | [-3.21, +14.93] pp | 9/12 |
| v18_BC08_s7111 − v18_BC0_s7111 | +0.1191 | [+0.0884, +0.1547] | +16.15 pp | [+7.12, +27.00] pp | 12/12 |
| v18_BC08_s7111 − teacher_v17_DISTILL_LATTICE_R8_s4111_fix | +0.0015 | [-0.0171, +0.0222] | -4.17 pp | [-14.50, +5.47] pp | 6/12 |
| v18_BC3_s7111 − v18_BC0_s7111 | +0.1416 | [+0.1052, +0.1789] | +26.82 pp | [+17.45, +36.28] pp | 12/12 |
| v18_BC3_s7111 − teacher_v17_DISTILL_LATTICE_R8_s4111_fix | +0.0240 | [+0.0097, +0.0402] | +6.51 pp | [-4.17, +16.41] pp | 10/12 |

## Alcance inferencial

El conjunto de tareas incluye M/k conocidos y nuevas combinaciones de M/k. Las semillas de mundos son nuevas y se emparejan entre tratamientos. Algunas políticas se seleccionaron durante pilotos anteriores, por lo que este estudio conserva carácter confirmatorio limitado.

El número de trabajadores que obtiene comida y el número de profesiones son distintos resultados; para afirmar organización correcta se exige exactamente k grupos equilibrados.
La intervención que elimina mensajes modifica la disponibilidad del protocolo programado y no demuestra por sí sola cooperación social aprendida.
Se registran tanto repartos exactos al final como alcanzados en algún momento del episodio, para estudiar fragilidad y estabilidad.

Las rutas fuente y el código de entrenamiento se encuentran en los directorios v17_regime_coalition y v18_retention del mismo repositorio.