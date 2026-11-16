# Reproducción V202

La campaña científica completa terminó: 32 raíces, seis brazos, ocho grupos por raíz y 60.000 rondas por grupo. El registro anterior al entrenamiento es `358df109d6e0fefdded66b9c68751665393ac3c5`. `V202_REGISTRATION_RECEIPT.json` contiene los hashes descargados antes de ejecutar; el directorio científico incluye FREEZE, 192 JSON por raíz/brazo y 768 checkpoints NPZ.

Para ejecutar la campaña completa desde una copia con los archivos fuente, sus auditorías y el recibo, se usa Python del entorno del proyecto:

```powershell
& 'C:\Programación\MARL-million-144-20261110\.venv\Scripts\python.exe' -X utf8 -u '.\run_v202_relational.py'
```

El runner exige que `results/V202_RELATIONAL_ACQUISITION` no exista y verifica los hashes registrados. Para reproducir desde el paquete archivado, hacerlo en una copia nueva de fuentes y recibo, sin copiar ese directorio de resultados al destino de ejecución. Conservar los originales como referencia. No borrar resultados para liberar el mismo nombre ni modificar el protocolo para eludir el guardado. No es necesaria GPU; sí NumPy y Numba. Versiones exactas en FREEZE. Afinidad y prioridad están adaptadas al PC actual; cualquier adaptación a otro hardware debe registrarse.

Reproducción seleccionada ya ejecutada y verificada:

```powershell
& 'C:\Programación\MARL-million-144-20261110\.venv\Scripts\python.exe' -X utf8 '.\reproduce_v202_selected_world.py' --destination 'C:\Programación\AB_reproductions\V202_selected_world_20261116'
```

Ese destino ya existe. Para otra ejecución hay que escoger una carpeta nueva. El helper copia las fuentes congeladas, comprueba que importa el módulo copiado, reentrena el mundo 0 en los seis brazos y compara exactamente los 24 checkpoints con los originales. La verificación realizada dio 384 arrays/campos idénticos. Es una reproducción seleccionada en el mismo ordenador, no una repetición completa de las 32 raíces ni confirmación externa.

La auditoría independiente del evaluador puede ejecutarse con Node.js 24:

```powershell
node '.\validation_node\v202_independent_audit.cjs'
```

Requiere que la campaña haya terminado y protege su JSON de salida frente a sobrescritura. Reimplementa física y observaciones por enumeración literal y resuelve valores por iteración, incluyendo la ablación de pagos. Las 1.536 evaluaciones terminales y 32 mejores respuestas de índices fijos fueron verificadas. La comparación privada de desviaciones no es un certificado POMDP.

El análisis primario está congelado en `analyze_v202_relational.py`. `v202_posthoc_initial_and_gradient.py` y `synthesize_v202_results.py` son análisis posteriores identificados: no convierten la interpretación nueva o el cruce de umbral WARM en confirmación de H1. H1 permanece FAIL. La cota de mundos sin éxitos se conserva en `results/V202_ZERO_SUCCESS_BOUND.json` para evitar interpretar [0,0] bootstrap como probabilidad poblacional nula.

Los checkpoints incluyen RNG Philox, el siguiente bloque de aleatoriedad solapado, buffers PG de relaciones aún abiertas, tablas y conteos. Las relaciones PG incompletas al terminar no se usan como retornos completos. No aplicar de nuevo descuento 0,95: la terminación geométrica ya lo implementa.
