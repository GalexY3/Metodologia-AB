# CURRENT · Mercados de pareja · 28/10/2026 · primera muestra diádica real

**Rama:** `research/ab-r-mercados-pareja-20261028`, sin merge a main. **Investigador:** Alejandro Panera Pascual. **Pregunta:** ¿puede surgir homogamia de valor sin homofilia explícita? **Estado científico:** exploratorio, sin inferencia causal aplicable a España ni hipótesis reputacional validada.

## Autorizaciones y saldo
- MATE10 10/10; BRANCH8 8/8; BRANCH6 6/6 (un intento de instrumentación inválido fuera del contador); EVIDENCE6 6/6.
- **EVIDENCE20:** 20 ciclos autorizados; 7/20 previos N21–N27 y **10 nuevos válidos N28–N37**, total **17/20 válidos**, más **1 intento instrumental inválido N32** registrado y reparado, **3 autorizados sin iniciar** por R5. No considerar los 3 restantes realizados. **No hay nueva autorización concedida**.
- Tipos de N28–N37: 2 documentales, 1 auditoría calidad, 4 empíricos descriptivos, 2 reanálisis/sensibilidad, 1 planificación. No todos son experimentos. N1 nuevos=0, N2=N3=0, N1 portfolio no auditado. CT2 17→17, ordinal no probabilidad.
- [Informe real-data](research/ABR_REALDATA13_20261028/REPORT.md), [ledger A–J](research/ABR_REALDATA13_20261028/LEDGER.json), [prereg](research/ABR_REALDATA13_20261028/PREREG.json), [reproducibilidad](research/ABR_REALDATA13_20261028/REPRODUCE.md), [resultados corregidos agregados](research/ABR_REALDATA13_20261028/AGGREGATE_RESULTS_REPAIRED.json), [control de popularidad](research/ABR_REALDATA13_20261028/N33_N35_EXTRA_RESULTS.json). [Ledger maestro EVIDENCE20 actualizado](research/ABR_EVIDENCE20_20261028/LEDGER.json).

## Datos empíricos nuevos · Mixmosa (NO Tinder)
- [Repositorio público](https://github.com/dankras/mixmosa-anonymized-data), tablas originales accesibles mediante conector GitHub, fecha presente de inspección 28/10/2026. Encuentros presenciales de 8 minutos.
- **1.895 fechas completas** en 30 eventos, 410 participantes (203 hombres/207 mujeres), 997 sí masculinos, 573 femeninos, **259 sí mutuos** (13,67% de fechas); sin duplicados de evento+díada ni discordancias de banderas. README dice 2.961 fechas: diferencias de selección sin explicar, **denominador válido para esta campaña = 1.895**.
- `swiping.csv` 4.437 decisiones dirigidas: 3.790 corresponden a dos elecciones por las citas completas, 647 extras de alcance no explicado. 1.888 de 1.895 citas tienen ambos atributos disponibles.
- **N30:** nulo permutación dentro de evento 288,278 mutuos, frente a 259 observados (cola inferior ~0,003); nulo preservando frecuencia de «sí» de cada mujer dentro de su evento media 266,018 (cola inferior ~0,172). La conclusión depende del control, sin identificación causal.
- **N31:** atractivo físico de candidato (valoración independiente) correlaciona con recibir sí `r_male=.1905`, `r_female=.3563`, fecha-ponderado, sin controles causales.
- **N32:** ingreso autodeclarado codificado 1–9 correlaciona menos en esta muestra `r_male=.0375`, `r_female=.0968`; el primer cálculo n=0 fue **INVALID_INSTRUMENT**, reparado con commit `c6d1fb56`; no reportar versión errónea.
- **N33:** popularidad cross-date leave-one-focal-dyad: `r` entre 259 mutuos `-0.01587`, control de permutación por evento [−0,16435; 0,06853] (cuantiles 2,5/97,5%), sin fuerte homogamia de valor medida como popularidad.
- **N35:** 44 participantes repiten evento, dependencia entre observaciones; leave-one-event-out del exceso mutuo mantiene signo negativo pero no da IC causal.
- **N36:** Essex XLSX, Columbia/OpenML, eHarmony y otras fuentes no pasaron acceso+procesado de segunda muestra diádica; **sin replicación externa independiente**.
- **N37:** no hay variable pública de estatus ante terceros después de un rechazo, ni marca temporal detallada. No validar `S_i(t+1)=S_i(t)-delta` en humanos.

## R5 y autorización pendiente
**STOP_LOCAL_R5 tras 10/13 nuevos ciclos.** Conservar los **3 restantes** hasta obtener un segundo dataset con IDs diádicos y respuestas en ambos sentidos o señal reputacional pública realmente medida, licencia/cumplimiento ético y designar una prueba no adaptada a resultados de Mixmosa. No repetir semillas para forzar homogeneidad. La corrida sobre datos originales se hizo con scripts JS recuperados del commit y datos del conector GitHub; **CLEAN_CLONE_NOT_VERIFIED**, no se rehostearon filas individuales en este repo.
