# Revisión de literatura sobre emergencia de cooperación entre agentes simples

Fecha de búsqueda: 10 de noviembre de 2026. Este documento registra referencias y propuestas conceptuales. **No es un informe de experimentos propios nuevos, ni una preregistración de V9.**

## Criterio del investigador

El éxito del proyecto exige que la organización sea genuinamente colectiva, no una regla autosuficiente que cada agente aplica con conocimiento suficiente de un indicador global privilegiado. Conservar exactamente el objetivo de elegir endógenamente k estados entre diez, con cuotas N/k, hasta que el investigador decida otro enunciado. Se debe separar autoorganización, coordinación y cooperación con interdependencia causal. Una misma regla local programada en varios individuos **puede** dar lugar a comportamiento colectivo auténtico si su funcionamiento depende de interacciones; no es la identidad de las reglas la que invalida la colectividad, sino la ausencia de dependencia funcional respecto de otros.

## Trabajos primarios y evidencias

**Steels, L. (1995). A self-organizing spatial vocabulary. Artificial Life.** https://pubmed.ncbi.nlm.nih.gov/8925502/. Agentes distribuidos descubren convenciones léxicas mediante interacciones; el agente no requiere un cerebro profundo. Normas de actualización de repertorio preprogramadas.

**Baronchelli, A. et al. (2006). Topology-induced coarsening in language games. Physical Review E.** https://doi.org/10.1103/PhysRevE.73.015102. Una convención global emerge desde interacciones locales; topología afecta velocidad y necesidades de memoria.

**Centola, D. y Baronchelli, A. (2015). The spontaneous emergence of conventions: An experimental study of cultural evolution. PNAS.** https://pmc.ncbi.nlm.nih.gov/articles/PMC4343158/. Evidencia experimental humana, topología y coordinación local sin conocimiento global.

**Theraulaz, G., Bonabeau, E. y Deneubourg, J.-L. (1998). Response threshold reinforcements and division of labour in insect societies. Proceedings B.** https://pmc.ncbi.nlm.nih.gov/articles/PMC1688885/. Umbrales individuales variables que se modifican por experiencia: especialización de individuos inicialmente iguales. Es un modelo con reglas mecanísticas diseñadas, no una prueba de negociación neuronal.

**Bonabeau, E., Theraulaz, G. y Deneubourg, J.-L. (1998). Fixed Response Thresholds and the Regulation of Division of Labor in Insect Societies. Bulletin of Mathematical Biology.** https://doi.org/10.1006/bulm.1998.0041. Regulación de división de trabajo mediante umbrales.

**Huang, Z.-G. et al. (2012). Emergence of grouping in multi-resource minority game dynamics. Scientific Reports 2, 703.** https://www.nature.com/articles/srep00703. Población elige recursos con ocupación limitada; cuotas de referencia N/k; reglas individuales con información local generan agrupaciones endógenas de recursos. NO se demuestra nuestra condición específica de elegir exactamente k etiquetas entre diez y equilibrarlas; NO constituye demostración de cooperación comunicativa. Gran control para estudiar autoorganización por anti-congestión.

**Rubenstein, M., Cornejo, A. y Nagpal, R. (2014). Programmable self-assembly in a thousand-robot swarm. Science.** https://pubmed.ncbi.nlm.nih.gov/25124435/. Mil robots de capacidades locales restringidas se autoensamblan, utilizando algoritmos colectivos diseñados. Ejemplo de complejidad macroscópica con controles individuales simples; sin aprendizaje neuronal autónomo de estrategia colectiva.

**Valentini, G., Hamann, H. y Dorigo, M. (2015). Self-Organized Collective Decision-Making in a 100-Robot Swarm. AAAI.** https://ojs.aaai.org/index.php/AAAI/article/view/9720. 100 Kilobots, luz y mensajes de 3 bytes, selección colectiva de opciones mediante exploración e interacción.

