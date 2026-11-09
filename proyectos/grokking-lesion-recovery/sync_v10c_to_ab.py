"""Incremental V10C preservation in the previously published AB worktree.
The original V10B commit remains intact; new results are versioned on same branch.
"""
from pathlib import Path
import json,hashlib,shutil
SOURCE=Path(r"C:\Programación\grokking_lesion_20261109")
DEST=Path(r"C:\Programación\AB-grokking-lesion-v10-portable-20261109\proyectos\grokking-lesion-recovery")
assert (DEST/"ARCHIVE_MANIFEST.json").exists()
relfiles=[
 "full_100/v10c_scan.py",
 "full_100/v10c_repair.py",
 "full_100/analyze_v10c.py",
 "full_100/V10C_MASK_SCAN.json",
 "full_100/V10C_MATCHED_RAW.json",
 "full_100/V10C_MATCHED_ANALYSIS.json",
 "full_100/REPORT_V10C.md",
]
relfiles += [p.relative_to(SOURCE).as_posix() for p in sorted((SOURCE/"full_100"/"parity_matched_lesions").rglob("*.csv"))]
for rel in relfiles:
 src=SOURCE/rel; dst=DEST/rel
 if not src.is_file():raise FileNotFoundError(src)
 if dst.exists():raise FileExistsError(f"Refusing to overwrite old experimental results: {dst}")
 dst.parent.mkdir(parents=True,exist_ok=True)
 shutil.copy2(src,dst)

