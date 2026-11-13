# V51 — Aprendizaje de cuatro ocupaciones complementarias en equipos sociales

Ocho poblaciones de48 personas, organizadas exógenamente en12 cliques K4, una conexión permanente a cada uno de los otros3 miembros. Cada individuo escoge libremente entre cuatro profesiones mediante una MLP privada con parámetros independientes y recompensa exclusivamente alimentaria personal. Los actores ocupacionales parten de pesos aleatorios, aprenden durante1500 actualizaciones con12 mundos, horizonte48 y posibilidad de cambiar de profesión cada8 rondas pagando0,015 por modificación. **No existe objetivo de equilibrio ocupacional, reparto profesional planificado ni premio colectivo por especializarse.**

Las políticas de regalar son **anteriores y congeladas**: LOLA20 y control NL procedentes de V47, que aprendieron por interés privado en encuentros diádicos con gradiente de aprendizaje ajeno exacto. Las donaciones no se entrenan en V51. La estructura de equipos K4 es una condición externa que favorece disponer de tres vecinos estables; no se modela elección de la red.

## Evaluación final sobre seis semillas ambientales reservadas

| Modelo | Inicio | Comida | Balance medio | Balance terminal | Tres bienes recibidos | Dones/pers. | Mejor azar profes. | Δ vs azar | Balance terminal reubicado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v51_LOLA20_D3111_R7111 | monolith | 0.8753 | 1.0000 | 1.0000 | 0.9886 | 2.9886 | 0.4018 | +0.4735 | 1.0000 |
| v51_LOLA20_D3111_R7111 | random | 0.8747 | 0.9999 | 1.0000 | 0.9872 | 2.9872 | 0.4210 | +0.4537 | 0.9994 |
| v51_LOLA20_D3111_R8111 | monolith | 0.8752 | 0.9999 | 1.0000 | 0.9885 | 2.9886 | 0.4018 | +0.4735 | 1.0000 |
| v51_LOLA20_D3111_R8111 | random | 0.8747 | 0.9999 | 1.0000 | 0.9872 | 2.9872 | 0.4210 | +0.4537 | 1.0000 |
| v51_LOLA20_D4111_R7111 | monolith | 0.8751 | 1.0000 | 1.0000 | 0.9882 | 2.9882 | 0.4018 | +0.4734 | 1.0000 |
| v51_LOLA20_D4111_R7111 | random | 0.8748 | 1.0000 | 1.0000 | 0.9875 | 2.9875 | 0.4210 | +0.4539 | 1.0000 |
| v51_LOLA20_D4111_R8111 | monolith | 0.8751 | 0.9999 | 1.0000 | 0.9881 | 2.9882 | 0.4018 | +0.4733 | 1.0000 |
| v51_LOLA20_D4111_R8111 | random | 0.8748 | 1.0000 | 1.0000 | 0.9875 | 2.9875 | 0.4210 | +0.4539 | 1.0000 |
| v51_NL_D3111_R7111 | monolith | 0.2004 | 0.2223 | 0.2488 | 0.0000 | 0.0054 | 0.2000 | +0.0004 | 0.2477 |
| v51_NL_D3111_R7111 | random | 0.2004 | 0.2323 | 0.2326 | 0.0000 | 0.0050 | 0.2003 | +0.0001 | 0.2303 |
| v51_NL_D3111_R8111 | monolith | 0.2004 | 0.2876 | 0.3281 | 0.0000 | 0.0054 | 0.2000 | +0.0004 | 0.3275 |
| v51_NL_D3111_R8111 | random | 0.2004 | 0.3038 | 0.3218 | 0.0000 | 0.0050 | 0.2003 | +0.0001 | 0.3241 |
| v51_NL_D4111_R7111 | monolith | 0.2004 | 0.1644 | 0.1672 | 0.0000 | 0.0053 | 0.2000 | +0.0004 | 0.1667 |
| v51_NL_D4111_R7111 | random | 0.2003 | 0.1684 | 0.1667 | 0.0000 | 0.0049 | 0.2003 | +0.0000 | 0.1678 |
| v51_NL_D4111_R8111 | monolith | 0.2004 | 0.2666 | 0.2922 | 0.0000 | 0.0053 | 0.2000 | +0.0004 | 0.2928 |
| v51_NL_D4111_R8111 | random | 0.2003 | 0.3079 | 0.3125 | 0.0000 | 0.0049 | 0.2003 | +0.0001 | 0.3160 |

