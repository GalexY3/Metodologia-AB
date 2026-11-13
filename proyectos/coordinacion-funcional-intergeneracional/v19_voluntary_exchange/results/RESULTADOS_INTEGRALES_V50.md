# V50 — Tres relaciones simultáneas, cuatro ocupaciones y reciprocidad privada

Se transfirieron sin reentrenar las 12 poblaciones V47 (NL, LOLA5, LOLA20 × cuatro semillas) a un mundo de48 agentes, 4 profesiones de12 personas cada una y tres vecinos simultáneos, uno por especialidad complementaria. La decisión de donar a cada uno es unilateral y privada. La función de alimento reproduce exactamente `v25_multi_capacity.step_multi`: 0,20+0,55×cobertura de los3 bienes+0,25×cobertura completa−0,04×regalos enviados. El máximo alimentario ante tres contribuciones propias y tres bienes recibidos es 0,88.

Las profesiones y las parejas especializadas fueron asignadas por el investigador; **no se observó aprendizaje ocupacional**. El matching puede reorganizarse dentro de cada episodio en probabilidades0, 0,25 y1, con q0,95 de continuidad temporal, máximo48 rondas y gamma0,995. Cada política tiene un logit Bernoulli para el primer encuentro y los cuatro estados de reciprocidad de memoria de una ronda, separado por cada uno de sus3 enlaces.

## Resultados completos agregados de las cuatro semillas neuronales

| Método | Rotación | Memoria | Alimento | Cobertura completa | Donación mutua | Retorno causal propio | Agentes positivos por semilla |
| --- | --- | --- | --- | --- | --- | --- | --- |
| NL | 0.0 | carry | 0.2007 | 0.0000 | 0.0000 | -0.0301 | 0,0,0,0 |
| NL | 0.0 | public | 0.2007 | 0.0000 | 0.0000 | -0.0301 | 0,0,0,0 |
| NL | 0.0 | none | 0.2007 | 0.0000 | 0.0000 | -0.0424 | 0,0,0,0 |
| NL | 0.25 | carry | 0.2007 | 0.0000 | 0.0000 | -0.0333 | 0,0,0,0 |
| NL | 0.25 | public | 0.2007 | 0.0000 | 0.0000 | -0.0301 | 0,0,0,0 |
| NL | 0.25 | none | 0.2007 | 0.0000 | 0.0000 | -0.0424 | 0,0,0,0 |
| NL | 1.0 | carry | 0.2007 | 0.0000 | 0.0000 | -0.0414 | 0,0,0,0 |
| NL | 1.0 | public | 0.2007 | 0.0000 | 0.0000 | -0.0316 | 0,0,0,0 |
| NL | 1.0 | none | 0.2007 | 0.0000 | 0.0000 | -0.0424 | 0,0,0,0 |
| LOLA5 | 0.0 | carry | 0.8747 | 0.9865 | 0.9911 | 0.0814 | 47,46,45,47 |
| LOLA5 | 0.0 | public | 0.8747 | 0.9865 | 0.9911 | 0.0814 | 47,46,45,47 |
| LOLA5 | 0.0 | none | 0.4509 | 0.1555 | 0.2618 | -0.0736 | 0,0,0,0 |
| LOLA5 | 0.25 | carry | 0.8747 | 0.9866 | 0.9911 | 0.0379 | 42,40,41,42 |
| LOLA5 | 0.25 | public | 0.8747 | 0.9866 | 0.9911 | 0.0792 | 48,47,47,47 |
| LOLA5 | 0.25 | none | 0.4508 | 0.1552 | 0.2614 | -0.0736 | 0,0,0,0 |
| LOLA5 | 1.0 | carry | 0.8747 | 0.9866 | 0.9910 | -0.0343 | 0,0,0,0 |
| LOLA5 | 1.0 | public | 0.8748 | 0.9868 | 0.9912 | 0.0829 | 45,45,45,46 |
| LOLA5 | 1.0 | none | 0.4510 | 0.1557 | 0.2613 | -0.0736 | 0,0,0,0 |
| LOLA20 | 0.0 | carry | 0.8760 | 0.9898 | 0.9938 | 0.9783 | 48,48,48,48 |
| LOLA20 | 0.0 | public | 0.8760 | 0.9898 | 0.9938 | 0.9783 | 48,48,48,48 |
| LOLA20 | 0.0 | none | 0.2750 | 0.0548 | 0.0624 | -0.0432 | 0,0,0,0 |
| LOLA20 | 0.25 | carry | 0.8759 | 0.9896 | 0.9933 | 0.4339 | 48,48,48,48 |
| LOLA20 | 0.25 | public | 0.8759 | 0.9896 | 0.9935 | 0.6740 | 48,48,48,48 |
| LOLA20 | 0.25 | none | 0.2750 | 0.0547 | 0.0625 | -0.0432 | 0,0,0,0 |
| LOLA20 | 1.0 | carry | 0.8763 | 0.9906 | 0.9938 | 0.0359 | 39,39,40,42 |
| LOLA20 | 1.0 | public | 0.8762 | 0.9904 | 0.9938 | 0.3520 | 48,48,48,48 |
| LOLA20 | 1.0 | none | 0.2750 | 0.0548 | 0.0624 | -0.0432 | 0,0,0,0 |

