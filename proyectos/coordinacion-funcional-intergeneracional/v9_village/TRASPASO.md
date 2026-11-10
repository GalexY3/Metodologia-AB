# Transferencia entre equipos de la simulación de aldea

Estado verificado el 10/11/2026. Repo privado GitHub GalexY3/Metodologia-AB, rama research/aldea-individual-rl-pilot-20261110. Carpeta proyectos/coordinacion-funcional-intergeneracional/v9_village.

Contenido: simulador village.py, tests test_village.py, controles baselines.py, diagnóstico independiente de evaluación diagnose.py, generador de visor build_dashboard.py, panel HTML autocontenido PANEL_ALDEA.html, informes README.md y RESULTADOS_PILOTO.md, BASELINES.json, DIAGNOSTICO_NUEVAS_SEMILLAS.json y 11 corridas en runs/pilot_* con latest.pt, config.json, history.jsonl, replay.json, status.json y control.json. Smoke-tests temporales omitidos por .gitignore.

Ningún entrenamiento se ha dejado programado para ejecutarse posteriormente. Los archivos guardados permiten inspeccionar resultados y recuperar parámetros del optimizador.

Para llevarlo a otro PC con git ya instalado, desde PowerShell en un directorio de trabajo:

git clone --branch research/aldea-individual-rl-pilot-20261110 https://github.com/GalexY3/Metodologia-AB.git

En repositorio ya clonado con cambios propios, revisar git status primero; no sobrescribir trabajo existente. Desde el directorio v9_village usar Python con torch y numpy instalados.

Interpretación: la recompensa del actor es EXCLUSIVAMENTE su propia comida. Los agentes desconocen N, cuota 81 y censo. Tres réplicas sin mensajes superaron en alimento al brazo con comunicación, pero sin éxito exacto, y en N324 hubo mejora pasajera e inestabilidad. Resultado exploratorio no demuestra cooperación funcional. No convertir las métricas globales de auditoría en observaciones del agente.

El código y todos los checkpoints piloto están versionados en esta rama. Los scripts pueden generar otros experimentos con nombres diferentes sin modificar los anteriores.
