# Auditoría adversarial: crítica de Gemini sobre recompensa V4

**Fecha:** 10/11/2026. **Estado:** crítica recibida tras la terminación de los dos entrenamientos V4 de 10.000 actualizaciones (C1, C2), y después de su primera evaluación reservada. Las críticas y los análisis nuevos no se tratarán como preregistros de V4 original. No reescribir checkpoints ni logs históricos.

## 1. Lo que sí resulta correcto

V4 cambió deliberadamente la recompensa de progreso anterior por una recompensa de NIVEL GLOBAL `r=-D_k(t+1)−0,03*churn_t`, para recompensar la cercanía sostenida al objetivo y desalentar cambios inútiles. Esta intervención **cambia el objetivo descontado del aprendizaje** y debería haberse contrastado factorialmente con recompensa diferencial, en vez de considerarla superior por anticipado. La crítica de Gemini motiva un experimento controlado que compara ambos regímenes usando los mismos pesos iniciales y la misma arquitectura.

La fórmula de distancia presentada por Gemini es correcta y coincide con `society10.py`:

`D_k=1−Σ_{j=1}^{k} min(p_(j),1/k)`, donde p_(j) son las k frecuencias más altas. El evaluador permite cualquier subconjunto k de etiquetas entre diez. Los tests muestran que con 36 agentes k=2/3/4, D=0 si se utilizan exactamente k colores con N/k agentes cada uno.

Es correcta la advertencia sobre organización en dos regímenes: hace falta extinguir los colores sobrantes y, a la vez, no sobreocupar los k supervivientes. Pero esa estrategia no está implementada como regla y su adquisición por agentes independientes no se ha demostrado.

## 2. Lo refutado directamente por los registros

**No hubo colapso del churn hacia cero.** En V4-10000 los últimos registros muestran C1 churn=0,87963 y C2=0,88287, frente al 0,9 de la elección uniforme independiente entre diez estados. En actualización 2000: C1=0,88287; C2=0,88519. Ambas políticas permanecieron prácticamente en actividad aleatoria, en lugar de apagarse. La hipótesis causal específica de «la penalización induce parálisis» es incompatible con estos datos.

**La recompensa negativa no equivale a un gradiente negativo uniforme.** REINFORCE usa `logπ(a|s)×(G_t−baseline)`. El baseline de V4 es leave-one-out de retornos de OTROS MUNDOS del MISMO k, que no incluye la acción que se está evaluando. El valor −0,45 puede tener ventaja positiva frente a −0,55. Un programa con recompensas siempre negativas puede aprender: el problema práctico es intensidad/varianza del gradiente de ventaja, no que los castigos «hundan todas las acciones».

**Escala de churn mal comparada.** V4 usa `churn=numero_de_cambios/N`. La penalización extra de un solo cambio es 0,03/36≈0,000833 por mundo; bajar la distancia D en 1/N incrementa `−D` en 1/36≈0,02778. La multa adicional de esa acción es aproximadamente el 3% del beneficio inmediato, NO lo supera. Por supuesto, con múltiples agentes simultáneos, cualquier cambio puede ser neutro o incluso empeorar D; la elección de un peso 0,03 era una hipótesis, no una garantía de rendimiento.

## 3. Correcciones conceptuales a la propuesta de Gemini

**El delta no es exactamente shaping preservador de política con gamma=0,98.** Para potencial `Φ(s)=−N D_k(s)`, el término de Ng, Harada y Russell (1999) es `F(s,s')=γΦ(s')−Φ(s)=N[D_k(s)−γD_k(s')]`. La propuesta `N[D_k(s)−D_k(s')]` coincide solo para gamma=1. Como recompensa principal de PROGRESO sigue siendo válida y merece experimentación, pero no se debe atribuir sin más una garantía de invarianza de políticas óptimas. Véase publicación de autor: https://wordpress.andrewng.org/index.php/publication/policy-invariance-under-reward-transformations-theory-and-application-to-reward-shaping/ ; https://link.springer.com/article/10.1007/s00521-021-06259-1

