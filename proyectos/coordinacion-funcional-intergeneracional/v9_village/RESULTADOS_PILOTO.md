# Aldea de diez profesiones — Resultados de la primera batería MARL

Fecha de realización: 10/11/2026. **Exploratorio, no confirmatorio.** El objetivo central del usuario sigue siendo cooperación genuinamente colectiva, imposible de inferir directamente de un reparto conveniente.

## Enunciado

Población N=36 o 324 y diez profesiones equivalentes. Cada individuo recibe, exclusivamente, su recompensa personal r_i=min(n_j/(N/4),(N/4)/n_j), donde n_j es el número de personas de su profesión j. El óptimo único por tipo de reparto es cuatro profesiones de N/4 miembros cada una (4×9 o 4×81); se permite cualquier elección de cuatro etiquetas entre diez.

Cada agente usa una política tanh-RNN con 700 parámetros propios (hidden=12), memoria individual, observación de su profesión y propia comida, profesiones de d vecinos y, en las condiciones C1, mensajes simbólicos emitidos por otros. Ningún actor recibe la distribución global, el número óptimo de profesiones, la cuota 9/81, el valor de D4 ni la recompensa contrafáctica de cambiar de empleo. Las 10 profesiones son productivamente equivalentes. Los agentes actúan simultáneamente.

El aprendizaje aplica REINFORCE con retorno personal, baseline por mundos del mismo individuo y entropía. NO hay recompensa colectiva durante el entrenamiento; D4 se calcula solo como auditoría. Las señales de comunicación (silencio y cuatro símbolos) carecen de semántica programada, se transmiten a todos los vecinos y se reciben al turno siguiente.

## Batería

Piloto N=36: 120 actualizaciones; 24 sociedades por actualización; horizonte 24 turnos; evaluación de desarrollo en 48 sociedades, horizonte 40 turnos, política estocástica. Es decir, 2.880 episodios de entrenamiento por condición, de 24 turnos. Tres semillas 1411, 2522, 3533 para C0 y C1 con grado cinco; una semilla 1411 para los otros grados y el control blind.

Piloto N=324: 120 actualizaciones; 12 sociedades por actualización; horizonte 20; evaluación de desarrollo 24 sociedades y horizonte 40. Es decir, 1.440 episodios de entrenamiento en el brazo principal, con 324 políticas individuales. **Los presupuestos entre N=36 y N=324 no son equivalentes.**

Controles: aleatorio, congelado, imitación de un vecino elegido al azar y red inicial sin entrenar. Datos adicionales de evaluación de pesos congelados en dos nuevas semillas 660003,760007, 96 sociedades/semilla, 48 turnos, **post hoc**: no es el test reservado formal.

## Resultados principales de desarrollo tras 120 actualizaciones

| Modelo | N | Vecinos | Comunicación | Alimento | D4 | Grupos ocupados | Con hambre | Éxitos exactos |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| Aleatorio (control) | 36 | 5 | no | 0,4923 | 0,4141 | ~10 | 94,9 % | 0/64 |
| Blind, sin vecinos | 36 | 5 ocultos | no | 0,5000 | 0,4091 | 9,81 | 93,7 % | 0/48 |
| Grado 2, anillo | 36 | 2 | no | 0,5359 | 0,3715 | 9,46 | 90,0 % | 0/48 |
| Grado 5, anillo | 36 | 5 | no | 0,5530 | 0,3536 | 9,29 | 88,0 % | 0/48 |
| Grado 8, anillo | 36 | 8 | no | 0,5770 | 0,3299 | 9,06 | 83,2 % | 0/48 |
| Grado 5, enlaces reconfigurados | 36 | 5 | no | 0,5394 | 0,3686 | 9,46 | 88,0 % | 0/48 |
| Grado 5, con símbolos C1 | 36 | 5 | sí | 0,5043 | 0,4045 | 9,77 | 94,2 % | 0/48 |
| Aleatorio (control) | 324 | 5 | no | 0,4110 | 0,5374 | ~10 | 100 % | 0/64 |
| Grado 5, anillo | 324 | 5 | no | 0,5789 | 0,3326 | 9,96 | 95,3 % | 0/24 |

