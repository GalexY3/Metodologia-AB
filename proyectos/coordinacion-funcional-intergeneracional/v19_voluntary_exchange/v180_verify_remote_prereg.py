"""Check exact Git object bytes and recorded timing without changing the index."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[2]
PREFIX=ROOT.relative_to(REPO).as_posix()+'/'


def git(*args):return subprocess.check_output(['git',*args],cwd=REPO)


def main():
    rows=[]
    for label,folder,source,protocol in (
        ('V175','v175_learned_memory','v175_memory_evolution.py','PREREG_V175_LEARNED_ECOLOGICAL_MEMORY.md'),
        ('V176','v176_frozen_memory','v176_frozen_memory_causal.py','PREREG_V176_FROZEN_MEMORY_CAUSAL.md'),
        ('V177','v177_gate_game','v177_cognitive_gate_game.py','PREREG_V177_COGNITIVE_GATE_GAME.md'),
        ('V178','v178_private_affine_M5','v178_private_affine_rival.py','PREREG_V178_PRIVATE_AFFINE_RIVAL.md'),
        ('V180','v180_open_policy_space','v180_open_policy_space.py','PREREG_V180_OPEN_POLICY_SPACE.md')):
        path=ROOT/f'results/{folder}/FREEZE.json';freeze=json.loads(path.read_text());commit=freeze['prereg_commit']
        date=int(git('show','-s','--format=%ct',commit))
        assert date<=path.stat().st_mtime,(label,'commit later than local freeze')
        for name,key in ((source,'source_sha256'),(protocol,'protocol_sha256')):
            content=git('show',commit+':'+PREFIX+name)
            digest=hashlib.sha256(content).hexdigest()
            assert digest==freeze[key] and content==(ROOT/name).read_bytes(),(label,name,digest)
            rows.append(dict(study=label,commit=commit,path=name,sha256=digest,remote_bytes_match_local_and_frozen=True,
                             commit_epoch=date,local_freeze_mtime=path.stat().st_mtime))
    commit='2766f863cda02bff7cd67eebeb8a682de358065e'
    path=ROOT/'results/v180_open_policy_space/SELECTION.json'
    assert git('show',commit+':'+PREFIX+path.relative_to(ROOT).as_posix())==path.read_bytes()
    first_validation=min(p.stat().st_mtime for p in (ROOT/'results/v180_open_policy_space/validation').glob('*.npz'))
    assert int(git('show','-s','--format=%ct',commit))<=first_validation
    helper=git('show','e5dd0826c29f97d246d80d5a8e8f16072e56552b:'+PREFIX+'research_resource_limits.py')
    assert helper==(ROOT/'research_resource_limits.py').read_bytes()
    out=ROOT/'research/V175_V180_20261115/REMOTE_PREREG_BYTE_AUDIT.json';assert not out.exists()
    out.write_text(json.dumps(dict(checks=rows,selection_commit=commit,selection_exact=True,
          earliest_saved_validation_epoch=first_validation,resource_helper_exact=True,
          verification_type='Git object bytes and recorded temporal ordering; not scientific peer review.'),indent=2),encoding='utf8')
    print('REMOTE_PREREG_VERIFIED',len(rows),'source/protocol byte checks plus selection/helper',flush=True)


if __name__=='__main__':main()
