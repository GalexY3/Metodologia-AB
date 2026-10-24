# AB-M037 — Blindaje de información no adquirida y del tiempo de medición

**Estado:** propuesta metodológica complementaria a AB 3.2.1/O1–O4. No nueva versión normativa ni evidencia de superioridad de AB. Procedencia: LARP AB75 24-10-2026 (rama `research/ab75-information-20261024` / PR #17).

## Hallazgo instrumental que motiva la propuesta
En una campaña de diseño de consultas costosas, las políticas solo leían etiquetas piloto, pero el motor transformaba esas etiquetas usando **cuantiles, media y desviación estándar de todas las respuestas**, incluidos individuos aún no consultados. Aunque no hubiera ninguna instrucción de la función de selección que leyese directamente el objetivo de los demás, la normalización constituía **filtración transductiva del resultado global**. Los primeros 75 contrastes fueron invalidados para inferencias operativas. La transformación se reemplazó por una función de constantes fijas, hash R1 congelado ANTES de reejecutar 75 contratos; como el rediseño fue post-exposición, la campaña sigue siendo exploratoria.

## Puerta F37 para nuevos AB con etiquetas parciales
1. Declarar explícitamente el **conjunto informativo** disponible en cada decisión: covariables x accesibles, predicciones, etiquetas ya pagadas, su timestamp, coste y su política de acceso.
2. Comprobar todo el pipeline de preprocesado (transformaciones de objetivo, imputación, calibración, encoding, normalización, indicadores de prevalencia), no solo el código inmediato de selección. Ninguna transformación de y puede usar momentos, rangos ni parámetros estimados desde respuestas no adquiridas, salvo que el experimento declare expresamente un **oráculo no implementable**.
3. **Test contrafactual de no-filtración:** manteniendo x y las etiquetas ya adquiridas, sustituir por valores arbitrarios todas las respuestas aún ocultas y afirmar que la próxima asignación **NO CAMBIA**. Registrar seed, ruta de código y resultado; aplicar también a parámetros de normalizadores/cache.
4. Cuando las etiquetas son temporales, declarar (y_i(t)) y si se reutiliza (y_i(t_0)) para estimar el valor de (y_i(t_1)). Medir el coste real de refresco, el número de observaciones únicas y el presupuesto de consultas repetidas.
5. Reparación tras resultados observados: no borrar outputs originales; versión/hashes/commit ANTES del replay; declarar explícitamente **POST_EXPOSURE_EXPLORATORY** aunque el código resultante funcione y los cálculos sean reproducibles. Si la corrección modifica la variable transformada, reconoce que cambió el **estimando**.
6. Testear la corrección de sesgo, la varianza y el **MSE por separado** y comparar un estimador competente sobre el mismo coste de información. La mejora de insesgamiento no implica automáticamente mejora en MSE.
7. No otorgar 2/3 o 3/3 por descubrir un leakage ni por repararlo: es instrumentación, no mecanismo científico novedoso.

**Falsador/coste de adopción:** si el sistema tiene realmente acceso legítimo y ya costeado al conjunto completo de y o si F37 duplica una prueba automatizada existente, la puerta puede ser redundante; registrar esa excepción con procedencia. Si el estimando es intrínsecamente transductivo y presupone todas las etiquetas conocidas, declararlo sin equipararlo a adquisición parcial.

**Nivel de evidencia de la propuesta:** recomendación operativa tras un fallo de instrumentación real del experimento; eficacia para detectar fallos futuros NO VALIDADA. Fuentes: teoría conocida de muestreo adaptativo y estimación HT, no una nueva ley.
