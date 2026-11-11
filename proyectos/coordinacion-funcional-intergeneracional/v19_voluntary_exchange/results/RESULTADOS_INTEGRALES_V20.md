# V20 — Dependencia de trayectoria y cooperación voluntaria dirigida

Resultados exploratorios congelados el 11/11/2026. Las políticas y archivos originales permanecen en `runs/` y `results/`.

## Contrato experimental

Poblaciones de 24 agentes con redes neuronales privadas, sin parámetros compartidos, recompensas globales, profesor ni obligación de donar. Una donación cuesta 0,12 en el régimen final. El alimento se obtiene individualmente, según bienes recibidos y coste de donar. Las profesiones de entrenamiento están asignadas exógenamente y no se aprende aún la división del trabajo.

Se compararon diez entrenamientos de 600 actualizaciones, con 16 mundos por actualización, horizonte de 32 períodos y 24 agentes por mundo; **73.728.000 transiciones individuales de entrenamiento** en total. Las rutas comparadas son coste alto constante, coste ascendente gradual y salto brusco tras un tramo inicial de bajo coste.

## Rendimiento al finalizar el entrenamiento

| Semilla | Constante: alimento | Gradual: alimento | Brusco: alimento | Gradual menos constante |
| --- | --- | --- | --- | --- |
| 3111 | 0.461 | 0.572 | 0.604 | +0.111 |
| 4111 | 0.202 | 0.356 | 0.486 | +0.154 |
| 5111 | 0.200 | 0.349 | — | +0.149 |
| 6111 | 0.202 | 0.416 | — | +0.214 |

Ganancia descriptiva media gradual frente a constante sobre cuatro semillas: +0.157 raciones. No es una estimación confirmatoria sobre la distribución de inicializaciones.

## Censo causal de los 24 individuos

La auditoría vectoriza, por cada mundo, 24 intervenciones distintas sobre la decisión inicial de donar o no donar. Incluye seis semillas de entorno, 24 mundos por semilla, dos potenciales tratamientos, tres regímenes de información y tres tareas (red circular k=2, reconectada k=2, circular k=3), durante 48 períodos. Hay **311.040 pares de trayectorias contrafactuales** en esta matriz (622.080 brazos); los mundos comparten estructura y no constituyen réplicas estadísticamente independientes.

Cada retorno causal es la diferencia en el alimento descontado del individuo cuya donación inicial fue forzada; un resultado positivo indica retorno favorable en esa intervención, no el valor causal de toda la institución.

| Política | Alimento desarrollo | Tasa donación | Retorno k2 circular | Agentes positivos | Retorno reconectada | Retorno k3 |
| --- | --- | --- | --- | --- | --- | --- |
| v20_SMOOTH_s3111 | 0.572 | 0.728 | +0.228 | 22/24 | +0.055 | +0.116 |
| v20_SMOOTH_s4111 | 0.356 | 0.273 | +0.037 | 9/24 | -0.063 | -0.043 |
| v20_SMOOTH_s5111 | 0.349 | 0.279 | +0.013 | 8/24 | -0.063 | -0.044 |
| v20_SMOOTH_s6111 | 0.416 | 0.388 | -0.019 | 9/24 | -0.038 | -0.052 |
| v20_CONST_s3111 | 0.461 | 0.470 | +0.231 | 13/24 | +0.038 | +0.113 |
| v20_CONST_s4111 | 0.202 | 0.003 | -0.121 | 0/24 | -0.120 | -0.120 |
| v20_CONST_s5111 | 0.200 | 0.000 | -0.121 | 0/24 | -0.121 | -0.120 |
| v20_CONST_s6111 | 0.202 | 0.003 | -0.120 | 0/24 | -0.119 | -0.120 |
| v20_ABRUPT_s3111 | 0.604 | 0.738 | +0.059 | 15/24 | -0.023 | -0.003 |
| v20_ABRUPT_s4111 | 0.486 | 0.522 | +0.099 | 13/24 | +0.004 | +0.012 |

En particular, la red gradual de semilla 3111 presenta retorno neto +0,228 y 22/24 agentes positivos; las otras tres semillas graduales tienen efectos mucho menores. En las tareas transferidas, buena parte de las políticas pierde el beneficio causal. La conclusión no puede generalizarse a cualquier inicialización, topología u objetivo.

## Ablación del mecanismo: donación directa y reputación

Los siguientes experimentos adicionales pertenecen al auditor anterior de seis agentes, todos de paridad par: ese muestreo no es representativo del censo individual y se conserva únicamente como prueba de mecanismo.

| Semilla | Información completa | Sin memoria del donante directo | Sin señal pública de generosidad | Sin ambas |
| --- | --- | --- | --- | --- |
| 3111 | +0.345 | +0.245 | +0.004 | -0.126 |
| 4111 | +0.165 | +0.105 | -0.066 | -0.122 |

[Inferencia] El retorno por donar parece depender particularmente de la visibilidad de la generosidad de los vecinos, compatible con reputación y reciprocidad indirecta. Esa intervención no identifica por sí sola una motivación mental ni una norma social interiorizada.

## Hallazgos negativos y riesgos de identificación

El aumento brusco supera al gradual en alimentación en las dos semillas para las que se probó, pero no se observa una superioridad causal uniforme. Aumentar la alimentación no prueba mayor reciprocidad. El auditor original intervenía seis índices pares y sobrerrepresentaba una profesión: la auditoría de todos los individuos reduce considerablemente varios efectos medios.

Los resultados de alimentación son evaluaciones de desarrollo. Los efectos causales proceden de pesos congelados y semillas ambientales separadas. Las diez políticas se examinaron inicialmente con cuatro semillas neuronales para dos tratamientos y dos para el tercero; no se ha cuantificado aún su comportamiento tras entrenamientos mucho mayores que 600 actualizaciones. Las pruebas fuera de distribución son cambios pequeños de red y k, no escalado de población.

No se declara OBJETIVO COMPLETADO. Aunque hay realizaciones concretas de reciprocidad aprendida, todavía falta robustez entre inicializaciones, estabilidad temporal, escalado y elección endógena de ocupaciones.

## Integridad y procedencia

Código y modelos: `v20_curriculum.py`, `v20_mechanism_ablation.py`, `v20_all_agents_causal.py`; archivos de datos `runs/v20_*/v20_history.jsonl`, `runs/v20_*/targeted_latest.pt` y `results/v20_allagents_*.json`. Los ficheros del repositorio pueden incluir modificaciones de experimentos previos sin relación con V20: no incluir cambios ajenos al confirmar la campaña.

SHA-256 de los programas usados

```
v20_curriculum.py: 2f539c183e76651b5212a1712b8e56980d08cb48de03858361b3fa90f006f216
v20_all_agents_causal.py: 2ab65c7e973890d0e171e3f06ec20cf7f5083c7f6fed26fcf49820cf026bd33a
v20_mechanism_ablation.py: 289b9fb33c1dcd679b3846ab2cc36328c040d4f33fec5c8f0717aa65f8c86a69
targeted_gifts.py: 7fa22d46016595fd87b8b0bf5a9edae1f5472cb8e2f95c85e42d9e350ffa8527
train_targeted.py: 897282c85bbf77d7c3af04e27fec892c7cb8c404124f6287f1ce521dec4a271d
```
