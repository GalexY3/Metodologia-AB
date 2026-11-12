# V24b — Rescate de cooperación mediante ventana de bajo coste prolongada

Preinscripción exploratoria del 12/11/2026. Se redacta después de observar en V24 resultados de desarrollo a 200 actualizaciones, con donaciones próximas al 2–3%, y antes de entrenar V24b. **No forma parte de los contrastes preregistrados de V24.**

## Hipótesis de mecanismo

En k=4 un regalo dirigido beneficia a un receptor con una categoría útil, pero la bonificación completa exige recibir tres tipos de especialidades distintas. La tasa basal aleatoria de contacto útil puede resultar demasiado baja para que redes privadas identifiquen reciprocidad condicional antes de la subida de coste. V24b prueba si una ventana extensa de donación muy barata permite formar ese circuito antes de imponer el coste alto de 0,12.

Se conserva la función de recompensa y el algoritmo de V24. Las diferencias únicas respecto a los pilotos V24 son programa de coste, duración y número de épocas: primera etapa fija de coste 0,002 hasta u=800; subida lineal al coste 0,12 entre u=801 y u=1100; coste 0,12 fijo desde u=1100 hasta u=1800. Arquitectura donante original de percepción de complementariedad binaria, ocupaciones de cuatro clases con información local, recompensa individual y parámetros privados, sin compartir políticas ni imitarlas.

## Diseño

N=48, k=4, grado=6, dos semillas 3111 y 4111, 1800 actualizaciones, lote 16, horizonte 48. En entrenamiento se intercalan mundos monolíticos y asignaciones ocupacionales aleatorias. Estructura social circular fija. Se evalúa desde poblaciones monolíticas, aleatorias y equilibradas, en grafo circular y reconectado, al coste final 0,12.

Si la variante prolongada aumenta la donación durante el periodo barato pero colapsa tras la transición, concluir que el precio final supera la cooperación individualmente rentable en ese diseño. Si resiste, trasladar la misma intervención a N=120 sin seleccionar modelos a partir de semillas de auditoría. No introducir ningún objetivo central de cuotas.

## Resultado relevante

Se necesita a la vez cobertura material de categorías distintas, alimentación mayor que 0,2, donaciones voluntarias positivas y estabilidad tras la subida de coste. Una frecuencia de donaciones elevada sin alimento no satisface el criterio. Se reportará también la evaluación a coste elevado durante la etapa barata, para distinguir rendimiento asistido por el currículo de rendimiento autónomo con coste máximo.
