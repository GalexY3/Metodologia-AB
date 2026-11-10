# Entrenador MARL V6 · Un millón o más de episodios

Aplicación de entrenamiento real, con panel local semejante al simulador HTML aportado, pero sin curvas generadas artificialmente. En la RTX 4070 SUPER se ha instalado PyTorch con CUDA en un entorno aislado.

La población principal tiene 144 personas neuronales, cada una con pesos independientes. Cada persona dispone de diez estados, cinco contactos, memoria exponencial de información local y libertad de solicitar cambios a un vecino o de adoptar un estado propio. La única señal de evaluación del comportamiento es global y compartida. La tarea es conseguir repartos entre k=2,3,4 estados endógenos a cuotas iguales.

## Panel

Abrir desde el sobremesa el archivo ABRIR_PANEL.ps1 usando Ejecutar con PowerShell. También se puede lanzar en PowerShell:

powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Programación\MARL-million-144-20261110\proyectos\coordinacion-funcional-intergeneracional\v6_million\ABRIR_PANEL.ps1"

Dirección local del panel: http://127.0.0.1:8765

Pulsar INICIAR/REANUDAR con 1.000.000 de episodios. El panel muestra exactamente los registros que produce PyTorch, con visualización de los 144 agentes, mensajes enviados, histograma de diez colores, curvas separadas de k=2,3,4 y reproducción de una sociedad en desarrollo. Pausar, continuar y guardar/detener funcionan en los límites de actualización. No es necesario mantener abierto el navegador, pero sí el ordenador encendido y el proceso de Python ejecutándose.

El modelo se guarda en runs/principal/latest.pt cada cien actualizaciones; la reanudación conserva los pesos y el optimizador. El progreso se registra en history.jsonl y status.json. El panel lee estas fuentes, nunca inventa puntos de la curva.

## Archivos y reproducibilidad

engine.py define grafo cinco-regular, política individual y entorno; trainer.py realiza el entrenamiento de larga duración y checkpoints; server.py crea la interfaz local; index.html es la visualización; validate.py reserva la evaluación final con seis controles; test_v6.py contiene invariantes matemáticos, geométricos y de privacidad; PREREG_V6.md fija el protocolo.

El entorno Python instalado se encuentra en C:\Programación\MARL-million-144-20261110\.venv. Para usarlo manualmente desde la carpeta del proyecto:

python trainer.py --run principal --episodes 1000000 --side 12 --batch 48 --horizon 16 --hidden 64
python server.py

Evitar dos entrenamientos simultáneos sobre el mismo directorio. El servidor enlaza solamente 127.0.0.1, no abre puertos públicos.

Un millón de episodios equivale a un millón de SOCIEDADES repetidas, no a un solo mundo con un millón de turnos. Nunca interpretar D decreciente como prueba de cooperación si no se reducen los colores a k, no aparecen repartos exactos y no disminuye el churn. El objetivo no está garantizado por el presupuesto ni por el número de parámetros.


## Parámetros finales del entrenamiento principal

**324 agentes (18×18)**, frente a las 144 personas iniciales usadas durante las pruebas de ingeniería. Se ha probado en la RTX 4070 SUPER con CUDA. La interfaz ofrece también 144 y 576 agentes para NUEVOS experimentos, pero el modelo principal se entrena exclusivamente con 324, batch48, horizonte16, hidden64 y semilla6123. Los resultados y los checkpoints del modelo principal quedan en runs/principal; un millón de episodios son exactamente 1.000.032 sociedades completas al cerrar la última actualización.
