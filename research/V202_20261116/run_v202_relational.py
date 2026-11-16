"""Execute only the registered V202 program; never restart existing output."""
from pathlib import Path
import hashlib
import json
import platform
import time
import importlib.metadata
from research_resource_limits import apply_limits

B=Path(__file__).resolve().parent


def main():
    registration=json.loads((B/'V202_REGISTRATION_RECEIPT.json').read_text(encoding='utf-8'))
    assert registration['remote_bytes_verified_before_training']
    for name,expected in registration['source_sha256'].items():
        assert hashlib.sha256((B/name).read_bytes()).hexdigest()==expected,name
    from v202_relational_learning import run_world,ARMS
    from v202_exact_evaluation import evaluate,deviation_audit
    from analyze_v202_relational import analyze
    folder=B/'results/V202_RELATIONAL_ACQUISITION';folder.mkdir(exist_ok=False)
    freeze=dict(registration=registration,python=platform.python_version(),
        packages={p:importlib.metadata.version(p) for p in ['numpy','numba']},
        worlds=32,groups=8,steps=60000,arms=list(ARMS),objective='Own realized return only',
        roles_fixed=True,capital_fixed=True,parameters_shared=False,transfers_binding=False)
    (folder/'FREEZE.json').write_text(json.dumps(freeze,indent=2),encoding='utf-8')
    start=time.perf_counter()
    for world in range(32):
        for arm in ARMS:
            trained=run_world(world,arm,destination=folder)
            groups=[]
            public='_PUBLIC_' in arm
            for g in range(8):
                p=trained['probabilities'][g];loss=trained['losses'][g]
                groups.append(dict(group=g,losses=loss.tolist(),
                    evaluation=evaluate(p,loss,public),deviations=deviation_audit(p,loss,public)))
            row=dict(world=world,arm=arm,root_seed=trained['root_seed'],
                training_counts=trained['counts'].tolist(),training_history=trained['history'],
                ongoing_uncompleted_PG_relationships=trained['ongoing_uncompleted_PG_relationships'],
                uncompleted_PG_steps_not_used_for_update=trained['uncompleted_PG_steps_not_used_for_update'],
                native_probabilities=trained['probabilities'].tolist(),groups=groups)
            dest=folder/f'{arm}_world{world:02}.json';assert not dest.exists()
            dest.write_text(json.dumps(row,indent=2),encoding='utf-8')
            print('V202_WORLD',world,arm,'functional',sum(x['evaluation']['functional'] for x in groups),
                  'GOOD',sum(x['evaluation']['discounted_GOOD_joint_rate'] for x in groups)/8,
                  'elapsed',round(time.perf_counter()-start,1),flush=True)
    result=analyze(folder)
    print('V202_DONE',json.dumps(result['primary']),flush=True)


if __name__=='__main__':
    print('LIMITS',apply_limits(2),flush=True)
    main()
