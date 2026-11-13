# V42 — Factibilidad estratégica de reciprocidad sin liquidación contractual

Simulación preregistrada el 13/11/2026 sobre el componente diádico de la economía de cuatro profesiones con N48/k4. Se construyeron 24 parejas disjuntas de oficios complementarios (i, i XOR1), con los mismos pagos materiales y topología del simulador. Se verifica primero el código físico original que permite entregar un producto pagando el coste c, sin condicionar ni impedir la donación del otro participante. **La norma de reciprocidad contingente grim-trigger está introducida como oráculo hipotético, no fue aprendida por las redes neuronales**.

## Mecánica de un único regalo recíproco

| Coste | Alimento por persona cooperando | Ahorro privado si defrauda | Pérdida del vecino que no recibe |
| --- | --- | --- | --- |
| 0.04 | 0.3433 | +0.0400 | -0.1833 |
| 0.12 | 0.2633 | +0.1200 | -0.1833 |

En un par, recibir una especialidad que falta aporta exactamente v=0,55/3≈0,18333 unidades por turno. Si ambos donan, cada persona obtiene b+v−c; si una persona incumple mientras la otra dona, el desertor se ahorra c y su contraparte pierde v. El resto de las46 personas conserva exactamente el mismo alimento. Esto valida la posibilidad material sin contratos.

## Continuidad incierta y equilibrio condicional de la pareja

La norma hipotética se mantiene mientras ambos se hayan ayudado siempre y se interrumpe definitivamente si uno incumple. Con vida de continuación geométrica q y descuento temporal gamma0,995, el cálculo de la ganancia descontada de seguir cooperando frente a desertar una sola vez es (gamma·q·v−c)/(1−gamma·q). La condición de incentivos es gamma·q·v ≥ c.

**Umbral de continuidad a coste0,04:** q ≥ 0.2193. **A coste0,12:** q ≥ 0.6578.

## Validación Monte Carlo del valor presente, con duración aleatoria

| Coste | Prob. continuidad | Ventaja analítica cooperación | Ventaja simulada | Error estándar | Dentro 4 SE |
| --- | --- | --- | --- | --- | --- |
| 0.04 | 0.0 | -0.0400 | -0.0400 | 0.00000 | sí |
| 0.04 | 0.15 | -0.0149 | -0.0147 | 0.00015 | sí |
| 0.04 | 0.2 | -0.0044 | -0.0045 | 0.00018 | sí |
| 0.04 | 0.25 | +0.0075 | +0.0076 | 0.00021 | sí |
| 0.04 | 0.4 | +0.0548 | +0.0547 | 0.00033 | sí |
| 0.04 | 0.5 | +0.1019 | +0.1018 | 0.00045 | sí |
| 0.04 | 0.6 | +0.1723 | +0.1724 | 0.00061 | sí |
| 0.04 | 0.75 | +0.3815 | +0.3811 | 0.00107 | sí |
| 0.04 | 0.8 | +0.5193 | +0.5202 | 0.00137 | sí |
| 0.04 | 0.95 | +2.4346 | +2.4437 | 0.00521 | sí |
| 0.04 | 0.98 | +5.5730 | +5.5725 | 0.01039 | sí |
| 0.12 | 0.0 | -0.1200 | -0.1200 | 0.00000 | sí |
| 0.12 | 0.15 | -0.1089 | -0.1089 | 0.00006 | sí |
| 0.12 | 0.2 | -0.1043 | -0.1043 | 0.00008 | sí |
| 0.12 | 0.25 | -0.0990 | -0.0992 | 0.00009 | sí |
| 0.12 | 0.4 | -0.0781 | -0.0780 | 0.00015 | sí |
| 0.12 | 0.5 | -0.0573 | -0.0574 | 0.00020 | sí |
| 0.12 | 0.6 | -0.0262 | -0.0261 | 0.00027 | sí |
| 0.12 | 0.75 | +0.0663 | +0.0663 | 0.00048 | sí |
| 0.12 | 0.8 | +0.1271 | +0.1268 | 0.00061 | sí |
| 0.12 | 0.95 | +0.9734 | +0.9736 | 0.00230 | sí |
| 0.12 | 0.98 | +2.3602 | +2.3582 | 0.00459 | sí |

Los valores simulados proceden de duraciones geométricas exógenas, con al menos200.000 episodios independientes por punto y semilla fija. Las incertidumbres aquí provienen del muestreo de duraciones del oráculo matemático, no de variación entre entrenamientos neuronales: los modelos no fueron entrenados. El signo de la ganancia es **propiedad de una pareja que ya sabe aplicar esta norma** y no implica que la norma surja espontáneamente.

## Hipótesis

| Prueba preregistrada | Resultado |
| --- | --- |
| h42a_material_mechanics | cumple |
| h42b_threshold_signs | cumple |
| h42c_monte_carlo_4se_all | cumple |
| h42d_profitable_indefinite_pair_both_costs | cumple |

## Significado sociológico y limitaciones

[Inferencia] El juego material permite estrategias de reciprocidad condicional con incentivos positivos cuando existe suficiente continuidad futura; en la misma economía los agentes de V41 abandonaron la ayuda unilateral tras aprender, incluso teniendo buenas oportunidades colectivas de intercambio. Esto sugiere que conviene investigar la capacidad de descubrir y estabilizar convenciones de castigo o recompensa en relaciones de duración incierta, antes de aumentar simplemente el tamaño de las redes.

No se infiere que el juego completo de cuatro profesiones tenga equilibrio único o que la duración incierta baste para aprender cooperación; la deducción se limita al subsistema aislado de parejas complementarias y su norma oracular. En un horizonte finito y conocido, la deserción puede propagarse hacia atrás bajo hipótesis de racionalidad e información propias de juegos repetidos con equilibrio único de etapa, pero no se ha demostrado ese razonamiento para el sistema MARL completo.

## Reproducción

Preregistro PREREG_V42_SHADOW_OF_FUTURE.md, evaluador v42_shadow_future.py, casos mecánicos en test_v42_shadow_future.py, CSV y METRICAS_V42.json con semillas y desviaciones. SHA256:
PREREG_V42_SHADOW_OF_FUTURE.md: 4a1e6172f5bf21323358975ff155e66bf818048c6dae86a36f439bd52e820393
v42_shadow_future.py: 927239eaf9c6f5de647a594d96c4bf21705de54244e528316f18fb03f18397c3
test_v42_shadow_future.py: 35a99cada3258cebf3d2d0127b90cd7cd40c2794a6b2f819470ed54580e65b61