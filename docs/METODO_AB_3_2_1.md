# AB 3.2.1 — Protocolo de investigación abductivo-bayesiana contextual

**Fecha:** 19 de octubre de 2026. **Estado:** revisión metodológica provisional posterior a doce contrastes planificados y cinco contrastes adversariales adaptativos. **No se declara método superior demostrado ni descubrimiento original de nivel 2/3.**

## 1. Propósito

Utilizar IA, herramientas estadísticas, literatura y experimentos para generar, confrontar y revisar explicaciones del mundo. La verdad científica relevante, la identificación del estimando y la validez de la evidencia preceden al volumen de hallazgos, la apariencia de creatividad o la productividad del sistema. AB es reemplazable. La metodología no debe convertir su supervivencia ni el número de ciclos en objetivos intrínsecos.

La estructura científica básica de AB 3.2 se mantiene; 3.2.1 añade cinco reparaciones operacionales motivadas por la campaña AB–Goodhart 2026-10-19. **Estas reparaciones son compromisos de diseño razonables, no descubrimientos de eficacia end-to-end para LLMs.**

## 2. Reparaciones respecto a AB 3.2

**R1. Estimando primero, estadístico después.** Cada pregunta debe declarar unidad, población, tratamiento, comparación, outcome verdadero, outcome proxy, interferencia y criterio de daño. No puede utilizarse un contraste de medianas o signos para sostener una afirmación sobre la media. No confundir caída de correlación M-Y con daño absoluto Y.

**R2. Comparador competente y paridad informativa.** La evaluación de AB no puede utilizar un control deliberadamente ingenuo que ignore datos disponibles. Como mínimo comparar: (i) análisis convencional competente que utilice los mismos datos; (ii) un protocolo completo AB; (iii) controles nulos con la misma información, presupuesto, tiempo y criterios. La ganancia debe atribuirse a la metodología, no al acceso desigual al outcome verdadero ni a más cómputo.

**R3. Corrección por multiplicidad condicionada a lo que realmente se reivindica.** Registrar el árbol de selección exploratoria, el número de afirmaciones confirmatorias, independencia entre desarrollo y confirmación y el riesgo de reutilización. Si se selecciona exactamente una hipótesis sobre un piloto y se contrasta **una sola vez** en una muestra nueva verdaderamente independiente, una prueba de nivel 0,05 puede controlar el error de esa afirmación sin dividir necesariamente 0,05 entre todas las candidatas descartadas. Si se presentan varias afirmaciones, se reutiliza el holdout o se hacen múltiples análisis adaptativos, corresponde otra contabilidad del error. No aplicar Bonferroni por reflejo ni omitirla por comodidad.

**R4. Descomponer la dependencia de los resultados respecto al mecanismo impuesto.** Para cada hallazgo de simulación, incluir ablación específica que quite o invierta su supuesto generador: sin costo de fraccionamiento, sin escasez de presupuesto, indicador perfectamente fiel, canal estratégico deshabilitado, ruido distinto, congestión baja. Si la pérdida desaparece al retirar una penalización estipulada, la pérdida no está descubierta: estaba codificada.

**R5. Gobernanza orientada al cuello de botella de evidencia.** AB-DECIDE puede cerrar una campaña antes de usar los ciclos autorizados. Continuar solo si una nueva clase de observación, agente o intervención permite distinguir hipótesis donde las corridas existentes no pueden. Un cupo no es un objetivo; una falta de datos de campo no se corrige con mil semillas adicionales del mismo generador.

## 3. Ciclo operativo AB

**A. Pregunta y contrato de verdad.** Definir fenómeno, variables, cómo se identificaría lo real y qué datos están efectivamente disponibles. Especificar supuestos no verificables y su impacto.

**B. Hipótesis rivales abiertas.** Registrar hipótesis preferida, nula, contraejemplos plausibles y H_otras. Diferenciar lo heredado de literatura, lo deducido matemáticamente y lo especulado.

**C. Experimento discriminante.** Elegir intervención, contrafactual, potencia, medición y controles. Prematricular estimando, tamaño de presupuesto, endpoints y condiciones de aceptación. No optimizar un único score de novedad.

**D. Instrumentación y diagnóstico.** Probar que el código mide el estimando, verificar invariantes, recalibrar pruebas ante asimetría o colas pesadas, controlar seeds, versiones y pérdidas. Invalidar inmediatamente un ensayo si cambia implícitamente el objetivo.

**E. Exploración bajo presupuesto.** Ejecutar. Medir también intentos fallidos, hallazgos que no generalizan y sensibilidad a supuestos. Explorar ≠ confirmar.

**F. Auditoría adversarial con alternativas competentes.** Un revisor o procedimiento separado intenta explicar el resultado como bug, confusión, data leakage, ejemplo construido, extrapolación, corrección estadística errónea, sesgo de selección o antecedente publicado. Cualquier mejora debe sobrevivir a un baseline razonable.

**G. Confirmación.** Nuevas semillas o datos no utilizados para elegir hipótesis, con distinción entre nuevas realizaciones del mismo generador y auténtica replicación externa. Medir tamaño del efecto y error, no solo significación.

