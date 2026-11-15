> Estado histórico. Consultar ESTADO_20261115_V194.md para el resultado final y su recibo de entrega.

# V192 en ejecución — proceso original

Estado transitorio. V187–V190 terminó y está publicado. El turno anterior es progreso verificable: nueva evidencia, cierre de arquitectura y entrega remota. El objetivo global sigue activo; no declararlo logrado por estos resultados.

Nueva incertidumbre: dos redes neuronales que aprenden con observaciones separadas y afrontan ambas entradas locales retenidas. No se reabre el emisor tabular de V190. Ambas estiman sus pagos y eligen acciones; la suma modular de acciones debe igualar la suma de funciones locales. La tarea, intereses comunes y feedback siguen impuestos; no equivale a institución material aprendida.

Prerregistro V192: babedeedbf604d9a05f134f80a1eb82383bcd402, árbol f6cd047ab9c7e07ee7a6d6cfcc800fd434bfc1bf. Sus17archivos, incluidos cuatro pares de datos y un candidato excluido antes de entrenar, se descargaron por HTTPS y compararon byte a byte. Recibos en results/V192_PREREG_RECEIPT.json y V192_REMOTE_PREREG_VERIFIED.json. Fuentes V191/V192 congeladas: no editarlas tras ver resultados.

Proceso original: sesión exec_command **51396**, log results/V192_CONSOLE.log. Consultar ese handle y el log; no reiniciar por timeout. Un procesoGPU, dos hilos, BelowNormal, seisCPU, máximo35%memoriaGPU y pausas. No tocar servicios Python ajenos3504,15036,15080.

Orden y gates en PREREG_V192_DUAL_NEURAL_PRIVATE_CREDIT.md: primero ORACLE_FULL, cuatro pares de agentes,60kactualizaciones. Si menos de3/4pares terminan test conjunto>=.95, cancelar PRIVATE_FULL y PRIVATE_BANDIT_IS; son no ejecutados, no resultados negativos. Si pasa, ejecutar ambas ramas privadas completas con cuatro pares cada una. Primario exploratorio tardío requiere3/4pares PRIVATE_FULL con t_gen>=5*t_mem, diferencia>=2000, finaltrain>=.99 y finaltest>=.95. Contraste distinto de feedback: al menos3/4 FULL finaltest>=.95 y mediana FULL−BANDIT>=.10. No cambiar parámetros para rescatar negativos.

V191 verifica exactamente que regresión MSE de todos los pagos y regresión bandit ponderada por1/(31*q) tienen la misma expectativa de pérdida/gradiente.18contrastes numéricos,1848entradas de feedback, aislamiento y dos pasos sintéticosGPU; sin entrenamiento científico. Se conservan generador inicial que omitió un valor y bug de serialización np.bool, corregidos antes de registro. Datos finales en results/V191_DUAL_NEURAL_AUDIT_V2; no se sobrescriben al revalidar. Un candidato del contexto192003 fue rechazado por cobertura marginal, sin consultar resultados neuronales.

El control usa interlocutores virtuales que ya conocen su función; eso suministra una convención. PRIVATE_FULL recibe un oráculo contrafactual propio; no lo llamar aprendido ni gratuito. BANDIT solo recibe su pago. El gradiente esperado coincide, pero Adam y la información disponible difieren. No se reivindica originalidad algorítmica, integración de acciones o sincronización genérica. Antecedentes nuevos a registrar con alcance de lectura: COMA2018, Expected Policy Gradients, Klein et al.NIPS2004/Kinzel-Kanter2002.

Congelar un compañero que no generaliza puede bajar el test conjunto por construcción. Una intervención posterior deberá medir la generalización local del aprendiz activo y mantener exploración, controlando información del feedback. No confundir sistema con varios aprendices y necesidad causal de coadaptación. Ver docs/V191_DUAL_NEURAL_IDENTIFICATION.md.

CT2 histórico61, nueva rama sin puntuación,N2=N3=0. Canonical score SHA2560db038a35ee828a59c96de2a9e5e071545b26213ed692a29e79ad68f26778047. Git localHEADc032a32d2d8d7710a6ad5a88519b0801ea186891, índice del usuarioSHA2560fc87bbef0de6ced68aa787004ef36d3c7934f757f51b5d8505665bd071184a1. Hay cambios ajenos: no stage-all/reset/pull/merge. Publicar en research/aldea-memory-v175-20261115 mediante índice separado y lista explícita; verificar blobs usando ls-tree/cat-file, no git show con rutas largas. Última evidencia completa previa5cdf2e113459aa8f0f8b2c2e776ed9888fec6e12, recibo remoto4d07f238cc21845de0f65ef1a4f871383d9d0eb7. No subagentes ni mensajes a terceros.
