# V3C — Informe de simulaciones reales con más agentes y mayor capacidad

**Fecha:** 2026-11-10. **Estado:** entrenamiento y evaluación reservada completados para los cuatro diseños de V3C; resultados negativos respecto a estabilidad. Experimentos previamente fijados en [PREREG_V3C_SCALING.md](PREREG_V3C_SCALING.md). Este estudio surge después del negativo V3B-120/V3B-600, por tanto es ampliación exploratoria, no validación confirmatoria predefinida antes de conocer los resultados iniciales.

## Qué se ha simulado realmente

Se entrenaron OCHO poblaciones de agentes neuronales individuales. Cada agente tiene parámetros θ_i propios, sin compartición de pesos entre individuos; cada uno observa el estado local, puede elegir libremente su próximo color, puede enviar cero o una petición a un vecino y recibir múltiples solicitudes. **La única recompensa de aprendizaje** es el cambio de distancia global al reparto ideal, idéntico para todos los individuos en cada mundo: r_t=N[D(t)−D(t+1)]. El entrenador no suministra crédito contrafactual individual ni un crítico que acceda al censo global. Las redes son equivariantes por etiquetas de color dentro de cada individuo. C1 prohíbe enviar mensajes, pero no el cambio voluntario; C2 permite enviar y recibir mensajes; C3 retira los mensajes solo en evaluación de los pesos de C2, conservando la capacidad física de cambiar.

Cada actualización comporta 12 sociedades simuladas de 24 turnos. Las configuraciones fueron N36/H64/2000 actualizaciones; N120/H24/1500; N120/H64/2000 y N240/H64/1000. Todos los brazos principales usan la semilla de entrenamiento 411, con pesos iniciales apareados C1/C2 de cada configuración. Los episodios de desarrollo se utilizaron para describir la progresión, sin seleccionar checkpoints por éxito.

## Resultados test reservados

Los modelos se congelaron antes de simular **sociedades nuevas**, con semillas no empleadas en entrenamiento ni desarrollo. Horizonte 120 turnos. Distancia D=0 significa reparto global exactamente perfecto; menor D indica mayor acercamiento. El resultado operacional «estable» exige D≤0,06 y cambio de color ≤5% durante los **diez últimos turnos**. Los controles de azar continuo se diferencian del azar con parada programada a los 24 turnos.

| N | Hidden | Updates | k | D sin mensajes C1 | D con mensajes C2 | Estables C1/C2 | Estables azar→parar | Sociedades por condición |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 36 | 64 | 2000 | 2 | 0,06889 | 0,06083 | 0 / 0 | 69 | 100 |
| 36 | 64 | 2000 | 3 | 0,08972 | 0,08778 | 0 / 0 | 28 | 100 |
| 36 | 64 | 2000 | 4 | 0,11528 | 0,11278 | 0 / 0 | 15 | 100 |
| 120 | 24 | 1500 | 2 | 0,03841 | 0,03698 | 0 / 0 | 51 | 64 |
| 120 | 24 | 1500 | 3 | 0,05716 | 0,05651 | 0 / 0 | 40 | 64 |
| 120 | 24 | 1500 | 4 | 0,06094 | 0,06159 | 0 / 0 | 32 | 64 |
| 120 | 64 | 2000 | 2 | 0,03229 | 0,03828 | 0 / 0 | 52 | 64 |
| 120 | 64 | 2000 | 3 | 0,05143 | 0,04453 | 0 / 0 | 43 | 64 |
| 120 | 64 | 2000 | 4 | 0,06367 | 0,06250 | 0 / 0 | 31 | 64 |
| 240 | 64 | 1000 | 2 | 0,02969 | 0,02960 | 0 / 0 | 47 | 48 |
| 240 | 64 | 1000 | 3 | 0,03498 | 0,03568 | 0 / 0 | 42 | 48 |
| 240 | 64 | 1000 | 4 | 0,04453 | 0,04401 | 0 / 0 | 36 | 48 |

