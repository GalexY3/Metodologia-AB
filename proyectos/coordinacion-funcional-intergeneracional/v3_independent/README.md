# V3B — Independencia individual y cooperación como hipótesis

La especificación actual se encuentra en [PROTOCOL.md](PROTOCOL.md). La [respuesta a la auditoría de Argon](ARGON_RESPONSE.md) distingue objeciones verificadas, hipótesis y exageraciones.

Cada agente dispone de sus propios pesos, elige por sí mismo su próximo color entre los k posibles, puede enviar una solicitud a como máximo un vecino y recibir múltiples mensajes. La recompensa de entrenamiento es **únicamente el progreso global compartido**. No existe cabeza de «aceptar petición» distinta de elegir el color sugerido.

El modelo es equivariante respecto a etiquetas de color sin compartir pesos ENTRE agentes. Las redes observan vecinos directos, snapshots recibidos y último resultado colectivo; no observan el histograma global.

## Pruebas y entrenamiento

En GalexY_travel se ha ejecutado una prueba de diez invariantes, todos correctos, y dos ejecuciones de arranque con DOS actualizaciones de REINFORCE por condición. Son pruebas técnicas, NO resultados sobre aprendizaje cooperativo.

Ejecutar las pruebas:

```powershell
cd C:\Programación\AB-cooperacion-individual-v3-20261110\proyectos\coordinacion-funcional-intergeneracional\v3_independent
& 'C:\Programación\Grokking\.venv\Scripts\python.exe' -m unittest -v test_individual.py
```

Entrenamiento independiente con mismo modelo y parámetros desde cero:

```powershell
& 'C:\Programación\Grokking\.venv\Scripts\python.exe' train_independent.py --mode C1 --seed 311 --updates 60
& 'C:\Programación\Grokking\.venv\Scripts\python.exe' train_independent.py --mode C2 --seed 311 --updates 60
```

C1 permite los cambios autónomos y desactiva mensajes; C2 permite mensajes y cambios autónomos. El evaluador también puede medir C3: ejecutar los modelos C2 con mensajes desactivados, sin alterar los pesos.

**Pendiente:** múltiples cohortes de aprendizaje, tests bloqueados con semillas nuevas, convergencia más larga, métricas de desequilibrio relativo al azar, perturbaciones imprevistas y estudios de roles por identidad. Los checkpoints de entrenamiento no se guardan en este repositorio hasta completar y auditar un experimento, para no confundir las ejecuciones de arranque con evidencia científica.
