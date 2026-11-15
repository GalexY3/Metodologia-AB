# PREREG V196 — ¿Aprendizaje social autónomo o dependencia de la intervención de exploración?

15 de noviembre de 2026. Registrado **después de conocer los seis resultados de V195**: la exploración conjunta programada de votar según señales, al 10% de oportunidades, aumenta el resultado congelado frente a exploración individual y al aprendizaje original. Sin embargo, el evaluador V195 congeló las políticas: esto prueba que ejecutan una convención sin pulso mientras NO pueden aprender, pero NO prueba que la convención sobreviva a un aprendizaje individual continuo después de retirar la intervención. Este subestudio usa los pesos finales V195 ya fijados; todas las condiciones se declaran antes de ejecutarlo. Es auditoría de robustez prospectiva condicional, no experimento independiente original.

## Hipótesis y falsadores
**H1:** en al menos 4/6 escenarios k={4,8,12}×{UNANIMITY,MAJORITY}, continuar aprendiendo durante8000 nuevas reuniones sin pulso, con epsilon=.08, conservará al final al menos el75% del valor exacto del Q inicial que surgió con pulsos.
**H2:** en 4/6, PLASTIC_KEEP_PULSE_10 retendrá mayor valor exacto que PLASTIC_NO_PULSE_EPS08. Si ocurre, el sostén externo tiene valor causal y el logro anterior no puede reivindicarse como completamente autónomo.
**H3:** si la pérdida se debe a exploración incoherente durante aprendizaje, la reducción de epsilon a.02 o a0 mejorará la retención frente a.08. Si todos los escenarios fracasan incluso con epsilon0, es un problema más profundo de incentivos endógenos.
**H4:** la condición FREEZE conservará teóricamente el valor original exacto (la política no cambia), de modo que un deterioro por sí solo en resultados estocásticos no debe confundirse con desorganización.

## Universo y física
Recuperar sin sobrescribir los pesos originales de JOINT_SIGNAL_PULSE_10 en V195 para k4/8/12 y reglas UNANIMITY/MAJORITY: 32 mundos×20 grupos, m=k−1 electores, cada pérdida privada Li∈{1,7}, fija por persona. Entorno GOOD Pr=.6, señal INDIVIDUAL exactitud.8, votación según regla exógena. El estado GOOD/BAD no se muestra a los agentes; el entorno les paga +1 si ratifican GOOD, −Li si ratifican BAD, y0 si rechazan. No hay formación de nuevos grupos ni nuevas profesiones. Todas las Q iniciales deben coincidir byte por byte con el fichero V195 y entre brazos, y cada Q pertenece solo a un individuo. Son nuevos estados aleatorios posteriores a V195, con semilla completamente nueva V196-environment por k y regla y cintas idénticas entre brazos.

## Condiciones (todas inician de Q V195 exacta)
FREEZE: epsilon=0, ninguna actualización, ninguna intervención; mera estabilidad del evaluador y control.
PLASTIC_NO_PULSE_EPS08: Q-learning con alpha=.10, epsilon=.08, sin pulso, 8000 nuevas rondas.
PLASTIC_NO_PULSE_EPS02: idéntico, epsilon=.02, sin pulso.
PLASTIC_NO_PULSE_EPS00: idéntico, epsilon=0, sin pulso, pero Q se sigue actualizando a partir de los resultados reales.
PLASTIC_KEEP_PULSE_10: epsilon=.08, conserva las oportunidades del10% de exploración grupal simultánea de voto según señal propia, como en el entrenamiento V195.
En todos los brazos los Q de cada persona se actualizan únicamente con su recompensa individual realizada; no hay gradiente de grupo ni etiquetas del estado. En FREEZE no se produce aprendizaje en absoluto.

## Observaciones y criterios
Simular 8000 rondas de vida posterior y, en tiempo t=0,2000,4000,6000,8000, calcular valor EXACTO del perfil codicioso mediante una segunda rutina matemática que integra Poisson-binomial. No seleccionar máximos de trayectorias. Publicar también recompensa real durante adaptación, frecuencia de YES entre señales positivas/negativas, distribución de pérdidas, porcentaje de grupos con aprobación GOOD<.01, desviación estratégica individual estimada y conservación del Q de origen. El valor exacto se calcula bajo ejecución congelada en ese instante, NO sobre la conducta epsilon-greedy utilizada para adaptar. Esta separación es crítica.

Bootstrap emparejado por32 mundos, 10000 remuestreos, para diferencias a8000 respecto a0 y entre PLASTIC_NO_PULSE_EPS08 y PLASTIC_KEEP_PULSE_10; los grupos, reuniones y checkpoints no son unidades independientes. Mostrar todas las combinaciones y fracasos. El signo del resultado de H2 no acredita superioridad causal en un entorno humano ni novedad frente a literatura de coordinación, memoria y exploración.

Limitar procesos a2 cores de análisis por trabajo si hay uso concurrente, no interferir con experimentos de otros agentes. Guardar nuevos scripts, resultados, Q finales, SHA256 de origen, metodología y restricciones. No modificar V195 ni AB_PROGRESO. CT2=61,N2=0,N3=0. El objetivo principal solo se completa con institucionalización y especialización efectivamente aprendidas, falsadores, originalidad y evidencia independiente.
