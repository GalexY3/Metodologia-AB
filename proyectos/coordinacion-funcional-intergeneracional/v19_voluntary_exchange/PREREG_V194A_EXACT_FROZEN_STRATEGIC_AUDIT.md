# V194A — Auditoría causal del bloqueo del voto privado, registrada antes de leer los resultados restantes

15/11/2026. En el primer resultado V194 k4 UNANIMITY se observó baja aprobación de políticas privadas, frente a señal-follow. La interpretación de trampa de coordinación requiere una auditoría exacta del estado congelado. Este subestudio fue diseñado **después de observar el resultado k4 unanimidad**, antes de contrastar los otros escenarios, y NO será llamado confirmación prospectiva independiente.

## Pregunta
¿Están las políticas privadas atrapadas en un equilibrio de no aprobación, donde cada individuo carece de incentivos marginales por ser no pivotal, aunque mejorarían todos si un número suficiente cambiara simultáneamente de estrategia? O ¿es un fallo de código, crédito de recompensa, aprendizaje defectuoso o aversión privada genuina al riesgo de apoyar contratos?

## Fórmulas y método
Cargar Q al final del entrenamiento V194, sin modificar el entrenador ni sus resultados. En evaluación las decisiones codiciosas con empate exacto de Q se resuelven con uniformidad aleatoria; se representarán por probabilidades de acción {0,.5,1}. **No** forzar 0 cuando dos Q son idénticas ni declarar que un empate demuestra decisión aprendida.

Para señal θ∈{G,B} y modalidad informativa INDEPENDENT, cada voto j tiene Pr(Y_j|θ)=pθ·Pr(Y_j|señal positiva)+(1−pθ)·Pr(Y_j|negativa), donde pG=.8 y pB=.2. La probabilidad de alcanzar umbral h se obtiene por polinomio generador Poisson-binomial de m votos. Para modalidad PUBLIC, condicionar primero a la ÚNICA señal s, calcular Poisson-binomial de los votos bajo s (las monedas de desempate son individuales) e integrar s con pθ. La selección del canal con voto privado también tiene distribución Poisson-binomial, y su aprobación se modelará como mezcla. No usar los resultados numéricos de evaluación para ajustar estos cálculos.

Pérdida privada Li∈{1,7}, recompensa real individual E[r_i]=.6·P(aprobar|G)−.4 Li·P(aprobar|B)−.02·P(PUBLIC). Para cada votante y su señal s, el incentivo marginal de votar SÍ equivale a la recompensa positiva en G y pérdida en B multiplicadas por probabilidad pivotal de los m−1 restantes. Se informa de ganancia local máxima al cambiar cada política binaria, promediada sobre señales y modalidades; para la adopción de canal se usa la probabilidad de que el resto de votos de selección quede justo en el umbral−1. La mejor respuesta unilateral es una comprobación de estabilidad local, no de racionalidad global, evolución o aprendizaje garantizado.

Se comparará el bienestar EXACTO predicho por las políticas congeladas con la media de 2000 evaluaciones por mundo guardada en JSON; diferencias de Monte Carlo se reportarán sin cambiar código. El modelo de probabilidades implementado independientemente del entrenador puede capturar errores de construcción y de estadísticas. Calcular:
1. Bienestar exacto esperado y diferencia vs observado, por brazo y escenario.
2. Frecuencia de grupos cuya aceptación con política congelada es prácticamente nula pese a que un acuerdo bueno generaría ganancias para todos.
3. Fracción de agentes con incentivo individual explotable; fracción de grupos con baja explotabilidad y alta ganancia si TODOS siguen señal positiva.
4. Número mínimo de cambios individuales simultáneos para que una mayoría o unanimidad apruebe en un estado de señal positiva; registrar distribución, sin modificar agentes.
5. Diferencias por tipo privado alto/bajo y por modalidad de comunicación.

**Controles:** verificar suma de probabilidades =1, identidades de cola binomial en política homogénea, concordancia escalar independiente con enumeración de 100 perfiles para m<=7, y que el oráculo techo sea Pr(GOOD)=.6, no un agente racional privado. Guardar todos los brazos, incluso los resultados negativos, conservar hashes, sin editar entrenamiento ni AB.

La mera existencia de Nash subóptimo en juegos de coordinación es un resultado conocido (Claus/Boutilier, Matignon y revisiones MARL); sirve para evitar un falso descubrimiento N2. El efecto de información correlacionada ya estudiado por Basak, Deb & Kuvalekar (2026 AER). El siguiente mecanismo original deberá permitir superar una barrera conjunta **sin imposición externa** y con incentivos privados, además de superar rivales competentes y comparar fuera de la física formulada para ello.
