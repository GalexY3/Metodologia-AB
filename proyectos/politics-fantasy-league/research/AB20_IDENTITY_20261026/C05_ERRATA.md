# Errata C05

**Fallo observado:** Actions 40362392089, resultado STOP_R5 `ARCHIVE_LINK_NOT_UNIQUE`. La instrumentación suponía que el texto «Todos los diputados y diputadas de todas las legislaturas» aparecería *dentro* del anchor JSON. En la fuente HTML aparece como rótulo de fila; el anchor solamente dice «JSON».

**Corrección prospectiva y trazable:** reemplazar detección por texto de anchor con URL exacta observada en el enlace original público del Congreso, comprobando que continúa presente en el catálogo y manteniendo la validación de host HTTPS. La observación fallida no constituye un ciclo extra ni confirma ausencia de fuente. Conservar logs y ambos commits.

**Alcance:** prueba puramente documental; la existencia de un nombre homónimo en otra legislatura no resolvería identidad jurídica de la votación.
