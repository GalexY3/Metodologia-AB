# Politics Fantasy League — AB20 / identidad y adscripción temporal

**Informe final / 26 de octubre de 2026**  
**Tipo de investigación:** observacional documental, revisión adversarial y pruebas de ingeniería locales.  
**Alineación:** AB 3.2.1, O1–O6. **No ejecución de GitHub Actions tras aviso presupuestario**.

## A. Estado y autorización

- **Autorizados 20; cerrados 20/20:** C01–C10 en GitHub Actions antes del aviso, C11–C12 y C19 mediante investigación documental pública, C13–C18 y C20 mediante pruebas locales (C18 incorporó hechos institucionales ya documentados). No hay nuevos experimentos con personas, ni ensayos causales ni replicaciones científicas externas.
- **D = 2,0**, rama `B_IDENTITY_HISTORY`, identificadores y adscripción parlamentaria a lo largo del tiempo.
- **CT2 línea:** inicio **20/100**, cierre registrado **30/100** pero **auditoría post hoc corrige el final a 29/100**. La subida C13 29→30 se atribuyó solamente a tests sintéticos y no cumple O4 como fundamento científico. Se conserva el valor registrado y la corrección, sin sustituirlo clandestinamente. CT2 es confianza ordinal en la posibilidad de llegar a 2/3, NO una probabilidad.
- **N1 nuevos = 0; N1 cartera auditados = 0; N2 = 0; N3 = 0.** Se ha avanzado en ingeniería/documentación, no acreditado un descubrimiento científico 1/3–3/3.
- **PFL-V1 rev.3 = 36,350 %** con nueve subáreas. No se emite porcentual rev.4 porque faltan auditoría hito por hito, fuentes y derechos. Seis gates de publicación continúan sin cumplir.

## B. Evidencia y contraste secuencial

**C01–C04 (GH/CI):** índice de fichas XV con 412 códigos `codParlamentario` únicos. Un procedimiento ingenuo de búsqueda textual de toda página dio 5/8 enlaces únicos; extraer el título H2 produjo 8/8 en desarrollo y 16/16 en perfiles reservados. No demuestra que el ID sea inmutable entre legislaturas.

**C05–C08 (GH/CI):** un nombre de votación de abril 2024 no aparece por comparación exacta en 412 fichas actuales ni en el archivo general de 6.325 periodos; transformaciones ortográficas conservadoras no lo resuelven. El BOCG contemporáneo confirma cambios institucionales, no explica ese nombre. La página estática de composición no expone historia completa (carga dinámica). Conservadas reparaciones de esquema y búsquedas fallidas; no cuentan como nuevos ciclos.

**C09–C10 (GH/CI):** un caso de los dos grupos históricos discordantes está en un cambio oficial SUMAR→Mixto efectivo 03/07/2025. Votos nominales antes y después indican **GSUMAR→GMx**, mientras otro caso de control se mantiene **GVOX→GVOX**. Esto es coherencia documental de dos personas enlazadas por fuente, no efecto causal ni capacidad de puntuación real.

**C11 (web institucional):** BOCG 15-D-51 documenta cinco cambios Sumar→Mixto de efectos **05/12/2023**, publicado **15/12/2023**, con coincidencias parciales con acta de Mesa **12/12/2023**. El acto jurídico, su anuncio y el momento de conocimiento no son la misma fecha.

**C12 (web institucional):** en el mismo boletín hay **8 bajas y 8 altas en el Pleno** con fechas **06/12** y **12/12** respectivamente; **5 bajas y 5 altas de grupo** con efecto **05/12**. La numeración 358–365 es orden de credenciales, **no ID permanente de persona**. La diferencia impone clases de acontecimiento separadas.

**C13 (local):** implementación experimental de eventos tipados (`PLENO_SEAT`, `PARLIAMENTARY_GROUP`, `INTERNAL_ORGAN`), fechas de efectos/publicación y no asignación de identidad ni score. **9/9** tests iniciales. El código está en este archivo local, no incorporado a la app de producción.

**C14 (local, adversarial):** encontró fallo reproducible: movimientos opuestos de mismo grupo y día producían estados diferentes según el ID de fila. Se corrigió con **STOP ante orden jurídico indeterminado**. **10/10** tests.

**C15 (local, adversarial):** detectó aceptación de `first_public_at` consciente pero inventado. Se corrigió: el contrato sin evidencia temporal firmada solo admite **null**. **11/11** tests.