summary="""# CURRENT — grokking y reparación tras lesión neuronal (portátil)

**Fecha de captura:** 2026-11-09. **Estado:** V10B y V10C completados y auditados localmente; ambas evaluaciones son **exploratorias, no confirmatorias**.

**Autoridad del investigador:** comparar redes con 100% de precisión (en conjuntos observados), una con generalización tardía grokking y otra con generalización más continua, para medir su robustez ante eliminación permanente de unidades y su capacidad **condicional** de recuperación cuando ambas sufren daño funcional equivalente. Igual accuracy global no implica mismos circuitos.

**Empieza por** `README.md`, `full_100/PREREG_V10B.md`, `full_100/V10_ELIGIBILITY.json`, `full_100/V10_ANALYSIS.json`, `full_100/PREREG_V10C.md`, `full_100/REPORT_V10C.md`, `full_100/V10C_MATCHED_ANALYSIS.json`, `ARCHIVE_MANIFEST.json`.

**V10B:** cinco pares de redes (MLP 300 neuronas; 30 bits con paridad en 3) llegan a 100% train/val/test en los datos evaluados al paso 8000. Grupo A regularización L1 λ=1e-5, generalización tardía; grupo B L1 λ=.001, adquisición más rápida. 150 pruebas de lesión en 30, 90, 150 neuronas, con máscaras emparejadas. Grupo A fue más robusto a igual número de neuronas eliminadas. No es demostración de recuperación más rápida porque pierde menos precisión inicialmente.

**V10C:** análisis de sensibilidad posterior al V10B, con máscaras nuevas 1001..2000, selección de las primeras cinco por par de redes que causan entre 10 y 40pp de daño en ambos y difieren <=5pp, elegidas **antes de observar recuperación**. 25 pares de máscaras, 50 lesiones de 150/300 unidades. Promedio de pérdida inicial de validación A=23,808pp, B=23,768pp. Déficit acumulado de validación A−B medio por semilla = −8,614 unidades precisión×paso, favorable a A en 4 de 5 semillas, una favorable a B. Recuperaciones observadas a >=99% durante 400 pasos A=22/25, B=17/25. **Solo n=5 pares de redes independientes**; máscaras son repeticiones anidadas. Superposición de ejemplos erróneos entre brazos, Jaccard medio=0,183: equiparar caída de accuracy NO iguala tipo de daño. L1 distinta confunde cualquier inferencia causal sobre grokking.

**Dictamen actual:** asociación exploratoria entre historia + régimen L1 y robustez/recuperabilidad, sin causalidad aislada del grokking. No se ha demostrado novedad publicable, superioridad metodológica AB ni un mecanismo universal. Se conserva resultado V10B de perturbación física aleatoria y V10C de emparejamiento por severidad; ninguno sustituye al otro.

**Siguiente trabajo:** diseño factorial que desacople tipo de historia de L1, grupo con aprendizaje continuo auténtico, semillas nuevas y partición de datos reservada, múltiples tareas/arquitecturas, análisis de tipos de error y daño por pérdidas/márgenes, lesionado vs continuo, estudio de mecanismos internos. Registrar negativos y controles adversariales.

**Ruta original sobremesa:** `C:\\Programación\\grokking_lesion_20261109`. **Github:** `GalexY3/Metodologia-AB`, rama `research/grokking-lesion-v10-portable-20261109`, carpeta `proyectos/grokking-lesion-recovery/`. El snapshot excluye checkpoints intermedios redundantes y contiene checkpoints finales V7/V9/V10, curvas, datos, código y su manifiesto con hashes.
"""
(DEST/"CURRENT.md").write_text(summary,encoding="utf-8")
(SOURCE/"CURRENT.md").write_text(summary,encoding="utf-8")
readme_path=DEST/"README.md"
readme=readme_path.read_text(encoding="utf-8")
readme=readme.replace("todavía pendiente de ejecutar en el momento de esta instantánea","ejecutado y auditado localmente; consultar REPORT_V10C.md")
readme += """
## Nuevo resultado V10C: reparación tras igualar la gravedad inicial de la lesión

El estudio [V10C](full_100/REPORT_V10C.md) ya está completo. Se seleccionaron cinco máscaras nuevas por cada uno de los cinco pares de redes **antes** de entrenar la recuperación, obligando a que ambas redes perdieran entre 10 y 40 puntos de precisión y difiriesen <=5 puntos porcentuales en daño inicial. En 50 trayectorias de reconstrucción, la caída media inicial de validación fue A 23,808pp frente a B 23,768pp; la diferencia media de área de déficit A−B fue −8,614 en cinco unidades de replicación, con A favorable en 4 de 5 semillas. Se recuperaron al menos hasta el umbral de 99% 22/25 ensayos A y 17/25 B. Sigue siendo un resultado **exploratorio condicionado por la selección de daño**, con regularización L1 distinta entre grupos y baja coincidencia de ejemplos dañados (Jaccard promedio 0,183). No demuestra causalidad del grokking.

Archivos: [protocolo](full_100/PREREG_V10C.md), [informe](full_100/REPORT_V10C.md), [selección de máscaras](full_100/V10C_MASK_SCAN.json), [resultados individuales](full_100/V10C_MATCHED_RAW.json), [auditoría/análisis](full_100/V10C_MATCHED_ANALYSIS.json), [código de selección](full_100/v10c_scan.py), [código de reconstrucción](full_100/v10c_repair.py) y [análisis](full_100/analyze_v10c.py).

Para verificar los resultados guardados desde otro PC:

```powershell
python full_100/analyze_v10c.py
```
"""
readme_path.write_text(readme,encoding="utf-8")
mp=DEST/"ARCHIVE_MANIFEST.json"
manifest=json.loads(mp.read_text(encoding="utf-8"))
by_path={r["path"]:r for r in manifest["included_files"]}
def h(path):return hashlib.sha256(path.read_bytes()).hexdigest()
for rel in relfiles+["CURRENT.md","README.md"]:
 fp=DEST/rel
 by_path[rel]={"path":rel,"bytes":fp.stat().st_size,"sha256":h(fp)}
manifest["included_files"]=sorted(by_path.values(),key=lambda r:r["path"])
manifest["included_count"]=len(manifest["included_files"])
manifest["included_bytes"]=sum(r["bytes"] for r in manifest["included_files"])
manifest["incremental_update"]="V10C mask scan, 50 matched-damage repairs, report and handoff added after initial portable snapshot on 2026-11-09; same GitHub branch"
mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
bad=[r["path"] for r in manifest["included_files"] if not (DEST/r["path"]).exists() or h(DEST/r["path"])!=r["sha256"]]
print(json.dumps({"new_raw_files":len(relfiles),"manifest_included":manifest["included_count"],"all_hashes_valid":not bad,"bad":bad,"bytes":manifest["included_bytes"]},ensure_ascii=False))
if bad:raise RuntimeError(f"Bad archive hashes: {bad}")
