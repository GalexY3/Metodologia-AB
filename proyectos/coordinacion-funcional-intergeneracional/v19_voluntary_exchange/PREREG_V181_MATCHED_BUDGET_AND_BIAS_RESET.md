# V181 — Presupuesto total y reinicio de intercepto

15/11/2026. Todos los resultadosV175–V180 son conocidos y están publicados. La comparación secundaria V178afín desde cero(3000generaciones) frente aV180FULLpreparada+OPEN(6000totales) no iguala presupuesto total. La conclusión principalV180 de solo1/8colapsos es válida para su intervención emparejada; no equivale a demostrar superioridad de un currículo frente a6000generaciones de la representación ampliada.

## A–C. Pregunta y controles

¿La ventaja de preparar una política sin intercepto persiste al igualar generaciones y frente al reinicio del intercepto de una política afín ya entrenada? No es una arquitectura nueva ni confirmación independiente. Es una corrección prospectiva del contraste interpretativo, posterior a observarV180.

Usar las8poblaciones AFFINE_FULL finales deV178, semillas178115–178122. Continuar3000generaciones adicionales con semillas180115–180122,en el mismo emparejamiento y con la misma cinta inicial de continuación que losOPEN deV180. Dos brazos:

- CONTINUE: conservar sus tres genes, incluido intercepto evolucionado.
- RESET_BIAS: misma población y reiniciar únicamente intercepto a0 antes de continuar. No reiniciarlo después; vuelve a mutarN(0,.1) en cada generación.

Los dos brazos usan siempreAFFINE_FULL,100grupos×5personas,1000pasos y fitness privado pasos100–999. Mutar todos los3genes, reproducción proporcional y reasignación comoV178/V180. Guardar todas las curvas,poblaciones,RNG y6checkpoints de continuación. Reutilizar el control existenteOPEN deV180; no contarlo como una observación nueva. Cada trayectoria total tiene6000generaciones. La intervención histórica FULL→OPEN incluye haber mantenido el intercepto neutral antes y haberlo inicializado a0 al activarlo; no atribuirla a un único componente si el control de reinicio produce lo mismo.

Antes de entrenar, verificar los hashes originales de las16poblaciones fuente (FULL yAFFINE_FULL), queRESET cambia solo el tercer gen, y que la primera generación de continuación calculada conFULL reproduce exactamente la primeraQdeOPENV180 usando su misma semilla. Kernel físicoV178 permanece congelado y previamente auditado; no se altera.

## D–G. Criterios y límites

Primario de ventaja histórica robusta: mediana pareada de Q_OPEN_V180−Q_CONTINUE≥.20 y signo positivo en al menos6/8pares, Y el mismo criterio frente aRESET_BIAS. Informar las24cantidades (8controles previos+16continuaciones nuevas). Si el controlCONTINUE recupera altaQ, duración puede explicar parte de la diferencia. SiRESET_BIAS basta, no atribuir la ventaja exclusivamente al aprendizaje previo deS,A. Si ninguno basta, la instancia de trayectoria tiene un rival de presupuesto más fuerte; la prioridad general de currículo y dependencia histórica sigue sin acreditarse.

Qes media de últimas500generaciones de la continuación. No escoger checkpoints favorables, prolongar más ni ampliar automáticamente tras un negativo. Unidad de comparación:8historias originales emparejadas; no16nuevas poblaciones independientes de todo lo anterior. No pruebas de equivalencia basadas solo en cercanía puntual.

## H–J. Registro

Auditoría causalD1 deV180. Congelar protocolo,código y auditoría en remoto antes de continuar. Máximo2workers×3threads,BelowNormal,seisCPU. Mantener los archivosV175–V180 y sus dos publicaciones, incluida corrección de bytes, intactos. CT2histórico61,N2=N3=0 sin incremento. La investigación global sigue activa.
