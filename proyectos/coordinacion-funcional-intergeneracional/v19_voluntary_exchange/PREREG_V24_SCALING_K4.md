# V24 — Generalización de aprendizaje conjunto a cuatro ocupaciones

Fecha 12/11/2026. Preinscripción previa a ejecutar entrenamiento V24. Dependencia conceptual de V23, sin importar pesos de modelos V20–V23.

## Problema

El éxito local de V23 con 24 agentes y dos profesiones no permite extrapolar a sociedades con más profesiones y personas. El motor de intercambio calcula cobertura de k−1 bienes complementarios, y para k=4 se necesitan tres bienes de especialidades diferentes en una misma ronda para alcanzar la bonificación completa. Esta exigencia puede crear una barrera para la cooperación desde cero.

## Cambios explícitos de arquitectura

Se conserva el mecanismo de recompensa de V19 y su voluntariedad de donaciones dirigidas. Se generaliza el actor ocupacional de Bernoulli a Categorical con k=4 opciones de nueva profesión. Su observación local incluye frecuencias de roles en sus contactos, contribuciones públicas por tipo, la propia profesión y el historial individual. El actor donante utiliza la misma arquitectura V23 inicialmente, con percepción binaria de complementariedad, para medir la necesidad de información específica de cada categoría. La arquitectura semántica opcional se documentará y contrastará aparte.

La política de movilidad y la política de donación comienzan ambas aleatoriamente con pesos privados para cada agente. Las redes no reciben el tamaño objetivo de cada ocupación, una clasificación deseable de los enlaces ni recompensa colectiva. El método de entrenamiento sigue siendo optimización de retorno propio descontado mediante REINFORCE.

## Experimentos

Pilotos N=48, k=4, grado de red 6, 2 semillas, y ampliación N=120, k=4 con dos semillas si pasan integridad. En sociedades monolíticas iniciales los individuos deberán aprender 3 alternativas de ocupación necesarias para recibir bienes diferentes; en sociedades aleatorias aprenderán organización dinámica desde asignación desordenada.

Controles: roles fijados en ocupaciones uniformemente equilibradas, de forma exógena y explícitamente etiquetada como control; distribución aleatoria fija de roles; bloque de donaciones; cambios ocupacionales aleatorios equiprobables o con probabilidad limitada; ausencia de historial social de donaciones. Debe medirse tanto alimento como cobertura de las k−1 categorías distintas, tasas de plena cobertura, donaciones, distribución final de ocupaciones y magnitud de cambios individuales.

## H1

N=48 y k=4 presentan cooperación superior a la ausencia de donaciones y movilidad aleatoria. La ausencia de este resultado será un falsador de la escalabilidad simple de la arquitectura.

## H2

N=120 preserva retorno material, cobertura de distintas categorías y organización ocupacional frente a los controles. Es una prueba exploratoria, no una promesa de éxito; se informarán costes, dependencias e inestabilidades.

## Advertencias

La fracción de enlaces entre roles diferentes ya no cuantifica adecuadamente la complementariedad: una red con una sola especialidad distinta puede tener fracción alta y seguir sin cubrir las tres faltantes. Por ello la auditoría V24 añade la fracción de tipos complementarios distintos accesibles por vecindad y la composición ocupacional. La generalización de arquitectura y población se analiza como dos intervenciones distintas, no como réplica exacta de V23.

El objetivo general continúa abierto; la condición «OBJETIVO COMPLETADO» exige pruebas causales y robustas que alcancen cooperación y división del trabajo desde cero, sin planificador, en múltiples semillas y configuraciones.
