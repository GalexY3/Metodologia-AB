# AB-R · Puerta N38: segunda muestra independiente · 28/10/2026

**Responsable del programa:** Alejandro Panera Pascual. **Estado:** una fase documental/de planificación AB A–J válida, **cero experimentos y cero análisis de parejas de una segunda muestra**, dos plazas restantes sin iniciar. Rama `research/ab-r-mercados-pareja-20261028`, no merge a main.

## Motivación y alcance
La subcampaña REALDATA13 obtuvo en Mixmosa, con 1.895 citas completas, 259 aceptaciones recíprocas y 30 eventos, una correlación de popularidad de los participantes entre aceptaciones mutuas `r≈−0,01587` usando likes de otras citas (exclusión de la díada focal). El contraste por evento incluía ese valor. Este resultado observado NO respalda la diagonal fuerte de algunas simulaciones, pero no es una refutación externa general de homogamia sobre constructos latentes. **Repetir el estudio en datos verdaderamente independientes es necesario antes de ajustar y contrastar una nueva teoría.**

## Datos realmente inspeccionados y bloqueos

### 1. Essex · Rational Inattention in Online Dating (Ortega 2018)
[Registro institucional](https://researchdata.essex.ac.uk/85/) confirma `AnonymizedData.xlsx`, 67 kB, licencia CC BY 4.0 y aprobación ética de experimento de 2018 en Reino Unido. El fichero no pudo descargarse en esta sesión mediante contenedor (error DNS) ni abrirse como tabla en navegador. **No se inspeccionaron filas o columnas; su validez para este estimando se desconoce.**

### 2. eHarmony · McFee y Lanckriet
[Catálogo](https://brianmcfee.net/data/eharmony.html) informa de dos cortes temporales, archivos de atributos normalizados/ofuscados y etiquetas por **par de usuarios**. Los archivos gzip no se descargaron ni inspeccionaron. Incluso con ellos, la etiqueta binaria positiva/negativa no implica disponer de dos decisiones individuales de aceptación; por tanto, no dar por equivalente a reciprocidad en Mixmosa. Los atributos no pueden interpretarse como renta o atractivo sin diccionario.

### 3. Columbia/OpenML · original
[Repositorio](https://github.com/datasets/speed-dating) ofrece `data/speed-dating.csv`. Su Git blob sha verificado es `7a39a97ed38fdc388b55a79e54c167e95552dabb`. Sin embargo, la lectura mediante conector GitHub devolvió `content=""` tanto en UTF-8 como Base64 y en rangos parciales; el acceso al raw con contenedor tampoco resolvió DNS. **No se realizó un análisis de sus registros completos.** Documentación de fuente indica 8.378 filas/195 campos, incluidos `iid,pid,wave,dec,dec_o,match`, pero esa estructura concreta no ha sido validada a partir de las filas. Además, [Andrew Gelman (2015)](https://statmodeling.stat.columbia.edu/2015/08/01/if-you-leave-your-datasets-sitting-out-on-the-counter-they-get-moldy/) documenta advertencias sobre inconsistencias entre `dec`, `dec_o` y `match` en ciertas versiones; sería obligatoria una auditoría cruzada por díada antes de calcular resultados.

### 4. Columbia · copia reducida realmente analizada para el control de acceso
El archivo [`keithmcnulty/speed_dating/speed_data_data.csv`](https://github.com/keithmcnulty/speed_dating/blob/master/speed_data_data.csv) sí fue leído: Git blob `239a05b5ca40bbb746ee12c27de61327a3ffd953`, 427.919 caracteres, **8.378 filas** y **15 columnas**: `gender,age,income,goal,career,dec,attr,sinc,intel,fun,amb,shar,like,prob,met`. Se comprobaron 4.194 filas etiquetadas hombre, 4.184 mujer, 3.373 `dec=1`, 4.763 `dec=0` y 242 decisiones ausentes o no binarias. **No hay identificador de la contraparte (`pid`), de evento (`wave`) ni resultado mutuo**. Por construcción no permite calcular `Corr(popularidad_h,popularidad_m | aceptación_mutua)` ni una permutación de aceptación dentro de evento, los dos contrastes que queríamos replicar. Estos conteos son auditoría de compatibilidad, **no replicación** de resultados Mixmosa.

### 5. Columbia · Parquet completo legible como Base64, aún no analizado
En [`ZharlieSineFine/Speed-Dating-Reciprocal-Recommender-System`](https://github.com/ZharlieSineFine/Speed-Dating-Reciprocal-Recommender-System), el archivo `Stage 0 Data and Pre-processing/speed_dating_clean.parquet`, Git blob SHA `c873e1466f9594f3b709b0da70d7dc4a2739b1cd`, sí se recuperó como **403.601 caracteres Base64** mediante conector GitHub; una versión CSV demasiado grande retornó contenido vacío. Su contenido binario no pudo materializarse como fichero Parquet de trabajo ni analizarse por filas dentro de las herramientas actuales. Su README declara datos limpios y trabajo de recomendación recíproca, pero **todavía no se puede conceder validación de nombres, tipado, IDs o concordancia de decisiones.** Este archivo es la vía más directa para continuar si puede descargarse a un entorno Python o Work con acceso.

## Puerta N39 (no ejecutada)
Una fuente suficiente debe proporcionar realmente un registro por pareja potencial evaluada con:
- ID seudónimo de ambos participantes y evento/horizonte de exposición;
- decisiones individuales de ambos lados, o definición inequívoca de resultado mutuo;
- suficientes citas por persona para popularidad calculada sin la díada focal;
- tasa/filtrado de observaciones conocidas, calidad del join, versiones/hashes y derechos de uso;
- un control de aleatorización condicionado a la composición real del evento y, cuando sea posible, a propensiones individuales;
- evaluación preregistrada de correlación de popularidad en los emparejamientos recíprocos, presentada con cobertura de candidatos y sensibilidad a dependencia por participante.

La pretensión de una réplica de Mixmosa debe separar **convergencia del estimando de popularidad**, de **confirmación del mecanismo social**: dos datasets de citas rápidas no validan por sí mismos un mercado digital español ni el descenso efectivo de reputación social tras un rechazo.

## Cómputo AB y decisión
Saldo inicial: tres plazas autorizadas N38–N40. **N38 completado como planificación documental de acceso**, sin experimento con personas ni simulación. **N39 y N40 siguen sin iniciar.** Inválidos en este bloque: cero. CT2 conserva **17/100**, ordinal y no probabilidad; hallazgos de nivel 2/3 y 3/3: cero. **AB-DECIDE = STOP_R5**, porque las siguientes acciones requieren un archivo diádico procesable; seguir repitiendo búsquedas y cómputos sintéticos no valida nada.

La acción concreta para desbloquear N39 es abrir la versión original de Columbia o el [Parquet completo](https://github.com/ZharlieSineFine/Speed-Dating-Reciprocal-Recommender-System/tree/main/Stage%200%20Data%20and%20Pre-processing) en Work o en un ordenador con descarga y Python, verificar el esquema y guardar resumen de calidad sin publicar información sensible. No se ejecutaron ni prometieron procesos de fondo. El [ledger](LEDGER.json) y la [auditoría de fuentes](SOURCE_ACCESS_AUDIT.json) permiten verificar los límites.
