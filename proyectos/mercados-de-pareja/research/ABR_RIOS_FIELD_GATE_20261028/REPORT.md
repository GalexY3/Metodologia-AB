# Mercados de pareja · N79 · Control adversarial de evidencia de campo y originalidad · 28/10/2026

**Tipo real:** `DOCUMENTARY_AB`, 1 ciclo A–J documental **completado**, 0 experimentos propios, 0 simulations, 0 filas humanas originales analizadas, 0 invalidaciones. Antes de N79: 12/20 válidos; después: **13/20 válidos, 7 plazas N80–N86 pendientes**. Rama `research/ab-r-mercados-pareja-20261028`; no merge a main.

**Prerregistro:** [PREREG_N79.json](PREREG_N79.json) congelado en commit `b140dc0d0943826706e156dc39d758d75bb8029b` **después de localizar bibliográficamente** Rios et al. 2022/2023 y Rios–Torrico 2023, **antes de la lectura completa** de sus métodos primarios. Es prerregistro del *test de elegibilidad documental y de originalidad*, no descubrimiento bibliográfico preregistrado ni contraste estadístico propio preregistrado. No hay fuente de código experimental nuevo que congelar, ni resultados de intervención propia.

## A. Pregunta, estimando y contrato de verdad
¿Existe ya evidencia original más fuerte que ESBM sobre redes de exposición realmente mostradas, reciprocidad, historial dinámico y mejora al alterar la política de asignación de perfiles? **Unidad documental:** paper fuente primaria y su diseño con mercados de la app, fechas, exposición efectiva y controles. **Estimando original ajeno:** efecto de cambiar el algoritmo sobre matches diarios en los mercados tratados frente a control, sujeto a tendencias paralelas/interferencia, y mecanismo de match previo sobre el like del decisor. No se estima ninguna relación causal propia del proyecto. Match = aceptación bilateral en app; no convivencia, bienestar ni duración. Riesgo de confundir trazas privadas/licencias.

## B. Rivales abiertos
- **H1** se verifica documentalmente: una plataforma real usó historia de exposición, propuestas bilaterales y dinámicas; cambia algoritmos y contrasta resultados en campo. Ya no es novedosa la contribución genérica del ESBM sobre ranking/reciprocidad/feedback histórico.
- **H0**: solo había simulaciones ajustadas con dato propietario, sin ninguna intervención, de modo que el control adversarial no aportaría información nueva sobre identificación.
- **H_otra**: aunque haya intervención de campo, su inferencia puede estar sesgada por tendencias, selección, equilibrio e interferencia; además su outcome corto plazo no mide las relaciones duraderas o desigualdad.

## C. Prueba discriminante documental y controles competentes
El prerregistro exigió inspeccionar documento original completo, enumerar variables observadas y fuentes de variación, separar `PROP` teoría/formalismo de `EMP` resultados empíricos, identificar muestra y efectos, y cotejar contra los controles previos de [Chen 2023](../PRIORS/SOURCES.json) SRC032, Hitsch 2010 SRC002/SRC053 y Topinkova–Diviak 2025 SRC021. Un resultado de simple catálogo no contaría ciclo. La evidencia primaria muestra intervención y diferencia frente al algoritmo del socio real, no solo un modelo caricaturizado. Pero esas comparaciones no se reejecutaron y la evidencia de Chen/Topinkova procede del registro previo, no de una relectura original en N79.

