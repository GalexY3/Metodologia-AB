# Reproducir V175

Python3.12; NumPy2.5.4; Numba0.68.0; llvmlite0.50.0. No se requiere CUDA, PyTorch ni archivos de datos humanos. Máximo dos workers de tres hilos, con prioridad y afinidad verificadas.

Leer PREREG_V175_LEARNED_ECOLOGICAL_MEMORY.md. La arquitectura y las reglas de reproducción están declaradas íntegramente; la referencia al RNN de Itao/Kaneko indica parentesco, no reproducción exacta del código neuronal original.

Antes de entrenar: `python v175_memory_evolution.py --audit-only`. Esa auditoría compara el motor con una referencia NumPy propia y con la función física original pública de Itao/Kaneko. Recuperar el archivo M_player/ds_game_multi_player.py del blob728376144bc819913a30445439d22a3db6d1effe de https://github.com/KenjiItao/ds_game y guardarlo en literatura/original_code/Itao_ds_game_multi_player.py. La copia original no se redistribuye aquí; su licencia no se ha verificado. El entrenamiento propio es independiente del archivo de terceros, pero se exige pasar primero la auditoría.

Tras verificar congelación remota: `python v175_memory_evolution.py --prereg-commit SHA`. Los directorios de salida existentes no se sobrescriben. Hay checkpoints posteriores a reproducción y estado RNG cada500generaciones; el ejecutor no reanuda automáticamente una sesión perdida. Inspeccionar procesos y archivos originales antes de reiniciar cualquier trabajo.

Un positivo aquí es un piloto computacional: aún requiere explotación por invasores, lesiones causales de memoria, más semillas independientes y revisión de prioridad. No dar por descubierta una norma porque suba la eficiencia.
