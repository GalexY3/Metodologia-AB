# Reducción del feedback después de memorizar y siguiente prueba

15/11/2026. Nota derivada después de cerrar el archivo V191–V194. No modifica sus datos ni su informe. La reducción es algebraica y no se reclama como teorema original. La prueba siguiente todavía no se ha registrado ni ejecutado.

## Qué problema recibe el aprendiz cuando el compañero ya memoriza

Se comprobaron los cuatro checkpoints parentales originales. En sus cortes1200,1100,1100,1200, ambas redes aciertan el100%de sus entradas locales de entrenamiento bajo desfases opuestos. Los desfasesAson14,25,10,0.

Sea j un compañero congelado que, sobre sus entradas de entrenamiento, elige codiciosamente `u_j=f_j(x_j)+g_j modP`. Mantiene exploración epsilon-greedy: con probabilidad1−epsilon usa esa acción y, con probabilidadepsilon, una acción uniforme. El pago contrafactual propio de i vale1cuando `m+u_j=f_i(x_i)+f_j(x_j) modP`. Por sustitución,

`E[R_i(m)|x_i]=(1−epsilon)*1[m=f_i(x_i)−g_j]+epsilon/P`.

La acción ganadora revelada por el vector contrafactual tiene, por tanto, la distribución de una etiqueta local correcta desplazada por un desfase aprendido, con ruido uniforme. Es la misma ley marginal de clasificación local que en el control oráculo, salvo la permutación de clases. No exige que el compañero generalice en sus entradas retenidas: durante aprendizaje se muestrean sus entradas conocidas.

La igualdad de leyes de datos no garantiza curvas iguales entre modelos con historias y momentos diferentes. En V193 se conservan precisamente las historias parentales y los estados de Adam. El resultado empírico es más específico: las redes activas coinciden bit a bit con sus continuaciones conjuntas en los checkpoints comparados. La reducción explica por qué este juego permite tal resultado; no es una demostración sobre otros juegos o instituciones.

## Cuello de botella que permanece

La formación de convenciones PRIVATE_FULL ocurre con una infraestructura contrafactual suministrada externamente. V193 prueba que puede congelarse al interlocutor después de memorizar; no prueba que pueda retirarse esa información rica. V194 prueba que el algoritmo binario puede aprender con interlocutores correctos desde inicializaciones nuevas; no prueba que dos aprendices coadaptándose sigan estables al cambiar simultáneamente su feedback y conservar sus momentos previos.

La prueba de validez prioritaria antes de una reivindicación de autonomía es retirar FULL después de la primera memorización y continuar ambos agentes solo con pagos realizados. Debe registrarse antes de ejecutar: usar los cuatro cortes ya seleccionados por entrenamiento, mantener los60000pasos totales, comparar con las continuaciones FULL existentes y medir entrenamiento, test local y conjunto. Si falla, los controles con un solo aprendiz binario y compañero congelado distinguirían incapacidad del componente, cambio de estado del optimizador y realimentación entre compañeros. Estos controles han de fijarse antes de observar el resultado, sin rescate mediante tasas nuevas.

Un éxito demostraría que un apoyo informativo transitorio basta en este modelo. Seguiría siendo una historia de formación favorecida por el investigador, no una institución inventada ni formación desde cero con feedback binario. Un fallo localizaría una dependencia que la congelación de parámetros no elimina. Ninguno de los dos resultados acredita por sí solo originalidad2/3.

El reparto fijo o rotativo de un presupuesto de feedback igualado sigue siendo otra incertidumbre prometedora para estudiar funciones informativas. Sus roles serían asignados externamente. Antes de convertirlo en contribución original harían falta rivales fuertes sobre ruido, tasas heterogéneas, precondicionamiento Adam y aprendizaje con información privilegiada, además de una predicción discriminante y confirmación independiente.

Esta nota es una decisión de prioridad y una reducción verificable, no un ciclo experimental completado. CT2 histórico61, rama nueva sin puntuación, N2=N3=0. El objetivo global permanece activo.
