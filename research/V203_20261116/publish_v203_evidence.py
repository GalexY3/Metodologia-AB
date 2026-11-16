"""Binary archive publication using an isolated Git index and a branch lease.

The connector is used for prospective text registration. Large binary states
are handled by local Git; no user index, branch or HEAD is changed.
"""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import urllib.parse

B=Path(__file__).resolve().parent
REPO=B.parents[2]
EXPECTED='a73932856b9f88d27b166f3d0abc74be3dd154bb'
BRANCH='research/aldea-memory-v175-20261115'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def git(args,env=None):
    return subprocess.check_output(['git',*args],cwd=REPO,env=env,stderr=subprocess.STDOUT).decode('utf-8').strip()


def main():
    folder=B/'research/V203_20261116'
    assert not (folder/'EVIDENCE_GIT_COMMIT.json').exists()
    files=json.loads((folder/'PUBLICATION_FILES.json').read_text(encoding='utf-8'))
    original_HEAD=git(['rev-parse','HEAD'])
    gitdir=Path(git(['rev-parse','--absolute-git-dir']))
    original_index=sha(gitdir/'index')
    assert original_HEAD=='c032a32d2d8d7710a6ad5a88519b0801ea186891'
    assert original_index=='0fc87bbef0de6ced68aa787004ef36d3c7934f757f51b5d8505665bd071184a1'
    assert sha(B/'results/AB_PROGRESO_CT2_CT3.json')=='0db038a35ee828a59c96de2a9e5e071545b26213ed692a29e79ad68f26778047'
    remote=git(['remote','get-url','origin'])
    assert remote in ['https://github.com/GalexY3/Metodologia-AB.git','https://github.com/GalexY3/Metodologia-AB','git@github.com:GalexY3/Metodologia-AB.git'],'Unexpected remote; do not display credentials.'
    remote_HEAD=git(['ls-remote','origin',f'refs/heads/{BRANCH}']).split()[0]
    assert remote_HEAD==EXPECTED,(remote_HEAD,EXPECTED)
    git(['fetch','--no-tags','origin',EXPECTED])
    index=(folder/'V203_ISOLATED_GIT_INDEX').resolve()
    assert index.is_relative_to(folder.resolve()) and not index.exists()
    env=os.environ.copy();env['GIT_INDEX_FILE']=str(index)
    env['GIT_OPTIONAL_LOCKS']='0'
    git(['read-tree',EXPECTED],env)
    blobs={}
    for f in files:
        p=Path(f['local']);assert sha(p)==f['sha256'],f['remote']
        assert f['remote'].startswith('research/V203_20261116/')
        blob=git(['hash-object','-w','--no-filters',str(p)],env)
        git(['update-index','--add','--cacheinfo',f'100644,{blob},{f["remote"]}'],env)
        blobs[f['remote']]=blob
    tree=git(['write-tree'],env)
    commit=git(['commit-tree',tree,'-p',EXPECTED,'-m',
        'V203 results: exact gradients do not acquire from cold, supplied agreement improves'],env)
    subprocess.run(['git','merge-base','--is-ancestor',EXPECTED,commit],cwd=REPO,env=env,check=True)
    changed=git(['diff-tree','--no-commit-id','--name-only','-r',commit],env).splitlines()
    assert all(p.startswith('research/V203_20261116/') for p in changed)
    assert sha(gitdir/'index')==original_index and git(['rev-parse','HEAD'])==original_HEAD
    print('PUSHING',commit,'files',len(files),flush=True)
    result=git(['push',f'--force-with-lease=refs/heads/{BRANCH}:{EXPECTED}','origin',f'{commit}:refs/heads/{BRANCH}'],env)
    print(result,flush=True)
    assert git(['ls-remote','origin',f'refs/heads/{BRANCH}']).split()[0]==commit
    assert sha(gitdir/'index')==original_index and git(['rev-parse','HEAD'])==original_HEAD
    # Verify Git objects without path-length-dependent git-show operations.
    listing=subprocess.check_output(['git','ls-tree','-r','-z',commit],cwd=REPO,env=env)
    found={}
    for record in listing.split(b'\0'):
        if not record:continue
        meta,name=record.split(b'\t',1);found[name.decode('utf-8')]=meta.decode().split()[2]
    for f in files:
        assert found[f['remote']]==blobs[f['remote']]
        raw=subprocess.check_output(['git','cat-file','blob',blobs[f['remote']]],cwd=REPO,env=env)
        assert hashlib.sha256(raw).hexdigest()==f['sha256']
    receipt=dict(commit=commit,tree=tree,parent=EXPECTED,branch=BRANCH,
        pushed=True,git_blobs_verified=len(files),original_HEAD_preserved=True,original_index_preserved=True,
        HTTP_archive_verification_pending=True)
    (folder/'EVIDENCE_GIT_COMMIT.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    print(json.dumps(receipt,indent=2),flush=True)


if __name__=='__main__':main()
