# PF-SEQ32S · priors acumulativos emergentes, no diseñados anticipadamente

Esta tabla se amplía **después** de cada observación y no enumera objetivos futuros. Conserva las campañas anteriores, sin reescribir PF-P, PF-R, etc. No hay actualización bayesiana numérica: las observaciones son fuentes relacionadas o ejecuciones técnicas, no muestras calibradas de un modelo estadístico.

| ID | Prior / hipótesis y procedencia | Evidencia favorable observada | Evidencia adversa, alcance, falsador |
|---|---|---|---|
| PF-S01 | Un directorio institucional indexado puede **no** suministrar un fichero original reutilizable de partidos. Inspección del Registro RPP. | Portal RPP consultado vía web devolvió 502; metadatos describen filtros y PDF a demanda, no dump garantizado. | Fallo de acceso localizado; navegación funcional alternativa o export posterior lo refutaría. No significa que ningún dato exista. |
| PF-S02 | Un vínculo oficial indexado a un JSON histórico de personas **no implica** que el recurso siga descargable. | Link de julio 2026 indexado con campos en el buscador; CI nativo 40341944931 devolvió 404 al obtener el original. | Cache de buscador y endpoint cambiante; un archivo de Congreso recapturado de forma autenticada refuta indisponibilidad permanente. Contrato local de proyector aprobado sin captura real. |
| PF-S03 | Un acto único de nombramientos institucionales del BOE permite construir un **conjunto positivo pero acotado** de personas y cargos con fechas documentales. | Real Decreto 835/2023, 22 nombramientos; HTTPS 193.759 bytes SHA256 `16f05bba24508af229870b68dbfb72ba258e62416713a8cfe5c49c70ba792efe`; reextracción y match 22/22 en CI 40342982881. | Misma disposición y un solo momento; no prueba identidad legal RPP, continuidad a octubre 2026, actividad parlamentaria, primera publicación previa o valoración política. Corrigió fallo de gramática «del Interior» tras ver CI. Falsador: nuevo original o corrección BOE que altere registros. |

**Fuentes primarias:** [BOE 835/2023](https://www.boe.es/buscar/doc.php?id=BOE-A-2023-23543), [PDF](https://www.boe.es/boe/dias/2023/11/21/pdfs/BOE-A-2023-23543.pdf), [Catálogo Congreso](https://www.congreso.es/gl/opendata/diputados), [Registro](https://servicio.mir.es/nfrontal/webpartido_politico.html).

**Regla permanente:** 'nombre en un documento oficial' ≠ 'identificador único de una persona a través de legislaturas'; 'cargo nombrado en 2023' ≠ 'cargo vigente en 2026'; 'formación electoral' ≠ 'partido jurídico inscrito'; la observación del boletín no crea puntos fantasy.