## D. Instrumentación y procedencia original
1. **SRC054:** Ignacio Rios, Daniela Saban y Fanyin Zheng, *Improving Match Rates in Dating Markets Through Assortment Optimization*, publicación web 7 abr 2022; M&SOM 25(4) 1304–1323 (2023), DOI https://doi.org/10.1287/msom.2022.1107 . PDF original disponible en repositorio Imperial, https://spiral.imperial.ac.uk/server/api/core/bitstreams/2e71c36d-4b6f-4626-a286-ffcab6948057/content . Se inspeccionó texto extraído del **PDF original de 58 páginas**: pp. PDF P6–P7 (plataforma y datos), P13–P15 (identificación de historial, modificación 17-may-2019), P27–P31 (dos mercados, tablas 2 y 3) y P53–P54 (segunda intervención y placebo, Tabla 20). La captura visual PDF P0 funcionó; capturas web posteriores de otras páginas devolvieron **cache miss**, así que los valores tabulares proceden del texto PDF indexado, sin auditoría visual de tablas completas.
2. **SRC055:** Ignacio Rios y Alfredo Torrico, *Platform Design in Curated Dating Markets*, arXiv https://arxiv.org/abs/2308.02584 , manuscrito 2023 (y revisiones). Texto original arXiv HTML abierto, sección 1 y resumen de resultados, con modelado de una/dos direcciones, matches secuenciales/no secuenciales, garantías teóricas y simulaciones con datos privados. No afirmar un segundo experimento de campo en ese artículo.
3. **Datos brutos**: ambos artículos remiten a `industry partner` propietario, con plataforma anónima por NDA. Ningún CSV, microfila, licencia de datos o historial individual descargado, ningún código del algoritmo inspeccionado. Repositorio GitHub contiene solo auditable material documental y resultados agregados publicados. Las dos publicaciones pueden compartir fuente; **NO replicaciones independientes**.

## E. Resultado documental discriminante
**En el paper SRC054** el socio tenía ~800.000 usuarios activos en >150 mercados, y en cada sesión ofrecía 3 a 9 perfiles diarios (media 3,53), recabando likes y descartes, con restricciones de elegibilidad bilateral. Los investigadores informan de observar `assortments` mostrados, decisiones por perfil, inicio de sesión, historial de encuentros y `backlogs` (personas que dieron like y todavía no fueron vistas por la otra parte). No se han visto esos registros desde el proyecto.

La modificación de plataforma de **17 mayo 2019** admitió mostrar candidatos inactivos previamente excluidos del backlog y fue empleada como variación cuasiexógena en la estimación del efecto de éxito previo sobre nuevos likes. El artículo informa de que **un match extra disminuye la probabilidad posterior de like al menos un 3 %** bajo su modelo y supuestos. No confundirlo con pérdida pública de estatus por rechazo; es respuesta privada **después de éxito**.

Se describen dos intervenciones posteriores comparando `Dating Heuristic` vs algoritmo antiguo del socio real, usando diferencias en diferencias por ciudad. **Houston 19–25 ago 2020** frente a Austin y Dallas–Fort Worth con cambio estimado +27,286 matches/día y **+27,13 %** respecto al efecto fijo de Houston (Tabla 2, p PDF P29/P30). **Austin 9–15 sep 2020** frente Houston y Dallas–Fort Worth: +52,857 matches/día, **+37,95 %** (Tabla 20 p PDF P54). Son **estimaciones ajenas**. En Houston 839 de los 890 matches de la semana posterior fueron secuenciales/backlog (Tabla 3); la fracción de perfiles libres del algoritmo fue solo **38,30 %** durante la primera intervención y **49,57 %** en la segunda, según los autores. No atribuir efectos exclusivamente a una feature.

**En el paper SRC055** el algoritmo bidireccional, la temporalidad y las políticas secuenciales ya son objetos formales de estudio, con garantías de aproximación condicionadas a su propio objetivo y supuestos. Sus resultados de datos reales alimentan simulaciones de recomendaciones, no observaciones experimentales nuevas identificables por separado.

**Dictamen de originalidad:** la noción ESBM de "mostrado → like → reciprocidad → match", su política de recomendación dinámica y un mecanismo de historial de **éxitos** no son una contribución general original. La diferenciación entre etapas más amplias (relación estable, bienestar, normas y exclusiones) sigue siendo una *agenda abierta*, no resultado mejor que los estudios publicados.

