# Reproducir V182–V186

La evidencia conserva los resultados originales; no ejecutar scripts de una sola salida sobre ellos. Trabajar en una copia nueva y asignar destinos alternativos. El paquete SHA256 incluye fuentes, normas derivadas del archivoCC0, fixturesMATLAB,cintas,curvas,redes,checkpoints,protocolos y resultados negativos. No incluye el ZIP original252MB ni Octave481MB: están identificados por URL y hash y pueden adquirirse con los scripts correspondientes.

Entorno usado:Python3.12.16,NumPy2.5.4,Numba0.68.0,PyTorch2.11.0+cu128,CUDA12.8,RTX4070SUPER. Ver MANIFEST deV185 y metadatos de adquisición deOctave11.3.0. scipy y matplotlib para lectura/análisis. Los pesos son archivos propios dePyTorch; no cargar checkpoints ajenos no confiables como si fueran estos.

## Reproducción física

1. `v182_download_yaman_original.py` adquiere el archivo oficial desdeZenodo8401555,verifica MD5,tamaño,SHA256yCRC,yextrae `.m` sin modificar. Los fuentes tienen licenciaCC0según el depósito.
2. `v182_audit_yaman_archive.py` lee los ocho archivos.mat,1.200ajustes. El resultado válido incluye `valid:true`; el parser inicial invalidado se conserva por trazabilidad y no es evidencia de ceroajustes.
3. `v182_acquire_octave.py` adquiere una distribución oficial portátil,sin instalar ni modificarPATH. Su hash identifica bytes descargados; no se afirma verificación de firmaGPG.
4. `v182_validate_port.py prepare`, `execute`, `verify` generan fixtures,ejecutan códigoMATLABoriginal medianteOctaveycontrastan51salidas. Los replaycopies solo cambian nombres y proveedoresRNG; las reglas físicas permanecen iguales. Las rutasOctaveWindows se ajustan a otro equipo sin modificar fórmulas. No lanzar los main originales de30workers para esta validación.

## Repetir contrastes con destinos nuevos

Los siguientes ejemplos conservan parámetros y semillas. Se cambia únicamente el destino de resultados. Ejecutarlos desde el directorio donde están los módulos. Mantener los recibos originales de preregistro y los padres congelados en sus rutas verificadas.

```python
from pathlib import Path
from research_resource_limits import apply_limits
apply_limits(3)
import v183_run_timing as experiment
experiment.OUT = Path('results/replica_V183')
experiment.technical_gate()
experiment.run()
```

ParaV184usar `v184_pasture_replication` y `results/replica_V184`. Sus300normas incluyen celdas exactamente idénticas entre asignaciones: copiar resultados simétricos es intencional y no representa vidas nuevas.

```python
from pathlib import Path
from research_resource_limits import apply_limits
apply_limits(2)
import v185_collective_grokking as experiment
experiment.OUT = Path('results/replica_V185')
experiment.technical()
experiment.run()
```

Las congelaciones deV185no se ejecutaron porque faltó su condicióntrain99%. El helper original contiene un problema de restauración delByteTensorRNGsi un futuro replayse carga directamente enCUDA; V186lo corrige mediante `.cpu()`. No alterar silenciosamenteV185para producir un resultado nuevo. Una variante corregida requeriría fuente/recibo distintos. Esta limitación no afecta las cuatro ejecuciones realizadas,que nunca llamaron a ese helper.

ParaV186crear un destino nuevo,ejecutar allí `audit()` y `replay()` antes de `run()`. MantenerPARENTenloscheckpointsV185originales,porque el preregistro congela sus hashes. Si se usan padres generados por una réplica nueva,registrar sus hashes y tratarlo como nueva confirmación,no como replayidéntico del mismo estado. La prueba histórica25000→30000deV186reprodujo exactamente dos veces pesos,baselineyRNG; no garantiza identidad entre hardware/versiones.

## Auditoría y lectura

LosJSONSUMMARYy metrics contienen todos los criterios. `close_v182_v186.py` genera informe,figuras,ledger y nuevo manuscrito solo cuando todos los jobs han terminado; es una operación de cierre única con backups,no una prueba de hipótesis adicional. El negativoV183(.054893frente a margen.25) debe permanecer negativo. No convertir reparaciónexterna de códigos en formación institucional privada ni cada checkpoint/semilla en estudio independiente.

La publicación usa un índiceGitaislado y `hash-object --no-filters` para preservar exactamenteCRLF/LF. El manifiesto SHA256 registra bytes, no solo el contenido queGitnormaliza. El repositorio local del usuario y su índice no se reasignan.
