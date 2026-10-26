# Politics Fantasy League — AB-H BRANCHING20 · cierre R5 tras C04
**Fecha:** 26-10-2026  
**Rama:** `research/pfl-abh-branch20-20261026` (derivada de `main` tras AB Atlas 0.3)  
**Autorización nueva:** 20 ciclos BRANCHING. **Consumidos:** 4. **Conservados:** 16.  
**Estado:** `STOP_R5`, NO cierre ficticio de las 20 plazas.

## Contabilidad y trazabilidad
Antes de empezar se comprobó el histórico: AB20 previo cerrado 20/20 según informe final incorporado posteriormente, aunque el ledger legado de GitHub aún indicaba 12/20; AB20B cerró 20/20 con pares C01-C20 PREREG/RESULT y consta en [PR #15](https://github.com/GalexY3/Metodologia-AB/pull/15), **abierta, no fusionada**. La evaluación de AB Atlas O7 es otra línea y NO cuenta como ciclos de Politics Fantasy.

Los resultados aquí documentados no actualizan automáticamente PR #15 y NO incorporan todo su árbol. El módulo `typed_refs.py` se importó desde AB20B para su uso como guardia independiente, sin afirmar nuevas propiedades científicas.

## Ciclos individuales, adaptativos
**C01 — fuente masiva del Congreso.** Prerregistro congelado antes de seguir el enlace `JSON` de «Todos los diputados y diputadas de todas las legislaturas» en [catálogo oficial](https://www.congreso.es/gl/opendata/diputados). El enlace de exportación apuntó a `Diput__20260725050229.json`, pero esta sesión obtuvo `CACHE_MISS`. **Inconcluso**, no implica ausencia de un ID global ni caída demostrada del proveedor. No se asigna identidad.

**C02 — alcance real de `codParlamentario`.** Tras C01, se prerregistraron dos figuras públicas para cotejo XIV/XV. El [listado de órgano XIV](https://www.congreso.es/en/organos/composicion-en-la-legislatura?_organos_selectedLegislatura=XIV&_organos_selectedOrganoSup=1&_organos_selectedSuborgano=358&p_p_id=organos&p_p_lifecycle=2&p_p_resource_id=searchOrgano) exhibe Rufián Romero 187 y el [XV](https://www.congreso.es/es/organos/composicion-en-la-legislatura?_organos_selectedLegislatura=XV&_organos_selectedOrganoSup=-20&_organos_selectedSuborgano=343&p_p_id=organos&p_p_lifecycle=2&p_p_resource_id=searchOrgano) 312. El [grupo XIV](https://www.congreso.es/en/grupos/composicion-en-la-legislatura?_grupos_gruposView=true&_grupos_idGrupo=204&_grupos_idLegislatura=XIV&_grupos_mostrarFicha=true&p_p_id=grupos&p_p_lifecycle=2&p_p_resource_id=diputadosSearch) señala Díaz Pérez 171 y el [órgano XV](https://www.congreso.es/es/organos/composicion-en-la-legislatura?_organos_selectedLegislatura=XV&_organos_selectedOrganoSup=1&_organos_selectedSuborgano=312&p_p_id=organos&p_p_lifecycle=2&p_p_resource_id=searchOrgano) 342. **Dos de dos casos seleccionados** muestran códigos distintos, refutando la hipótesis de inmutabilidad numérica para esos casos. No es una tasa poblacional ni adjudicación independiente de identidad por tercero. No inferir automáticamente igualdad entre registros usando el nombre.

**C03 — registro jurídico de partidos.** Se inspeccionaron los procedimientos oficiales del Ministerio del Interior: [Información 992323](https://sede.interior.gob.es/portal/sede/tramites/detalle-tramite?id=22), [certificado 992324](https://sede.interior.gob.es/portal/sede/tramites/detalle-tramite?id=23), e [inscripción 992320](https://sede.interior.gob.es/portal/sede/tramites/detalle-tramite?id=24). Existe vía institucional de solicitud, pero en este ciclo **no se descargó ni verificó una ficha registral con identificador y cronología**. Prohibido equiparar partido legal, coalición, candidatura, grupo parlamentario o sigla solo por cadenas coincidentes. Estado inconcluso, `R5` sobre la identificación jurídica.

**C04 — guarda de referencias tipadas (AB-P).** Se importó en la rama el módulo conservador de [AB20B C17](https://github.com/GalexY3/Metodologia-AB/pull/15), junto con seis pruebas focalizadas: igualdad exacta de namespace; desigualdad de mismo número entre legislaturas; desigualdad de mismo número entre familias de expediente; rechazo de campos vacíos; rechazo de atestación aportada por llamador; y prohibición de scoring personal. **6/6 PASS en Python local de staging**, sin Actions. El código quedó publicado, pero **aún no conectado al servidor HTTP, no se hizo clone limpio y no se comprobó E2E en esta rama**. No contar como gate de lanzamiento.

## Separación epistemológica, desarrollo y validación
**AB-R:** solo contraste documental exploratorio y dos casos negativos delimitados, sin validación de identidad longitudinal poblacional, sin baseline de enlazado adjudicado, sin holdout. **CT2 identidad 29/100 constante; N1/N2/N3 nuevos: 0.**

**AB-P:** módulo fuente-tipado disponible en rama para reducir riesgos de uniones ilícitas. Sigue pendiente su integración HTTP y aceptación de seguridad. **PFL-V1 rev.3 36,35% constante; seis gates de lanzamiento bloqueados, 0/6 acreditados.** No calcular puntuaciones de políticos reales.

**VSDS:** 1/3, inalterado. La ejecución de tests de software no modifica este indicador.

## Incidencias y limitaciones
Quedan tres complaints abiertas sobre: (i) enlace masivo del Congreso inaccesible para este entorno; (ii) ausencia de ficha primaria del Registro de Partidos en la evidencia adquirida; (iii) guarda técnica no integrada, validada únicamente en staging. Estas complaints son observaciones/limitaciones, no errores sistémicos confirmados.

**GitHub Actions:** ningún workflow solicitado manualmente. Todos los commits de la nueva rama usan `[skip ci]` para evitar `push`/PR Actions. La documentación oficial de GitHub confirma la semántica de `[skip ci]`; no sustituye la CI normal cuando se quiera integrar. No se crea PR que induzca validaciones costosas.

**AB Atlas:** un único delta `updates/0001-abh-br20-20261026.json`, 16 operaciones, 3 nodos adicionales, 6 relaciones, 4 receipts de ejecución y 3 complaints, sin cambios a seed, seis gates, CT2, VSDS o porcentaje de producto. Se comprobó por código en memoria la unicidad de IDs y referencias respecto del `seed.json` real. **`python ab_atlas/atlas_delta.py check` todavía no se ha ejecutado**: el repositorio privado no está montado localmente y se evitaron GitHub Actions. No presentar el chequeo parcial como validación integral.

## Razón concreta para detenerse
Los siguientes ensayos originales dependerían de una ficha RPP con historia jurídica (partidos), de una correspondencia de personas entre legislaturas autenticada/adjudicada, o de un corpus original de eventos con fecha efectiva y primera publicación verificables. Seguir probando variantes sobre los mismos dos nombres, fuentes conocidas o fixtures no produciría nueva evidencia discriminante. Por `R5`, las **16 plazas restantes no se consumen** y se pueden reanudar cuando exista evidencia nueva.

## Necesidades antes de reanudar
Una vía de obtención documental de Registro de Partidos; un crosswalk institucional o pequeño conjunto de casos independientes adjudicados entre legislaturas; conocimiento de derechos aplicables a reutilización y primeras fechas públicas; en AB-P una auditoría real de controles de servidor, autenticación y pruebas HTTP/E2E cuando el presupuesto permita la CI. Evitar pedir credenciales o identificadores personales sensibles para esta tarea en el chat. No se piden más ciclos.
