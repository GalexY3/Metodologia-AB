# V49 — ¿Puede la reputación observable restaurar los incentivos de cooperación entre desconocidos?

**Preregistro 13/11/2026, antes de ejecutar V49.** V48 ha mostrado que LOLA20 conserva ~99 % de intercambios mutuos con cambio completo de compañero por ronda, pero el efecto privado de donar se vuelve negativo. V49 ensaya si esa pérdida de retorno se debe a que la reputación no acompaña a la persona cuando cambia de interlocutor.

## Pregunta causal

¿La simple observación por parte de cada nuevo compañero de la **última acción de donación de la persona actual** —información pública individual vinculada a su autor— restaura el retorno privado del regalo inicial cuando las parejas cambian de manera exógena dentro de una trayectoria?

## Entorno e intervención

Se congelan los mismos 12 checkpoints finales V47 (NL, LOLA5, LOLA20 × semillas neuronales 3111,4111,5111,6111). Cada ronda, las48 políticas se emparejan bipartitamente entre24 especialistas tipo0 y24 tipo1, garantizando siempre parejas complementarias, según semillas y código V48. Cada persona dona voluntariamente una única unidad; alimento propio `b+v*recibe−c*dona`, b0,20, v0,55/3 y c0,04. Vida por sociedad q0,95, máximo48, gamma0,995; sin contratos, recompensas grupales ni aprendizaje adicional.

En V48 la observación «compañero donó anteriormente» corresponde a **la persona que fue mi pareja en el turno previo** (señal carry), aunque la pareja actual sea distinta. Se contrasta con una señal `public` que corresponde a **la acción efectivamente realizada el turno previo por mi pareja actual** —a quien pudo ser destinatario un tercero. Se cambia solo la **información disponible para el cálculo de la próxima acción**, no el entorno físico ni las políticas.

Controles:
- `carry`: observación V48, mismo calendario de personas y acción.
- `public`: conducta anterior real del compañero actual, vinculada a la identidad correcta; señal exacta.
- `scrambled`: conducta previa de otra persona de la **misma clase profesional** del compañero actual, elegida mediante permutación exógena para conservar la distribución marginal por especialidad pero romper su atribución individual.
- `public_noise20`: señal pública correcta pero invertida de forma independiente con probabilidad 0,20, con aleatoriedad separada.

Se prueban tasas de reemparejamiento por ronda r∈{0,25;0,60;1,00}, fijadas antes de evaluar. Todas las condiciones mantienen exógenamente los mismos mundos, secuencias de vida y posibles cambios de pareja. La incorporación de señal pública es un **servicio de información externo** diseñado por el investigador: si logra restaurar cooperación, no significa que la sociedad haya inventado ese servicio reputacional.

## Medición

Seis semillas ambientales reservadas antes de V49: `995101,995107,995109,995121,995131,995137`; 128 mundos/semilla para indicadores agregados y8 mundos/semilla para intervención causal de los48 individuos por separado. En cada par de intervención t0 sí/no, ambas ramas comparten exactamente vida, pareja, uniformes de decisión, reportes de información ajena y errores de medición. Se informará alimento por persona-ronda viva, donación mutua, socios distintos, efecto descontado propio de forzar vs prohibir la donación inicial, y fracción de agentes con efecto causal positivo. La diferencia material inmediata es exactamente−0,04.

## Hipótesis preregistradas

H49a: al menos3/4 de las políticas LOLA20 con información `public` y r1 mantienen retorno causal positivo para≥24/48 personas y mutualidad ≥0,25.

H49b: en≥3/4 de los LOLA20, `public` supera a `carry` por ≥+0,05 unidades de retorno causal privado en r1.

H49c: en≥3/4 de los LOLA20, `public` supera a `scrambled` por ≥+0,05 unidades de retorno causal en r1.

H49d: en≥3/4 de los LOLA20, la señal pública exacta supera a `public_noise20` por al menos +0,015 en retorno causal privado bajo r1.

Se reportan las cuatro hipótesis sin elegir a posteriori regímenes exitosos. El efecto de la reputación puede ser nulo o adverso incluso si ofrece más información, porque los actores no fueron entrenados con ese canal.

## Interpretación y límites

[Inferencia] Si restaurar una señal individual auténtica mejora el retorno causal de donar frente a señales falsas o heredadas de otro, tendríamos evidencia de un mecanismo de **reputación como infraestructura de apropiación temporal de reciprocidad**. Un agente que contribuye puede influir en lo que futuros compañeros están dispuestos a entregarle si reconocen su comportamiento pasado.

Esta es una prueba de transferencia de políticas congeladas a un canal reputacional introducido exógenamente: no demuestra que individuos hayan construido espontáneamente el registro, la atribución de autor ni las normas de utilización de esa información. Solo se empareja una persona por ronda y las profesiones permanecen fijas y complementarias. La prueba general exigirá aprender en redes abiertas con múltiples socios y profesiones endógenas.