## Hipótesis preregistradas

| Hipótesis | Resultado |
| --- | --- |
| h50a | cumple |
| h50b | cumple |
| h50c | cumple |
| h50d | cumple |
| h50e | cumple |

## Diseño contrafactual y controles

Las seis semillas ambientales reservadas996101/996107/996109/996121/996131/996137 se aplicaron a cada condición con64 mundos para alimento, mutualidad y cobertura. Para el contraste individual se utilizaron4 mundos por semilla, duplicando cada mundo48 veces para forzar o impedir únicamente el primer regalo del individuo en uno de sus tres enlaces. Se mantienen las mismas vidas, grafo de contactos y uniformes de acción para todas las decisiones posteriores. El coste inmediato del sujeto tratado es exactamente−0,04. Se guardan por separado los retornos futuros privados descontados y la distribución individual de efectos.

En el brazo carry cada vínculo conserva la última acción de su ocupante anterior; en public se observa la última donación real del compañero actual hacia un individuo de la misma profesión del receptor; en none se anula la observación de la conducta ajena. El registro reputacional público y la profesión de cada compañero se aportan desde el entorno y no son inventados por los agentes.

El código V50 implementa los tres enlaces con una función NumPy propia y prueba paridad física frente al motor torch `v25_multi_capacity.step_multi` para decisiones y roles idénticos, ajustando el grafo original a tres vecinos para la comparación. La prueba de igualdad del pago original pasa con varias semillas y configuraciones.

## Lectura sociológica y límites

[Inferencia] La generalización de las políticas LOLA a tres enlaces simultáneos y necesidades profesionales complementarias muestra que una estrategia contingente privada puede sostener colaboración funcional en redes más densas cuando los bienes de los demás aportan valor directo y la conducta de cada autor es observable. No prueba organización laboral emergente porque cada individuo fue situado desde fuera en una especialidad y recibió exactamente los tres tipos de vecinos necesarios.

El juego de roles tiene una arquitectura favorable impuesta, y las políticas de regalar fueron entrenadas antes en parejas diádicas mediante gradientes exactos del aprendizaje ajeno. Esta transferencia congelada no es aprendizaje conjunto de profesiones y donaciones ni evolución espontánea de una institución reputacional. La robustez ante otras topologías, desequilibrio laboral y entradas de nuevos individuos sigue pendiente.

## Reproducibilidad

Preregistro, motor V50, pruebas de paridad con V25, CSV de108 escenarios, contrastes y métricas, 12 archivos JSON completos por modelo y escenario. Hashes:
PREREG_V50_MULTINEIGHBOR_FOUR_ROLES.md: f37aa2f04d07dd497bfbe6c28d3fe3dce3ddcbf7c5816b0fc401541b7a3f6b8b
v50_four_role_network.py: cfe421251a95a974cbbac837438700a882830fd86e7ccdc2634e5fff69590580
test_v50_four_role_network.py: b92fccc527ab0239255cea70d0e9dd76ea4c0007e9543c2b7a930a7a96b082a1
v50_summarize.py: 4cf636ef0ec2abb6102b1ae0ceba2b30e57912b29b1f239608328e516605cccf