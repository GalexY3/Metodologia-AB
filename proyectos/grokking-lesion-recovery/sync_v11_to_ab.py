"""Append V11 results/checkpoints to portable AB branch and verify SHA256.
Do not alter the original experimental trajectories, protocols or results.
"""
from pathlib import Path
import json,hashlib,shutil
SOURCE=Path(r"C:\Programación\grokking_lesion_20261109")
DEST=Path(r"C:\Programación\AB-grokking-lesion-v10-portable-20261109\proyectos\grokking-lesion-recovery")
manifest_path=DEST/"ARCHIVE_MANIFEST.json"
manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
tracked={item["path"]:item for item in manifest["included_files"]}
allow_ext={".py",".md",".csv",".json",".txt",".toml"}
def include_pt(p):
 rel=p.relative_to(SOURCE).as_posix()
 if p.suffix.lower()!=".pt":return False
 if rel.startswith("full_100/parity_runs/") and p.name=="ck_005000.pt":
  return "_nt500/" in rel and ("lambda1e-05_" in rel or "lambda0.001_" in rel) and any(f"_seed{i}_" in rel for i in range(5))
 if rel.startswith("full_100/v11_common_runs/") and p.name in ("ck_005000.pt","ck_007000.pt","ck_009000.pt"):
  return True
 return False
def sha(fp):
 h=hashlib.sha256()
 with fp.open("rb") as f:
  for block in iter(lambda:f.read(1048576),b""):h.update(block)
 return h.hexdigest()
new=[]
for src in sorted(SOURCE.rglob("*")):
 if not src.is_file() or "__pycache__" in src.parts or src.suffix.lower()==".pyc":continue
 if src.suffix.lower() not in allow_ext and not include_pt(src):continue
 rel=src.relative_to(SOURCE).as_posix()
 dst=DEST/rel
 if not dst.exists():
  dst.parent.mkdir(parents=True,exist_ok=True)
  shutil.copy2(src,dst)
  new.append(rel)
 elif rel=="CURRENT.md":
  shutil.copy2(src,dst)
 elif sha(src)!=sha(dst):
  # Source-side changes after the previous frozen snapshot must not silently overwrite history.
  raise RuntimeError(f"Existing version differs (preserve, investigate): {rel}")
 tracked[rel]={"path":rel,"bytes":dst.stat().st_size,"sha256":sha(dst)}
readme=DEST/"README.md"
base=readme.read_text(encoding="utf-8")
if "## V11 — control adversarial de la historia de grokking" not in base:
 base+="""\n## V11 — control adversarial de la historia de grokking\n
[Informe V11](full_100/REPORT_V11.md), [protocolo](full_100/PREREG_V11.md), [robustez V11](full_100/V11_ROBUSTNESS.json) y [reparación V11C](full_100/V11C_ANALYSIS.json).

Tras 4.000 actualizaciones de entrenamiento **con el mismo λ L1=0.0001** y rendimiento 100% en ambas historias, la ventaja de resistencia inicial (A−B=−11.16pp) se redujo casi a cero (−0.48pp) ante 90/300 neuronas eliminadas. En reconstrucción manteniendo la misma L1, las cinco parejas no mostraron una ventaja reproducible: 2 semillas favorecen a A, 3 a B; diferencia media de AUC A−B=−3.48, prueba exploratoria de inversión de signos p=0.6875. La evidencia disponible no acredita que el grokking, separadamente de la regularización, mejore la reparación. Las máscaras no son replicaciones independientes de entrenamiento.

Se incluyen 10 checkpoints iniciales V10 paso5000 y los checkpoints V11 5000/7000/9000, así como las 200 curvas completas de reparación V11B/V11C. Los anteriores resultados positivos V10 permanecen documentados para comparación. No se ha demostrado equivalencia estadística ni una ausencia universal de dependencia de trayectoria.
"""
 readme.write_text(base,encoding="utf-8")
tracked["README.md"]={"path":"README.md","bytes":readme.stat().st_size,"sha256":sha(readme)}
manifest["included_files"]=sorted(tracked.values(),key=lambda z:z["path"])
manifest["included_count"]=len(manifest["included_files"])
manifest["included_bytes"]=sum(z["bytes"] for z in manifest["included_files"])
manifest["incremental_update_v11"]="V11 common-regularization, robustness and recovery controls, local audit and negative findings added to same branch on 2026-11-09."
manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
wrong=[z["path"] for z in manifest["included_files"] if not (DEST/z["path"]).is_file() or sha(DEST/z["path"])!=z["sha256"]]
print(json.dumps({"new_files":len(new),"new_checkpoints":sum(f.endswith(".pt") for f in new),
 "included_count":manifest["included_count"],"included_mb":round(manifest["included_bytes"]/1e6,2),
 "sha_errors":wrong,"new_names_example":new[:12]},ensure_ascii=False))
if wrong:raise RuntimeError("Hash audit failed")
