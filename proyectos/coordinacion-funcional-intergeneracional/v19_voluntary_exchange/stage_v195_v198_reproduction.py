"""Copy only frozen dependencies and parents into a fresh reproduction folder."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil

B = Path(__file__).resolve().parent


def main(experiment, destination):
    root = Path(destination).resolve()
    assert root.is_absolute() and not root.exists()
    assert not root.is_relative_to(B.resolve())
    stem = 'V195_WITHDRAW' if experiment == '195' else 'V198_EXPECTED_DRIFT'
    receipt_path = f'results/{stem}_PREREG_RECEIPT.json'
    receipt = json.loads((B/receipt_path).read_text(encoding='utf-8'))
    expected = dict(receipt['source_sha256'], **receipt['binary_parent_sha256'])
    extras = [receipt_path, f'results/{stem}_SOURCE_PREREG.json']
    if experiment == '195':
        extras += ['audit_v195_withdraw_numpy.py', 'audit_v192_numpy.py']
    else:
        extras += ['audit_v198_voting_numpy.py']
    for path in extras:
        expected[path] = hashlib.sha256((B/path).read_bytes()).hexdigest()
    root.mkdir()
    for path, sha in expected.items():
        source, target = B/path, root/path
        assert hashlib.sha256(source.read_bytes()).hexdigest() == sha, path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        assert hashlib.sha256(target.read_bytes()).hexdigest() == sha, path
    (root/'STAGED_REPRODUCTION.json').write_text(json.dumps(dict(experiment=experiment,
        original_commit=receipt['remote_commit'], files=expected, new_training_executed=False), indent=2), encoding='utf-8')
    print(json.dumps(dict(destination=str(root), files=len(expected), new_training_executed=False)), flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('experiment', choices=['195', '198'])
    p.add_argument('destination')
    a = p.parse_args()
    main(a.experiment, a.destination)
