"""Final byte-level portability correction for V12 on Windows.
Preserve the exact raw bytes of V12_GATES and V12_ROBUSTNESS because the
post-selection TEST audit recorded their SHA256 BEFORE test was opened.
These two use deterministic CRLF checkout. Other text files use LF.
"""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parent
MP=ROOT/"ARCHIVE_MANIFEST.json"
man=json.loads(MP.read_text(encoding="utf-8"))
auditpath=ROOT/"full_100"/"V12_TEST_AUDIT.json"
audit=json.loads(auditpath.read_text(encoding="utf-8"))
frozen={
 "full_100/V12_GATES.json":audit["gate_file_sha256"],
 "full_100/V12_ROBUSTNESS.json":audit["validation_file_sha256"],
}
sha=lambda v:hashlib.sha256(v).hexdigest()
for rel,expected in frozen.items():
 got=sha((ROOT/rel).read_bytes())
 if got!=expected:raise RuntimeError(f"Frozen test-audit hash mismatch: {rel} {got} expected {expected}")
exts={".py",".md",".json",".csv",".svg",".txt",".toml"}
n_changed=0
for file in ROOT.rglob("*"):
 if not file.is_file() or "__pycache__" in file.parts:continue
 if file.suffix.lower() not in exts and file.name not in (".gitattributes",".gitignore"):continue
 rel=file.relative_to(ROOT).as_posix()
 if rel in frozen or rel=="ARCHIVE_MANIFEST.json":continue
 old=file.read_bytes()
 normalized=old.replace(b"\r\n",b"\n")
 if old!=normalized:
  file.write_bytes(normalized)
  n_changed+=1
# Ensure all future checkouts reproduce the same exact bytes.
gitattributes=(
 "* text=auto eol=lf\n"
 "full_100/V12_GATES.json text eol=crlf\n"
 "full_100/V12_ROBUSTNESS.json text eol=crlf\n"
 "*.pt -text\n"
 "*.png -text\n"
 "*.jpg -text\n"
 "*.jpeg -text\n"
 "*.zip -text\n"
)
(ROOT/".gitattributes").write_bytes(gitattributes.encode("utf-8"))

port=ROOT/"V12_PORTABILITY_AUDIT.json"
obj=json.loads(port.read_text(encoding="utf-8"))
obj["v12_final_line_endings"]={
 "files_normalized_from_CRLF_to_LF":n_changed,
 "crlf_preserved_for_test_audit_hashes":list(frozen),
 "source_recorded_sha256_preserved":True,
 "rule":"Git eol=lf for text by default; eol=crlf for two frozen evidence JSON; pt binary"
}
port.write_bytes((json.dumps(obj,ensure_ascii=False,indent=2)+"\n").encode("utf-8"))

allowed={".py",".md",".json",".csv",".svg",".txt",".toml",".pt"}
files=[]
for path in sorted(ROOT.rglob("*")):
 if not path.is_file() or "__pycache__" in path.parts or path.name=="ARCHIVE_MANIFEST.json":continue
 if path.suffix.lower() not in allowed and path.name not in (".gitattributes",".gitignore"):continue
 raw=path.read_bytes()
 files.append({"path":path.relative_to(ROOT).as_posix(),"bytes":len(raw),"sha256":sha(raw)})
man["included_files"]=files
man["included_count"]=len(files)
man["included_bytes"]=sum(z["bytes"] for z in files)
names={z["path"] for z in files}
man["omitted_files"]=[z for z in man.get("omitted_files",[]) if z["path"] not in names]
man["omitted_count"]=len(man["omitted_files"])
man["omitted_bytes"]=sum(z["bytes"] for z in man["omitted_files"])
man["cross_platform_git_eol"]="LF normally, except two evidence files forced CRLF to preserve SHA recorded before test"
MP.write_bytes((json.dumps(man,ensure_ascii=False,indent=2)+"\n").encode("utf-8"))

errors=[z["path"] for z in files if sha((ROOT/z["path"]).read_bytes())!=z["sha256"]]
freeze_bad=[rel for rel,expected in frozen.items() if sha((ROOT/rel).read_bytes())!=expected]
print(json.dumps({"files":len(files),"bytes":man["included_bytes"],
 "normalized_text_files":n_changed,"sha_mismatches":errors,
 "frozen_test_hash_errors":freeze_bad},ensure_ascii=False),flush=True)
if errors or freeze_bad:raise RuntimeError("Cross-platform integrity audit failed")
