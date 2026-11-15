# Reproducir los rivales privados y la auditoría posterior

Registro anterior a entrenar: `a0113021889e89b729e4513adafee1081cde48b2`. Incluye algoritmo, reglas de análisis y protocolo, nueve archivos verificados por HTTP y seis padres binarios fijados por hash. La auditoría V199B es posterior a los resultados y se etiqueta como tal.

Extraer juntos los ZIP de `research/V199_20261115` en una carpeta vacía. Conservar las versiones anteriores. El archivo contiene las fuentes congeladas, padres, contextos y checkpoints; no hace falta descargar los PDF para ejecutar el código. Sus fuentes públicas y hashes figuran en el registro bibliográfico. No se incluye código original de los autores ni se promete reproducir sus benchmarks.

Preparar otra carpeta NUEVA fuera de la evidencia original:

```powershell
python deliver_v199.py stage --destination C:\AB_reproductions\v199_new
```

El preparador comprueba y copia únicamente dependencias, protocolo y padres, sin resultados de la nueva campaña. No lanza entrenamiento. Dentro de ese destino ejecutar:

```powershell
python v199_private_baselines.py run
python analyze_v199_private_baselines.py
python audit_v199_private_baselines.py
python v199b_expectile_mechanism_audit.py
```

Las salidas no se sobrescriben. La primera orden ejecuta las dos cohortes completas, incluyendo la inversión de señales. Los384registros por mundo se derivan después al cerrar el informe;192corresponden a nuevas raíces, el resto conserva la procedencia parental. Los métodos apareados no multiplican las réplicas. No cambiar hiperparámetros y seguir llamando a ello el mismo estudio registrado.

Entorno utilizado: Python3.12, NumPy2.5.4, NumBa0.68, dos hilos y prioridad BelowNormal, sin GPU. El perfil Windows de afinidad supone el equipo original de24hilos lógicos; para otro Windows hay que registrar el ajuste de recursos y los nuevos hashes como réplica adaptada. No se garantiza identidad de bits entre hardware/versiones distintos. Los estados RNG se guardan al finalizar bloques completos de100pasos, sin monedas futuras pendientes.

Después de verificar resultados se puede repetir la auditoría analítica V199B. Congelar los compañeros sirve para diagnosticar respuestas, no para reconstruir la trayectoria estocástica ni acreditar equilibrio. La pérdida expectil conocida no se presenta como teorema nuevo.

`python deliver_v199.py verify --include-archive` verifica documentos, imágenes, hashes, CRC, fuentes congeladas e integridad de los registros. Sus controles del índice Git y puntuación corresponden al workspace original; no usar ese modo como requisito de una réplica en otro repositorio. Los controles científicos independientes son los scripts específicos. Leer el informe para distinguir criterios principales fallidos, secundarios positivos, daño distributivo y ausencia de salida.
