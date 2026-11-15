# Reproducir V195 neuronal y V197–V198

No ejecutar los entrenamientos de nuevo dentro de la carpeta original de evidencia. Los scripts rechazan sobrescribir resultados. Los dos registros previos están en los commits `7d519eb122a99108955f3f5b105e19e1da998c82` y `aef89672df24c52bb39d50a7fa777505d9c9cd9e`, con comprobaciones HTTP guardadas.

Descargar los ZIP de `research/V195_V198_20261115` y extraerlos juntos en una carpeta vacía. Para V195 también hacen falta las dependencias/padres identificados en el archivo V191–V194: se incluyen en el nuevo archivo los padres y fuentes estrictamente necesarios, fijados por SHA. Los resultados viejos de votación se incluyen íntegros como procedencia separada, sin cambiar sus fuentes ni sus fechas. No se redistribuyen PDF de terceros.

Con Python3.12, NumPy2.5.4, NumBa0.68, Torch2.11+CUDA12.8y Matplotlib, preparar un destino NUEVO fuera del directorio original. El perfil de afinidad Windows congelado corresponde al equipo de24hilos lógicos usado aquí; en otro Windows hay que publicar el ajuste de recursos y su nuevo hash como réplica adaptada. No se promete identidad de bits entre hardware o librerías diferentes:

```powershell
python stage_v195_v198_reproduction.py 195 C:\AB_reproductions\withdraw_new
python stage_v195_v198_reproduction.py 198 C:\AB_reproductions\drift_new
```

El preparador verifica y copia solamente fuentes, recibos y padres congelados. No copia la carpeta de resultados del experimento y no lanza entrenamiento. Ya se validaron las dos preparaciones locales con29y18archivos, respectivamente; esa copia no es una réplica científica.

En el primer destino ejecutar `python v195_withdraw_counterfactual.py run` y después `python audit_v195_withdraw_numpy.py`. Requiere GPU CUDA; se usa como máximo35%de memoria, dos hilos CPU y prioridad baja. Mantiene60000pasos totales de las historias parentales. La auditoría técnica histórica ya se incluye: no ejecutarla sobre una copia que conserve su salida, pues el modo técnico impide sobrescribirla.

En el segundo destino ejecutar `python v198_voting_expected_drift.py run` y después `python audit_v198_voting_numpy.py`. Usa CPU/NumBa con dos hilos, sin GPU. Es integración de deriva media oráculo, no entrenamiento descentralizado realizable. Los puntos intermedios Q se guardan para auditorías futuras.

V197 es un recálculo de políticas congeladas ya existentes: `python v197_tie_policy_audit.py` en una copia nueva con las carpetas V195_CORRELATED_EXPLORATION y V196_POST_PULSE_PLASTICITY, sus fuentes y reportes originales, sin la salida previa V197_TIE_POLICY_AUDIT.json. No borra ni sobrescribe esos datos.

Las verificaciones finales de archivo son de solo lectura. Conservar todos los negativos y controles cancelados. Los hashes/CRC prueban integridad, las auditorías NumPy prueban cálculo; ninguna de ellas es confirmación científica independiente, institución aprendida o justificación para elevar CT261.
