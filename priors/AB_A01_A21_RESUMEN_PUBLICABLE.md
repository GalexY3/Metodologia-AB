# Registro resumido de priors metodológicos AB (A01–A21)

Los enunciados siguientes son hipótesis, advertencias o reglas de diseño. No implican probabilidades numéricas ni validación general de AB. Las entradas A01–A15 proceden del historial previo; A16–A21 se añaden tras BR30. Se omiten enlaces externos, identificadores personales y detalles de acceso.

## A01

AB 3.2.1 no tiene superioridad empírica acreditada frente a un investigador convencional competente de IA.

## A02

No convertir más etapas de auditoría o una puntuación total mayor en sinónimo de mayor calidad científica.

## A03

El presupuesto de confirmación y las correcciones por multiplicidad deben depender del procedimiento real de selección y del estimando, no de reglas mecánicas.

## A04

Los hallazgos causales simulados deben sobrevivir a ablaciones que eliminen el mecanismo que parece imponer el resultado.

## A05

El siguiente experimento debe aportar un tipo de evidencia más discriminante; nuevas semillas del mismo generador no aportan validación externa.

## A06

Las ramas autorizadas por BRANCHING deben contabilizar hipótesis exploradas y evidencia compartida para limitar selección retrospectiva.

## A07

AB debe registrar BARRERA_DE_ACCESO y cambiar de categoría de evidencia si falla el dataset primario, en vez de declarar replicación con resúmenes o microdatos simulados.

## A08

La fidelidad inicial del proxy debe comprobarse bajo el régimen de decisiones concreto; estar relacionado nominalmente con Y es insuficiente.

## A09

Un comparador aparentemente distinto puede resultar algebraicamente idéntico bajo el modelo y por ello no identificar un efecto.

## A10

Una interfaz que funciona y un evaluador de respuestas verificable no demuestran que el instrumento mida los procesos conductuales o el bienestar que la investigación pretende inferir.

## A11

Seleccionar entre cada vez más modelos mediante un indicador de validación estimado con pocas observaciones puede aumentar el optimismo del indicador mucho más que el rendimiento de evaluación independiente. Esto no implica necesariamente un descenso absoluto del resultado al aumentar la búsqueda.

## A12

Cuando los resultados se evalúan mediante criterios en tensión, el contraste metodológico justo compara reglas de selección con igual algoritmo, umbrales y datos. Incluso diferencias sustantivas de métricas pueden arrojar resultados indistinguibles en un dominio con buen desempeño y márgenes amplios.

## A13

La positividad es condición de identificación para estimación por propensiones, pero no garantiza precisión útil; los estimadores no normalizados pueden tener alta varianza cuando algunas probabilidades de inclusión son pequeñas.

## A14

Ante un sesgo en un sistema secuencial, comparar explícitamente una política adaptativa con una política de selección congelada es necesario para distinguir selección estática de retroalimentación.

## A15

Un contraste de políticas aprendidas con ensayo aleatorizado puede ser no concluyente aun con holdout y propensión conocida o estimada; deben auditarse la precisión, la estabilidad entre IPS y AIPW y el rendimiento predictivo de las funciones de respuesta antes de declarar que una regla supera a otra.

## A16

Mantener un registro científico versionado por proyecto en GitHub y reservar Google Drive para informes extensos, vinculando ambos mediante commits y referencias verificables, mejora la inspeccionabilidad operacional; no se ha demostrado que mejore la calidad científica frente a otra gestión competente.

## A17

Las salvaguardas de error deben corresponder a la selección, número de afirmaciones, estructura de dependencia y objetivo FWER/FDR; parar opcionalmente y corregir de forma mecánica pueden cambiar simultáneamente falsos positivos, potencia y coste.

## A18

Un posterior numérico puede ser muy preciso y estar profundamente equivocado si el prior, la verosimilitud o el conjunto de hipótesis son incorrectos. Deben documentarse sensibilidad, alternativas no modeladas y chequeos predictivos.

## A19

Ajustar variables no es automáticamente controlar confusión; colliders, mediadores, instrumentos inválidos e interferencia pueden cambiar el estimando o introducir sesgo. Declarar DAG, intervención, outcome y contraste precede al análisis.

## A20

Seleccionar características con etiquetas del test y tratar remuestreos dependientes como estudios independientes pueden producir confianza espuria aun cuando el código se ejecute correctamente; los controles deben preservar el grano y la independencia de la evidencia.

## A21

La independencia confirmatoria y las reglas de parada tienen un coste de información: pueden disminuir potencia o cambiar el objetivo. La decisión AB-DECIDE debe justificar ese coste frente a una alternativa competente, no aplicar una regla universal de partición o de parada.

## Estado

La evidencia computacional es principalmente sintética. Ninguna entrada demuestra superioridad general de AB frente a métodos competentes. Las actualizaciones deben preservar la historia y los falsadores, y distinguir resultados confirmatorios de exploratorios.
