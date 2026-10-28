# ESBM v2: compatibilidad general y dinámicas de relaciones · Contrato estructural

La versión v2 [esbm_dynamic.py](esbm_dynamic.py) amplía el [ESBM v1](../ABR_INTEGRAL9_20261028/THEORY_AND_DIMENSIONS.md) solo en dimensiones **implementadas**, no en toda la teoría. Es un artefacto experimental de dinámica computacional **sin calibración externa** y NO representa frecuencias reales de orientación, identidad, rechazo o estabilidad.

## Grafo de compatibilidad y estimandos

Población ficticia N=144: 60 etiqueta F, 60 M, 24 X, permutadas al azar; además 72 agentes aceptan potenciales parejas de cualquier etiqueta, 36 con mismo marcador y 36 con uno diferente. Etiquetas y proporciones son inventadas. La arista de disponibilidad `O_ij=1` requiere que **ambas personas** incluyan la etiqueta de la otra en su ámbito aceptado; nunca se infiere orientación por identidad o apariencia. El control `heterosexual_restricted` exige solo aristas F/M, dejando X excluida por construcción. Es un **contraejemplo de exclusión institucional del diseño**, no una recomendación normativa ni muestra de patrones LGBTQ+.

En cada período `t=0..15`, las parejas activas pueden disolverse (shock independiente y hazard estipulado); las personas solteras reciben hasta `K=7` exposiciones dirigidas entre los individuos solteros compatibles. Las políticas de recomendación cambian la distribución de **candidatos mostrados**, no la definición de elegibilidad. El actor emite `A_ij(t)` y j puede contestar positivamente `R_ji(t)`, condicionados al envío de A. Solo aristas con ambos sí participan en matching exclusivista **cardinalidad máxima**, no estable de Gale–Shapley ni maximización de bienestar. El nuevo vínculo permanece hasta un shock de disolución. Un persona puede haber formado varias parejas secuencialmente, **nunca dos simultáneamente**, bajo este submodelo.

El umbral privado varía con rechazo recibido: `bias_i=min(.8,bias_i+.08)`, aumentando la probabilidad de solicitudes futuras. El módulo público introduce una penalización **artificialmente observable** `rep_i=max(-1.8,rep_i-.08)` que reduce la respuesta a futuras solicitudes de i. Son parámetros estipulados. No hay registro del mundo real que sustente una difusión automática de cada rechazo, y comparar los dos módulos **no identifica** pérdidas reputacionales reales.

La duración condicional en cada período usa riesgo `h=min(.90,(.12+.065*[grupo diferente]+.004*[distancia edad])*factor)`; escenarios `factor=.40,1,1.75`. No se han estimado probabilidades de ruptura ni se ha modelado calidad de relación, satisfacción, consentimiento continuo, infidelidad, bienestar, cohabitación o matrimonio. La media de duraciones terminadas excluye los vínculos todavía activos (censura a derecha), y es estadísticamente sesgada como estimación de duración media poblacional. Reportar simultáneamente vínculos acumulados, disoluciones y vínculos activos.

## Por qué no confundir resultados del modelo

- **Impresiones:** total dirigido sobre personas disponibles en ese período; cambia cuando las parejas se forman y dejan el mercado.
- **Solicitudes:** decisiones positivas unilaterales dentro de impresiones. La respuesta no es necesariamente otra impresión del destinatario.
- **Reciprocidad:** respuestas positivas condicionadas a solicitud.
- **Parejas formadas:** matching entre respuestas positivas; varias parejas a lo largo de 16 períodos por persona son posibles.
- **Parejas activas al final:** stock, con `formed-dissolved=active`.
- **Visibilidad:** Gini de impresiones recibidas; más cobertura/parejas no garantiza menor desigualdad de visibilidad ni bienestar.
- **Homofilia:** diferencia de grupo normativo en oportunidades vs vínculos; las normas y preferencias son parámetros distintos.
- **Población compatible:** personas con al menos otra arista de afinidad consentida, por oposición a 144 residentes ficticios.

## Comparadores y límites

10 condiciones, 6 semillas fijadas preregistradas (101,211,307,401,503,601), N=144, 16 ticks, k7. Shock de aceptación/supervivencia por `seed,t,i,j` compartido entre escenarios; **como cambian las relaciones, también cambian conjuntos de riesgo y número acumulado de impresiones**, así que contrastes pareados de escenarios son **experimentos de simulación**, no estimaciones de efectos directos a oportunidades constantes.

Alternativas aún ausentes: redes multiciudad y migración, composición cultural cuantificada, clase social e instituciones laborales/familiares reales, poder estructural y discriminación, orientación no reducible a alcance de etiquetas, calidad de relación y violencia, ingresos/tiempo de búsqueda, relación no exclusiva, metas de fertilidad, longitudinalidad humana y algoritmos de recomendación observados.

**Condición de avance de originalidad:** predicción nueva prerregistrada que supere Fong (2024), Chen (2023), Topinkova–Diviak (2025), Hu y Markowitz (2026), Büyükeren et al. (2026) y controles formales en una muestra independiente. No se alcanza con 60 corridas sobre parámetros artificiales.
