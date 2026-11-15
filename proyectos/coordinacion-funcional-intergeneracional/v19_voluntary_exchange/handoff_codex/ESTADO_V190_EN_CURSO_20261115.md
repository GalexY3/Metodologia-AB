> FINALIZADO. El proceso terminó; consultar ESTADO_20261115_V190.md. Se conserva debajo el estado transitorio original.

# V190 en ejecución — conservar el proceso original

Estado transitorio. No sustituye al futuro informe final. V187 y V188 terminaron; V189/V189B son auditorías y construcción matemática de contextos, sin entrenamiento neuronal.

V190 se registró en remoto antes de entrenar: `c918d5b326afb6320d7339b94d24c5f21511fba8`, árbol `82d62155330ed1f0cda5e7b69b76e81ab7370ced`. Los 17 archivos registrados se descargaron por HTTPS y se compararon byte por byte. Recibos en `results/V190_PREREG_RECEIPT.json` y `results/V190_REMOTE_PREREG_VERIFIED.json`. Auditoría técnica: 16 comprobaciones de métricas con soportes por historia, sin fallos, más muestreo y marginales; reutiliza auditoría independiente de redes V188.

Proceso científico original: sesión `exec_command` **31818**, PID **27480**, log `results/V190_CONSOLE.log`. Un único proceso GPU, máximo 35% de memoria, dos hilos, BelowNormal y seis CPU. No lanzar una segunda copia si una consulta expira. El entrenamiento tarda aproximadamente 16 minutos y ejecuta 32 historias de 60000 actualizaciones, agrupadas por ocho semillas y cuatro soportes emparejados. No hay parada por test ni ampliación del horizonte tras negativos.

Resultados anteriores de este bloque: V187 calibra un efecto clásico: urnas limitadas alcanzan precisión >=.99 en 93/100 historias, ilimitadas 0/100. Es reimplementación de métodos de Spike et al., no ejecución del código original: el enlace publicado devuelve 404. V188 no transfiere ese éxito a receptores neuronales: test medio fijo .9911, REINFORCE .3227, urna ilimitada .1797, limitada .0425; gate prospectivo falla, sin memorización informativamente completa. No se hicieron congelaciones condicionalmente canceladas.

V189 valida 9600 cotas informacionales y descubre que su primer prototipo no iguala las etiquetas. V189B conserva ese prototipo y construye cuatro pares con idénticas frecuencias de a, b e y antes de cualquier entrenamiento. En LOW, chi=16 y un código perfecto en train de 16 símbolos no puede superar 124/589 en test manteniendo train perfecto. En HIGH, chi=31. La estructura está programada; los aprendices no reciben las coloraciones.

Leer `PREREG_V190_LOSSY_MEMORIZATION_AND_GENERALIZATION.md`. Si falla el primario, cerrar esta arquitectura como vía para identificar grokking colectivo; no rescatarla con pequeñas variantes. Un candidato necesitaría congelaciones informacionalmente comparables, confirmación independiente y una arquitectura con varios aprendices que generalicen antes de una afirmación fuerte. Los papeles, el interés común y el canal actuales están impuestos. CT2 histórico permanece 61; rama nueva sin puntuación, N2=N3=0.

Git: HEAD local c032a32d2d8d7710a6ad5a88519b0801ea186891; índice del usuario SHA256 0fc87bbef0de6ced68aa787004ef36d3c7934f757f51b5d8505665bd071184a1. Publicar únicamente archivos explícitos mediante índice separado. Verificar blobs con ls-tree y cat-file (git show con rutas largas falla en Windows). El bloque V187–V190 aún no tiene archivo final de resultados; sí están remotos los prerregistros V187, V188 y V190. La última entrega científica completa es V182–V186, recibo en research/V182_V186_20261115/PUBLICATION_RECEIPT.json.
