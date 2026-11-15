"""Publish explicit evidence with a separate index; leave user HEAD untouched."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
from urllib.request import urlopen
from research_resource_limits import apply_limits

B = Path(__file__).resolve().parent
REPO = B.parents[2]
OUT = B/'research/V199_20261115'
PARENT = 'a0113021889e89b729e4513adafee1081cde48b2'
BRANCH = 'research/aldea-memory-v175-20261115'
HEAD = 'c032a32d2d8d7710a6ad5a88519b0801ea186891'
INDEX_SHA = '0fc87bbef0de6ced68aa787004ef36d3c7934f757f51b5d8505665bd071184a1'


def git(*args, env=None, binary=False):
    p = subprocess.run(['git', *args], cwd=REPO, env=env, capture_output=True)
    assert p.returncode == 0, p.stderr.decode('utf-8', errors='replace')
    return p.stdout if binary else p.stdout.decode('utf-8').strip()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert not (OUT/'PUBLICATION_RECEIPT.json').exists()
    assert git('rev-parse', 'HEAD') == HEAD
    index = Path(git('rev-parse', '--git-path', 'index'))
    if not index.is_absolute():
        index = REPO/index
    assert sha(index) == INDEX_SHA
    assert 'GalexY3/Metodologia-AB' in git('remote', 'get-url', 'origin')
    git('-c', 'pack.threads=2', 'fetch', '--no-tags', 'origin', 'refs/heads/'+BRANCH)
    assert git('rev-parse', 'FETCH_HEAD') == PARENT, 'Inspect remote changes before retrying.'
    isolated = OUT/'publication.index'
    assert not isolated.exists()
    env = os.environ.copy(); env['GIT_INDEX_FILE'] = str(isolated)
    git('read-tree', PARENT, env=env)
    prefix = B.relative_to(REPO)
    paths = json.loads((OUT/'PUBLICATION_FILES.json').read_text(encoding='utf-8'))
    expected = {}
    for relative in paths:
        path = B/relative
        assert path.resolve().is_relative_to(B.resolve()) and path.is_file()
        repo_path = (prefix/relative).as_posix()
        blob = git('hash-object', '-w', '--no-filters', '--', repo_path)
        git('update-index', '--add', '--cacheinfo', '100644', blob, repo_path, env=env)
        expected[repo_path] = dict(sha256=sha(path), blob=blob)
    tree = git('write-tree', env=env)
    message = OUT/'COMMIT_MESSAGE.txt'
    message.write_text('Publish V199 private learners and posthoc incentive audit: primary hypotheses fail, cooperation and adaptation separated; CT2 unchanged\n', encoding='utf-8')
    commit = git('commit-tree', tree, '-p', PARENT, '-F', str(message), env=env)
    git('merge-base', '--is-ancestor', PARENT, commit)
    (OUT/'PUSH_STATE.json').write_text(json.dumps(dict(commit=commit, parent=PARENT, tree=tree, files=len(paths)), indent=2), encoding='utf-8')
    print('PUBLISHING', commit, 'files', len(paths), flush=True)
    git('-c', 'pack.threads=2', 'push', '--force-with-lease=refs/heads/'+BRANCH+':'+PARENT,
        'origin', commit+':refs/heads/'+BRANCH)
    assert git('ls-remote', 'origin', 'refs/heads/'+BRANCH).split()[0] == commit
    entries = {}
    for item in git('ls-tree', '-rz', '--full-tree', commit, binary=True).split(b'\0'):
        if item:
            meta, path = item.split(b'\t', 1)
            entries[path.decode('utf-8')] = meta.split()[2].decode()
    for path, item in expected.items():
        assert entries[path] == item['blob']
        assert hashlib.sha256(git('cat-file', 'blob', item['blob'], binary=True)).hexdigest() == item['sha256']
    archives = []
    for item in json.loads((OUT/'ARCHIVE_MANIFEST.json').read_text(encoding='utf-8'))['shards']:
        path = (prefix/'research/V199_20261115'/item['archive']).as_posix()
        url = f'https://raw.githubusercontent.com/GalexY3/Metodologia-AB/{commit}/{path}'
        h, count = hashlib.sha256(), 0
        with urlopen(url, timeout=45) as response:
            while chunk := response.read(4*1024*1024):
                h.update(chunk); count += len(chunk)
        assert count == item['bytes'] and h.hexdigest() == item['sha256']
        archives.append(dict(archive=item['archive'], bytes=count, sha256=h.hexdigest(), actual_HTTP_verified=True))
        print('VERIFIED_REMOTE_ARCHIVE', item['archive'], count, flush=True)
    assert git('rev-parse', 'HEAD') == HEAD and sha(index) == INDEX_SHA
    receipt = dict(commit=commit, parent=PARENT, tree=tree, branch=BRANCH, files=len(paths),
        commit_url='https://github.com/GalexY3/Metodologia-AB/commit/'+commit,
        local_HEAD_unchanged=True, user_index_SHA256=INDEX_SHA,
        all_direct_git_blobs_match_raw_local_bytes=True, archives=archives,
        all_actual_remote_archives_HTTP_verified=True)
    (OUT/'PUBLICATION_RECEIPT.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    isolated.unlink()
    print(json.dumps(receipt), flush=True)


if __name__ == '__main__':
    print('LIMITS', apply_limits(2), flush=True)
    main()
