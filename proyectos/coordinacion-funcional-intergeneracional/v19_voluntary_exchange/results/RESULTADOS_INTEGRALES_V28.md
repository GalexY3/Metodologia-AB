# V28. Cooperación observada y racionalidad secuencial en el horizonte finito

Auditoría congelada de 12/11/2026. Se evaluaron cuatro checkpoints de coaprendizaje V23 N24/k2 y dos de entrega multiunidad V25 N48/k4 a precio 0,04. Seis semillas ambientales y 24 mundos por semilla, 48 rondas por mundo, misma política congelada en toda la trayectoria. Se registró por turno número de regalos enviados por individuo, alimentación y cobertura material. No se entrenó ningún modelo nuevo para esta ronda.

## Perfil de contribuciones por período

| Política | Familia | Regalos t1–8 | Regalos t41–48 | Diferencia | Ratio | Regalos turno 48 |
| --- | --- | --- | --- | --- | --- | --- |
| v23_SMOOTH_s3111 | v23 | 0.7286 | 0.7351 | +0.0066 | 1.009 | 0.7367 |
| v23_SMOOTH_s4111 | v23 | 0.8780 | 0.8661 | -0.0119 | 0.986 | 0.8623 |
| v23_SMOOTH_s5111 | v23 | 0.3645 | 0.3650 | +0.0005 | 1.001 | 0.3652 |
| v23_SMOOTH_s6111 | v23 | 0.6328 | 0.6244 | -0.0084 | 0.987 | 0.6299 |
| v25_N48_C04_s3111 | v25 | 0.0349 | 0.0139 | -0.0210 | 0.398 | 0.0152 |
| v25_N48_C04_s4111 | v25 | 0.0246 | 0.0109 | -0.0138 | 0.441 | 0.0114 |

La columna de regalos en V23 equivale a probabilidad de donar una vez (0–1); en V25 es número de regalos por persona (0–3). No comparar esas magnitudes sin considerar distinta capacidad. Los perfiles contienen tasas observadas, no retornos causales del último turno.

## Proposición estratégica y sus supuestos

En el último turno, donar reduce exactamente la comida propia en el coste unitario (0,12 en V23, 0,04 en V25), mientras los demás no pueden modificar sus regalos simultáneos en respuesta a la donación actual. No existe futuro dentro de la trayectoria, de modo que la donación no puede recuperar ese coste. Bajo racionalidad secuencial plena, conocimiento común del horizonte y ausencia de valor terminal/reputación interepisódica, este razonamiento se propaga hacia atrás. Una trayectoria sin donaciones ni cambios de oficio es un equilibrio perfecto en subjuegos; más detalles, premisas y demostración en V28_FINITE_HORIZON_GAME_THEORY.md.

Las redes aprendidas V23 continúan donando en el último turno. La evidencia de cooperación conductual en el entrenamiento no es una prueba de que la política conjunta sea un equilibrio secuencialmente racional; precisamente las donaciones finales son una desviación de la elección óptima a un turno vista. V25 parece acercarse al régimen de no contribución conforme avanza la trayectoria, pero tenía ya regalos casi nulos, lo que limita la interpretabilidad de la disminución.

## Implicación para rediseño de experimentos

[Inferencia] Para investigar sostenibilidad estratégica más allá de convenciones finitas podría ser necesario un horizonte indeterminado, continuidad social entre episodios o activos de reputación con valor posterior. Estas intervenciones modifican el juego y deben probarse contra controles, no presumirse mejoras automáticas de capacidad de razonamiento.

## Datos y reproducción

JSON por ronda results/v28_temporal_profiles.json; seis semillas por modelo. Código de auditar v28_temporal_profiles.py, función de reporte v28_summarize.py. Contrastes entre segmentos calculados por bootstrap descriptivo agrupado por semilla ambiental, sin inflar n por mundos. Los pesos V23 y V25 permanecen en sus correspondientes runs/ ya versionados.

SHA256 de archivos:
v28_temporal_profiles.py: 3188b038f646d62371167003229cb2741296321c28ad7a7ce2e98709b039c831
v28_summarize.py: 77fd0b35dd4439fcf3e6c54de1596aaa80ac2dd9725eff945787a606045cdf27
V28_FINITE_HORIZON_GAME_THEORY.md: 71acec835a38ba5946f11acac89d0d64d325a147bba23d4889ef7ebfe5ae38f9