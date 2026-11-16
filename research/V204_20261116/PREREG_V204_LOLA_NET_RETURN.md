# V204: rival LOLA exacto con retorno monetario neto

16/11/2026. Prospectivo: todavía no se han ejecutado trayectorias V204. El control V203 falló desde COLD aun con gradientes verdaderos. Ahora se cambia una clase causal: el agente diferencia a través del siguiente paso de aprendizaje ajeno. Es un portado de **LOLA-Ex, ecuación 4.4 de Foerster et al., AAMAS 2018**, a nuestro juego; no es un algoritmo nuevo, una ejecución del código original ni una réplica de sus benchmarks. El artículo ya contempla la generalización a más de dos jugadores.

Sean U_i=(1−beta)V_i los retornos privados netos normalizados, incluyendo cada pago dado como coste unitario y cada pago recibido como ingreso. No hay recompensa TEAM, subvención ni coste rebajado. Se usa el campo

`f_i = grad_i U_i + eta sum_(j != i) [grad_j U_i]^T Hessian_(i,j) U_j`.

El multiplicador `grad_j U_i` se trata como constante en el backward, como especifica el artículo original. Diferenciar también ese multiplicador o diferenciar exactamente un objetivo de lookahead finito es otro método. Se fija **eta=20**, equivalente a anticipar un paso de tamaño 1 sobre V_j no normalizado (V_j=20 U_j); no se ha elegido tras observar trayectorias. La escala externa es la misma que la EPG de V203. Las unidades de recompensa y el paso anticipado importan; un fracaso aquí no refuta LOLA para todo eta.

Información: modelo físico, pérdidas y parámetros ajenos conocidos; todas las políticas y Hessianas exactas. Sigue siendo un control oracular, no aprendizaje con recompensa privada realizada. Se conserva íntegramente el juego V202/V203 y el canal de pagos ex post GOOD. La mezcla actual epsilon(t)=0,20−0,18 min(t/48,1) se congela al calcular el campo. No se diferencia el calendario futuro de exploración.

Diez puntos deterministas: COLD, WARM y los mismos ocho JITTER sd=0,001 de V203 (Philox 2031600…2031607). La comparación usa las diez trayectorias EPG V203 existentes, cuyos campos propios se han contrastado con la nueva implementación. La diferencia de interés es añadir el término de Hessiana; reutilizar esos controles conocidos no crea diez nuevos mundos ni una prueba externa. No se aplican p-valores o CIs.

Integración: RK45 hasta t=6000, rtol=1e−8, atol=1e−10, campo proyectado a logits [−12,12], sobrepaso máximo guardado 0,001. Guardar la misma malla de 83 puntos V203, con evaluaciones nativas y mejores respuestas en t=0,60,600,6000. Tiempo de optimización, no rondas. COLD y WARM se repiten con rtol=1e−9 y atol=1e−11; discrepancia de probabilidades finales >1e−4 invalida estabilidad numérica. No se ajusta la tolerancia para conseguir un resultado deseado.

Límite de recursos: máximo 5000 evaluaciones de campo por integración, un proceso BelowNormal, afinidad de seis CPU lógicos, dos hilos Torch/BLAS. El benchmark técnico midió aproximadamente 0,059 s por campo en este equipo; se limita así cada integración a un orden de cinco minutos de cálculo, sin garantía temporal absoluta. Un límite alcanzado o fallo numérico se conserva y se continúa con los demás puntos; el caso queda sin endpoint válido, no como fracaso sustantivo de adquisición. Una precisión fallida se declara. No relanzar ni modificar eta a partir de resultados.

Predicción H1 del control: COLD y al menos 6/8 JITTER alcanzan **funcionalidad estable**, definida como el criterio funcional V202 (ganancia privada mínima >=0,02, GOOD>=0,20 y caída GOOD al retirar pagos>=0,10) y regret público máximo <=0,01, todo en política nativa a t=6000. Si hay endpoints faltantes o precisión inválida en COLD, no declarar H1 confirmada. WARM comprueba conservación/mejora del acuerdo suministrado y no cuenta como adquisición. Todos los valores continuos, fallos, estados y beneficios individuales se informan.

Auditoría previa: 2880 comprobaciones escalares de gradientes y 36 formas bilineales de Hessianas, sobre tres políticas arbitrarias, usando evaluador independiente de 27 estados y gradientes analíticos previos para contrastes. Error máximo de gradiente cruzado 3,21e−11, Hessianas 1,49e−14. Estos son tests técnicos, no trayectorias elegidas favorablemente. Fuentes y resultados técnicos se publican y descargan con hash antes de integrar.

Regla de decisión: si H1 falla, no concluir imposibilidad general, no barrer tasas y no atribuir todo al error de muestreo o a omitir cualquier conciencia del aprendizaje ajeno. Si se cumple, auditar por implementación independiente y trasladar la prueba a aprendices sin acceso a parámetros/modelo. En ambos casos, no acreditar originalidad del método ni nivel 2/3: LOLA es el rival establecido. LIO es otro antecedente que ya incluye una opción de coste en la cadena; su comparación completa sigue pendiente. CT2 histórica 61 intacta, rama nueva sin puntuar, N2=N3=0.

Fuentes: [artículo original LOLA](https://arxiv.org/pdf/1709.04326), [código de los autores](https://github.com/alshedivat/lola), [LIO](https://proceedings.neurips.cc/paper/2020/hash/ad7ed5d47b9baceb12045a929e7e2f66-Abstract.html).
