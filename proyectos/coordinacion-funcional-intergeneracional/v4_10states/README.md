# V4 — Selección endógena de k estados entre diez

Versión que sustituye el problema fácil de V3: ahora cada agente puede escoger cualquiera de diez estados, mientras la sociedad debe ocupar **exactamente k estados distintos, con 1/k de la población en cada uno**. Solo se entrenan k=2,3,4. Los k colores ganadores no están predeterminados ni se comunican a los agentes.

## Fundamentos y resultados disponibles

El objetivo real es D_k=min_{|S|=k}TV(p,1_S/k) = 1−Σ_{j=1}^k min(p_(j),1/k), donde p_(j) son las k frecuencias más altas. Es D=0 si y solo si hay exactamente k colores usados y N/k individuos por color (cuando N es divisible por k).

Si 36 agentes se asignan de forma IID uniforme entre diez estados, la probabilidad exacta de resolver el reparto al azar en una sola asignación es combinatorio: P=C(10,k)·36!/((36/k)!^k·10^36), aproximadamente 4,08e−25 para k2, 4,06e−19 para k3 y 4,51e−15 para k4. **No cero**, aunque prácticamente imposible por ese mecanismo.

Los agentes tienen **matrices neuronales distintas θ_i**, observan color propio, colores de vecinos conectados y mensajes recibidos. Mensajes: uno saliente como máximo, hasta cinco entrantes. Cada agente siempre puede escoger directamente cualquiera de los diez colores. El escalar de D total y su cambio anterior son feedback públicos idénticos para todos. La única recompensa de entrenamiento es el nivel global del error y la rotación global, sin créditos individuales: r=−D(t+1)−0,03·churn(t). Los actores no ven histogramas globales.

[PREREG_V4.md](PREREG_V4.md) fija tarea, cambios respecto a V3, hiperpárametros y evaluación reservada. [test_v4.py](test_v4.py) pasó **9 tests**, incluyendo cuotas con subconjuntos arbitrarios (0,2,5,9), gradientes θ_i independientes, permutación de las diez etiquetas y ausencia de fugas de mensajes no recibidos.

## Entrenamientos largos iniciados y todavía NO declarados completados

**GalexY_travel, condición C2 con mensajes:** `C:\Programación\AB-ten-states-v4-20261110\proyectos\coordinacion-funcional-intergeneracional\v4_10states\runs\tenstates_N36_H64_seed421_C2_u10000`

**DESKTOP-I4SULKD, condición C1 sin mensajes:** la misma ruta `C:\Programación\AB-ten-states-v4-20261110\proyectos\coordinacion-funcional-intergeneracional\v4_10states\runs\tenstates_N36_H64_seed421_C1_u10000`.

Ambos se iniciaron con `train_v4.py`, 10.000 actualizaciones previstas por brazo, 12 mundos por actualización, 32 turnos por mundo, H64, N36, seed421, Adam .001, gamma .98, clip por agente y baseline leave-one-out ENTRE MUNDOS de k igual. Se guardan `LATEST.pt` y `TRAINING_LOG.json` cada 250 actualizaciones y checkpoints inmutables `MILESTONE_XXXXX.pt` en 500,1000,2000,5000,10000. Si un proceso falla, no inventar su conclusión: revisar último checkpoint y reanudar con la misma configuración `--resume`, sin lanzar dos entrenamientos en paralelo sobre la misma carpeta.

**Resultados preliminares (DESARROLLO, no prueba reservada):** hasta 2000 actualizaciones C2, ningún caso exacto en el lote fijo de desarrollo y distancia al objetivo próxima al IID-10 aleatorio; C1 mostró una tendencia parecida en sus primeros hitos. La comparación greedy de C2 en actualización1000 mejoraba la distancia frente al muestreo pero peor que un modelo GREEDY recién inicializado; no se ha demostrado aprendizaje organizativo. Véase `development_diagnostics/C2_u1000.json`.

El **test reservado** `evaluate_v4.py` exige AMBOS `FINAL_MODEL.pt` con update exactamente10000; prueba k2/3/4, C1,C2,C3, sus versiones greedy, random siempre, random→quieto y quieto, sin modificar pesos; guarda `holdout/LOCK.json` con SHA256 de ambos checkpoints y scripts antes de calcular el primer resultado. No abrir test ni reportar final anticipadamente.

## Continuidad en GitHub

Repositorio `GalexY3/Metodologia-AB`, rama `research/cooperacion-10-estados-v4-20261110`; código, prereg, tests, diagnósticos y protocolo se suben allí. Los pesos del sobremesa y los de Travel se mantienen en sus discos hasta consolidación, sin conflictos ni sustitución de branches. El repositorio es público: no guardar secretos. Las rutas `runs/` están ignoradas por defecto y cualquier checkpoint a versionar exige `git add -f`; no tocar datos de V2/V3. Para facilitar traspaso, publicar por separado commits de resultados terminados en ramas específicas y fusionar conscientemente.

**Cautela:** generaciones aquí designa episodios repetidos con los MISMOS parámetros θ_i persistentes, no sustitución de personas por descendientes. Ninguna semilla independiente adicional está entrenada aún para V4; si hay éxito, requiere replicación prospectiva.
