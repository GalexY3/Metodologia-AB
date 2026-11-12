# V40. Brecha causal entre el beneficio alimentario privado y social de una oferta

Auditoría preregistrada después de los resultados V39, ejecutada con seis checkpoints contractuales finales V30/V31, cuatro profesiones y N48 o N120, dos precios c0,04 y c0,12, seis semillas ambientales reservadas por checkpoint y 8–12 mundos por semilla. Se congelaron todas las redes privadas. Las decisiones de ocupación y ofertas se simularon normalmente durante 24 rondas, y en la ronda25 se impuso para cada persona individualmente la primera oferta de regalo frente a su prohibición, manteniendo iguales las demás propuestas y ocupaciones. Las dos reglas de liquidación comparadas son contratos recíprocos bilaterales y regalos unilaterales.

## Efectos materiales marginales, por propuesta dirigida

| Modelo | Coste | Cambio privado unilateral | Beneficio a receptor | Beneficio social neto | Ofertas unilat. útiles | Cambio privado contractual | Personas privadas positivas con contrato |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v30_MUTUAL_C04_s3111 | 0.04 | -0.0400 | +0.1036 | +0.0636 | 37.2% | +0.0342 | 48/48 |
| v30_MUTUAL_C04_s4111 | 0.04 | -0.0400 | +0.1029 | +0.0629 | 37.0% | +0.0358 | 48/48 |
| v31_N120_MUTUAL_C04_s3111 | 0.04 | -0.0400 | +0.1027 | +0.0627 | 37.2% | +0.0368 | 120/120 |
| v31_N120_MUTUAL_C04_s4111 | 0.04 | -0.0400 | +0.1033 | +0.0633 | 37.2% | +0.0367 | 120/120 |
| v31_N120_MUTUAL_C12_s3111 | 0.12 | -0.1200 | +0.1052 | -0.0148 | 38.1% | +0.0127 | 116/120 |
| v31_N120_MUTUAL_C12_s4111 | 0.12 | -0.1200 | +0.1075 | -0.0125 | 38.6% | +0.0125 | 118/120 |

La utilidad privada de una donación unilateral forzada es exactamente −c en el turno intervenido. El beneficio del destinatario depende de si aporta un tipo profesional que faltaba; el beneficio social neto inmediato es igual al beneficio recibido por ese destinatario menos c, en unidades de alimento total. El test de conservación confirma que no hay efectos inmediatos sobre terceros distintos del destinatario. Una oferta contractual puede no ejecutarse si falta contrapropuesta, y si se ejecuta ambas partes intercambian un bien; por tanto, el cambio privado del donante puede ser positivo al mismo tiempo que paga su unidad.

El resultado de intervención es **local y marginal**. No puede explicar automáticamente la diferencia agregada V39 entre ejecutar de golpe todas las propuestas bajo ambos regímenes, porque el beneficio por unidad puede depender de la redundancia, de otras ofertas simultáneas y de qué vecinos ya estén satisfechos. V40 tampoco simula la adaptación de los agentes después de cambiar las reglas de liquidación; esa cuestión corresponde a entrenamientos de un juego distinto.

## Hipótesis preregistradas y falsaciones

| Hipótesis | Resultado |
| --- | --- |
| h40a_all_exact_own_cost | cumple |
| h40b_positive_social_low_cost | cumple |
| h40c_nonpositive_social_high_cost | cumple |
| h40d_positive_contract_private | cumple |

H40a exige identidad mecánica del coste privado; H40b requiere beneficio social inmediato marginal positivo en ≥3/4 de los modelos de coste0,04; H40c espera neto marginal social no positivo en al menos uno de los dos modelos de coste0,12; H40d espera retorno privado inmediato contractual medio no negativo en ≥4/6 checkpoints. Las hipótesis se concibieron tras observar V39, por lo que son contrastes exploratorios preregistrados antes de V40, no replicaciones ciegas.

## Incertidumbre y alcance

Seis ambientes reservados por modelo, 8 o12 mundos por ambiente, intervención independiente sobre cada persona. La persona es unidad de tratamiento en un mundo simulado, pero la inferencia sobre políticas neuronales debe considerar que solo hay seis entrenamientos distintos y algunos son pares de la misma semilla a tamaños diferentes. Los intervalos bootstrap descriptivos agrupados por semilla ambiental se guardan en METRICAS_V40.json. No convertir el número de intervenciones en el número de redes entrenadas.

[Inferencia] La brecha entre ganancia material de terceros e incentivo marginal propio ayuda a separar eficacia técnica potencial y estabilidad estratégica. Una regla contractual puede operar como mecanismo de apropiación simultánea de beneficios, aunque la entrega de todas las propuestas bajo una norma unilateral genere mayor alimento agregado a bajo precio. Esto no demuestra surgimiento endógeno de instituciones ni reciprocidad diferida sostenible.

## Reproducibilidad

Preregistro PREREG_V40_INDIVIDUAL_SOCIAL_WEDGE.md, código v40_marginal_wedge.py, pruebas test_v40_wedge.py, resultados originales results/v40_marginal_v30_*.json y results/v40_marginal_v31_*.json, resumen COMPARACION_V40.csv y METRICAS_V40.json. SHA256:
PREREG_V40_INDIVIDUAL_SOCIAL_WEDGE.md: 19d0cf6059bf3e90aa4910f1c1260084b5fa49e97035072d46b6b4ba5a78e3ae
v40_marginal_wedge.py: 4815cb546085475eb49ea1005673b9ee10e4e87e67f1f98e57bceac06edfb83a
v40_summarize.py: 501781ae4aadba41f13665c9fe3615733e29c72ef64a204e470338811da2779f
test_v40_wedge.py: bbc228024f349ea5d7856d399c4099de5f644ec42a63ced571f20dc0f2e06a35