**Una mejora de un agente no siempre da +1.** Si un cambio reduce D exactamente en 1/N, entonces `r=N ΔD=+1`. Sin embargo, cambios entre colores no supervivientes, cambios compensatorios, empates y acciones simultáneas pueden tener ΔD=0, distinto de +1 o incluso incremento de D. No existe un «crédito individual +1» suministrado a cada agente. Todos reciben únicamente UN escalar de resultado total.

**Con episodios finitos, la recompensa delta prioriza más la distancia terminal.** Para gamma<1 y `Σ γ^t(D_t−D_{t+1})`, telescopando: `D_0−(1−γ)Σ_{t=1}^{T-1} γ^{t-1} D_t −γ^{T-1}D_T`. El estado inicial no depende de las decisiones; por tanto maximizar progreso acumulado pondera sobre todo el D terminal en comparación con la penalización de nivel sostenida. Es una diferencia de objetivo importante, no un mero arreglo de signo.

## 4. Resultado V4-10000 (ya evaluado y congelado)

Por cada k se evaluaron 100 sociedades nuevas por condición, horizonte120 turnos, ambos modelos entrenados con seed421:

| k | C1 (sample) D | C2 (sample) D | C2 (greedy) D | Azar continuo D | Exactos C2 | Estables C2 |
|---|---:|---:|---:|---:|---:|---:|
| 2 | 0,6494 | 0,6561 | 0,5669 | 0,6583 | 0/100 | 0/100 |
| 3 | 0,5256 | 0,5283 | 0,4356 | 0,5256 | 0/100 | 0/100 |
| 4 | 0,4161 | 0,4103 | 0,3219 | 0,4172 | 0/100 | 0/100 |

El número medio de estados ocupados en C2 sample al final es entre 9,7 y 9,8 de diez; churn entre 0,879 y 0,884. Fracaso de coordinación estable, NO inmovilidad.

Un CONTROL ADICIONAL POSTHOC de políticas `greedy` NO ENTRENADAS dio D inferiores a las políticas `greedy` después de 10.000 actualizaciones: para C2 greedy sin entrenar D k2=0,51694 / k3=0,38972 / k4=0,29361, frente a los pesos entrenados k2=0,5669 / k3=0,4356 / k4=0,3219. No interpretar diferencias de estas muestras exploratorias como prueba de deterioro causal general, pero sí como advertencia de que «greedy mejor que sampling» no confirma aprendizaje.

## 5. Nueva prueba falsable: V4-D, recompensa diferencial, sin multa de actividad

Protocolo prospectivo DE LA EXTENSIÓN en `PREREG_V4_DELTA500.md`. Se entrenan desde cero C1/C2 con seed421 idéntica a V4, k2/3/4, N36, hidden64, batch12, T32, Adam .001, gamma .98 y **solo** `r=N*(Dprev−Dnext)` (sin coste de churn), 500 actualizaciones para piloto, logs y checkpoints intactos. El mismo código y las mismas políticas independientes se mantienen. Test matemático `test_delta_reward.py` pasó 5/5, incluyendo recompensa +1 por mejorar D en 1/N, −1 por empeorar y 0 si no cambia.

La nueva intervención se considerará favorable solo si muestra una reducción de D de desarrollo y un número de estados utilizados más próximo a k que la referencia IID-10; el experimento debe reconocer si fallan ambas condiciones. No iniciar automáticamente otro experimento 10000 sin evidencia. La evaluación posterior tendrá 100 mundos nuevos por k y modalidad, sin seleccionar el mejor de los checkpoints 100/250/500.

**Conclusión:** el argumento causal concreto de Gemini sobre recompensa negativa y colapso de actividad es incorrecto, pero su sugerencia de probar una señal diferencial constituye una buena hipótesis de ingeniería experimental. Es necesario comprobar su efecto, no prometer el resultado.