**Foerster, J., Assael, Y., de Freitas, N. y Whiteson, S. (2016). Learning to Communicate with Deep Multi-Agent Reinforcement Learning. NeurIPS.** https://papers.neurips.cc/paper_files/paper/2016/file/c7635bfd99248a2cdef8249ef7bfbef4-Paper.pdf. RIAL y DIAL descubren protocolos comunicativos en tareas de información privada. RIAL admite redes de parámetros propios o compartidos; DIAL emplea gradientes entre agentes en entrenamiento centralizado, ejecución distribuida. Distinguir cooperación descentralizada al actuar de autonomía plena en el aprendizaje. Implementación de terceros: https://github.com/minqi/learning-to-communicate-pytorch.

**Das, A. et al. (2019). TarMAC: Targeted Multi-Agent Communication. ICML.** https://proceedings.mlr.press/v97/das19a.html. Mensajes y destinatarios aprendidos sin supervisión comunicativa, usando recompensas de tarea; también comunicación en múltiples rondas.

**Wang, T. et al. (2020). ROMA: Multi-Agent Reinforcement Learning with Emergent Roles. ICML.** https://proceedings.mlr.press/v119/wang20f.html. Roles latentes, regularizadores para identificabilidad y especialización, evidencia en tareas StarCraft; sesgos inductivos explícitos en arquitectura. Código: https://github.com/TonghanWang/ROMA.

**Bard, N. et al. (2020). The Hanabi Challenge: A New Frontier for AI Research.** https://research.google/pubs/the-hanabi-challenge-a-new-frontier-for-ai-research/. Juego plenamente cooperativo con información imperfecta y necesidad de interpretar otras acciones.

**Hu, H., Lerer, A., Peysakhovich, A. y Foerster, J. (2020). Other-Play for Zero-Shot Coordination. ICML.** https://proceedings.mlr.press/v119/hu20a.html. Adiestramiento por autopartida puede memorizar convenciones no transferibles; Other-Play evalúa interacciones con compañeros desconocidos.

**Lowe, R. et al. (2019). On the Pitfalls of Measuring Emergent Communication. AAMAS.** https://arxiv.org/abs/1903.05168. Demuestra mediante juegos simples que mensajes informativos/correlacionados con acciones pueden no afectar la conducta del receptor. Exige intervenciones sobre mensajes, escucha causal, ablations.

**Eccles, T. et al. (2019). Biases for Emergent Communication in Multi-agent Reinforcement Learning. NeurIPS.** https://discovery.ucl.ac.uk/id/eprint/10093988/. Sesgos de escucha y señalización que facilitan comunicación aprendida frente a la dificultad de exploración conjunta sin entrenamiento centralizado.

**Leibo, J. Z. et al. (2021). Scalable Evaluation of Multi-Agent Reinforcement Learning with Melting Pot. ICML.** https://proceedings.mlr.press/v139/leibo21a.html. Pruebas de generalización social sobre compañeros, reciprocidad, reparto de recursos y partición de tareas. El repositorio actual ha crecido respecto a los tamaños declarados en el artículo original: https://github.com/google-deepmind/meltingpot.

**Level-Based Foraging (LBF), entorno simulador.** https://github.com/semitable/lb-foraging. Agentes con capacidades diferentes deben unir sus niveles para recolectar ciertos recursos; tiene modo de recompensa compartida. Caso paradigmático de complementariedad material, pero esa necesidad puede estar incorporada por las reglas del entorno.

**Aina, K. O. y Ha, S. (publicado 2025; volumen 2026). Deep reinforcement learning for multi-agent coordination. Artificial Life and Robotics.** https://link.springer.com/article/10.1007/s10015-025-01089-z. MARL con estigmergia y feromonas virtuales; coordinación descentralizada, distribución asimétrica del trabajo en simulaciones hasta ocho agentes. No extrapolar a 324.

**Koifman, Y., Barel, A. y Bruckstein, A. (2026). Distributed and decentralized task allocation for heterogeneous swarms. Artificial Life and Robotics.** https://link.springer.com/article/10.1007/s10015-025-01104-3. Dos tipos de robots, exploración y extinción de incendios; reglas de interacción local y cooperación por complementariedad de capacidades; no comunicación explícita ni aprendizaje neuronal de nuevos roles.

