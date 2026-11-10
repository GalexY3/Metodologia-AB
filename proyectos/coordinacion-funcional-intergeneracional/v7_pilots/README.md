# Laboratorio V7 — pilotos comparativos

V7 es una nueva batería *exploratoria* posterior al fracaso de V6 a 324 agentes. No modifica los modelos ni los registros V6. Todo lo que figura a continuación se refiere exclusivamente a los pilotos de 36 agentes. La tarea mantiene diez colores, objetivo endógeno k=2,3,4, grafo de grado cinco, parámetros neuronales individuales y recompensa de sociedad compartida.

El programa principal está en `experiment.py`. La memoria recurrente y la puerta de mantener/cambiar se implementan en `GatedColorGRU`; la condición `gated` usa la misma parametrización sin transmisión del estado recurrente entre turnos. La condición `legacy` importa el actor V6. El método evolutivo optimiza la suma descontada de la recompensa colectiva por perturbaciones antitéticas sin asignar crédito individual.

Los tests de integridad están en `test_v7.py`. El protocolo preexperimental, resultados y limitaciones están en `PREREG_V7.md` y `REPORT_V7_PILOT.md`. Los resultados de desarrollo (NO test sellado) se conservan en `RESULTS_V7_PILOT_DEVELOPMENT.json`. Los pesos y el estado de optimización de cada brazo se guardan localmente bajo `runs/<nombre>`, excluidos de Git para evitar transferir pesos grandes.

## Visor

En DESKTOP-I4SULKD, ejecutar `ABRIR_PANEL_V7.ps1` con PowerShell, o visitar directamente http://127.0.0.1:8766/ si el servidor ya está activo. El panel es de solo lectura, actualiza curvas, muestra las evaluaciones por objetivo y puede reproducir una sociedad en k=4 a partir de datos guardados. No entrena ni modifica parámetros.

Para levantarlo manualmente desde este directorio:

```powershell
& "C:\Programación\MARL-million-144-20261110\.venv\Scripts\python.exe" -u server.py
```

## Reproducir los tests

```powershell
& "C:\Programación\MARL-million-144-20261110\.venv\Scripts\python.exe" -m unittest -v test_v7.py
```

## Experimento nuevo, conservando los anteriores

```powershell
& "C:\Programación\MARL-million-144-20261110\.venv\Scripts\python.exe" -u experiment.py --name trial_gru_2 --arm gru --side 6 --batch 12 --horizon 12 --hidden 12 --updates 40 --eval-batch 96
```

Con `--messages` se permite comunicación, por defecto no. Usar nombres nuevos para nuevos protocolos; el código rechaza reanudar un directorio con configuración diferente. Es imprescindible comparar selección estocástica y greedy; una puerta muy favorable a permanecer puede congelar todos los agentes durante la evaluación greedy sin que se haya aprendido el objetivo.

El presupuesto de 40 actualizaciones es diagnóstico. NO debe presentarse como confirmación del aprendizaje ni como refutación de la emergencia de coordinación.
