# V53 — ¿Merecen la pena materialmente los mecanismos de regulación inspirados en Stafford Beer?

## Naturaleza de la contrastación

Experimentamos con **proxies reguladores costosos** inspirados en el VSM y Ashby; no aplicamos el VSM en su forma íntegra. La producción S1 es un límite deliberadamente favorable de la sociedad V25/V51/V52: 48 personas ya diferenciadas en 12 equipos K4, cuatro especialidades por equipo, todos los trabajadores operativos entregan un bien a cada miembro vivo que lo necesita. No se aprendieron roles, convenios o reguladores nuevos en este experimento. **Alimento máximo sin perturbación: 0,88 por persona-ronda**. El valor real de cada supuesto beneficio se calcula con pérdidas del 5 % del volumen transferido y costes administrativos deducidos del alimento, y se mide supervivencia hasta la ronda96.

Se añade una ecología explícita que no existía en V25: reservas por persona inicialmente1,2, máximo2,2, consumo de subsistencia0,75 por ronda, muerte irreversible si las reservas se agotan, productores temporalmente incapacitados que consumen pero no envían bienes. La muerte elimina la capacidad productiva del especialista de su equipo y puede desencadenar cascadas. No hay intercambio de alimentos entre mundos ni dinero artificial creado por regulación.

Se simularon32 escenarios (4 distribuciones de perturbaciones ×8 regímenes de gestión), con seis semillas ambientales nuevas y128 mundos por semilla en cada combinación: **24.576 sociedades y2.359.296 rondas-sociedad**. Los episodios de fallo productivo son idénticos entre regímenes para cada pareja semilla/mundo. Las unidades individuales dentro de un mundo comparten shocks y no son réplicas independientes.

## Alimentación y supervivencia por arquitectura

| Entorno | Regulación | Población viva al final | Equipos completos al final | Alimento neto/persona viva | Fracción de persona-rondas vivas |
| --- | --- | --- | --- | --- | --- |
| QUIET | NONE | 1.0000 | 1.0000 | 0.8800 | 1.0000 |
| QUIET | LOCAL | 1.0000 | 1.0000 | 0.8760 | 1.0000 |
| QUIET | GLOBAL | 1.0000 | 1.0000 | 0.8720 | 1.0000 |
| QUIET | LOCAL_GLOBAL | 1.0000 | 1.0000 | 0.8680 | 1.0000 |
| QUIET | FORECAST | 1.0000 | 1.0000 | 0.8600 | 1.0000 |
| QUIET | PLACEBO | 1.0000 | 1.0000 | 0.8600 | 1.0000 |
| QUIET | POLICY | 1.0000 | 1.0000 | 0.8650 | 1.0000 |
| QUIET | FULL_PROXY | 1.0000 | 1.0000 | 0.8570 | 1.0000 |
| PATCHY | NONE | 0.0796 | 0.0750 | 0.7697 | 0.3864 |
| PATCHY | LOCAL | 0.3364 | 0.3347 | 0.7803 | 0.6261 |
| PATCHY | GLOBAL | 0.0798 | 0.0705 | 0.7405 | 0.5105 |
| PATCHY | LOCAL_GLOBAL | 0.9148 | 0.9140 | 0.7687 | 0.9655 |
| PATCHY | FORECAST | 0.8050 | 0.8034 | 0.7612 | 0.9215 |
| PATCHY | PLACEBO | 0.7903 | 0.7886 | 0.7610 | 0.9100 |
| PATCHY | POLICY | 0.8728 | 0.8719 | 0.7655 | 0.9471 |
| PATCHY | FULL_PROXY | 0.7445 | 0.7431 | 0.7583 | 0.8911 |
| SYSTEMIC | NONE | 0.0062 | 0.0062 | 0.7241 | 0.2187 |
| SYSTEMIC | LOCAL | 0.0433 | 0.0424 | 0.7383 | 0.3399 |
| SYSTEMIC | GLOBAL | 0.0047 | 0.0039 | 0.7186 | 0.2129 |
| SYSTEMIC | LOCAL_GLOBAL | 0.0341 | 0.0334 | 0.7311 | 0.3201 |
| SYSTEMIC | FORECAST | 0.0261 | 0.0255 | 0.7241 | 0.3046 |
| SYSTEMIC | PLACEBO | 0.0268 | 0.0262 | 0.7244 | 0.3044 |
| SYSTEMIC | POLICY | 0.0318 | 0.0311 | 0.7290 | 0.3156 |
| SYSTEMIC | FULL_PROXY | 0.0241 | 0.0235 | 0.7216 | 0.2985 |
| HEAVY | NONE | 0.0000 | 0.0000 | 0.6594 | 0.1309 |
| HEAVY | LOCAL | 0.0003 | 0.0003 | 0.6782 | 0.1771 |
| HEAVY | GLOBAL | 0.0000 | 0.0000 | 0.6481 | 0.1313 |
| HEAVY | LOCAL_GLOBAL | 0.0001 | 0.0001 | 0.6689 | 0.1808 |
| HEAVY | FORECAST | 0.0001 | 0.0001 | 0.6626 | 0.1712 |
| HEAVY | PLACEBO | 0.0001 | 0.0001 | 0.6627 | 0.1723 |
| HEAVY | POLICY | 0.0001 | 0.0001 | 0.6664 | 0.1744 |
| HEAVY | FULL_PROXY | 0.0001 | 0.0001 | 0.6599 | 0.1655 |