Los12 equipos de4 miembros se consideran funcionalmente equilibrados cuando contienen exactamente las cuatro profesiones distintas. Se informa por separado su fracción promediada durante48 rondas y la fracción de equipos equilibrados al terminar la ronda48. El alimento medio es la media por persona-ronda y puede diferir del alimento terminal.

Los controles preservan pesos y decisiones de regalo, pero sustituyen la elección aprendida de oficio por conservación de ocupación inicial, cambios aleatorios a tasas0,15/0,35/0,60 y reasignación de políticas profesionales **dentro de cada equipo K4** sin reentrenamiento. Ningún control recibe cuota de profesiones ni recompensa colectiva.

## Hipótesis preregistradas

| Criterio | Resultado |
| --- | --- |
| h51a | cumple |
| h51b | cumple |
| h51c | cumple |
| h51d | cumple |

H51a exigía que≥3/4 modelos LOLA20 alcanzasen≥50% de equipos con cuatro profesiones al final y alimento medio≥0,55 desde un inicio monolítico. H51b exigía ventaja alimentaria≥+0,05 sobre el mejor cambio de profesiones aleatorio. H51c exigía que ningún control NL alcanzase simultáneamente esos dos criterios. H51d exigía≥40% de equipos profesionales completos al reasignar internamente las políticas de elección profesional.

## Validez y enmienda

El preregistro inicial no distinguía con precisión «al final» de la media temporal. Antes de evaluar los checkpoints finales se añadió la métrica terminal y se preservó el estimando temporal original, sin cambiar ni umbrales ni políticas; véase AMENDMENT_V51_TERMINAL_MEASURES.md. El commit de código usado por los entrenamientos ya activos difiere solo por las tres métricas terminales añadidas posteriormente al evaluador; no se modificó el aprendizaje.

[Inferencia] Un resultado favorable mostraría que las recompensas individuales pueden inducir especialización complementaria cuando una política cooperativa preaprendida proporciona bienes útiles. La interpretación sigue condicionada a los equipos K4 externos y la reciprocidad heredada. Una reubicación fallida sugeriría convenciones posicionales y limitaría la generalización a nuevas agrupaciones.

## Límites

No hemos demostrado la aparición simultánea desde cero de cooperación y división del trabajo: el donante LOLA fue entrenado previamente y el cálculo de gradientes del compañero es un recurso extraordinario del laboratorio. Los equipos K4 no compiten por nuevos miembros, no eligen vecinos, no existe rotación intraepisodio y tampoco se han evaluado sociedades de120 personas en esta configuración.

## Código y pruebas

Preregistro, enmienda, motor de profesión privada, auditor de políticas congeladas, ocho snapshots finales con parámetros/Adam y series longitudinales, seis semillas ambientales por condición, controles y archivos JSON; CSV de comparación y SHA256:
PREREG_V51_ENDOGENOUS_FOUR_ROLES.md: 1ae03856652db48449f6be4f5985c2629462e82894204d7fb2c3a667caba578d
AMENDMENT_V51_TERMINAL_MEASURES.md: 2f55069be8407b4749a264f3a3a930f17df091fb81281b0c3d02fb94de8cb0a4
v51_endogenous_roles.py: 339cdeec3644afbbc25d9356946330c23f4d863f2bc90eea24ad4ed1d948b185
v51_frozen_audits.py: 4fd51e79c06045b4d6994c7fb1bc2c115cfc2cd2b64cb2b0a365c5aa1468f9f6
v51_summarize.py: 4d8af45a50d9e8595b75b71d23f589bc54bd6179ae765a085c3d662c58421ce9
test_v51_endogenous_roles.py: ffcfc6697a51c873dd6b026a818492b2e68e706a00169ceaadfeeda2a17ef83f
test_v51_frozen_audits.py: d586f0f2745a71f1bae25fade533bf8ce014e84bc9b0afe84ba3cc687cd195fe