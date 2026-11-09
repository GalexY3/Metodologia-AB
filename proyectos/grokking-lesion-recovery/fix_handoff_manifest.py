from pathlib import Path
import json,hashlib,shutil
SRC=Path(r"C:\Programación\grokking_lesion_20261109")
DST=Path(r"C:\Programación\AB-grokking-lesion-v10-portable-20261109\proyectos\grokking-lesion-recovery")
shutil.copy2(SRC/"CURRENT.md",DST/"HISTORICAL_CURRENT_PRE_V10.md")
p=DST/"ARCHIVE_MANIFEST.json"
m=json.loads(p.read_text(encoding="utf-8"))
for r in m["included_files"]:
 if r["path"]=="CURRENT.md":
  r["path"]="HISTORICAL_CURRENT_PRE_V10.md"
  break
else:raise RuntimeError("No source original CURRENT")
def h(path):
 return hashlib.sha256(path.read_bytes()).hexdigest()
for name in (".gitignore","CURRENT.md","README.md","requirements.txt"):
 f=DST/name
 m["included_files"].append({"path":name,"bytes":f.stat().st_size,"sha256":h(f)})
m["included_files"].sort(key=lambda r:r["path"])
m["included_count"]=len(m["included_files"])
m["included_bytes"]=sum(r["bytes"] for r in m["included_files"])
m["manifest_policy"]="ARCHIVE_MANIFEST.json is intentionally not self-hashed; it lists all other included files and all omitted source files"
p.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding="utf-8")
bad=[r["path"] for r in m["included_files"] if not (DST/r["path"]).exists() or h(DST/r["path"])!=r["sha256"]]
print(json.dumps({"included":m["included_count"],"bytes":m["included_bytes"],"sha_mismatches":bad},ensure_ascii=False))
if bad:raise RuntimeError("Hash verification failure")