**H. Doble actualización abductivo-bayesiana.** (1) Revisar hipótesis existentes con likelihood/prior defendibles o actualización cualitativa; (2) generar hipótesis nuevas motivadas por anomalías. La observación usada para inventar H_nueva no confirma de modo independiente H_nueva. Registrar lo que sorprendió, lo que no cambia, lo que refutamos y qué ensayo siguiente discrimina.

**I. Dictamen por dimensiones.** Separar: validez interna, identificación causal, transportabilidad, novedad científica, importancia, calibración, reproducibilidad, coste y ética. No sumar todas a una puntuación arbitraria que se pueda gamificar.

**J. AB-DECIDE.** CONTINUE, STOP, PIVOT o REPAIR con presupuesto de evidencia y razón explícita. Solicitud humana solamente si se justifica; formato en última línea cuando corresponda: `SOLICITUD DE X CICLOS EXTRA`.

## 4. Roles posibles de agentes IA

- **Proponente:** genera hipótesis y predicciones rivales, no puntúa su propio éxito.
- **Diseñador experimental:** identifica test falsable, estimando, presupuesto y baseline.
- **Implementador:** codifica exclusivamente lo congelado y ejecuta invariantes.
- **Auditor:** busca errores lógicos, presupuestarios, leakage y relaciones tautológicas, con capacidad de invalidar experimentos.
- **Analista estadístico:** responde al estimando, verifica calibración y multiplicidad.
- **Revisor de literatura:** confronta novedad aparente contra resultados previos y contraejemplos, con fuentes verificables.
- **Coordinador AB-DECIDE:** recomienda parar, continuar o cambiar de evidencia.
- **Investigador humano:** autoriza recursos y evalúa importancia, riesgos y decisiones de publicación.

La separación de roles no demuestra independencia estadística: si todos los agentes comparten modelo, contexto y fuentes, también pueden compartir errores. Registrar y contrastar esta dependencia.

## 5. Registro mínimo por ensayo

`id, parent_id, claim, estimand, null, rivals, assumptions, predicted_discriminant, falsification_rule, prereg_timestamp, budget, rng_seeds, code_commit_hash, source_refs, controls, negative_controls, observed_primary_endpoint, heterogeneity, validity_audit, selection_exposure, holdout_status, errors, external_replication_status, novelty_review, decision, value_of_next_evidence`.

Un ensayo recibe etiquetas independientes: `DESIGNED`, `RUN`, `INVALID`, `SUPPORTED_WITHIN_MODEL`, `REFUTED_WITHIN_MODEL`, `INCONCLUSIVE`, `EXTERNAL_CONSISTENCY`, `EXTERNAL_IDENTIFIED_EFFECT`. Esta última requiere diseño empírico identificador adecuado; una simulación sin datos de campo no puede obtenerla.

## 6. Grados de hallazgo

**Resultado matemático:** identidad bajo supuestos. Puede ser relevante pero no novedoso por defecto.

**Resultado computacional condicionado:** obtenido y auditado en un generador; no equivale a efecto empírico.

**Resultado empírico observado:** descripción de datos de humanos/instituciones, con sesgos y validez externa discutidos.

**Resultado causal empírico:** deriva de intervención aleatorizada o diseño de identificación argumentado; no lo aporta únicamente una simulación.

**Candidato a descubrimiento LARP 2/3:** requiere revisión de estado del arte, predicción discriminante novedosa, prueba con controles competentes, replicación fuera del entorno usado para formularlo e importancia científica. La escala de 'niveles' es interna; no existe verificación aquí.

## 7. Lecciones negativas de la campaña

La comparación C11 dio 100% de clasificaciones correctas al procedimiento que utilizaba Y y solo 50% al que miraba M; esto NO demuestra eficacia propia de AB, sino superioridad de utilizar la variable relevante. El control adicional C17 con igual información dio 82,78% a una regla AB compleja y 99,11% a un comparador sencillo. El desempeño depende del estimando y de la regla de decisión, y una restricción adicional puede introducir falsos negativos.

El contraste C15 demostró que en un modelo de publicaciones la degradación de la calidad desaparecía exactamente al retirar el coste asignado a fragmentar publicaciones. No reivindicarlo como 'emergencia' ni como constatación de efectos reales de bibliometría.

El contraste C13 mostró que, si solo se confirma una hipótesis preregistrada usando una muestra nueva independiente, Bonferroni para las 24 alternativas exploradas puede ser innecesariamente conservadora. No extrapolar a publicación adaptativa de varias afirmaciones.

## 8. Estado AB-DECIDE

**PIVOT A DATOS HUMANOS Y BENCHMARKS REALES; STOP en el generador sintético actual.** Diecisiete ciclos ejecutados en esta campaña: doce planificados y cinco de auditoría adaptativa. Siete autorizaciones de ciclos extra no consumidas. No hace falta otra batería artificial para decidir qué pasó dentro de estos generadores: hace falta un nuevo tipo de evidencia.

