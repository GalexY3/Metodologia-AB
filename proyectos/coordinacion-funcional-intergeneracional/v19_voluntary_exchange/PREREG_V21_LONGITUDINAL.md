# V21 – Preregistro, estabilidad, repeticiones y reputación

Fecha 12-11-2026. Base local en la rama research/aldea-v19-voluntary-exchange-20261111, commit 31d553db. Este preregistro precede a V21.

**Pregunta primaria.** ¿La cooperación aprendida por redes privadas para donaciones voluntarias con coste 0,12 se mantiene al prolongar la optimización individual? ¿Aumenta la tasa de retorno individual positivo con más experiencia?

**H1 (duración).** La política entrenada con currículo de coste mantiene mayor alimentación que el entrenamiento constante para la misma semilla tras 1000 actualizaciones adicionales al coste final. Su aceptación requiere contrastes pareados y un auditor de todas las personas, no solo los índices pares.

**H2 (red social).** El efecto causal positivo de donar se mantiene cuando se redistribuyen los enlaces sociales o el número de profesiones. La estabilidad debe cuantificarse por semilla y por individuo, con diferencias de topología y número de profesiones evaluadas en las mismas poblaciones de prueba.

**H3 (identidad).** La reputación del donante observada por terceros y la recepción de favores desempeñan papeles causalmente diferentes. La retirada de señales de reputación debería reducir los retornos en una población que haya aprendido a hacer donaciones condicionales.

Se prolongarán los modelos SMOOTH y CONST para 3111/4111 con 1000 actualizaciones adicionales, usando Adam y generadores restaurados. Se mantiene el coste 0,12, arquitectura de 24 actores privados, lote 16, horizonte 32, gamma, semilla y topología. Se evaluarán escenarios congelados con k=2 y k=3, topologías circular y reconectada y observación social manipulada. Se medirá efecto de intervención sobre **24/24 agentes** con semillas ambientales no entrenadas. Antes de interpretar una diferencia se revisarán diferencias entre agentes, dependencia de la inicialización y función de distribución de retornos, no únicamente promedios.

**Criterio de objetivo.** No concluir «OBJETIVO COMPLETADO» por el solo hecho de que un modelo sea cooperativo. Se requiere robustez multi-semilla y fuera de distribución, mantenimiento tras entrenamiento, ausencia de coordinación preprogramada y eventualmente elección endógena de ocupación (hoy exógena). La validez de las estimaciones y las comparaciones de uso del mismo PRNG también deben superar auditoría.

**Control de procedencia.** No modificar archivos antiguos ni procesos en marcha ajenos. Nuevos resultados en carpetas v21_*, variables de ambiente y hashes, auditoría reproducible, pruebas de integridad y git commit explícito sin recoger archivos ajenos.
