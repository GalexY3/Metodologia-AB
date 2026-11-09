"""Create a self-contained portable snapshot in AB worktree without touching source data.

Copies code, preregistrations, reports, CSV trajectories, JSON evidence and exact
final PyTorch checkpoints for the principal analyses. Intermediate checkpoints
remain on source workstation; their hash/size are recorded for provenance.
"""
from __future__ import annotations
from pathlib import Path
from collections import Counter
import hashlib, json, os, shutil, datetime, csv

SOURCE=Path(r"C:\Programación\grokking_lesion_20261109")
WORKTREE=Path(r"C:\Programación\AB-grokking-lesion-v10-portable-20261109")
DEST=WORKTREE/"proyectos"/"grokking-lesion-recovery"
assert SOURCE.is_dir() and WORKTREE.is_dir()
assert not DEST.exists(), f"Refusing to overwrite existing project {DEST}"
DEST.mkdir(parents=True)
ACCEPT_EXT={".py",".md",".json",".csv",".txt",".toml"}
ALLOW_CKS=set()
for seed in range(5):
 for lam in ("1e-05","0.001"):
  ALLOW_CKS.add(f"full_100/parity_runs/lambda{lam}_seed{seed}_lr0.001_width300_nt500/ck_008000.pt")
for seed in range(3):
 for wd in ("1.0","3.0"):
  ALLOW_CKS.add(f"full_100/runs/wd{wd}_scale1.0_lr0.001_seed{seed}_split20261109/checkpoint_012000.pt")
 for wd in ("1.0","2.5"):
  ALLOW_CKS.add(f"gated_runs/cleanWD{wd}_noiseWD0.05_init1.0_s{seed}_train0.55/ck_022000.pt")

def sha256(path):
 h=hashlib.sha256()
 with path.open("rb") as f:
  for block in iter(lambda:f.read(2*1024*1024),b""):
   h.update(block)
 return h.hexdigest()

included,omitted=[],[]
for path in sorted(SOURCE.rglob("*")):
 if not path.is_file():continue
 rel=path.relative_to(SOURCE)
 posix=rel.as_posix()
 if "__pycache__" in rel.parts or path.suffix.lower()==".pyc":continue
 copy= (path.suffix.lower() in ACCEPT_EXT) or (posix in ALLOW_CKS)
 manifest={"path":posix,"bytes":path.stat().st_size,"sha256":sha256(path)}
 if copy:
  dest=DEST/rel
  dest.parent.mkdir(parents=True,exist_ok=True)
  shutil.copy2(path,dest)
  assert sha256(dest)==manifest["sha256"]
  included.append(manifest)
 else:
  omitted.append(manifest)
