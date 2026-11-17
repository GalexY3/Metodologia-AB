# AB 3.2.1-O8 — Grados autoevaluados (2/3\*, 3/3\*) frente a grados confirmados

**Fecha:** 17/11/2026. **Estado:** anexo normativo adoptado por decisión del investigador,
prospectivo y reversible. No modifica retrospectivamente grados ni campañas anteriores. Su
eficacia para mejorar decisiones está NO_VALIDADA. Extiende O4 §B sin cambiar su texto.

## 1. Motivo

O4 exige para 2/3 «predicción discriminante novedosa contrastada con fuentes/prior art, rival
fuerte y confirmación independiente pertinente». En la práctica aparece un estado intermedio
frecuente y valioso: el equipo ha verificado todo lo que puede verificar, pero la novedad, la
relevancia o la corrección de algunas partes solo pueden confirmarlas personas ajenas. Antes ese
estado quedaba como «candidato no concedido», sin estructura y con riesgo de inflarse o de
olvidarse. Caso que lo motivó: la rama AA/Nash de cooperacion-emergente (C05–C07, 17/11/2026),
con contraejemplo verificado en Lean, confirmado con el código original de los autores y
reconocido públicamente por el primer autor, pero sin lectura experta externa de sus
aportaciones nuevas.

## 2. Definiciones

- **2/3\* (autoevaluado).** Se cumplen TODOS los criterios de 2/3 hasta donde el equipo puede
  comprobarlos: predicción discriminante, rival fuerte, validez interna, búsqueda de prioridad
  registrada (con su alcance) y relevancia argumentada. Además se publica una **lista cerrada de
  pendientes externos**: cada elemento dice qué afirmación falta por confirmar, por qué no la puede
  confirmar el equipo y qué evidencia externa la confirmaría.
- **2/3 (confirmado).** 2/3\* cuya lista de pendientes queda resuelta con evidencia externa
  independiente: lectura experta de alguien ajeno al equipo y a sus herramientas, revisión por
  pares (también de workshop), moderación con evaluación sustantiva o réplica de terceros.
- **3/3\* y 3/3** se definen igual sobre los criterios de 3/3 de O4.
- 1/3 no cambia: no tiene asterisco.

## 3. Qué cuenta como evidencia interna y qué como externa

Cuenta como **interna** (sirve para 2/3\*, nunca para quitar el asterisco por sí sola): la
verificación formal (Lean, Coq), la re-derivación independiente dentro del equipo, las réplicas
del mismo equipo, la ejecución del código original de terceros y la confirmación entre agentes
de IA. Un verificador formal certifica la corrección del enunciado formalizado, no su
fidelidad al objeto real, ni su novedad, ni su relevancia.

Cuenta como **externa**: un juicio o una réplica de personas ajenas al equipo. Un reconocimiento
público de un autor afectado confirma exactamente la afirmación a la que responde, no las
extensiones posteriores.

## 4. Reglas

1. Contadores separados: N2\*, N2, N3\*, N3. Nunca se suman ni se informa N2\* como N2.
2. Todo informe que cite un 2/3\* debe mostrar el asterisco y enlazar su lista de pendientes.
3. Si un pendiente externo resulta desfavorable, el elemento baja de grado y se registra el
   motivo; no se reformula la lista para conservar el asterisco.
4. El asterisco no sube CT2 por sí mismo. CT2 sigue midiendo la confianza en la trayectoria.
5. Campos mínimos en el ledger: `grade_self`, `grade_confirmed`, `pending_external_checks`
   (lista), `confirmation_events` (fuente, fecha, alcance), `downgrade_events`.

## 5. Reversibilidad

Este anexo puede revertirse o sustituirse por decisión del investigador o por una evaluación
AB-META que muestre que induce inflación de grados o costes sin beneficio.