## F. Auditoría adversarial
- Los **tres mercados** de evaluación no constituyen cientos de unidades asignadas aleatoriamente. El paper afirma que uno fue elegido aleatoriamente para tratamiento en cada intervención, pero un diseño DID con pocos clusters requiere cautela: tendencias paralelas no se *prueban* mediante p no significativo, puede haber shocks simultáneos y datos desconocidos fuera de la compañía.
- La modificación de 2019 de backlog introduce una fuente cuasiexperimental potencial; exclusión causal, selección de usuarios y ausencia de interferencia requieren supuestos. Es especialmente relevante la restricción temporal de 3 días para minimizar spillovers, pero no los elimina por demostración.
- Las estimaciones +27 % y +38 % NO son tasas poblacionales de emparejamiento humano ni ganancias en relación duradera. En ESBM el total de exposiciones cambia endógenamente con la formación de pareja y las condiciones carecen de paridad informativa; comparación directa de tamaños de efecto no es legítima.
- `Rios–Torrico` no puede contarse como fuente externa **independiente** sin verificar cohorte y derechos; es una extensión relacionada.
- El histórico ESBM de **rechazo privado**, **señal reputacional pública** y **éxito previo** son **tres mecanismos distintos**. El paper estudia el último, no valida el hipotético castigo público tras rechazo.
- Todas las cifras y métodos se atribuyen a autores originales. No se accedió a datos brutos y no se ejecutó su DID; la verificación visual de algunas tablas PDF quedó bloqueada aunque el texto original se abrió. No se confirma reproducibilidad externa de su experimento.

## G. Confirmación independiente
**No realizada.** Son dos intervenciones del mismo socio en diferentes mercados/semanas; para nosotros son evidencia publicada por terceros, no un holdout propio ni una replicación externa sobre fuente pública. La teoría Rios–Torrico es un desarrollo del mismo problema, no una segunda muestra verificada.

## H. Actualización abductivo-bayesiana
- Dos registros nuevos **SRC054/SRC055**; **55 registros**, no 55 cohortes independientes.
- Siete eventos append-only **U059–U065**, seis priors actualizados (P-NOVELTY, P-PLATFORM-RANKING, P-FEEDBACK, P-DYADIC_ACCESS, P-OPPORTUNITY, P-PUBLIC_REPUTATION) y nuevo prior **P-HISTORY-SUCCESS**: **27 priors** cualitativos, **65 revisiones**. `NO_CHANGE_WITH_REASON` sobre acceso, oportunidades propias y reputación pública.
- Nueva rival a medir: **saciación por éxito reciente** reduce la probabilidad de emitir nuevos likes. No estimamos coeficiente en ESBM ni importamos el −3 % como calibración universal.

## I. Dictamen científico y CT2
**Validez documental:** fuente original y métodos legibles; contraste de novedad directo contra ESBM. **Validez interna propia:** no hay estimación nueva. **Identificación causal propia:** NO. **Reproducibilidad de fuente privada:** NO. **N1 nuevo/N2/N3:** 0/0/0. **Grado de novedad científica propia:** 0/3. `CT2=7→6/100` **ordinal, no probabilidad**, por antecedente público directamente solapado con algoritmo de ESBM; en contraste persiste abierta la posibilidad de una predicción nueva sobre resultados duraderos. DRIFT **D0,4** misma rama y estimando científico, nueva clase de fuente original.

## J. AB-DECIDE
**N79 = DOCUMENTARY_AB válido cerrado con resultado adversarial**, ninguna prueba de usuarios nueva. **`STOP_R5` con 7 plazas N80–N86 ya autorizadas NO iniciadas.** Próxima ruta requiere acceso legal a una fuente de observaciones propias (opciones HCMST/Essex/pairfam/E218862/E112322 o contacto autorizado con industria), de modo que una predicción focal **distinta** del artículo Rios pueda ejecutarse y confrontarse con sus baselines. No repetir auditoría del mismo manuscrito como otro ciclo. No main merge.

## Trayectoria CT2
[CT2_TRAJECTORY.json](CT2_TRAJECTORY.json), [CT2.svg](CT2.svg) ambos 0–100 + zoom; puntos N77=7, N78=7, N79=6, solo decisiones registradas.
