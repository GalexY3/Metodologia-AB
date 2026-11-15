"""Verify actual registered bytes over HTTPS before starting V190."""
from pathlib import Path
import hashlib
import json
from urllib.request import urlopen

B = Path(__file__).resolve().parent
COMMIT = 'c918d5b326afb6320d7339b94d24c5f21511fba8'
TREE = '82d62155330ed1f0cda5e7b69b76e81ab7370ced'
assert not (B/'results/V190_LOSSY_MEMORIZATION').exists()
registration = json.loads((B/'results/V190_SOURCE_PREREG.json').read_text(encoding='utf-8'))
receipt = dict(registration, remote_commit=COMMIT, remote_tree=TREE, before_training=True)
checks = []
for path in list(registration['source_sha256']) + ['results/V190_SOURCE_PREREG.json']:
    local = (B/path).read_bytes()
    url = f'https://raw.githubusercontent.com/GalexY3/Metodologia-AB/{COMMIT}/proyectos/coordinacion-funcional-intergeneracional/v19_voluntary_exchange/{path}'
    with urlopen(url, timeout=45) as response:
        remote = response.read()
    assert remote == local, path
    checks.append(dict(path=path, bytes=len(local), sha256=hashlib.sha256(remote).hexdigest(), identical=True))
(B/'results/V190_REMOTE_PREREG_VERIFIED.json').write_text(json.dumps(dict(commit=COMMIT, checks=checks, before_training=True), indent=2), encoding='utf-8')
(B/'results/V190_PREREG_RECEIPT.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
print(json.dumps(dict(commit=COMMIT, files_verified=len(checks), before_training=True)))