missing=ALLOW_CKS-{x["path"] for x in included}
if missing:raise ValueError(f"Missing expected final checkpoints: {missing}")
summary={
 "timestamp_utc":"2026-11-09",
 "source_workstation":"DESKTOP-I4SULKD",
 "source_directory":str(SOURCE),
 "scope":"portable curated reproducible snapshot; not complete byte-for-byte archive of every intermediate checkpoint",
 "included_count":len(included),
 "included_bytes":sum(x["bytes"] for x in included),
 "omitted_count":len(omitted),
 "omitted_bytes":sum(x["bytes"] for x in omitted),
 "final_checkpoints_included":sorted(ALLOW_CKS),
 "included_files":included,
 "omitted_files":omitted,
}
(DEST/"ARCHIVE_MANIFEST.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
(DEST/".gitignore").write_text(
 "__pycache__/\n*.pyc\n.pytest_cache/\n# Regenerated intermediate checkpoints are excluded by default; the frozen checkpoints are tracked explicitly.\n*.pt\n# Temporary and environment files\n.venv/\n*.log\n*.tmp\n",encoding="utf-8")
readme="""# Grokking, lesiones y recuperación neuronal — laboratorio AB

## Objeto

Comparación computacional de redes que llegan al mismo nivel de precisión por trayectorias distintas y posterior respuesta a ablaciones neuronales permanentes. Proyecto experimental independiente dentro del repositorio metodológico AB.

**Estado epistemológico (09-11-2026): exploratorio, NO confirmatorio.**

La investigación pasó por pilotos semigrokking-parcial (V1–V8), una comparación de grokking de distintas latencias al 100% en suma modular (V9) y un contraste más próximo a la pregunta científica entre generalización tardía y rápida en paridad binaria (V10). No debe atribuirse causalidad al evento grokking únicamente por comparar dos condiciones que difieren en regularización L1.

## Resultado V10B (muestra de cinco semillas)

Se entrenaron cinco pares de redes MLP con 300 unidades ocultas para paridad de los tres primeros de 30 bits. Los modelos de ambas condiciones alcanzaron 100% de precisión sobre conjuntos finitos de entrenamiento, validación y prueba; las latencias de generalización difirieron. El contraste se generó con diferentes fuerzas de regularización L1, **un confusor causal directo importante**.

Se aplicaron 150 ensayos de ablación permanente, en tres dosis (30, 90, 150 neuronas), cinco máscaras emparejadas y cinco pares de redes. El grupo tardío resistió mejor las lesiones aleatorias y mostró menor déficit acumulado respecto a su control sin lesión, **pero también sufrió menor daño inmediato**. Por eso la evidencia disponible respalda una diferencia exploratoria de *robustez* entre estas condiciones, no una demostración causal de mejor *regeneración tras un daño equivalente*.

Lecciones verificadas, limitaciones, protocolos y métricas se conservan sin recalificar resultados exploratorios como confirmatorios.

## Puntos de entrada

- [CURRENT.md](CURRENT.md) — estado exacto y próximo contraste.
- [full_100/PREREG_V10B.md](full_100/PREREG_V10B.md) — diseño preespecificado antes de lesiones V10B.
- [full_100/V10_ELIGIBILITY.json](full_100/V10_ELIGIBILITY.json) — clasificación de las diez trayectorias.
- [full_100/V10_ANALYSIS.json](full_100/V10_ANALYSIS.json) — agregación y auditoría local de las 150 lesiones.
- [full_100/V10_LESION_RAW.json](full_100/V10_LESION_RAW.json) — observaciones por semilla, dosis y máscara.
- [full_100/V10_UNIT_MECHANISM.json](full_100/V10_UNIT_MECHANISM.json) — sondas de contribución funcional.
- [full_100/PREREG_V10C.md](full_100/PREREG_V10C.md) — protocolo de sensibilidad con daño igualado (todavía pendiente de ejecutar en el momento de esta instantánea).
- [REPORT_V7.md](REPORT_V7.md) y [full_100/V9_ANALYSIS.json](full_100/V9_ANALYSIS.json) — pilotos anteriores, incluidos resultados negativos.
- [ARCHIVE_MANIFEST.json](ARCHIVE_MANIFEST.json) — SHA-256 de archivos conservados y omitidos.

## Reproducción desde otro PC

En Windows PowerShell, tras clonar el repositorio o cambiar a la rama correspondiente, instalar Python con PyTorch y NumPy. Ejecutar desde el directorio de este proyecto:

```powershell
python -m pip install torch numpy
python full_100/classify_v10.py
python full_100/analyze_v10.py
python full_100/v10_unit_probe.py
```

Para una NUEVA semilla (por ejemplo seed 5), entrenar ambos brazos en la misma partición antes de calificar trayectorias:

```powershell
python full_100/parity_v10.py --ntrain 500 --seed 5 --l1 0.00001 --steps 8000
python full_100/parity_v10.py --ntrain 500 --seed 5 --l1 0.001 --steps 8000
```

Los entrenamientos originales generaron checkpoints `.pt`; se incluyen los finales para las diez redes V10B, seis V9 y seis V7. Se excluyen miles de snapshots intermedios, reproducibles desde el código y las semillas. La instantánea contiene todas las curvas CSV disponibles y los resultados JSON de ensayos de lesión, además de los protocolos y análisis.

**Nota**: la arquitectura de paridad comparte la capa oculta de 300 unidades entre ambos grupos; las unidades no deben interpretarse como neuronas biológicas. La generalización 100% fue comprobada únicamente sobre muestras finitas, no en las 2^30 entradas posibles.

## Gobernanza

La carpeta original del sobremesa permanece intacta en `C:\\Programación\\grokking_lesion_20261109`; esta copia se ubicó de forma aislada en `proyectos/grokking-lesion-recovery` sin modificar los demás proyectos de AB. No se ha adoptado un nuevo hallazgo confirmado, ni se ha demostrado superioridad del protocolo AB o la originalidad científica de la hipótesis.
"""
(DEST/"README.md").write_text(readme,encoding="utf-8")
current="""# CURRENT — traspaso portátil de grokking y lesión neuronal

**Fecha de captura:** 2026-11-09. **Estado:** V10B completo, V10C de igualación de lesión pendiente. **Autoridad científica**: la especificación del usuario es comparar igual capacidad final (ahora 100%) con historia de grokking frente a aprendizaje progresivo, para medir resistencia y reconstrucción. No confundir robustez con plasticidad.

**Primero leer**: `README.md`, `full_100/PREREG_V10B.md`, `full_100/V10_ELIGIBILITY.json`, `full_100/V10_ANALYSIS.json`, `full_100/V10_UNIT_MECHANISM.json`, `full_100/PREREG_V10C.md`, `REPORT_V7.md`.

**Hallazgos exploratorios**: V10B construyó 5 parejas de paridad 30bits (3 relevantes) con igual 100% train/val/test a paso8000. L1 grokking tardío λ=1e-5, L1 aprendizaje rápido λ=.001. Latencia fit→95% val: A 3100–4000 pasos; B 400–800 pasos. Lesiones: dosis30/90/150 de 300; 5 máscaras por pareja, 150 ensayos. Estado de auditoría local PASS. El grupo A pierde menos precisión tras lesión y presenta menor déficit acumulado, pero diferencias de magnitud de daño y L1 impiden conclusión causal sobre recuperación. Las sondas neuronales indican concentración funcional diferente, también susceptible a confusión por L1.

**Siguiente tarea concreta:** ejecutar la sensibilidad V10C: seleccionar máscaras disjuntas bajo criterio PREVIO sobre daño validación (10–40 pp en ambos grupos con diferencia ≤5 pp, 150 unidades eliminadas); estudiar curvas de recuperación solo después de congelar el listado de máscaras, sin seleccionar por velocidad. Auditar pérdidas inicialmente equiparadas y corregir sesgos de selección; controlar características del daño. Es una prueba exploratoria, no confirmatoria. Requerirá más semillas e idealmente regularización idéntica con manipulación independiente de trayectoria. No presentar una ventaja de resistencia como recuperación más rápida.

**Original local:** `C:\\Programación\\grokking_lesion_20261109`. Esta copia conserva scripts, datos sintéticos, informes, curvas y checkpoints finales, pero omite snapshots intermedios (ver ARCHIVE_MANIFEST.json). Todo código local de los experimentos anteriores está dentro de esta carpeta. No hay automatización residente configurada para correr entrenamientos entre chats.
"""
(DEST/"CURRENT.md").write_text(current,encoding="utf-8")
(DEST/"requirements.txt").write_text("numpy\ntorch\n",encoding="utf-8")
print(json.dumps({
 "dest":str(DEST),
 "included_files":len(included),
 "included_mb":round(sum(x["bytes"] for x in included)/1e6,2),
 "omitted_intermediate_files":len(omitted),
 "omitted_mb":round(sum(x["bytes"] for x in omitted)/1e6,2),
 "final_checkpoints":len(ALLOW_CKS),
 "manifest_kb":round((DEST/"ARCHIVE_MANIFEST.json").stat().st_size/1024),
},ensure_ascii=False,indent=2))
