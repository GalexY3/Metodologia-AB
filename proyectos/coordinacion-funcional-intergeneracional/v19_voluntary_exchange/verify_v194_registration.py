"""Verify the frozen oracle-bandit control before scientific training."""
from pathlib import Path
import hashlib
import json
from urllib.request import urlopen

B=Path(__file__).resolve().parent
COMMIT='9b0d9ffd13d7ad353fb06fe45357c7279c988329'
TREE='5163c29ed346d8ba1c79dfc199cf593f96442610'
assert not (B/'results/V194_ORACLE_BANDIT').exists()
registration=json.loads((B/'results/V194_SOURCE_PREREG.json').read_text(encoding='utf-8'))
checks=[]
for path in list(registration['source_sha256'])+['results/V194_SOURCE_PREREG.json']:
    local=(B/path).read_bytes()
    url=f'https://raw.githubusercontent.com/GalexY3/Metodologia-AB/{COMMIT}/proyectos/coordinacion-funcional-intergeneracional/v19_voluntary_exchange/{path}'
    with urlopen(url,timeout=45) as r:remote=r.read()
    assert local==remote,path
    checks.append(dict(path=path,bytes=len(remote),sha256=hashlib.sha256(remote).hexdigest(),identical=True))
receipt=dict(registration,remote_commit=COMMIT,remote_tree=TREE,before_training=True)
(B/'results/V194_REMOTE_PREREG_VERIFIED.json').write_text(json.dumps(dict(commit=COMMIT,checks=checks,before_training=True),indent=2),encoding='utf-8')
(B/'results/V194_PREREG_RECEIPT.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print(json.dumps(dict(commit=COMMIT,HTTP_files_verified=len(checks),before_training=True)),flush=True)
