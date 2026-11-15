# V195 neural — Retirar el apoyo contrafactual después de memorizar

15/11/2026. Namespace `WITHDRAW_COUNTERFACTUAL`, distinto de los experimentos preexistentes V195 de votación privada. V192–V194 están terminados y archivados. No se ha ejecutado ninguna continuación de este experimento. Las repeticiones de trayectorias históricas para verificar código no son observaciones nuevas.

## Incertidumbre causal

V193 mostró que, después de memorizar, una red puede generalizar mientras su interlocutor queda congelado. Conservaba un vector de31pagos contrafactuales externos. V194 mostró capacidad del estimador binario desde cero frente a interlocutores correctos suministrados. Falta comprobar si ambos agentes, con sus historias y momentos aprendidos, pueden seguir generalizando cuando se retira simultáneamente el vector y solo reciben el pago de la acción realizada.

La reducción algebraica de `docs/V194_REDUCCION_Y_PRIORIDAD_V195.md` explica el problema local después de memorizar. No se reclama como teorema original. Tampoco se reivindica originalidad de información privilegiada transitoria, curricula, importancia estadística o transferencia de entrenamiento a ejecución.

## Tratamiento y rivales

Usar los cuatro primeros checkpoints de memorización de PRIVATE_FULL de V192, elegidos exclusivamente con entrenamiento: semillas192115–192118, cortes1200,1100,1100,1200. En esos cortes ambas redes aciertan todas sus entradas locales bajo desfases opuestos aprendidos. Se conservan pesos, momentos AdamW y RNG individual. Mismos datos locales384train/577test, redes cuadráticas128, P31, epsilon.1, AdamW .001, weight_decay1, betas(.9,.98),60000pasos totales. No usar test para seleccionar cortes, parámetros ni parada.

Condición principal BOTH_BANDIT: después del corte propio, ambos aprendices reciben exclusivamente sus pagos realizados. La pérdida conocida es `(Q_U-r)^2/(31*q_U)` con probabilidad de muestreo desprendida del grafo. El mundo calcula el pago pero no construye ni entrega tablas contrafactuales. Ambos pagos proceden de acciones anteriores a las dos actualizaciones. No hay parámetros ni gradientes compartidos entre agentes o historias.

Referencia: continuaciones PRIVATE_FULL originales, final train/test conjunto1en4/4. Criterio principal previamente fijado: al menos3/4historias terminan con train conjunto codicioso>=.99 y test conjunto codicioso>=.95, y la mediana del déficit de test frente a FULL es<=.02. Evaluar el punto final60000, conservar todas las curvas, sin rescate por picos. La precisión de conducta exploratoria se informa separada: su techo es aproximadamente.8161.

Si y solo si falla ese criterio, ejecutar los dos controles ya fijados FREEZE_A_BANDIT_B y FREEZE_B_BANDIT_A desde los mismos padres. El compañero congelado permanece en su propio corte y mantiene la misma exploración. El aprendiz activo conserva sus momentos y recibe feedback binario. Cada control pasa si al menos3/4historias terminan con test LOCAL activo>=.95 y mediana del déficit frente a V193_FULL<=.02. Medir esa precisión bajo el desfase parental elegido con entrenamiento, evitando acreditar un cambio unilateral de convención. V193_FULL alcanzó1en ambas direcciones. Si la condición principal pasa, ambos controles se cancelan como no ejecutados; no se presentan como negativos.

Si el control con aprendiz único funciona y la condición conjunta falla, la interacción simultánea contribuye al fallo en esta intervención. Si ambos fallan, quedan abiertos el cambio de varianza, el estado del optimizador y la transferencia de FULL a BANDIT. No se concluirá imposibilidad fundamental del feedback privado. No reinicializar optimizadores, aumentar presupuesto ni ajustar tasas en V195.

## Igualación de relojes, auditoría y preservación

Para mantener las operaciones CUDA batch4 originales, los cortes1100reciben100actualizaciones BANDIT del tratamiento antes de combinarse en el reloj1200. Cada prefijo se calcula con cuatro copias técnicas idénticas de la misma historia y se conserva una sola: no son semillas nuevas. Los compañeros congelados no reciben pasos de optimizador. Estos prefijos forman parte del experimento y se ejecutan únicamente después del registro remoto. Se guardan estados alineados, métricas cada100pasos y pesos/momentos/RNG cada5000.

Antes del registro se exige repetir bit a bit la trayectoria BANDIT histórica5000→10000de V192 con el motor nuevo, incluyendo ambos modelos, momentos y RNG, además de comprobar pagos contra enumeración explícita y contra el motor contrafactual en fixtures. Esa repetición no prueba la hipótesis. Después, auditar las métricas finales con un forward NumPy independiente y enumeración cartesiana, así como los pesos congelados si se activan controles.

El manifiesto fija hashes de todas las dependencias ejecutadas, datos y padres. Publicar código, protocolo, auditoría técnica y manifiesto antes de entrenar; comprobar bytes HTTP remotos. Los binarios parentales ya archivados quedan fijados por hash. Un proceso GPU con35%máximo de memoria, dos hilos CPU, BelowNormal, afinidad existente y mínimo.4segundos por100actualizaciones. Preservar errores, negativos y controles cancelados.

Éxito demostraría suficiencia de un apoyo informativo transitorio en este modelo, con una historia inicial favorecida externamente. No demostraría formación binaria desde cero, invención de institución ni ley sociológica. Fracaso localizaría una dependencia que la congelación de V193 no elimina. Cuatro raíces reutilizadas no son confirmación independiente. CT2 histórico61sin cambios, rama nueva sin puntuación, N2=N3=0.