La métrica D4 representa solo un criterio externo de evaluación; no está en la recompensa de ningún actor. El umbral «hambre» es r_i<0,85, sin fallecimientos. Los promedios de alimentación no incluyen el caso ideal 1 en ningún brazo.

La regla de imitación local NO es una garantía de mejora. Entre 36 agentes, produjo alimento medio 0,671 con grado 2, pero solo 0,443 con grado 5 y 0,415 con grado 8. En N=324, con grado 5 produjo 0,601, mostrando fuerte dependencia de escala y red. Ningún caso obtuvo reparto exacto.

## Replicación inicial con tres semillas independientes

Grado cinco, N=36, misma configuración y semillas emparejadas en C0 sin comunicación y C1 con comunicación.

| Semilla | C0 sin mensajes | C1 con mensajes |
|---|---:|---:|
| 1411 | 0,5530 | 0,5043 |
| 2522 | 0,5146 | 0,5051 |
| 3533 | 0,5218 | 0,5123 |
| Media | 0,5298 | 0,5072 |

En este presupuesto de entrenamiento, C1 no supera C0. No se pretende demostrar perjuicio causal de comunicación: la condición comunicativa tiene mayor espacio de exploración, produce mensajes con semántica no preestablecida y se evaluó con tres semillas. Todas obtuvieron 0/48 soluciones exactas.

## Dinámica de entrenamiento N=324

En N=324, la política estocástica pasó de ~0,412 raciones al inicio a 0,6306 en la actualización 110, pero en la 120 retrocedió a 0,5789. La proporción hambrienta en el último registro alcanzó 95,3 % y las diez profesiones siguieron casi completamente ocupadas (9,96 de media).

El resultado refleja aprendizaje incompleto e inestabilidad. Reducir el error respecto al azar no equivale a organizar cuatro profesiones viables, y menos a establecer coordinación cooperativa causal.

## Comprobación post hoc en sociedades nuevas

Se congelaron los checkpoints finales y se evaluaron sobre 192 sociedades adicionales por brazo (96 para cada una de dos nuevas semillas), con 48 turnos. Los resultados promediados de alimento fueron aproximadamente:

- N=36, grado 5, sin mensajes: 0,5659; 0,5285; 0,5181, media 0,5375.
- N=36, grado 5, con mensajes: 0,4973; 0,4996; 0,5059, media 0,5009.
- N=36, sin observación de vecinos: 0,5026 en política estocástica, pero 0,6730 en política determinista.
- N=36, grado 8, sin mensajes: 0,5915.
- N=324, grado 5, sin mensajes: 0,5754.
- No se observó un único reparto exacto en estas evaluaciones.

La política determinista del control blind puede parecer notablemente eficaz aun sin observar vecinos: ese comportamiento **no demuestra cooperación**. Puede producirse organización distributiva por adaptaciones de agentes independientes a la recompensa y por diferencias de pesos, posiciones fijas y etiquetas memorizadas. Este hallazgo hace imprescindibles las pruebas de generalización social y de causalidad comunicativa.

En el brazo C1 se comparó retrospectivamente la misma red con mensajes desactivados. La alimentación media resultó aproximadamente 0,505–0,510 sin mensajes y 0,497–0,506 con mensajes. Esta maniobra modifica la secuencia de números aleatorios del proceso estocástico; NO debe venderse como contraste causal limpio sin nuevas intervenciones emparejadas.

## Conclusión provisional

El nuevo enunciado permite ejecutar 324 agentes con pesos neuronales individuales y recompensas de supervivencia propias. Se observa progreso parcial de alimentación y una posible relación con la estructura local. No aparece todavía el resultado final deseado: **cuatro profesiones elegidas colectivamente, con 81 habitantes por profesión y equilibrio duradero**. Ningún resultado permite afirmar que las redes hayan aprendido negociación o cooperación en sentido fuerte.

Los datos invitan a separar cambios de arquitectura, información social, número de vecinos y exploración temporal, y a estudiar coordinación intertemporal, riesgo de fundación de profesión vacía, memoria y mensajes útiles. No aumentar simplemente la red o el número de episodios sin especificar nuevos controles.

El software, los checkpoints de cada brazo, las curvas, el visor HTML portable y los resultados se conservan en este directorio del repositorio GitHub.
