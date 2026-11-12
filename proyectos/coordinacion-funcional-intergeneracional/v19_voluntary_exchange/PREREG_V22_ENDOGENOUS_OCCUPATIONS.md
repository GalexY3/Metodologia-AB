# V22 — Aprendizaje individual de división del trabajo (preregistro)

Fecha: 12-11-2026. Se prepara antes de entrenamientos V22.

## Pregunta

¿Pueden 24 redes privadas aprender decisiones de movilidad ocupacional que sostengan el intercambio beneficioso de V21 cuando la distribución inicial del trabajo deja de estar diseñada exógenamente?

## Arquitectura y limitaciones

Se mantiene congelada una política de donación voluntaria aprendida exclusivamente mediante recompensa individual en V21. Cada agente recibe además un actor privado, inicializado aleatoriamente, que decide si cambia de una de dos profesiones a la otra cada ocho rondas; no existe objetivo global de ocupación ni reparto normativo, y cambiar de profesión tiene un coste individual de 0,015. Las decisiones se entrenan con REINFORCE sobre el alimento propio descontado, sin un profesor de ocupaciones ni parámetros compartidos. El alcance de la prueba es N=24, k=2, redes de grado 2 en entrenamiento.

Las sociedades de aprendizaje alternan entre inicios monolíticos (todos comparten una profesión, de identidad aleatoria) e inicios aleatorios, con todas las redes ocupacionales privadas. El agente observa únicamente su alimento, roles de contactos, donaciones anteriores e historial individual de cambios. Los roles se mantienen entre rondas hasta una decisión posterior, lo que permite costes y dependencia temporal.

Esta arquitectura reutiliza una política donante preentrenada y congelada. Si funciona, el hallazgo será *aprendizaje escalonado de cooperación y división ocupacional*, no descubrimiento simultáneo desde cero.

## H1

Desde un inicio monolítico, la política aprendida para cambiar de profesión debe superar el control sin cambios y el control de cambio aleatorio en alimentación media, enlaces interprofesionales y balance ocupacional. Reportar resultados completos aunque la hipótesis fracase.

## H2

La mejora, si existe, debe sobrevivir a un grafo reconectado y un grado mayor. La señal social se ablaciona retirando observaciones al actor de donación congelado. Esto separa el éxito ocupacional de la comunicación que sostiene las contribuciones.

Se compararán dos políticas donantes congeladas V21_LONG_SMOOTH_s3111 y V21_LONG_SMOOTH_s4111, sin seleccionar nuevos pesos a partir de los casos de evaluación. Dos semillas para el nuevo actor ocupacional, entrenamiento con la misma dotación, 600 actualizaciones exploratorias (escala susceptible de extensión preregistrada posterior). Se preservan checkpoints a 1, 150, 300, 450 y 600 y registros por condición.

## Criterio de éxito

Alimentación de una población de 24 agentes y 2 profesiones por encima del control aleatorio, una fracción considerable de enlaces entre profesiones complementarias, y decisiones ocupacionales aprendidas que sigan funcionando fuera del reparto preconfigurado. La igualdad 12/12 por sí sola no basta. Un éxito en V22 todavía no demuestra cooperación universal, formación de k arbitrario ni robustez poblacional de gran escala.

No declarar OBJETIVO COMPLETADO sin corroboración sobre las dos inicializaciones, las pruebas congeladas de nuevas sociedades, integridad del código y controles de ausencia de mecanismo exógeno.
