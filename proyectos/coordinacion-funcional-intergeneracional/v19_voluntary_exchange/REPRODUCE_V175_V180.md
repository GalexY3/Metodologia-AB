# Reproducir el bloque V175–V180

El paquete de evidencia se extrae en un directorio que actúe como raíz de `v19_voluntary_exchange`. Preservar cualquier salida existente. Los ejecutores crean directorios nuevos y rechazan sobrescribirlos. Para repetir las evoluciones, utilizar otra copia limpia; para inspeccionarlas basta cargar las poblaciones, curvas y matrices guardadas. El ZIP preserva los bytes exactos, incluidos saltos de línea. Para verificar hashes directamente en una nueva copia Git, clonar con `git -c core.autocrlf=false clone ...`; no cambiar silenciosamente la configuración de una copia de trabajo existente. La publicación usa `hash-object --no-filters` para conservar la identidad de los archivos.

## Dependencias y recursos

Python 3.12; NumPy 2.5.4; Numba 0.68.0; llvmlite 0.50.0; SciPy, pandas y Matplotlib según `results/V175_V180_FINAL_AUDIT.json` y `research/V175_V180_20261115/ENVIRONMENT.json`. No se necesita CUDA ni PyTorch para este bloque. `uv pip install --python RUTA_PYTHON ...` permite instalar las versiones en un entorno aislado. No ejecutar instalaciones sobre otro entorno sin revisar su resolución de dependencias.

Los scripts limitan cada worker a tres hilos, prioridad BelowNormal y la máscara de CPU16515072 en este PC. En otro equipo, adaptar explícitamente esa máscara en `research_resource_limits.py` y registrar el nuevo hash; esa adaptación operativa no constituye identidad binaria con la ejecución archivada. Máximo dos workers. No reiniciar una corrida porque un tiempo de observación haya expirado: verificar procesos y archivos. Hay checkpoints y RNG cada500generaciones, pero no reanudación automática implementada.

## Fuente externa de física

Los entrenamientos usan código propio. Sus auditorías exigen la copia original de `M_player/ds_game_multi_player.py` del repositorio [KenjiItao/ds_game](https://github.com/KenjiItao/ds_game), blob inmutable `728376144bc819913a30445439d22a3db6d1effe`. Guardar en `literatura/original_code/Itao_ds_game_multi_player.py`. La copia usada tiene SHA256 `c2fe660960452fbfd53b26973894851533038cc95c214eb02eeebcc46326b031`,21861bytes; se añadió un salto de línea terminal al contenido recuperado. `literatura/original_code/V173_DOWNLOAD_MANIFEST.json` conserva la procedencia. No importar el archivo original de DOS jugadores: su código principal no está protegido y ejecutaría campañas.

No se redistribuye código de terceros cuya licencia no se verificó. Recuperarlo desde su fuente pública. La modificación AST de V180 añade únicamente el intercepto al score; no modifica el original en disco.

## Orden de reproducción en una copia sin resultados

```powershell
python v175_memory_evolution.py --audit-only
python v175_memory_evolution.py --prereg-commit e5dd0826c29f97d246d80d5a8e8f16072e56552b
python v176_frozen_memory_causal.py --audit-only
python v176_frozen_memory_causal.py --prereg-commit d78039270b2ca6a86eb044d2d02014bc09234d81
python v177_cognitive_gate_game.py --prereg-commit 56637552a6304ff9f77ff5caf891c39684a59810
python v178_private_affine_rival.py --audit-only
python v178_private_affine_rival.py --m 5 --prereg-commit 459056ca268ac59b1592476a724d8358dcfc8888
python v180_open_policy_space.py --stage audit
python v180_open_policy_space.py --stage maintenance-screen --prereg-commit a99703a14f88d5c544e8ffd2cb3998ddfabafbf7
```

M16 no se ejecutó: falló la condición prospectiva de V178. La selección original de V180 está congelada en `2766f863cda02bff7cd67eebeb8a682de358065e`. En una reproducción exacta de sus poblaciones, verificar que la selección corresponde al archivo archivado antes de:

```powershell
python v180_open_policy_space.py --stage validate --selection-commit 2766f863cda02bff7cd67eebeb8a682de358065e
```

Si se cambian poblaciones o selección, ese commit ya no es un preregistro de la selección nueva: conservarla y registrarla por separado antes de usar poblaciones reservadas. Pasar un SHA por CLI registra una referencia; la verificación remota real se conserva en el historial Git y los recibos de publicación. Ningún script autentica por sí mismo que el texto del protocolo exista en ese commit.

## Reproducción humana

El archivo de [Buntaine et al.,OSF8fzmq](https://osf.io/8fzmq/) se conserva localmente en `datos_humanos/metaketa_china_2021`. El ZIP humano no se incluye en nuestro paquete público. Su manifiesto y metadatos sí. Para obtenerlo y reconstruir los resultados en una copia nueva:

```powershell
python v179_download_cpr_evidence.py
python v179_profile_cpr_archive.py
python v179_replicate_waterway_effects.py
```

El descargador valida tamaño y CRC; el perfilador y el análisis exigen el SHA original. No ejecutan R de terceros ni analizan hogares. La réplica cubre una especificación de calidad del agua, sus intervalos CR2 y10000permutaciones; no todos los resultados del artículo. El contraste entre destinos de información es adicional y no confirmatorio.

## Auditoría y documentos

`close_v175_v180.py` vuelve a calcular cantidades importantes, reproduce los56puntos finales V178/V180 y genera figuras estáticas. Parte de su auditoría comprueba la preservación histórica de V169–V174 y requiere el paquete previo `research/V169_V174_20261115/EVIDENCE.zip`; esa comprobación no es necesaria para ejecutar los nuevos entrenamientos. Los diez puntos finales de V175 ya se reejecutan en la auditoría V176.

Los scripts de integración bibliográfica y editorial son operaciones de una sola vez y preservan copias anteriores; no ejecutarlos sobre una carpeta ya integrada para simular una nueva investigación. El manuscrito V180 es un borrador académico de trabajo. El ledger separa ciclos científicos, auditorías post hoc y reproducción humana.

La identidad de motores y la reproducción de evidencia existente no son confirmación científica independiente de una predicción nueva. CT2 histórico61/100 yN2=N3=0 permanecen.