**Resultado principal:** 0 sociedades estables tanto C1 como C2 en todas las tareas test de esta batería, con independencia del aumento de N, tamaño de red o presupuesto. A diferencia del control azar→parar, las políticas aprendidas siguen cambiando una proporción alta de estados; en C2 se sitúa aproximadamente entre 0,49–0,52 para k2, 0,64–0,66 para k3, y 0,72–0,73 para k4. Son valores cercanos al churn de decisiones uniformes independientes, (k−1)/k. Es compatible con aprendizaje débil de conservar estado, no prueba matemática de que no exista ningún cambio en pesos.

La distancia D muestra diferencias pequeñas y de signo mixto entre C1 y C2. Con N120/H64,k3 la condición C2 mejora D=0,04453 frente a 0,05143 de C1, pero con N120/H64,k2 empeora (0,03828 frente a 0,03229). Con N240 los cambios de D son muy pequeños. Por tanto, **no hay evidencia consistente de ventaja por comunicación en esta batería**. El 0% de estabilidad del azar continuo tampoco demuestra una ventaja aprendida: dicho control sigue cambiando por diseño.

La normalización D/E[D_IID] se encuentra cerca de 1 en muchos tratamientos, indicando proximidad a la asignación de colores IID. E[D_IID] cae con 1/√N y no es un límite matemático de alcanzabilidad. Mantener D≤0,06 como umbral absoluto vuelve la tarea proporcionalmente más fácil con N elevado; exigir churn bajo y contrastar contra azar→parar evita una interpretación engañosa de «estabilidad».

## Límites fundamentales

Solo UNA semilla de entrenamiento (411) en cada configuración V3C; los 100/64/48 mundos nuevos por condición no son réplicas independientes del entrenamiento. Las cuatro configuraciones tienen presupuestos distintos y, aunque comparan tamaños y capacidad, **no son un diseño factorial completo** para atribuir un efecto causal al número de neuronas o al tamaño poblacional. Cada vida simulada en V3C tiene 24 turnos, aunque haya miles de episodios/generaciones computacionales; prolongar la duración de una vida a 96 turnos fue otro experimento posterior, cuyos checkpoints están guardados pero cuya evaluación no forma parte de la tabla.

No se ha probado que sea imposible aprender cooperación bajo la recompensa global. Este resultado sí falsifica, para los regímenes evaluados, la predicción simple de que aumentar N o tamaño neuronal y las actualizaciones **bastaría automáticamente** para conseguir coordinación estable. La memoria de los agentes sigue siendo W1 (estado actual y último feedback público), no recurrente a varios turnos. Si se cambia esa memoria, el algoritmo de asignación temporal de crédito, la estructura de redes o el curriculum, debe tratarse como un NUEVO experimento registrado.

## Reproducibilidad

Resultados completos, curvas 0..120, azar continuo, azar de parada, C3, exactitud de reparto, comunicación y SHA256 de pesos/modelo/script por configuración en:
- `holdout_v3c/N36_H64_U2000_seed411/`
- `holdout_v3c/N120_H24_U1500_seed411/`
- `holdout_v3c/N120_H64_U2000_seed411/`
- `holdout_v3c/N240_H64_U1000_seed411/`

Cada carpeta contiene `LOCK.json`, `SUMMARY.json` y los 18 casos k×tratamiento. Los pesos finales y los logs íntegros de los ocho entrenamientos se encuentran en `runs/v3c_N{N}_H{H}_seed411_{C1,C2}_updates{U}/`. Los registros del piloto anterior V3B con tres cohortes y del experimento V3B de 600 actualizaciones se conservaron en sus propias carpetas.

**Interpretación científica:** aprendices individuales + feedback colectivo + red local + peticiones no han producido hasta ahora cooperación estable en este entorno. La investigación requiere estudiar dificultades de aprendizaje temporal, y hacer falsable la función de los mensajes con evaluaciones y controles realistas.
