"""Publish an explicit evidence list using an isolated index; never stage the user tree."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import urllib.request

BASE=Path(__file__).resolve().parent
REPO=BASE.parents[2]
OUT=BASE/'research/V182_V186_20261115'
BRANCH='research/aldea-memory-v175-20261115'
PARENT='4164292c0d32adcb58c2d9ce4e944427578b8da2'
EXPECTED_HEAD='c032a32d2d8d7710a6ad5a88519b0801ea186891'
EXPECTED_INDEX='0fc87bbef0de6ced68aa787004ef36d3c7934f757f51b5d8505665bd071184a1'


def git(*args,env=None):
    result=subprocess.run(['git',*args],cwd=REPO,env=env,capture_output=True,text=True,encoding='utf-8')
    if result.returncode:
        raise RuntimeError(f'Git failed {args[0]}: {result.stderr}')
    return result.stdout.strip()


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert not (OUT/'PUBLICATION_RECEIPT.json').exists()
    assert git('rev-parse','HEAD')==EXPECTED_HEAD
    user_index=Path(git('rev-parse','--git-path','index'))
    if not user_index.is_absolute():user_index=REPO/user_index
    assert digest(user_index)==EXPECTED_INDEX
    remote=git('remote','get-url','origin')
    assert 'GalexY3/Metodologia-AB' in remote,remote
    git('-c','pack.threads=2','fetch','--no-tags','origin','refs/heads/'+BRANCH)
    assert git('rev-parse','FETCH_HEAD')==PARENT
    isolated=OUT/'publication.index'
    assert not isolated.exists()
    env=os.environ.copy();env['GIT_INDEX_FILE']=str(isolated)
    git('read-tree',PARENT,env=env)
    relative=BASE.relative_to(REPO)
    files=json.loads((OUT/'PUBLICATION_FILES.json').read_text(encoding='utf-8'))
    expected={}
    for file in files:
        path=BASE/file
        assert path.resolve().is_relative_to(BASE.resolve()) and path.is_file(),path
        repo_path=(relative/file).as_posix()
        blob=git('hash-object','-w','--no-filters','--',repo_path)
        git('update-index','--add','--cacheinfo','100644',blob,repo_path,env=env)
        expected[repo_path]=digest(path)
    tree=git('write-tree',env=env)
    message=OUT/'COMMIT_MESSAGE.txt'
    message.write_text('Publish V182–V186: original-code audit, retained timing negative, and causal communication bottleneck; no CT2 increase\n',encoding='utf-8')
    commit=git('commit-tree',tree,'-p',PARENT,'-F',str(message),env=env)
    assert git('merge-base','--is-ancestor',PARENT,commit)==''
    print('PUBLISHING',commit,'files',len(files),flush=True)
    git('-c','pack.threads=2','push','origin',commit+':refs/heads/'+BRANCH)
    assert git('rev-parse','HEAD')==EXPECTED_HEAD and digest(user_index)==EXPECTED_INDEX
    for path,sha in expected.items():
        data=subprocess.check_output(['git','show',commit+':'+path],cwd=REPO)
        assert hashlib.sha256(data).hexdigest()==sha,path
    manifest=json.loads((OUT/'ARCHIVE_MANIFEST.json').read_text(encoding='utf-8'))
    archive_path=(relative/'research/V182_V186_20261115/EVIDENCE.zip').as_posix()
    url='https://raw.githubusercontent.com/GalexY3/Metodologia-AB/'+commit+'/'+archive_path
    h=hashlib.sha256();count=0
    with urllib.request.urlopen(url,timeout=90) as response:
        while block:=response.read(4*1024*1024):h.update(block);count+=len(block)
    assert count==manifest['bytes'] and h.hexdigest()==manifest['sha256']
    receipt=dict(commit=commit,parent=PARENT,tree=tree,branch=BRANCH,files=len(files),
                 commit_url='https://github.com/GalexY3/Metodologia-AB/commit/'+commit,
                 local_HEAD_unchanged=True,user_index_SHA256=EXPECTED_INDEX,
                 all_direct_git_blobs_match_raw_local_bytes=True,
                 actual_remote_archive_HTTP_verified=True,archive_bytes=count,archive_sha256=h.hexdigest())
    (OUT/'PUBLICATION_RECEIPT.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    isolated.unlink()  # one verified task-owned index file; not the user index
    print(json.dumps(receipt),flush=True)


if __name__=='__main__':main()
