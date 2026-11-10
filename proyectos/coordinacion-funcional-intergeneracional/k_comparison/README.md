# Comparación de la aldea: k=2 versus k=4

Se conserva la tarea económica: diez profesiones disponibles, ocupación óptima q=N/k por profesión, recompensa personal r_i=min(n_j/q,q/n_j), redes individuales y cinco vecinos. Ningún agente recibe k, q, N, el censo de profesiones ni el error global. La recompensa de entrenamiento es exclusivamente su alimentación.

## Resultado

La conclusión es NEGATIVA respecto a encontrar el reparto óptimo. Con N=36, los tres entrenamientos estocásticos k2 terminaron cerca de 0,26 de comida y ninguno resolvió exactamente el reparto. Una variante greedy k2 logró ~0,89 sobre 192 mundos nuevos y 1 mundo exacto, pero su política estocástica no alcanzó ese resultado.

En N=324, ambas condiciones, k2 y k4, terminaron después de 240 actualizaciones alrededor de 0,5 raciones. En una auditoría de políticas greedy, k2 colapsó en una profesión de 324 habitantes, mientras k4 colapsó en dos profesiones de 169/155. La cifra 0,5 se explica algebraicamente por el límite productivo de las profesiones saturadas. No se demostró cooperación.

Consultar INFORME_Y_REFORMULACIONES.md para detalle, cautelas y nuevos diseños de interdependencia colectiva.

## Archivos

- village.py: copia del motor V9 con parámetro --k 2 o --k 4; los pilotos V9 anteriores permanecen intactos.
- make_k_general.py: script que DOCUMENTA la transformación inicial del código; es una migración de una sola ejecución, no volver a ejecutar sobre código ya transformado.
- test_k.py: siete pruebas, incluida comparación exacta contra la economía original cuando k=4.
- evaluate_compare.py: evaluación post hoc en dos semillas y controles sin aprender.
- inspect_traps.py: auditoría de las distribuciones de los checkpoints finales.
- COMPARACION_POSTHOC.json y AUDIT_TRAPS.json: resultados detallados.
- build_comparison.py: genera COMPARACION_K2_K4.html, panel autónomo sin conexión a Internet.
- runs/: 3 entrenamientos k2 en N=36, 1 entrenamiento k2 en N=324 hasta actualización 120, y continuaciones de k2 y k4 de 120 a 240. Todos los checkpoints y registros están incluidos.
- Los entrenamientos k4 originales hasta actualización 120 se conservan en el directorio hermano ../v9_village/runs y están presentes en el mismo repositorio.

## Pruebas y visor

En GalexY_travel, desde esta carpeta, se utilizó el Python del entorno C:\Programación\Grokking\.venv. Para el cambio de ordenador se requieren PyTorch y NumPy compatibles.

Comandos PowerShell ejecutables desde esta carpeta:

    & 'C:\Programación\Grokking\.venv\Scripts\python.exe' -m unittest -v test_k.py
    & 'C:\Programación\Grokking\.venv\Scripts\python.exe' -u evaluate_compare.py
    & 'C:\Programación\Grokking\.venv\Scripts\python.exe' -u inspect_traps.py
    python build_comparison.py
    Start-Process .\COMPARACION_K2_K4.html

Investigación exploratoria y retrospectiva: N324 tiene solo una semilla independiente de entrenamiento; los controles externos al aprendizaje se consultaron post hoc. No utilizar estos resultados como test confirmatorio ni afirmar grokking. El siguiente paso puede ser probar si una sociedad aprende a salir de una trampa de Nash mediante migraciones voluntarias coordinadas y señales locales, sin introducir recompensa colectiva.
