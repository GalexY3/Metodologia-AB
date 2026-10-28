# AB-R BRANCH6 · Informe final y revisión adversarial

**Autor del programa:** Alejandro Panera Pascual. **Fecha:** 28 de octubre de 2026. **Rama:** `research/ab-r-mercados-pareja-20261028`; no se modificó `main`. **Objeto:** distinguir preferencias por candidatos de alto valor, asignación bilateral, mercados locales, asincronía y reputación observada, sin introducir utilidad por similitud.

## Marcadores AB
| Indicador | Resultado |
|---|---|
| Ciclos autorizados | 6 (N09–N14) |
| Ciclos completos válidos | **6** (3 `EXPERIMENTAL_AB` N09–N11 + 3 `PLANNING_AB_ONLY` N12–N14) |
| Intentos instrumentales inválidos conservados | **1** (primera corrida N09; no cuenta ciclo extra) |
| Corridas válidas | **60 sintéticas**, 5 semillas (1103, 2207, 3301, 4409, 5501) |
| Ciclos confirmatorios externos | 0 |
| N1 nuevos concedidos / N2 / N3 | **0 / 0 / 0** |
| CT2 | **17 → 17**, ordinal, no probabilidad |
| DRIFT | D0, mismo dominio sustantivo |
| Prueba en clon limpio | **NO VERIFICADA** |
| Saldo de la autorización | **0** |

**Prerregistro:** [PREREG.json](PREREG.json), commit `58539794ccdd178aa81d25572f7aa47c8d220073`. **Código antes de ejecutar:** hash SHA-256 `f34516e4b0514956eed5e18523b9716d65a79dc7f1a58acb12659ac98fe89322` publicado en [SOURCE_FREEZE.json](SOURCE_FREEZE.json), commit `a7eeef166ae06ed8aec49e9d9f9f441923df4509`. Primera corrida inválida por error del *auditor* que detectaba pares bloqueantes: [INVALID_ATTEMPT_01.json](INVALID_ATTEMPT_01.json), commit `b35a4466`. No se utilizaron sus resultados. La reparación corrigió el orden de índices de utilidades y simplificó el código, y quedó congelada con hash SHA-256 `6f351329c3c9fdc5aad83dcb719962dc022b8b17203b94e6661ed322ffe0b632` en [REPAIR_FREEZE.json](REPAIR_FREEZE.json) (commit `14059774`) **antes** de repetir. El fallo original se conserva. El resultado válido por semilla está en [RUNS.csv](RUNS.csv), [SUMMARY.json](SUMMARY.json) y los criterios de aceptación/piloto en [QA_AND_GATES.json](QA_AND_GATES.json). La reejecución local reprodujo idénticos hashes de RUNS, SUMMARY y GATES.

**Problema de portabilidad:** el intento de conservar el gzip/base64 del código en GitHub fue bloqueado por controles de seguridad de la interfaz; por eso la fuente Python íntegra se adjunta **localmente** como parte del ZIP de reproducibilidad en la conversación y las huellas se conservan en GitHub. No se afirma disponibilidad del código en un clon limpio de la rama. No sustituir esta limitación por declaraciones de ejecución remota.

## N09 — Misma red de oportunidades, comparación con modelos competentes

Diseño: N=400 (200 hombres/200 mujeres), grafo bipartito aleatorio k-regular con 20 o 60 candidatos de sexo contrario por agente, preferencias 60/40 sin término por similitud y error diádico fijo con sd=0,08. Cinco semillas; se comparó **(a)** Gale–Shapley con rankings de todas las aristas disponibles, **(b)** greedy que acepta inmediatamente si existe consentimiento bilateral y utilidad ≥0,05, y **(c)** umbrales adaptativos con aspiración inicial 0,80 y descenso por experiencia. Ambos modelos secuenciales recorren las **mismas aristas en el mismo orden**, el DA conoce la red completa. Se auditaron pares bloqueantes en DA: **0 en todos los ensayos válidos**.

| k oportunidades distintas | Política | r valor inicial | Cobertura |
|---:|---|---:|---:|
| 20 | DA completo | 0,8638 | 96,0% |
| 20 | Greedy inmediato | −0,0071 | 96,2% |
| 20 | Búsqueda adaptativa | 0,3775 | 34,8% |
| 60 | DA completo | 0,9170 | 98,2% |
| 60 | Greedy inmediato | 0,0352 | 98,6% |
| 60 | Búsqueda adaptativa | 0,7114 | 80,5% |