**Sheng, L. et al. (2026). From individual decisions to team emergence: a survey on explainable cooperative multi-agent reinforcement learning. Artificial Intelligence Review.** https://link.springer.com/article/10.1007/s10462-026-11598-3. Taxonomía desde comportamiento individual y mecanismos de interacción hasta estrategias colectivas y evaluación. Se consulta como revisión de métodos, no como experimento primario.

## Comparación con nuestro V6–V8

V7 tiene diez canales equivariantes por color, una red GRU individual con 1.014 parámetros en H=12, observaciones locales y memoria, mensajes de estado y distribución local, puerta de conservar/cambiar, acceso al error global D y recompensas idénticas para todos; en pilotos N=36 no mostró ventaja robusta sobre azar. V6 con N=324, redes propias y feedback global se detuvo en 518.400 episodios sin señal de éxito.

V8 de «probar y revertir» aprendió a aceptar cambios favorables mediante el signo de un resultado global contrafáctico, pero no necesitó información de compañeros. Es un control de observabilidad y posibilidad de resolver la tarea; **no es cooperación colectiva aprendida**.

La función D se descompone exactamente en fuga fuera de los k grupos dominantes y exceso por encima de cuotas entre ellos:

D_k = sum_{j>k} p_(j) + sum_{j<=k} max(p_(j)-1/k,0).

La tensión de mecanismos es fundamental: el Naming Game puede reducir la fuga concentrando convenciones, pero un consenso único produce sobrecarga cuando k>1; el Minority Game regula congestión, pero puede conservar demasiados estados ocupados. Los umbrales de respuesta introducen especialización a tareas, aunque programan el mecanismo de actualización.

## Hipótesis metodológicas a debatir antes de hacer V9

**H1. Observabilidad distribuida:** no transmitir al actor el D contrafáctico de una acción; reservar recompensas globales para el entrenador. Dar información privada y mensajes locales para que el intercambio tenga valor causal.

**H2. Mecanismos separables:** sin imponer roles fijos, considerar un módulo mínimo de propagación/consolidación de convenciones y otro de respuesta a sobreocupación; estudiar si emergen sin ambos componentes programados.

**H3. Dependencia causal:** separar mera emisión de mensajes, escucha efectiva del receptor y contribución causal del intercambio al éxito global. Contrastar políticas entrenadas con y sin comunicación; manipular mensajes con pesos congelados y controlar placebo, tiempos y contrafactuales.

**H4. Roles:** si se mantiene la interpretación de los estados como «funciones», debe haber consecuencias funcionales de ocupar cada estado. Si solo son etiquetas, llamar al fenómeno coordinación distributiva y evitar afirmar división material del trabajo.

**H5. Generalización social:** cambiar socios, topología y orden de contactos, sustituir individuos por agentes de entrenamientos independientes, probar k inéditos, shocks, turnos sin comunicación. Hanabi/Other-Play y Melting Pot proporcionan inspiración.

**H6. Sencillez como variable experimental:** comparar agentes sin red (inventario Naming Game, umbral, Minority Game), redes de dos parámetros, MLP/GRU compactas y V7; igualar información y entorno. La cooperación no exige necesariamente pesos distintos si la regla común opera sobre interacciones efectivamente interdependientes.

**Cautela epistemológica:** no afirmar que se ha «descubierto cooperación» porque el rendimiento global aumente, porque existan k estados equilibrados o porque los mensajes sean informativos sobre acciones posteriores. Se requiere contraste contrafáctico de dependencia funcional. Tampoco confundir la existencia de una solución conjunta óptima como descripción matemática con la posibilidad de una estrategia autosuficiente ejecutable por cada individuo.

Estos son modelos externos y propuestas de adaptación; NO se han ejecutado nuevos experimentos propios de V9.
