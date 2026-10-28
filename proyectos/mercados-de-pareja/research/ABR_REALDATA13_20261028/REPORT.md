# Mercados de pareja · AB-R REALDATA13 · Informe N28–N37

**Autoría del programa:** Alejandro Panera Pascual. **Fecha:** 28/10/2026. **Rama:** `research/ab-r-mercados-pareja-20261028`, sin fusionar a `main`. **Autorización:** continuar las 13 plazas aún disponibles de EVIDENCE20 (de una autorización total original de 20). **Cierre:** 10 ciclos completos A–J N28–N37 dentro de su alcance, 1 intento instrumental inválido registrado y reparado, **3 plazas autorizadas sin iniciar** por R5. Sin nuevo hallazgo 2/3 o 3/3. CT2 17→17, juicio ordinal no probabilístico.

## Cambio científico relevante: primera fuente con observaciones diádicas reales

El [repositorio de Mixmosa](https://github.com/dankras/mixmosa-anonymized-data) ha permitido obtener realmente `csv/interactions.csv`, `csv/user_features.csv`, `csv/swiping.csv` y `csv/events.csv` mediante el conector GitHub. Son registros anónimos de **citas presenciales de 8 minutos**, no swipes de Tinder ni una muestra española. El README anuncia 2.961 citas, mientras `interactions.csv` contiene **1.895 citas completas**, una discrepancia de cobertura que no debe corregirse artificialmente.

Las 1.895 citas se distribuyen en 30 eventos y 410 participantes (203 hombres, 207 mujeres; 1.888 citas permiten cruzar atributos de ambos). No se detectaron duplicados evento-pareja ni discordancias entre el indicador mutuo y las dos respuestas, ni discordancias de los 3.790 swipes que corresponden a esas citas. El archivo `swiping.csv` contiene **4.437 decisiones**, de modo que 647 no forman parte de las 1.895 citas completas; se desconoce el motivo exacto de exclusión. No se supone que las 647 decisiones constituyan nuevas parejas.

En las fechas completas: los hombres dieron derecha/sí en **997/1.895 = 52,61%**, las mujeres **573/1.895 = 30,24%**, y hubo **259/1.895 = 13,67%** aceptaciones mutuas. Estos porcentajes son de las citas observadas, no tasas poblacionales de oportunidad de pareja.

## N30 · El exceso de reciprocidad depende del control correcto

Se fijaron 1.000 permutaciones con semilla 20261028, conservando todas las citas observadas. Al permutar las respuestas femeninas **dentro de cada evento**, preservando el total de sí por evento, la reciprocidad nula media fue 288,278 frente a 259 observadas (cuantil 2,5–97,5% de la aleatorización: 270–307; cola inferior ~0,003). **No se observa exceso positivo** bajo este control.

En cambio, al permutar solamente las decisiones de una misma mujer **dentro de su evento**, preservando exactamente su frecuencia de aceptación individual, el promedio nulo bajó a **266,018**, con cuantiles 252–280; cola inferior ~0,172, una diferencia no concluyente. Esto revela un cambio importante de interpretación al controlar la selectividad de cada actor.

**Precaución:** las permutaciones son una herramienta inferencial condicionada a las aristas de citas ya observadas. No convierten la asignación a citas en aleatoria ni separan causalmente atractivo, homofilia, reciprocidad estratégica o composición del evento. Las personas participan varias veces y los datos no son independientes por fila.

## N31–N32 · Atractivo externo y renta declarada

Se vinculó cada decisión de gustar a la calificación fotográfica independiente del candidato (definición del README de Mixmosa), y a sus nueve categorías numéricas de renta. En las citas con atributo observado, correlaciones Pearson entre atributo del candidato y recibir sí:

| Atributo del candidato | N decisiones | Correlación bruta | Asociación centrada por evento |
|---|---:|---:|---:|
| Atractivo fotográfico hombre | 1.865 | **0,1905** | 0,2179 |
| Atractivo fotográfico mujer | 1.839 | **0,3563** | 0,3265 |
| Ingresos varón, categorías 1–9 | 1.478 | **0,0375** | 0,0556 |
| Ingresos mujer, categorías 1–9 | 1.317 | **0,0968** | 0,0941 |

Todos son **resultados descriptivos fecha-ponderados, sin ajuste multivariable ni causal**, con grupos de ingresos desiguales debido a empates y ausencia selectiva de atributos. No identifican los coeficientes 60/40 del simulador; tampoco permiten declarar que la sociedad valore «más belleza que estatus» en general. El ingreso autodeclarado no equivale a estatus sociológico completo. La edad absoluta difiere en promedio 3,79 años entre las 1.888 fechas con rasgos completos y su correlación descriptiva con el interés mutuo es −0,0644.

**Error registrado en N32:** el primer script esperaba etiquetas de ingresos en inglés, mientras la tabla derivada contenía cadenas "1"–"9", por lo que su primera versión dio n=0. Se conservó [INVALID_N32_INCOME_01.json](INVALID_N32_INCOME_01.json), y el commit `c6d1fb567181cc809e4192cb4ff582a9eef2cec8` corrigió exactamente esa codificación. Las salidas de reciprocidad, fotos y popularidad permanecieron idénticas; los ingresos corregidos están en [AGGREGATE_RESULTS_REPAIRED.json](AGGREGATE_RESULTS_REPAIRED.json). El error no se cuenta como un ciclo válido adicional.

## N33 · Homogamia de popularidad observada

En lugar de imponer un valor de mercado, estimamos un proxy de **popularidad recibida en las otras citas de la misma persona**, excluyendo siempre la cita focal. Se exigieron al menos tres exposiciones adicionales de cada participante. Quedaron 1.890 citas evaluables, de ellas 259 mutuamente aceptadas, distribuidas en 30 eventos.

La correlación de popularidad entre los miembros de las 259 citas mutuamente aceptadas fue **r=−0,01587**. Entre todas las citas evaluables, `r=−0,04795`. Un control que permuta las etiquetas de aceptación mutua **solo dentro de cada evento**, manteniendo el número de mutuas por evento, dio correlación media **−0,05451**, con intervalo de referencia de permutación [−0,16435, 0,06853], que incluye el observado; cola superior ~0,258. **No hay un patrón de sorting positivo fuerte confirmado por este indicador en Mixmosa**.

Este proxy sigue usando otras citas del mismo evento, por lo que **no es una medida externa y prospectiva del valor latente**. Tampoco el resultado de una cita mutuamente aceptada equivale a convivencia, matrimonio o pareja consolidada. El control aleatoriza etiquetas entre aristas observadas; no mantiene la propensión individual al match de ambos participantes.

## N34–N35 · Desagregación, cobertura y dependencia

Las 647 decisiones extra de swiping no se imputan. El exceso de interés mutuo respecto a la expectativa de independencia dentro de evento fue **−29,256 citas**, o **−1,544 puntos porcentuales por cita**. Al retirar cada evento por turnos, ese exceso por cita oscila entre −1,805 y −1,389 puntos, siempre negativo, pero **eso no constituye un intervalo de confianza causal**. De los 410 participantes, 366 aparecen en un solo evento y 44 en varios, con un máximo de siete eventos: los errores estándar por cita independiente serían inadecuados.

## N36–N37 · Replicación, señal de rechazo y criterio R5

La auditoría de fuentes [SECOND_SOURCE_AUDIT.md](SECOND_SOURCE_AUDIT.md) revisó:
- Essex `AnonymizedData.xlsx`: público y CC BY 4.0 en ficha, bytes inaccesibles (XLSX incompatible con web y DNS no disponible).
- Columbia/OpenML `datasets/speed-dating`: archivo CSV registrado, con contenido vacío en esta herramienta; sin inspección numérica.
- `keithmcnulty/speed_dating`: CSV descargable por GitHub pero sin identificadores de ambos miembros visibles en la tabla reducida.
- eHarmony: `labels.csv.gz` por pares con resultado, atributos ofuscados; descarga no accesible aquí, y no interpretables como renta/belleza por nombre.
- Arias et al.: scripts accesibles, datos originales enlazados en Archive.org no examinados.

El dataset Mixmosa no ofrece una variable observada de **reputación social pública tras rechazo**, un timestamp completo de difusión de esa información ni medición posterior de estatus ante terceros. Por ello no podemos identificar la propuesta `S_i(t+1)=S_i(t)-δ` en personas reales. La regla sigue siendo hipótesis contrafactual de simulación.

## Evaluación de AB y decisión

N28 documental, N29 calidad, N30–N33 empíricos descriptivos, N34 reanálisis, N35 sensibilidad, N36 documental, N37 planificación. **Diez ciclos A–J válidos de alcance limitado**, más un intento instrumental inválido reparado; **tres plazas de las trece disponibles permanecen autorizadas pero no iniciadas**. No hay validación externa de nuestro mecanismo original, ni confirmación de originalidad frente a Hitsch 2010, matching estable o targeted search. Los resultados observados no reproducen una diagonal positiva fuerte del valor proxy entre aceptaciones mutuas. Esto disminuye las razones para ajustar el generador hasta obtener correlaciones llamativas.

**CT2=17/100** antes y después del bloque, porque el acceso a datos reales eleva la calidad del contraste, pero la hipótesis concreta permanece sin mecanismo novedoso discriminado ni segunda muestra independiente; escala ordinal y no probabilidad. N1 nuevos=0; N2=N3=0; histórico de N1 del proyecto no auditado. DRIFT D0.0.

**AB-DECIDE: `STOP_LOCAL_R5`**, preservar las tres plazas autorizadas no ejecutadas. Siguiente acción de más valor: conseguir un segundo archivo abierto con decisiones bilateralmente vinculadas, o un dataset consentido con información de exposiciones/reputación pública, e implementar un **holdout externo preregistrado**. No iniciar otras simulaciones sobre los mismos datos solo para elevar r.

## Evidencia y reproducibilidad
- [Contrato prospectivo y fuentes fijadas](PREREG.json), commit `a1146570712f2e545d097f3f498452bcbf9ce60a`.
- [Script principal congelado originalmente](analyze_mixmosa.js), commit inicial `9b7f3deab041eab4a4ca6ffed9c06d3669a2efae`, reparación de income `c6d1fb567181cc809e4192cb4ff582a9eef2cec8`.
- [Script secundario congelado antes de probar N33–N35](additional_checks.js), commit `cf873447a666da0a5ecc5fbc287e18a897b9e5c6`.
- [Resultados empíricos agregados corregidos](AGGREGATE_RESULTS_REPAIRED.json), [nulidad evento y LOO](N33_N35_EXTRA_RESULTS.json), [ledger A–J](LEDGER.json).
- [Manual de réplica de acceso al repositorio original](REPRODUCE.md): sin dependencias no estándar de Node, sin publicación de filas anonimizadas en nuestro repo. Reproducción local a través del conector, **clon limpio no probado**.
- Los datos de individuos proceden de un repositorio público que no muestra licencia explícita de redistribución en raíz; hemos almacenado solo **salidas agregadas, código y huellas**, dejando los registros originales en origen.

La continuación sigue disponiendo de tres plazas previamente autorizadas. **No se pide nueva autorización mientras persista ese saldo**; el botón de reanudación debe interpretarse como solicitud de un nuevo intento de acceso a fuente, no como permiso para ignorar R5.