La diferencia **greedy vs adaptativo** muestra que, con idéntica población, preferencias, grafo y orden de encuentro, variar el criterio de aceptación modifica el sorting. No prueba que los humanos utilicen esos umbrales. DA es el adversario fuerte: alcanza más cobertura y más sorting, pero dispone de conocimiento simultáneo del grafo, así que no existe paridad temporal/informativa y no puede afirmarse que un algoritmo sea socialmente superior por un mecanismo único. Es de nuevo incorrecto reclamar originalidad genérica a la homogamia sin gusto directo por semejanza: véase Hitsch et al. (2010), https://doi.org/10.1257/aer.100.1.130.

**Dictamen A–J:** resultado sintético válido después de corregir una auditoría inválida. **No hay contribución 2/3**, ni evidencia sobre un equilibrio del mercado humano.

## N10 — La reparación de los mercados locales cambia la conclusión

Diseño: N=1.200, en tres tratamientos de grupos perfectamente balanceados (100, 300, 1.200 personas por mercado). Cada persona tenía hasta **40 encuentros distintos programados** con perfiles del sexo contrario, sin repetición de aristas en ese horizonte; las salidas por match reducen exposiciones efectivas. q inicial 0,82, fatiga 0,015 por encuentro fallido, rechazo adicional 0,005. Dos semillas piloto debían superar 40% de cobertura y 50 parejas por tratamiento antes de permitir tres semillas adicionales; **el criterio pasó en los seis conjuntos piloto**, sin reajuste retrospectivo de parámetros.

| Tamaño de pool | r media (5 semillas) | Rango de r | Cobertura |
|---:|---:|---:|---:|
| 100 | 0,7256 | 0,6337–0,7617 | 59,90% |
| 300 | 0,7409 | 0,7233–0,7582 | 60,30% |
| 1.200 | 0,7366 | 0,6958–0,7569 | 59,43% |

**Hallazgo adversarial:** desaparece la fuerte relación monotónica que parecía observarse en BRANCH8, donde tamaño de pool y oportunidad efectiva/desbalance quedaban entrelazados. Las diferencias ahora son pequeñas frente a variabilidad entre semillas. **No se rechaza ni confirma equivalencia de mercado** sin un estudio de potencia, intervalos por mercados independientes y comparación más amplia. En particular, un único mercado de 1.200 no ofrece doce unidades de inferencia independientes y las cinco semillas no sustituyen replicación externa.

**Dictamen:** reparación válida y resultado negativo para una interpretación fuerte de BRANCH8; no adjudicar novedad independiente.

## N11 — Asincronía sobre grafo idéntico, pero tiempo no equivalente

Diseño N=400 y 40 aristas únicas por agente en el mismo grafo de oportunidades antes de emparejamientos. En **sincrónico**, los dos miembros valoran la arista al mismo tiempo; **asíncrono persistente**, cada sexo ve esa arista en diferente momento, quedando los likes hasta que reciba respuesta; **caducidad**, likes expiran a cinco ticks. Umbrales personales decrecen por vistas; no se aplicó castigo de rechazo todavía no observable. Se verificó que nadie puede aparearse dos veces.

| Régimen | r media | Rango de r | Cobertura |
|---|---:|---:|---:|
| Simultáneo | 0,6329 | 0,6008–0,6702 | 61,6% |
| Asíncrono persistente | 0,4440 | 0,2966–0,5126 | 60,2% |
| Asíncrono caducidad 5 | 0,3959 | 0,1877–0,5308 | 56,6% |

**Límite crucial:** la red potencial es la misma, pero el número de oportunidades *realmente evaluadas por ambos antes de salir* depende del calendario y de matches previos, y las diferencias de q por historial también dependen de la secuencia. Esto demuestra sensibilidad al procedimiento sintético compuesto, no una identificación causal humana del efecto «Tinder asincrónico» ni del vencimiento puro.

## N12 — Población española: denominador todavía no identificado

