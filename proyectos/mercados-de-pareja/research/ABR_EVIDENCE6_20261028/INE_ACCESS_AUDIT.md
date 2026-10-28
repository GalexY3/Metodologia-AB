# N15–N16 · Auditoría de accesibilidad a datos oficiales (28-10-2026)

## N15, población española por fecha, edad y sexo
Fuente primaria identificada: **INE ECP, tabla 59583**, «Población residente por fecha, sexo y edad», ámbito nacional, edad simple, unidad personas. Portal de metadatos oficial en datos.gob.es: https://datos.gob.es/es/catalogo/ea0042823-poblacion-residente-por-fecha-sexo-y-edad-ecp-identificador-api-59583 . URL de CSV institucional: https://www.ine.es/jaxiT3/files/t/csv_bdsc/59583.csv ; JSON: https://servicios.ine.es/wstempus/js/es/DATOS_TABLA/59583?tip=AM ; vista: https://www.ine.es/jaxiT3/Tabla.htm?t=59583 . La ficha INE muestra la última modificación de 6/8/2026 en el catálogo de Resultados provisionales.

**Ejecución de acceso efectuada**: la búsqueda web confirmó las seis distribuciones oficiales, pero la apertura directa de csv y JSON desde la herramienta de consulta respondió «not accessible»; Python requests al host devolvió `NameResolutionError` en el entorno sin resolución DNS. La descarga desde el gestor container respondió «url not viewed» (política de acceso), sin materializar bytes. No hay checksum del CSV ni suma comprobada de 20–39 por sexo, ni validación de cifras secundarias. Concluir **N15 `DATA_ACCESS_BLOCKED`**, no inventar cuentas.

Población objetivo necesaria: `20<=edad<=39` en 1 julio 2026, sexo H/M y total compatible con INE ECP. Pero **no se deriva de ello** la población soltera, heterosexual, voluntariamente activa o visible en una app. Estado civil formal tampoco equivale a disponibilidad romántica. Las estadísticas poblacionales jamás deben multiplicar automáticamente tasas sintéticas.

## N16, estudios cruzados de los cónyuges
Fuente primaria: **INE MNP/MNPM, tabla 60268**, «Matrimonios por nivel de estudios de los cónyuges», universo matrimonios de diferente sexo, desagregación nacional/provincias, unidad matrimonios, series 2010–2024 referidas en el portal. URL de dataset https://datos.gob.es/es/catalogo/ea0042823-matrimonios-por-nivel-de-estudios-de-los-conyuges-mnpm-identificador-api-60268 ; descarga https://www.ine.es/jaxiT3/files/t/csv_bdsc/60268.csv ; vista https://www.ine.es/jaxiT3/Tabla.htm?t=60268 . Metadatos accesibles, matriz cruzada de conteos **NO** descargada por la misma limitación del entorno. Tampoco hay hash de CSV. Se omite cálculo O/E y toda cifra de diagonal contemporánea. Concluir **N16 `MATRIX_ACCESS_BLOCKED`**.

En caso de conseguir CSV real, protocolo que debe ejecutarse sin retoques post hoc: filtrar `nacional` + año elegido (p.ej. 2024), clasificaciones comparables hombre/mujer, separar `No consta` (análisis primario completas, secundario reincluyendo desconocidos), obtener `n_{ij}`, `N=∑ij n_{ij}`; homogamia observada diagonal `O=∑i n_ii/N`; expectativa por independencia a márgenes observados `E=∑i (n_i+/N)(n_+i/N)`; exceso `O-E` y cociente `O/E`, además de test Chi-cuadrado con celdas suficientes y sensibilidad a agrupación educativa. Es **un estimando matrimonial**, NO un equivalente de swipe/usuario ni de homogamia latente en belleza/estatus.

## Reproducibilidad futura
Ejecución viable en ordenador con conexión y acceso oficial a URLs anteriores; debe guardarse respuesta HTTP, timestamp, SHA-256 y encabezado antes de procesar. El script de simulación no incorpora cifras españolas porque ninguna tabla nacional por cohortes fue materializada durante el ciclo.

**Decisión R5:** no gastar semillas ni grandes agentes para inferir parámetros que requieren datos externos; conservar acceso bloqueado hasta instrumento diferente.
