"""Verify registered small files over HTTP and pinned binary parents locally."""
from pathlib import Path
import hashlib
import json
from urllib.request import urlopen

B=Path(__file__).resolve().parent
COMMIT='2b2adb035e0826dff0c7a75981bea290c3e3a339'
TREE='941ddc241edca4e3c19263aec999f49f6f9f7c19'
assert not (B/'results/V193_FROZEN_PEER').exists()
registration=json.loads((B/'results/V193_SOURCE_PREREG.json').read_text(encoding='utf-8'))
checks=[]
for path in list(registration['source_sha256'])+['results/V193_SOURCE_PREREG.json']:
    local=(B/path).read_bytes();sha=hashlib.sha256(local).hexdigest()
    if path in registration['source_sha256']:assert sha==registration['source_sha256'][path]
    binary_parent=path.endswith('.pt')
    if not binary_parent:
        url=f'https://raw.githubusercontent.com/GalexY3/Metodologia-AB/{COMMIT}/proyectos/coordinacion-funcional-intergeneracional/v19_voluntary_exchange/{path}'
        with urlopen(url,timeout=45) as r:remote=r.read()
        assert remote==local,path
    checks.append(dict(path=path,bytes=len(local),sha256=sha,
                       remote_HTTP_byte_identical=not binary_parent,binary_parent_hash_locally_verified=binary_parent))
receipt=dict(registration,remote_commit=COMMIT,remote_tree=TREE,before_training=True)
(B/'results/V193_REMOTE_PREREG_VERIFIED.json').write_text(json.dumps(dict(commit=COMMIT,checks=checks,before_training=True),indent=2),encoding='utf-8')
(B/'results/V193_PREREG_RECEIPT.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print(json.dumps(dict(commit=COMMIT,HTTP_verified=sum(not c['binary_parent_hash_locally_verified'] for c in checks),
                      binary_parents_hash_verified=sum(c['binary_parent_hash_locally_verified'] for c in checks),before_training=True)),flush=True)