Se verificó directamente [INE, ECP 1/7/2026](https://www.ine.es/dyngs/INEbase/operacion.htm?c=Estadistica_C&cid=1254736177095&idp=1254735572981): **49.801.559 residentes**, 24.462.607 hombres, 25.338.952 mujeres. Se localizó la [tabla nacional INE 59583 de edad/sexo](https://www.ine.es/jaxiT3/Tabla.htm?t=59583), pero las celdas 20–39 del 1/7/2026 no se pudieron recuperar por los canales consultables. La cifra de 20–39 publicada anteriormente en fuente secundaria no queda certificada por este ciclo. Se corrigió expresamente una falsa pista: la tabla INE 59662 accesible en CSV corresponde a **islas**, no al total nacional. Se encontró información censal sobre **estado civil**, insuficiente como proxy de personas sin pareja que además buscan citas heterosexuales y usan la app. `DATA_BLOCKED`. No generar población de solteros simulados con un denominador de todos los residentes.

## N13 — Estructura de matrimonios educativos, sin tabla numérica completa

Se verificó que el [INE tabla 60268](https://ine.es/jaxiT3/Tabla.htm?t=60268) clasifica **matrimonios de diferente sexo** por educación de ambos cónyuges (14 niveles para cada uno, incluido «No consta») con varias fechas, pero no se pudo descargar la matriz cuantitativa. Por tanto no se calculó el cruce de margenes ni una tasa neta de homogamia. La fórmula futura se deja especificada con sus datos requeridos: `O=sum(n_ii)/N`; `E=sum(n_i+ n_+i)/N²`; `O/E` compara diagonal observada contra independencia marginal, sin resolver autoselección por edad ni preferencias. **Matrimonios ≠ swipes**, y un dato censal de 2001 no se tratará como observado en 2026. `ANALYSIS_BLOCKED`.

## N14 — El rechazo privado no implica pérdida de status transmitida a terceros

Dos fuentes revisadas: Campaioli, Zamperini y Cecchinato (2025), [*New Media & Society*](https://doi.org/10.1177/14614448251336437), diario de un mes de ocho participantes, sobre señales digitales, rechazo y vigilancia; Van der Zanden y Schokkenbroek (2024), [*Cyberpsychology, Behavior, and Social Networking*](https://doi.org/10.1089/cyber.2023.0751), encuestas sobre tipos, motivos y efectos del rechazo (primer estudio n=177). Estas fuentes tratan la experiencia de rechazo y canales de información, **no aportan una estimación verificada de pérdida global de estatus por cada swipe privado**. Solo cabría una dinámica reputacional dependiente de un canal observable a terceros, con límites de privacidad, supervisión ética y verificación de la propia señal. La ecuación material de pérdida global queda como hipótesis de mecanismo sintético, no afirmación sobre España. [Fuentes y obstáculos](SOURCES_AND_LIMITS.md).

## F: auditoría, H: actualización, I: dictamen

**R1:** estimandos separados: r entre emparejados, cobertura de toda la población y composición de parejas. **R2:** DA y greedy se ejecutaron en N09, con oportunidad grafo idéntica pero información temporal desigual respecto a DA. **R3:** hipótesis afectadas por exploración previa; cinco semillas no son confirmación independiente. **R4:** N10 elimina un fuerte gradiente aparente al retirar confusores, N11 conserva diferencias pero no separa todas las vías. **R5:** sin matriz española contemporánea o participantes elegibles, más semillas de este mismo generador pueden generar precisión interna sin transportabilidad.

Se verificó el hash de fuente antes de ejecución válida, reparación y nueva congelación; dos ejecuciones válidas producen resultados idénticos byte a byte. **El código Python íntegro no pudo adjuntarse a GitHub** porque la interfaz bloqueó el archivo comprimido opaco; está en el ZIP local entregado. `CLEAN_CLONE_NOT_VERIFIED`. El CSV por semilla y metadatos SHA están versionados, sin fingir que la referencia textual garantiza portabilidad. Un primer intento **inválido** permanece documentado, no reetiquetado como válido.

**N1 nuevo = 0, N2 = 0, N3 = 0; 2/3 NO ACREDITADO.** CT2 permanece **17/100**: aumentó comprensión de controles pero no evidencia externa o novedad. [Gráfico CT2](CT2_TRAJECTORY.svg) muestra exclusivamente tres puntos registrados en cierres de campañas (MATE10 20, BRANCH8 17, BRANCH6 17) y escala ampliada, no valores inventados en ciclos. CT2 no es probabilidad.

## J: AB-DECIDE

`STOP_CAMPAIGN`: la autorización 6/6 está consumida. La próxima clase de evidencia útil exige acceso a una matriz observable contemporánea, elegibilidad real del mercado de citas, o un comparador con idénticas historias de exposición y de información. El proyecto sigue siendo **exploratorio**. La opción metodológicamente preferible es un bloque condicionado a esos nuevos instrumentos, preservando la posibilidad de STOP bajo R5. Nuevos ciclos requieren autorización expresa.