**Advertencia sobre denominadores:** alimento neto por persona *viva* es una intensidad condicionada a supervivencia y puede subir cuando mueren personas dependientes; la métrica no debe usarse aisladamente para clasificar regímenes. Para cada celda también se informa el total de persona-rondas vivas y el alimento neto por persona inicial-ronda, evitando el sesgo de supervivencia. La supervivencia final y los equipos aún productivos son los resultados de viabilidad.

## Interacciones de las funciones y controles de información

Los proxies son: NONE (sin regulador); LOCAL (ayuda dentro de K4, coste0,004/persona/ronda); GLOBAL (traslados entre equipos con retardo de un turno, coste0,008); LOCAL_GLOBAL (ambos); FORECAST (+0,008 con información verdadera del siguiente shock); PLACEBO (misma función/coste que FORECAST, pero señal del shock atribuida a otros equipos); POLICY (+0,003 por umbral común de reserva adaptativo); FULL_PROXY (LOCAL_GLOBAL+FORECAST+POLICY). Todas las transferencias pagan pérdida material del 5 %, y el alimento queda en stocks conservativos. El lugar de llegada y la disponibilidad de almacén limitan el resultado efectivo.

| Contraste PATCHY | Δ supervivencia | IC descriptivo 95% bajo | IC descriptivo 95% alto |
| --- | --- | --- | --- |
| LOCAL_minus_NONE | 0.2568 | 0.2517 | 0.2616 |
| GLOBAL_minus_NONE | 0.0003 | -0.0053 | 0.0058 |
| LOCAL_GLOBAL_minus_LOCAL | 0.5785 | 0.5633 | 0.5911 |
| LOCAL_GLOBAL_minus_GLOBAL | 0.8350 | 0.8248 | 0.8452 |
| FORECAST_minus_LOCAL_GLOBAL | -0.1099 | -0.1154 | -0.1042 |
| FORECAST_minus_PLACEBO | 0.0147 | 0.0100 | 0.0182 |
| POLICY_minus_LOCAL_GLOBAL | -0.0421 | -0.0447 | -0.0394 |
| FULL_PROXY_minus_LOCAL_GLOBAL | -0.1703 | -0.1788 | -0.1601 |
| FULL_PROXY_minus_NONE | 0.6650 | 0.6596 | 0.6709 |

La interacción material observada en PATCHY entre LOCAL y GLOBAL equivale a **+0.5782** de supervivencia adicional más allá de sumar las mejoras individuales (comparadas contra NONE). Es una *interacción factorial bajo esta parametrización*, no una ley universal de complementariedad jerárquica.

## Hipótesis preregistradas

| Hipótesis | Estado |
| --- | --- |
| h53a_local_improves_patchy_by_5pp | cumple |
| h53b_global_plus_local_improves_over_local_by_5pp | cumple |
| h53c_forecast_improves_over_local_global_by_3pp | no cumple |
| h53d_forecast_at_least_placebo_patchy | cumple |
| h53e_no_administration_cost_under_quiet | cumple |
| h53f_full_proxy_not_perfect_under_systemic | cumple |

