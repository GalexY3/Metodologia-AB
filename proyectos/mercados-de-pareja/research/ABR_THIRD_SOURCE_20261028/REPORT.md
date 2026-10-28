# N56–N57 · Tercera fuente de aplicaciones y auditoría de novedad

**Fecha:** 28 de octubre de 2026. **Rama:** research/ab-r-mercados-pareja-20261028, no fusionada con main. **Autorización de origen:** 20 ciclos AB-R para N47 en adelante. Se habían ejecutado nueve, y restaban once. Se han realizado **dos ciclos documentales A–J N56 y N57**, cero experimentos nuevos y cero intentos inválidos; **saldo actual nueve ciclos autorizados NO ejecutados** (N58–N66), detenidos por R5. La actualización de fuentes y priors se realizó como **mantenimiento documental adicional sin computar ciclo**.

## N56 · Acceso a tercera fuente

[Topinkova y Diviak (2025), PLOS ONE](https://doi.org/10.1371/journal.pone.0327477) publica un estudio observacional sobre 10.528 usuarios activos de una app de citas checa, con dirigidos intentos de contacto y reciprocidad. El artículo remite los archivos al [OSF 6zcrs](https://osf.io/6zcrs/), pero no se recuperó fichero alguno: web HTTP 403 y descarga de contenedor bloqueada por DNS. **No se inspeccionaron microdatos, columnas, licencias de ficheros ni marcas temporales**. El artículo está publicado bajo CC BY, pero ello **no verifica los derechos de redistribución del dataset OSF**.

Los autores afirman explícitamente que no saben qué perfiles se mostraron a cada usuario. Su popularidad se deriva de grados de recepción de contacto durante el período. No se ha demostrado que su conjunto contenga popularidad conocida antes de mostrar perfiles, por lo que **no supera nuestro requisito conjunto de exposición completa + popularidad previa + decisiones bilaterales**. Aunque puede ser una excelente réplica *descriptiva* futura de redes de invitación, no debe proclamarse un experimento prospectivo sobre pérdidas públicas de prestigio.

Se localizaron también otras fuentes: [Topinkova y Schwemmer, 2025](https://doi.org/10.31235/osf.io/8hdws_v1), experimental sobre información de popularidad en perfiles ficticios sin reciprocidad humana real; [Moreno y cols., 2026](https://doi.org/10.1177/01461672251409231) con informes de ambos miembros de citas pero sin evidencia accesible aquí de universo de exposiciones; y [Šetinová y Topinková, 2021](https://doi.org/10.20377/jfr-540), que podría solaparse con la fuente checa 2017. Tampoco se descargaron los microdatos de estos trabajos. Ver [auditoría de fuentes](SOURCE_AND_NOVELTY_AUDIT.md).

## N57 · Prior art casi coincidente con la tesis general

El texto de Topinkova y Diviak documenta que los contactos masculinos iniciales son aspiracionales en deseabilidad, mientras los contactos recíprocos son bastante más semejantes en esa jerarquía. El resultado de la literatura es compatible con filtrado por rechazo o ausencia de reciprocidad, aunque no demuestra un efecto causal aislado del rechazo. Bajo medidas de indegree normalizado, informa diferencias de orden de −0,16 (Brno) y −0,08 (Praga) en intentos masculinos, más pequeñas entre aristas recíprocas (−0,032 y −0,019). Se consultó la exposición publicada y no se ejecutó ningún cálculo a partir del dataset propio.

**Resultado adversarial:** la afirmación genérica de “homogamia emergente de deseabilidad en contactos recíprocos sin preferir previamente semejanza” no es novedosa. Por su proximidad a nuestra tesis, CT2 baja **13→7/100**, juicio **ordinal de camino a un 2/3**, no probabilidad de que el fenómeno exista. Ningún hallazgo nuevo 1/3, 2/3 o 3/3 se acredita aquí.

Separar claramente:
- **Filtrado de no reciprocidad:** de contactos asimétricos se pasa a subset de intereses recíprocos, con reducción de diferencias.
- **Pérdida causal de estatus público del rechazado:** terceros observan el rechazo y luego revisan a la baja su valoración. No hay medición fiable de este segundo efecto en nuestros datos ni en la publicación citada.
- **Formación de relación:** contactos recíprocos no garantizan pareja estable o matrimonio.

## Gobernanza: source-backed priors ya persistentes

Por orden del investigador, se incorporó a las instrucciones del repositorio una norma **obligatoria para futuros descubrimientos documentales**: registrar la fuente y aportación concreta, y actualizar al menos un prior o justificar no-change. [Norma y esquema](../PRIORS/README.md), [SOURCES](../PRIORS/SOURCES.json), [PRIORS](../PRIORS/PRIORS.json) y [UPDATES](../PRIORS/UPDATES.json).

Se consolidaron **29 fuentes bibliográficas y de datos**, **14 hipótesis-priors cualitativas** y **25 entradas de actualización o revisión**, todas las fuentes vinculadas con al menos un cambio/no-cambio, con prueba de procedencia y límites. Los históricos se marcan como **backfill retrospectivo**: no se finge que fueran priors prerregistrados. Las probabilidades bayesianas se dejan nulas; no confundir CT2 con una probabilidad de hipótesis. Las entradas futuras requieren bibliografía deduplicada, fecha, qué aporta, estado real de acceso y qué nos haría revisar el juicio.

En el A–J N56 y N57 quedaron agregados los IDs de fuente, prior y actualización; el ledger maestro [ABR_TWO_WAY20](../ABR_TWO_WAY20_20261028/LEDGER.json) registra 11/20 ciclos válidos, 9 sin iniciar. **Ninguna fuente ha sido declarada procesada si solo se accedió a la ficha.**

## AB-DECIDE · R5

**STOP** con nueve plazas sin iniciar, porque otra simulación con la misma estructura no discrimina un mecanismo ya documentado y el nuevo depósito no es accesible con medidas prospectivas suficientes. Volver a abrir N58 exige como mínimo un instrumento independiente con conjunto de exposición, decisión de ambos miembros y tiempo para popularidad precontacto, una predicción distinta de Topinkova–Diviak, licencia verificable y un prereg antes de calcular resultados.

CT2 de esta subcampaña: **13→13 (N56)→7 (N57)**, ordinal. N1 nuevos=0; N2=N3=0. No hay permiso para relajar R5 por presupuesto disponible. El acceso a OSF podrá reintentarse sin fingir que ya se descargó.
