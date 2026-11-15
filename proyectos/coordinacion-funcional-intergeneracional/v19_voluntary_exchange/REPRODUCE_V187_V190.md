# Reproducción de V187–V190

Estos experimentos distinguen calibración de un mecanismo clásico, transferencia a otro aprendiz y una transición exploratoria. No acreditan grokking colectivo ni una institución material aprendida. Los archivos originales permanecen intactos; no se deben ejecutar los programas de entrenamiento sobre sus directorios de salida ya existentes.

Entorno original: Windows, Python3.12.16, NumPy2.5.4, Numba0.68.0, llvmlite0.50.0 y PyTorch2.11+cu128, RTX4070SUPER. Los análisis usan Matplotlib. Los detalles y límites de lectura bibliográfica están en el catálogo de referencias. La igualdad bit a bit entre equipos o versiones no está garantizada.

## Inspeccionar la evidencia

El informe es `results/INFORME_V187_V190_20261115.md`; el manuscrito integrado, `docs/TFM_MANUSCRITO_TRABAJO_V190.md`. La auditoría final está en `results/V187_V190_FINAL_AUDIT.json`. El evaluador NumPy independiente conserva todos los contrastes y los diagnósticos posteriores en `results/V188_V190_NUMPY_FINAL_AUDIT.json`.

En `research/V187_V190_20261115`, descargar todos los `EVIDENCE_XX.zip` y extraerlos en un directorio vacío común. `ARCHIVE_MANIFEST.json` guarda tamaño y SHA256 de cada ZIP; cada uno contiene el manifiesto de sus payloads. `EVIDENCE_PAYLOAD_SHA256.json` registra los hashes globales. Comprobar CRC y hashes de cada archivo, no solo los de los ZIP. La recepción remota se documenta en `PUBLICATION_RECEIPT.json`, fuera del archivo cuya publicación verifica.

Las carpetas de resultados incluyen las 200 historias clásicas V187, 32 historias neuronales V188, auditoría V189 y su prototipo excluido, cuatro pares de contextos V189B y las 32 historias V190. Los checkpoints guardan pesos, optimizadores, baseline y estados aleatorios. Las múltiples condiciones de una semilla están emparejadas. En V190 hay cuatro pares de contextos y dos semillas neuronales por pareja; las32 historias no son32 contextos independientes. No se suman checkpoints como réplicas.

Los PDF de terceros y los datos/resultados humanos de fases anteriores no se redistribuyen en este bloque. El manuscrito identifica las entregas previas. El código original de Spike et al. no estuvo disponible en el enlace publicado: V187 reproduce los métodos con una regla explícita para urnas vacías. No se presenta como ejecución del código de sus autores.

## Volver a entrenar sin sobrescribir evidencia

El helper `reproduce_v187_v190.py` copia únicamente los archivos congelados necesarios a un directorio nuevo y comprueba sus hashes. Cada experimento requiere un destino diferente. Sin `--run`, solo prepara la copia. Ejemplo PowerShell desde el directorio del proyecto:

```powershell
$pythonAB = 'C:\Programación\MARL-million-144-20261110\.venv\Scripts\python.exe'
& $pythonAB .\reproduce_v187_v190.py --experiment 187 --destination 'C:\Programación\AB_reproductions\V187_new' --run
& $pythonAB .\reproduce_v187_v190.py --experiment 188 --destination 'C:\Programación\AB_reproductions\V188_new' --run
& $pythonAB .\reproduce_v187_v190.py --experiment 190 --destination 'C:\Programación\AB_reproductions\V190_new' --run
```

Ejecutar secuencialmente. Se copian recibos históricos: una reproducción no adquiere por ello un nuevo registro prospectivo. Los resúmenes de fases anteriores que el protocolo usa como contexto se copian con sus bytes archivados; no son resultados nuevos. V190 comienza desde inicializaciones nuevas, no desde los pesos V188. Su recibo incluye el resumen V188 para fijar qué se conocía al registrar el contraste.

Cada programa verifica fuentes, registro y auditoría técnica y rechaza una salida existente. V187 usa CPU y tarda segundos tras compilación; V188 y V190 usan un único proceso GPU. El helper de recursos usa dos hilos, BelowNormal, seis CPU y máximo35% de memoria GPU; el bucle introduce descansos regulares. No lanzar copias simultáneas. Preservar logs y resultados discrepantes en vez de reemplazarlos por la corrida original.

## Auditorías y análisis

`audit_v188_v190_numpy.py` enumera las predicciones desde los pesos finales en NumPy, sin invocar `BatchedReceiver` ni el evaluador de entrenamiento. Comprueba precisiones codiciosas y esperadas y calcula diagnósticos estáticos del código. Sus rutas de entrada corresponden al archivo original; copiar una nueva colección completa a otro directorio para auditar una reproducción. El flag `--interim` documentó un checkpoint ya escrito durante la ejecución original; no representa otra historia entrenada.

`analyze_v187_v190.py` verifica registros, recomputa los tiempos de los umbrales y sus cinco evaluaciones consecutivas, audita los cuatro pares de datos y aplica el primario registrado. `close_v187_v190.py` crea el informe y amplía el manuscrito a partir del análisis. Estos helpers de entrega son de una sola ejecución y rechazan sobrescribir sus resultados. No es necesario volver a ejecutarlos para leer o comprobar los archivos archivados.

La auditoría V189 fue posterior a V188. V189B construyó los contextos antes de V190, sin consultar resultados neuronales. Los sondeos finales del techo del código y de desviaciones del emisor son posteriores, descriptivos y restringidos al receptor existente. No prueban equilibrio de Nash sobre todos los parámetros ni constituyen congelaciones experimentales. Las congelaciones cuyo requisito no se cumplió no se ejecutaron.

## Registro temporal y evaluación

V187: `368ad29abeae37db9de9aeced4769953ba3e60b8`. V188: `0ff3063594136db0959b740ffbbf26568c361fe8`. V190: `c918d5b326afb6320d7339b94d24c5f21511fba8`. El último registro incluyó datos, código y protocolo; sus17 archivos se descargaron y compararon por HTTPS antes del entrenamiento. Los recibos distinguen la congelación previa de la publicación posterior.

CT2 histórico 61, rama nueva sin puntuación, N2=N3=0. Una implementación en otro lenguaje que coincide con la original aporta independencia técnica; no confirma por sí sola una predicción social original.
