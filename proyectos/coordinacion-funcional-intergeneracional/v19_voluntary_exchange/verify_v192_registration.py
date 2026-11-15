"""Read actual registered bytes over HTTPS before any V192 training."""
from pathlib import Path
import hashlib
import json
from urllib.request import urlopen

B=Path(__file__).resolve().parent
COMMIT='babedeedbf604d9a05f134f80a1eb82383bcd402'
TREE='f6cd047ab9c7e07ee7a6d6cfcc800fd434bfc1bf'
assert not (B/'results/V192_DUAL_NEURAL_LEARNING').exists()
registration=json.loads((B/'results/V192_SOURCE_PREREG.json').read_text(encoding='utf-8'))
checks=[]
for path in list(registration['source_sha256'])+['results/V192_SOURCE_PREREG.json']:
    local=(B/path).read_bytes()
    url=f'https://raw.githubusercontent.com/GalexY3/Metodologia-AB/{COMMIT}/proyectos/coordinacion-funcional-intergeneracional/v19_voluntary_exchange/{path}'
    with urlopen(url,timeout=45) as r:remote=r.read()
    assert remote==local,path
    checks.append(dict(path=path,bytes=len(remote),sha256=hashlib.sha256(remote).hexdigest(),identical=True))
receipt=dict(registration,remote_commit=COMMIT,remote_tree=TREE,before_training=True)
(B/'results/V192_REMOTE_PREREG_VERIFIED.json').write_text(json.dumps(dict(commit=COMMIT,checks=checks,before_training=True),indent=2),encoding='utf-8')
(B/'results/V192_PREREG_RECEIPT.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print(json.dumps(dict(commit=COMMIT,verified_files=len(checks),before_training=True)),flush=True)
