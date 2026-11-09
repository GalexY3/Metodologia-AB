"""V12 portable archive verification and deterministic Git LF normalization.
Scope-limited to projects/grokking-lesion-recovery. No other repo changes.
"""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parent
mp=ROOT/"ARCHIVE_MANIFEST.json"
manifest=json.loads(mp.read_text(encoding="utf-8"))
old={e["path"]:e for e in manifest["included_files"]}
def digest(data):
 return hashlib.sha256(data).hexdigest()
normalized=[]
unexplained=[]
for rel,item in old.items():
 if rel in ("CURRENT.md","README.md"):continue
 path=ROOT/rel
 if not path.is_file():
  unexplained.append((rel,"missing"));continue
 raw=path.read_bytes()
 if digest(raw)!=item["sha256"]:
  lf=raw.replace(b"\r\n",b"\n")
  if digest(lf)==item["sha256"]:
   path.write_bytes(lf)
   normalized.append(rel)
  else:
   unexplained.append((rel,"unexpected-difference"))
if unexplained:raise RuntimeError("Unexpected archive drift: "+str(unexplained[:10]))

attr=ROOT/".gitattributes"
attr.write_text(
 "* text=auto eol=lf\n"
 "*.pt -text\n"
 "*.png -text\n"
 "*.jpg -text\n"
 "*.jpeg -text\n"
 "*.zip -text\n",encoding="utf-8")

readme=ROOT/"README.md"
body=readme.read_text(encoding="utf-8")
if "## V12 — réplica en GALEXY_TRAVEL" not in body:
 body += (
 "\n## V12 — réplica en GALEXY_TRAVEL\n\n"
 "El [informe científico V12](full_100/REPORT_V12.md) contiene dos gráficos, "
 "resultados completos y limitaciones. Se entrenaron diez pares nuevos sobre una "
 "partición independiente; cinco cumplieron todos los criterios de historia y "
 "capacidad antes de ser lesionados. La diferencia de robustez A−B disminuyó de "
 "−10,38 a −0,96 puntos porcentuales tras 4.000 actualizaciones finales con la "
 "misma L1=0,0001. La comparación posterior de reconstrucción con cien lesiones "
 "nuevas NO encontró una ventaja consistente del grupo tardío: dos de cinco "
 "semillas favorecieron a A y tres a B. Ni este resultado ni los pilotos previos "
 "identifican causalmente un efecto exclusivo del grokking.\n\n"
 "Evidencias: [selección](full_100/V12_GATES.json), "
 "[robustez](full_100/V12_ROBUSTNESS.json), "
 "[reparación](full_100/V12B_ANALYSIS.json), "
 "[test reservado](full_100/V12_TEST_AUDIT.json), "
 "[prerregistro V12](full_100/PREREG_V12.md) y "
 "[prerregistro de lesiones](full_100/PREREG_V12B.md). "
 "La carpeta V12 mantiene los checkpoints y curvas para reproducir los análisis.\n\n"
 "Para recomputar el análisis desde Windows, con Python y PyTorch/NumPy instalados, "
 "ejecutar full_100/v12_robustness.py, full_100/v12b_analysis.py y "
 "full_100/v12_make_report.py. Se puede verificar el manifiesto mediante "
 "SHA-256 byte a byte.\n"
 )
readme.write_text(body.replace("\r\n","\n"),encoding="utf-8")

audit={"source":"portable Git worktree on GALEXY_TRAVEL",
       "base_upstream_commit":"898bca86f48bb42fae72f6c8ab7b577a68b9faee",
       "git_eol_crlf_only_mismatches_corrected":len(normalized),
       "unexplained_mismatches":unexplained,
       "original_manifest_entries":len(old),
       "policy":"new .gitattributes forces LF for text; *.pt binary",
       "validation":{"v12_robustness":"V12_ROBUSTNESS.json",
                     "v12b_repair":"V12B_ANALYSIS.json",
                     "test_sealed":"V12_TEST_AUDIT.json"}}
(ROOT/"V12_PORTABILITY_AUDIT.json").write_text(json.dumps(audit,indent=2,ensure_ascii=False),encoding="utf-8")

allow={".py",".md",".json",".csv",".svg",".txt",".toml",".pt"}
included=[]
for p in sorted(ROOT.rglob("*")):
 if not p.is_file():continue
 if "__pycache__" in p.parts or p.suffix.lower()==".pyc" or p.name=="ARCHIVE_MANIFEST.json":continue
 if not (p.suffix.lower() in allow or p.name in (".gitignore",".gitattributes")):continue
 rel=p.relative_to(ROOT).as_posix()
 included.append({"path":rel,"bytes":p.stat().st_size,"sha256":digest(p.read_bytes())})
manifest["included_files"]=included
manifest["included_count"]=len(included)
manifest["included_bytes"]=sum(z["bytes"] for z in included)
included_names={z["path"] for z in included}
manifest["omitted_files"]=[z for z in manifest.get("omitted_files",[]) if z["path"] not in included_names]
manifest["omitted_count"]=len(manifest["omitted_files"])
manifest["omitted_bytes"]=sum(z["bytes"] for z in manifest["omitted_files"])
manifest["incremental_update_v12"]="Travel V12 and V12B, new split and seeds; test sealed until validation analysis frozen. Versioned and internally audited; includes new checkpoints, trajectories, results, svg figures."
manifest["manifest_policy"]="ARCHIVE_MANIFEST.json intentionally not self-hashed. Included files are all portable project files of known types. The omitted listing pertains to intermediate checkpoints left on original DESKTOP at previous snapshot."
mp.write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
bad=[z["path"] for z in included if not (ROOT/z["path"]).is_file() or digest((ROOT/z["path"]).read_bytes())!=z["sha256"]]
print(json.dumps({"normalized_line_ending_mismatches":len(normalized),
 "included_count":len(included),"included_mb":round(manifest["included_bytes"]/1e6,2),
 "omitted_count":manifest["omitted_count"],"hash_errors":bad},ensure_ascii=False),flush=True)
if bad:raise RuntimeError("Manifest hash validation failed")