**C16 (local, adversarial):** dos documentos con nombre normalizado idéntico se fusionaban incorrectamente. Corrección: estado separado por `(source_id, source_scoped_person_key)`; no fusionar documentos sin crosswalk verificado. **12/12** tests, con posible infraenlace deliberado.

**C17 (local):** controles de SHA-256 contra originales previamente fijados y URI institucional. **16/16** tests sintéticos. SHA-256 de los bytes no es firma del proveedor ni licencia de uso; el cuerpo original de 2024 **NO fue descargado de nuevo en este ciclo**.

**C18 (local y observación documental previa):** manifiesto de **3 agregados** de dos BOCG: seis bajas/seis altas de adscripción de grupo (5+1) y ocho bajas/ocho altas de escaño, con fechas separadas. **21/21** tests. No se construye microdato personal inexistente.

**C19 (fuentes legales oficiales):** el Congreso dispone de aviso de reutilización con condiciones de integridad, no desnaturalización, atribución y actualización. Ley 37/2007 admite modalidades de reutilización, sujetas a protección de datos y condiciones aplicables. **No es autorización explícita para construir calificaciones personales subjetivas ni acreditación jurídica de derechos fuente por fuente.** Gate de puntuación sigue bloqueado; requiere examen específico.

**C20 (local):** seis gates de lanzamiento e identidad sin aprobar. Primer test de falsificación mostró que seis referencias fraudulentas podían superar el chequeo; reparación exige un registro de recibos verificados **bajo control del servidor**. Como ese registro aún no existe, el sistema permanece **cerrado**. **28/28** tests locales finales. No confundir suite sintética con pruebas de una aplicación desplegada.

## C. Validez adversarial y dependencia

Los casos de C11 y C12 proceden del **mismo boletín**; no son muestras independientes. Los cambios de grupo de C09–10 se seleccionaron después de observar anomalías; no hay holdout confirmatorio. Los ensayos locales C13–20 prueban propiedades de un **modelo de datos**, no verdad jurídica de las personas reales, causación política, seguridad del sitio público o efecto científico social. Los códigos de perfil de una misma legislatura no son IDs universales demostrados. El acceso público tampoco permite inferir un `first_public_at` con hora.

## D. Registro y reproducibilidad

- `research/C13_PREREG` no está materializado en el archivo local: se preserva como commit [53bce789](https://github.com/GalexY3/Metodologia-AB/commit/53bce789a14ecd8dd0c89841da88e1ef64d8f3d6). Los pre-registros C11 y C12 están en GitHub; C14–C20 sí están congelados en JSON local antes de los tests.
- GitHub conservó **C01–C12** en `research/pfl-ab20-identity-temporal-20261026` antes de suspender. **C13–C20 están en ESTE ARCHIVO LOCAL; NO han sido incorporados al repositorio.** No fingir que existen commits remotos de esos resultados.
- Código y pruebas locales en `src/`, `tests/`, manifiesto en `data/`. Ejecutar `PYTHONPATH=src python -m unittest discover -s tests -p 'test*.py' -v`. **28 tests pasan**, bajo Python local en este entorno. Para reproducir desde un clon limpio deben copiarse estos archivos y repetirse las ejecuciones; no se ha hecho una reproducción externa.
- La trayectoria se conserva en `CT2_TRAJECTORY.csv/json`, y dos gráficos generados por Python: rango 0–100 y rango ampliado, con punto de auditoría final separado.

## E. Umbral 2/3

**NO ACREDITADO.** Puede existir valor ingenieril 1/3 en futura auditoría, pero no se adjudica como novedad científica. Antecedentes relevantes: temporal databases/bitemporality, entity resolution y provenance records (no revisión sistemática externa). Falta **predicción novedosa discriminante y examen de estado del arte**, comparador competente sobre fuentes reales, identificadores/personas adjudicadas por terceros, muestreo prospectivo fuera de desarrollo y medidas éticas de scoring.

## F. Producto y siguiente decisión

Completitud aprobada PFL-V1 revisión 3 **36,350 %**; seis puertas de lanzamiento todavía bloqueadas. Recomendación de **BRANCHING 20**, con foco principal en localizar **fuente institucional de persona con ID por legislatura, historia de grupo con fecha de efectos**, adjudicar una pequeña cohorte independiente y, solo cuando proceda, validar primera publicación, derechos y reglas antes de exponer un fantasy real. Conservar cero GitHub Actions en este flujo hasta controlar el saldo de facturación.

**SOLICITO BRANCHING 20 CICLOS**