H53a y H53b contrastan utilidad material de ayuda local e interequipos. H53c exigía ventaja de anticipación de shocks sobre la regulación reactiva, **una hipótesis que puede ser falsada** por costes y por la calidad del mecanismo de transferencia. H53d requiere que un mensaje correcto iguale o supere a un placebo con información atribuido a otros equipos; no se sustituye por la afirmación de que el pronóstico sea necesariamente útil. H53e prueba penalización real de administrar en un mundo estable. H53f verifica que añadir canales regulatorios no equivale a capacidad material ilimitada en un entorno de perturbaciones sistémicas.

## ¿En qué sentido cuestiona o respalda a Beer?

[Inferencia] Esta prueba apoya la idea general de que integrar funciones de coordinación a diferentes escalas **puede** incrementar la resiliencia material cuando las perturbaciones son heterogéneas y los excedentes transportables. No demuestra que las cinco funciones de Beer sean necesarias o suficientes, porque solo se implementan proxies parciales y porque las especialidades S1, la red y el suministro cooperativo se fijaron externamente.

[Inferencia] La disminución de supervivencia bajo FORECAST y FULL_PROXY en PATCHY, respecto de LOCAL_GLOBAL, apunta a rendimientos negativos de algunas capas adicionales con un diseño concreto de mensajes, costes y políticas. El hecho de que NONE sea viable sin gestión en QUIET **no refuta** el VSM en términos generales: puede haber funciones implícitas, además de que viabilidad depende de entorno, escala y criterio de supervivencia.

Asimismo, el colapso en HEAVY sugiere un límite por falta de recursos y redundancia productiva —el entorno K4 dispone de un único productor por especialidad—. Un regulador no puede reponer bienes inexistentes mediante comunicación. La ley de variedad requerida de Ashby funciona aquí como inspiración para estudiar la capacidad de regulación y la diversidad de perturbaciones; V53 no constituye una deducción formal de ese teorema.

## Alcance hacia emergencia sociológica

No hay emergencia de un S2–S5 espontáneo. V53 responde a una pregunta material previa: si se incorporase una capacidad de coordinación o anticipación, ¿existiría algún beneficio suficiente para compensar su coste? El siguiente experimento debe permitir a los individuos escoger, financiar y abandonar mecanismos de coordinación, con controles de información y de beneficio privado, para distinguir la aparición endógena de instituciones de su imposición experimental.

## Fuentes teóricas

Beer, S. (1984). *The Viable System Model: Its Provenance, Development, Methodology and Pathology*. JORS. https://doi.org/10.1057/jors.1984.2

Crisan Tran, C. I. (2008/2009). *Assessing the Viable System Model: an empirical test of the viability-hypothesis*. https://doi.org/10.1504/IJASS.2008.022795

Schwaninger, M. y Scheef, C. (2016). *A Test of the Viable System Model: Theoretical Claim vs. Empirical Evidence*. https://doi.org/10.1080/01969722.2016.1209375

Ashby, W. R. (1956), cibernética y ley de variedad requerida. https://ashby.info/Ashby-Mechanisms_of_intelligence.pdf

## Reproducción

PREREG_V53_VSM_MATERIAL.md, v53_vsm_material.py, test_v53_vsm_material.py, v53_material_raw.json con cada mundo y cada semilla, COMPARACION_V53.csv, CONTRASTES_V53.csv, METRICAS_V53.json y este informe. SHA256:
PREREG_V53_VSM_MATERIAL.md: 35da87f1b22fd88592ad85c4b23328349c35796fc4217174092e3087548595cb
v53_vsm_material.py: 95dce892d6281e075110252ff6b1d445b0dffc5d39a16c5dbf9d1ac8fe2d43ef
test_v53_vsm_material.py: f8ca5ae9643e8200167e9dfdb633fecdd17a107749f907110e171a2501970315
v53_summarize.py: be7e1a9e7b35ad9cd0156451a319e5a9210ccb75635766e7a109f939c0127b63