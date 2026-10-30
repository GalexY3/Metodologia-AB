# Tarea Codex 04 · N259–N276: paridad individual de trayectorias

**Dependencias:** recuperación verificable de fuentes/fixtures TS+Boost anteriores, fuente Python original intacta, congelación A–J y SHA previa. No repetir las 60 comparaciones agregadas como si fueran novedad. Solo ejecutar nuevas verificaciones diferenciales con contrato, recibos y controles.

**Estimando técnico:** igualdad dirigida y ordenada de eventos **por individuo y por tick**, separada de igualdad de matching como conjunto de aristas y de igualdad de función objetivo. Escenarios oficiales x 6 seeds [101,211,307,401,503,601]; N144/T16/K7. Congelar el conjunto de 60 antes de outcomes, pero seleccionar por valor discriminante si hay divergencia temprana.

**Instrumentación:** sin editar el original, conservar copia instrumentada de ambos motores con SHA. Serialización ordenada y auditable de (seed,scenario,tick,actor,receptor,exposición ordinal,propuesta,aceptación/rechazo,arista de candidato,identidad de emparejamiento,disolución,estado de la pareja). Registrar ganancia/pérdida de estado, atributos iniciales y los cinco tensores de shocks con hashes verificados; JSONL por semilla/caso y hash de cada archivo. Evitar deducir eventos a partir de métricas agregadas.

**Rivales/controles:**
- Comparator independiente por caso y por tick detecta PRIMER evento no coincidente, tanto orden como valor; comprobar canonicidad de IDs y pares `(min,max)` sin destruir la direccionalidad de propuestas.
- Para múltiples soluciones óptimas, distinguir igualdad de cardinalidad/peso de unicidad y de igualdad de aristas; no activar `ESBM_PARITY_IGNORE_UNPROVEN_UNIQUENESS=1` para declarar identidad de matching. Calcular/justificar unicidad cuando sea posible; dejar `UNRESOLVED_TIE` si no.
- Controles positivos en casos únicos pequeños con oráculo independiente y negativos con empates deliberados, permutaciones de IDs/orden y diferencias artificiales inyectadas. No declarar paridad si el comparador no detecta un error inyectado.
- Congelar tests y código SHA antes de outcome, registrar fallos, costes, límites de memoria y diferencia de semántica de float64 vs pesos enteros.

**Cierre:** informes con denominador de casos verdaderamente comparados y eventos/ticks comprobados; archivos de outputs individuales, manifest de SHA, ledger A–J por ciclo ejecutado, auditoría adversarial, priors y updates (`NO_CHANGE_WITH_REASON` cuando proceda). Ninguna validación sociológica/humana por sí misma. CT2 científica 7/100 y STOP_R5 humano intactos. 20 plazas máximo de todo N257–N276, y ninguna gastada por planificar.