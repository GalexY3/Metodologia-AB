# Reproducción de V191–V194

Este bloque conserva un resultado positivo de generalización tardía de dos redes, su falsación como necesidad de coadaptación continua y el control positivo del aprendiz binario. No acredita AB2/3 ni una institución material aprendida.

## Entorno y evidencia

Entorno original: Windows, Python3.12.16, NumPy2.5.4, Numba0.68.0, llvmlite0.50.0, PyTorch2.11+cu128, RTX4070SUPER. Los análisis usan Matplotlib. No se garantiza identidad bit a bit entre máquinas, versiones o algoritmos de CUDA. Las verificaciones exactas documentadas se realizaron en este equipo.

Informe: `results/INFORME_V191_V194_20261115.md`. Manuscrito integrado: `docs/TFM_MANUSCRITO_TRABAJO_V194.md`. Auditoría: `results/V191_V194_FINAL_AUDIT.json`. Fuentes y alcance de lectura en el catálogo bibliográfico; consultar también los protocolos originales.

En `research/V191_V194_20261115`, descargar todos los `EVIDENCE_XX.zip`, `ARCHIVE_MANIFEST.json` y `EVIDENCE_PAYLOAD_SHA256.json`. Extraer los ZIP en un mismo directorio vacío. El manifiesto de cada ZIP identifica sus payloads; el global externo identifica todos los archivos originales. Verificar tamaño, SHA256 y CRC, y luego todos los payloads. La recepción remota se documenta en `PUBLICATION_RECEIPT.json`, fuera de los ZIP cuya entrega verifica.

Se incluyen los datos originales V191/V2, el candidato de cobertura excluido, borradores y logs técnicos fallidos, curvas, pesos, estados de Adam y RNG de V192–V194. El estado parental se identifica por hash previo y se entrega íntegro. No se redistribuyen los PDF de terceros ni se duplican los datos humanos de otras fases; el manuscrito identifica los bloques anteriores.

## Ejecutar en directorios separados

Los programas originales rechazan una salida existente. El helper prepara una copia nueva sin cambiar las fuentes congeladas ni sobrescribir evidencia. Cada experimento necesita un destino diferente. Sin `--run`, solo verifica y prepara archivos:

```powershell
$pythonAB = 'C:\Programación\MARL-million-144-20261110\.venv\Scripts\python.exe'
& $pythonAB .\reproduce_v191_v194.py --experiment 192 --destination 'C:\Programación\AB_reproductions\V192_new' --run
& $pythonAB .\reproduce_v191_v194.py --experiment 193 --destination 'C:\Programación\AB_reproductions\V193_new' --run
& $pythonAB .\reproduce_v191_v194.py --experiment 194 --destination 'C:\Programación\AB_reproductions\V194_new' --run
```

Ejecutar secuencialmente. Se usa un proceso GPU, dos hilos CPU, BelowNormal, seis CPU, máximo35%de memoria GPU y descansos por bloque. Los recibos copiados son los registros históricos; no convierten una reproducción en un nuevo experimento prospectivamente registrado. Los resúmenes y estados de referencia copiados son entradas archivadas, no resultados nuevos.

V192 ejecuta primero ORACLE_FULL. Si su control no alcanza el criterio, cancela las dos condiciones privadas. Las canceladas se reportan como no ejecutadas. En el original no hubo canceladas. V194 ejecuta únicamente el control ORACLE_BANDIT_IS. Ambos parten de inicializaciones nuevas y reutilizan bloques emparejados entre condiciones.

V193 continúa los primeros checkpoints de memorización PRIVATE_FULL originales. No es una nueva réplica independiente. El helper copia además todos los checkpoints conjuntos de5000a60000, porque cada comparación de paridad necesita su referencia. Las historias con corte1100reciben100 pasos de intervención antes de agruparlas en1200con las otras dos; el compañero ya está congelado desde su corte original. El presupuesto activo termina en60000para cada historia. La red detenida mantiene la misma exploración, no solo su argmax.

## Auditorías

V191 contiene18identidades numéricas loss/grad/factorización y1848 comprobaciones de tablas. V191B usa pasos GPU sintéticos para verificar aislamiento; no entrena la tarea científica. Sus scripts técnicos y los de entrega rechazan sobrescribir resultados finales. No hace falta ejecutarlos de nuevo para inspeccionar la evidencia.

`v193_frozen_peer.py technical` reconstruyó históricamente los cuatro pares hasta5000. Pesos, momentos y RNG coincidieron bit a bit. El replay no se contabiliza como nueva evidencia ni requiere interpretar repeticiones técnicas como semillas. Si se revalida en otro equipo, conservar cualquier discrepancia y su entorno en una copia independiente.

`audit_v192_numpy.py` calcula el forward con NumPy y enumera explícitamente todos los pares cartesianos de entradas locales de train y test. El argumento opcional `checkpoint_path` permite reutilizar el cálculo en `audit_v193_v194_numpy.py`; no llama a los evaluadores de entrenamiento. Auditorías finales:96métricas únicas V192 y96combinadas V193/V194. Las64V193 contenidas en la segunda colección no se suman otra vez.

Las comparaciones de paridad V193 verifican los parámetros activos y momentos contra sus continuaciones conjuntas en12checkpoints por brazo, además de RNG. Los parámetros congelados se comparan con sus propios cortes parentales. Estas son verificaciones técnicas y contrafactuales emparejadas, no confirmación científica externa.

`analyze_v191_v194.py` verifica las fuentes previas y umbrales, resume el control y produce las figuras. La diferencia entre efectos FULL/BANDIT según origen del interlocutor se etiqueta descriptiva posterior. `close_v191_v194.py` crea el informe, el capítulo, el manuscrito y el ledger. Son helpers de una sola ejecución; leer sus resultados no exige ejecutarlos encima de la entrega.

## Qué interpretar

La métrica principal es precisión conjunta codiciosa sobre entradas locales retenidas de ambos agentes. No es el pago de la política exploratoria, cuyo techo programado con epsilon=.1 es.816129aun con funciones perfectas. La generalización de un activo congelando al compañero se mide también localmente; el test del par puede quedar limitado por el compañero detenido.

Los cuatro bloques son la unidad de análisis. V192 contiene12trayectorias de pares, V193ocho continuaciones y V194cuatro trayectorias emparejadas de control. No son24raíces independientes ni cientos de réplicas por contar checkpoints. Las fuentes revelan un oráculo de pagos contrafactuales en FULL, no una institución aprendida. Los intereses comunes y el juego son exógenos. Los programas COMA, EPG y Banditron no se ejecutaron aquí.

Verificación de solo lectura, sin sobrescribir informes o auditorías: `python verify_v191_v194_evidence.py`. Añadir `--metrics` recalcula las 192 métricas finales desde los pesos mediante NumPy. Antes de empaquetar puede usarse `--documents-only` para comprobar enlaces y hash del manuscrito.

Registros previos: V192 `babedeedbf604d9a05f134f80a1eb82383bcd402`; V193 `2b2adb035e0826dff0c7a75981bea290c3e3a339`; V194 `9b0d9ffd13d7ad353fb06fe45357c7279c988329`. CT2 histórico 61, nueva rama sin puntuación, N2=N3=0. El objetivo científico global permanece activo.
