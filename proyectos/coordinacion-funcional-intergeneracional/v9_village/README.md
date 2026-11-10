# Aldea de diez profesiones. Primer experimento de aprendizaje individual

## Formulación cerrada en esta fase

Población N, diez profesiones igualmente productivas, cuota q=N/4. Cada trabajador en una profesión de tamaño n_j recibe exclusivamente su propio alimento r_i=min(n_j/q,q/n_j). El máximo es 1 y se alcanza exactamente cuando n_j=q. Para N=324 el valor q=81; los pilotos de N=36 usan q=9 (similitud proporcional, no mismo número absoluto). La única distribución donde todos reciben 1 es cuatro grupos cualesquiera de q y seis profesiones vacías.

Los agentes no reciben la respuesta, ni N, ni q, ni la distancia global D4, ni el censo de profesiones, ni la recompensa contrafáctica de cambiar. En esta fase no existen muertes, nacimientos, energía acumulada ni límites de cambio. El indicador de hambre r_i<0,85 no modifica los pagos.

## Actor

Cada habitante conoce su profesión (diez indicadores), la frecuencia de profesiones entre sus d vecinos (diez), la frecuencia de cinco símbolos recibidos (cinco), sus raciones actuales, su cambio de raciones y el tiempo relativo del episodio. En total 28 características.

Opciones: permanecer, elegir una de diez profesiones y emitir (opcionalmente) uno de cuatro símbolos no interpretados o silencio. El símbolo emitido llega a los vecinos en el siguiente turno. No puede ordenarles cambiar.

Arquitectura: tanh-RNN individual, con 12 activaciones de memoria y 700 parámetros por habitante, cada uno con pesos separados. La comunicación utiliza 65 de los 700 parámetros; estos no se actualizan cuando el canal está desactivado. La memoria se reinicia entre sociedades.

Aprendizaje mediante REINFORCE del retorno exclusivamente individual, con baseline leave-one-out entre sociedades del MISMO individuo y regularización de entropía. No hay un crítico global ni una recompensa colectiva compartida.

## Red y condiciones

Topologías de anillo regular con 2, 5 u 8 vecinos y una variante rewired que conserva el grado. El grado cinco incorpora enlaces laterales y uno a la posición opuesta en el anillo. Condición blind: no observa profesiones ni mensajes de sus vecinos, pero sí su propio alimento. Condición communication: observa y envía símbolos entre vecinos; compararla con un brazo entrenado desde cero sin mensajes. Todos pueden cambiar de profesión independientemente en cada turno.

## Evaluación

Resultados alimentarios, hambre, número de grupos ocupados, frecuencia de cambio, exactitud, y distancia distributiva D4 calculada SOLO para el investigador. Los controles son escoger profesión al azar cada turno, congelarse en la primera elección, imitar a un vecino aleatorio y actuar con una red inicial sin entrenar. Evaluaciones estocásticas y deterministas separadas.

Esta es una batería exploratoria. Una mejora de alimento no demuestra comunicación, ni colaboración fuerte, ni que el modelo haya descubierto la cifra de cuatro. Para afirmar cooperación hay que intervenir mensajes, introducir compañeros desconocidos, variar la red y comparar contra controles que no ven a otros.

Los entrenamientos se guardan en runs/NOMBRE con checkpoint latest.pt, config.json, history.jsonl, replay.json y status.json. El HTML portable PANEL_ALDEA.html se genera con build_dashboard.py.

## Reproducción

En GalexY_travel está instalado PyTorch 2.15.0 CPU y NumPy 2.5.4 dentro de C:\Programación\Grokking\.venv. Para ejecutar las pruebas desde la carpeta v9_village en PowerShell, usar:

C:\Programación\Grokking\.venv\Scripts\python.exe -m unittest -v test_village.py

Para iniciar un nuevo entrenamiento:

C:\Programación\Grokking\.venv\Scripts\python.exe -u village.py --name otro_piloto --n 36 --degree 5 --updates 120 --batch 24 --horizon 24 --eval-batch 48 --eval-horizon 40 --seed 1411

Para rehacer el visor con los experimentos ya realizados:

python build_dashboard.py

El usuario requiere continuidad GitHub, preservar pesos y datos reproducibles y distinguir controles metodológicos de descubrimiento científico. La especificación de colectividad fuerte sigue en v8_diagnostic/CONTRATO_COLECTIVIDAD_V9.md.
