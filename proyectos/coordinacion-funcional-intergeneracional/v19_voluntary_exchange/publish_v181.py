"""Publish explicit V181 artifacts using a separate index and exact blob bytes."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[2]
PREFIX=ROOT.relative_to(REPO).as_posix()+'/'
OUT=ROOT/'research/V181_20261115'
EXPECTED='d0962768e2cdb50cedc0476e05481b1a30896809'
REF='refs/heads/research/aldea-memory-v175-20261115'
FILES=['v181_matched_budget.py','close_v181.py','publish_v181.py','PREREG_V181_MATCHED_BUDGET_AND_BIAS_RESET.md',
 'INICIO_INVESTIGACION_CIENTIFICA.md','handoff_codex/ESTADO_20261115_V181.md','docs/TFM_MANUSCRITO_TRABAJO_V181.md',
 'results/V181_PRE_RUN_AUDIT.json','results/V181_FINAL_AUDIT.json','results/V181_REVIEWED_STATISTICS.json',
 'results/TFM_V181_BUILD.json','results/FIG_V181_MATCHED_BUDGET.png','results/INFORME_V181_PRESUPUESTO_Y_REINICIO_20261115.md',
 'results/v181_matched_budget/FREEZE.json','results/v181_matched_budget/SUMMARY.json',
 'research/V181_20261115/EVIDENCE.zip','research/V181_20261115/SHA256.json','research/V181_20261115/PACKAGE_RECEIPT.json',
 'research/V181_20261115/LEDGER_A_J.json',
 'research/V175_V180_20261115/PUBLICATION_RECEIPT.json',
 'research/V175_V180_20261115/REMOTE_DELIVERY_FINAL.json',
 'research/V175_V180_20261115/PACKAGING_REVISION_SCIENTIFIC_PARITY.json']


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def git(*args,env=None):return subprocess.check_output(['git','-c','pack.threads=2',*args],cwd=REPO,env=env).decode('utf8').strip()


def main():
    head=git('rev-parse','HEAD');assert head=='c032a32d2d8d7710a6ad5a88519b0801ea186891'
    branch=git('branch','--show-current');idx=Path(git('rev-parse','--git-path','index'))
    if not idx.is_absolute():idx=REPO/idx
    initial_index=sha(idx)
    assert git('ls-remote','origin',REF).split()[0]==EXPECTED
    index=OUT/'git_publish.index';assert not index.exists()
    receipt=OUT/'PUBLICATION_RECEIPT.json';assert not receipt.exists()
    metadata=json.loads((OUT/'PACKAGE_RECEIPT.json').read_text())
    assert sha(OUT/'EVIDENCE.zip')==metadata['sha256']
    env=os.environ.copy();env['GIT_INDEX_FILE']=str(index)
    git('read-tree',EXPECTED,env=env)
    for name in FILES:
        p=ROOT/name;assert p.is_file(),name
        blob=git('hash-object','-w','--no-filters','--',str(p),env=env)
        git('update-index','--add','--cacheinfo','100644',blob,PREFIX+name,env=env)
    tree=git('write-tree',env=env)
    message=OUT/'git_publish_message.txt'
    message.write_text('research: validate history effect against matched budget and bias reset\n\n16new continuations,8paired histories,all6000generations total.\nRetain prior failures and the one failed warm history. Curriculum is imposed;\nCT2historical61,N2=N3=0; novelty and external confirmation remain pending.\n',encoding='utf8')
    commit=git('commit-tree',tree,'-p',EXPECTED,'-F',str(message),env=env)
    git('merge-base','--is-ancestor',EXPECTED,commit,env=env)
    git('push','--porcelain','origin',commit+':'+REF,env=env)
    observed=git('ls-remote','origin',REF).split()[0];assert observed==commit
    assert sha(idx)==initial_index and git('rev-parse','HEAD')==head and git('branch','--show-current')==branch
    for name in FILES:
        remote=subprocess.check_output(['git','cat-file','blob',commit+':'+PREFIX+name],cwd=REPO)
        assert remote==(ROOT/name).read_bytes(),name
    result=dict(commit=commit,tree=tree,parent=EXPECTED,remote_head_observed=observed,
       commit_url='https://github.com/GalexY3/Metodologia-AB/commit/'+commit,
       local_index_sha256=initial_index,original_index_preserved=True,local_head_preserved=head,
       local_branch_preserved=branch,direct_files_byte_verified=len(FILES),archive_sha256=metadata['sha256'],
       archive_bytes=metadata['bytes'],human_raw_data_uploaded=False,goal_active=True)
    receipt.write_bytes((json.dumps(result,indent=2)+'\n').encode('utf8'))
    print('V181_PUBLISHED',json.dumps(result),flush=True)


if __name__=='__main__':main()
