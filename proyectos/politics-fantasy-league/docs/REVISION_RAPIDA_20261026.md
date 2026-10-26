# Revisión rápida de software — 26/10/2026

Base revisada: `Metodologia-AB` commit `0b4961f`, proyecto `proyectos/politics-fantasy-league`. Revisión de ingeniería y producto, sin nueva campaña científica AB ni actualización de CT2, hallazgos o progreso.

## Evaluación

La base es útil para un WIP: ejecución local sin dependencias de producción, operaciones de mercado transaccionales, separación entre fixtures y evidencia histórica, límites de conocimiento explícitos y pruebas de concurrencia/contratos. La trazabilidad es una fortaleza.

El desarrollo está más avanzado como laboratorio/observatorio que como juego continuado. Hay mercado, clubes y alineaciones; la demo siembra dos jornadas una sola vez, y la futura conserva cobertura `NOT_AVAILABLE`. Falta el proceso que incorpora eventos, liquida una jornada y abre la siguiente. La infraestructura disponible tampoco equivale a un predictor político validado o a un servicio multiusuario.

## Problemas corregidos

- **Doble conteo de revisiones:** scoring y baseline contaban v1 y v2 del mismo evento como dos hechos. Ahora consumen una sola revisión pública al corte, antes de filtrar persona/fecha; una revisión posterior no altera una consulta anterior. Dos revisiones con la misma última fecha pública producen un error de ambigüedad. `first_public_at` debe referirse a la publicación de esa revisión. El historial conserva todas las versiones.
- **Peticiones JSON inválidas:** listas/objetos usados como identificadores llegaban a SQLite y cortaban la conexión. Devuelven HTTP 400 con `INVALID_ID`; los elementos anidados en alineaciones se rechazan como `BAD_LINEUP` sin modificar estado.
- **Barras del Observatorio invisibles:** la política CSP bloqueaba sus estilos inline. Se sustituyen por segmentos SVG proporcionales, colores en CSS y etiquetas accesibles; la política permanece estricta. El smoke visita ahora el Observatorio y comprueba geometría y violaciones CSP.
- **Pruebas dependientes de plataforma:** cuatro tests Node convertían URLs mediante `.pathname`, que conserva escapes y genera rutas incorrectas en Windows. Se usa `fileURLToPath`. Las fixtures de CSV/lecturas con tildes declaran UTF-8; atributos Git fijan LF para conservar los hashes de los archivos de evidencia al clonar en Windows.
- **Cobertura de CI incompleta:** el workflow anidado no se ejecuta desde el monorepo y el workflow raíz seleccionaba una parte de las pruebas. Se añade la suite completa Python/Node en Linux y Windows, con Python 3.10/3.13. El extra `test` declara NumPy, requerido por las regresiones computacionales existentes.

## Próximas mejoras, por orden

1. **Cerrar un ciclo jugable completo:** introducir un reloj controlable, estados de jornada y liquidación idempotente; probar compra → alineación → cierre → puntuación → clasificación → nueva jornada. Empezar con datos ficticios permite comprobar la mecánica sin depender de la ingesta real.
2. **Completar una integración real pequeña:** escoger una institución, un tipo de evento y un intervalo corto; reconciliar IDs y fechas de disponibilidad de principio a fin antes de ampliar el universo de actores. Medir cobertura, rechazos y revisiones. Mantener los puntos como regla del juego separada de la predicción.
3. **Facilitar la orientación:** conservar un estado actual breve al principio del README y trasladar el detalle cronológico de campañas a un índice. En la interfaz, dar una entrada clara a «Juego» y otra a «Observatorio/Laboratorio», según la tarea del usuario.

Dos cuestiones pendientes observadas: el borrador de alineación vuelve a cargar los titulares guardados al deseleccionar el último elemento; la instalación como wheel no incluye los JSON externos de `data/`, `examples/` y `product/` que usan los endpoints. Priorizar ambas si se distribuye la demo fuera de un checkout del repositorio.

## Validación

Las correcciones incluyen regresiones de cortes temporales, reasignación de personas/fechas, ambigüedad de versiones, HTTP inválido sin mutaciones y renderizado SVG. Los resultados de ejecución se documentan en la descripción de la PR; los jobs nuevos de Linux/Windows requieren su ejecución en GitHub Actions. Esta revisión no vuelve a capturar fuentes oficiales ni valida modelos con datos políticos reales.
