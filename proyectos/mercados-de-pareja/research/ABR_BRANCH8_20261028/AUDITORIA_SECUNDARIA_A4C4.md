# Auditoría secundaria A4C4 · Convergencia, divergencia y reparación verificable

**28/10/2026. Evidencia auxiliar de la campaña N01–N08, cero ciclos AB adicionales.** La rama conserva dos implementaciones efectuadas sobre la misma autorización. El instrumento principal fue `experiment.py.gz.b64` (SHA-256 descomprimido 39c693a8..., descrito en REPORT.md y LEDGER.json). La implementación secundaria posee fuente explícita `experiment_frozen_a4c4.py`, cuya huella SHA-256 **a4c4833535975ee613c9c9459200283990ac2309abf5514dc509cdf2d2e54b22** fue registrada en `SOURCE_FREEZE.json` antes de ejecutar. Ninguna es réplica externa de datos humanos ni debe promediarse con la otra como si fueran corridas idénticas.

**Salida secundaria por tres semillas (202, 404, 606).** `RESULTS.csv` conserva 42 registros iniciales (14 condiciones). Las filas N05 del archivo original son **INVALID** para el requisito de irreversibilidad: permitían volver a mostrar díadas que ya se habían rechazado. Este defecto se detectó en auditoría adversarial, quedó registrado antes de repararse en `REPAIR_N05_PREREG.json`, con fuente `repair_n05.py.gz.b64` y SHA-256 **7b6a1ec3db5ad1785633d636e824fb8df5973ac23a1e57f91488a577ef69ba49**. Los 12 resultados válidos de N05 corregido están únicamente en `RESULTS_REPAIRED_N05.csv`. Se registra **un intento auxiliar inválido, reparado dentro de N05, sin duplicar ciclo válido ni ocultarlo**.

| Prueba | Resultado secundario | Limitación |
|---|---|---|
| N01, DA / secuencial | Cobertura 99,50 % / 87,50 %; r=0,935 / 0,850; cero pares bloqueantes DA frente a 1802 secuencial de media | Información global DA y exposición secuencial no equiparadas |
| N02, fatiga / feedback | Cobertura 54,00 % / 72,06 %; r=0,890 / 0,924 | Los hazards dependen de selección temporal y umbrales impuestos |
| N03 pools 100,300,1200 | Cobertura respectivamente 1,61 %, 1,33 %, 1,61 % | Tan pocos emparejamientos impiden un contraste robusto de r |
| N04 asincrónico persistente / expira20 | Cobertura 13,44 % / 9,44 % | Feeds independientes y oportunidades efectivas distintas de bilateral simultáneo |
| **N05 reparado**: ninguno/privado/local10/público | Cobertura **37,33/37,33/36,22/34,56 %**; r **0,865/0,865/0,883/0,869** | El bloqueo de revisualización modifica exposición y cobertura respecto al instrumento principal |
| N06 y N07 | Verificación documental independiente de ECP julio 2026 y gráfica Banco de España DT2606 (correlación educativa ≈0,62–0,66 para antiguas cohortes y ≈0,55 recientes) | No existen aquí microdatos personales ni inferencia a apps |

**Lectura adversarial:** el instrumento secundario repara irreversibilidad N05 con `past_decision`, pero la instrumentación deja un gran volumen de rondas inefectivas al saltar pares repetidos. Esto contribuye a que la cobertura sea mucho menor que en el instrumento principal (37,33 % frente a 60,89 % para condición ninguna). **No corresponde atribuir toda la diferencia a difusión reputacional, ni declarar comparabilidad de los dos algoritmos**. Una réplica posterior deberá igualar explícitamente número de exposiciones nuevas realizadas por agente, estructura de feeds, azar de emparejamiento y barreras temporales.

**Documentos de soporte**: `experiment_frozen_a4c4.py`, `SOURCE_FREEZE.json`, `REPAIR_N05_PREREG.json`, `repair_n05.py.gz.b64`, `RESULTS.csv`, `RESULTS_REPAIRED_N05.csv`, `HAZARDS.csv` y `Q_TRACK.csv`. Portabilidad en clon limpio NO_VERIFICADA. Originales conservados, sin correcciones silenciosas. N1/N2/N3 nuevos = 0. Estado general: exploratorio.
