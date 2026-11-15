"""Independent final metrics and byte-exact frozen-parent comparisons."""
from pathlib import Path
import argparse
import json
import torch
from research_resource_limits import apply_limits
from audit_v192_numpy import audit

B=Path(__file__).resolve().parent


def main(include194):
    audits=[];frozen_checks=[];parity=[]
    for arm,role in [('FREEZE_A',0),('FREEZE_B',1)]:
        root=B/f'results/V193_FROZEN_PEER/{arm}'
        audits.append(audit('V193_'+arm,60000,root/'checkpoint_60000.pt'))
        final=torch.load(root/'checkpoint_60000.pt',map_location='cpu',weights_only=False)
        for s,seed in enumerate(range(192115,192119)):
            parent=torch.load(B/f'results/V192_DUAL_NEURAL_LEARNING/PRIVATE_FULL/first_memorization_s{seed}.pt',map_location='cpu',weights_only=False)
            for key,value in parent['models'][role].items():
                same=torch.equal(value,final['models'][role][key][s:s+1])
                frozen_checks.append(dict(arm=arm,seed=seed,parameter=key,bit_identical=same))
                assert same,(arm,seed,key)
        comparisons=json.loads((root/'CHECKPOINT_PARITY_WITH_JOINT.json').read_text(encoding='utf-8'))
        parity.extend([dict(arm=arm,**r) for r in comparisons])
    if include194:
        assert (B/'results/V194_ORACLE_BANDIT/SUMMARY.json').exists()
        audits.append(audit('V194_ORACLE_BANDIT_IS',60000,B/'results/V194_ORACLE_BANDIT/checkpoint_60000.pt'))
    failures=[c for a in audits for c in a['checks'] if not c['passed']]
    result=dict(audits=audits,checks=sum(len(a['checks']) for a in audits),failures=failures,
        max_error=max(c['error'] for a in audits for c in a['checks']),
        frozen_parameter_checks=frozen_checks,all_frozen_parameters_match_their_parent_cut=True,
        checkpoint_parity=parity,all_active_saved_models_match_joint_bitwise=all(r['model_all_bits_equal'] for r in parity),
        all_active_saved_optimizers_match_joint_bitwise=all(r['optimizer_all_bits_equal'] for r in parity),
        all_saved_rng_states_match_joint=True,independent_new_histories=0)
    assert all(r['RNG_states_identical'] for r in parity)
    path=B/('results/V193_V194_NUMPY_FINAL_AUDIT.json' if include194 else 'results/V193_NUMPY_FINAL_AUDIT.json')
    assert not path.exists();path.write_text(json.dumps(result,indent=2),encoding='utf-8')
    assert not failures,failures
    print(json.dumps({k:v for k,v in result.items() if k not in ['audits','frozen_parameter_checks','checkpoint_parity']}),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--include194',action='store_true');args=p.parse_args()
    print('LIMITS',apply_limits(2),flush=True);torch.set_num_threads(2);main(args.include194)
