"""Fetch actual remote bytes and issue a one-shot before-training receipt."""
from pathlib import Path
import argparse
import hashlib
import json
from datetime import datetime, timezone
from urllib.request import urlopen

B = Path(__file__).resolve().parent


def main(commit, tree):
    assert not (B / 'results/V195_WITHDRAW_COUNTERFACTUAL').exists()
    output = B / 'results/V195_WITHDRAW_PREREG_RECEIPT.json'
    assert not output.exists()
    registration = json.loads((B / 'results/V195_WITHDRAW_SOURCE_PREREG.json').read_text(encoding='utf-8'))
    checks = []
    for path in list(registration['source_sha256']) + ['results/V195_WITHDRAW_SOURCE_PREREG.json']:
        local = (B/path).read_bytes()
        if path in registration['source_sha256']:
            assert hashlib.sha256(local).hexdigest() == registration['source_sha256'][path]
        url = f'https://raw.githubusercontent.com/GalexY3/Metodologia-AB/{commit}/proyectos/coordinacion-funcional-intergeneracional/v19_voluntary_exchange/{path}'
        with urlopen(url, timeout=45) as r:
            remote = r.read()
        assert remote == local, path
        checks.append(dict(path=path, bytes=len(remote), sha256=hashlib.sha256(remote).hexdigest(), identical=True))
    for path, sha in registration['binary_parent_sha256'].items():
        assert hashlib.sha256((B/path).read_bytes()).hexdigest() == sha, path
    receipt = dict(registration, remote_commit=commit, remote_tree=tree, before_training=True,
                   verified_UTC=datetime.now(timezone.utc).isoformat())
    (B / 'results/V195_WITHDRAW_REMOTE_PREREG_VERIFIED.json').write_text(json.dumps(dict(
        commit=commit, checks=checks, before_training=True), indent=2), encoding='utf-8')
    output.write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    print(json.dumps(dict(commit=commit, HTTP_files_verified=len(checks), before_training=True)), flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('commit')
    p.add_argument('tree')
    a = p.parse_args()
    main(a.commit, a.tree)
