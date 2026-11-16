"""Post hoc intervention: marginalize only the CURRENT opponent advantage.

Keep the same private game, own ordinary policy gradient and past joint
advantages. No new learner or learning-success claim is introduced.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
from v205_two_stage_game import sigmoid,trajectories,aa_field,best_responses_p

B=Path(__file__).resolve().parent


def main():
    rng=np.random.Generator(np.random.Philox(2051930));rows=[]
    for case in range(12):
        theta=rng.normal(0,.8,(2,3));p=sigmoid(theta)
        gamma=[.5,.9,.99][case%3];c=[0.,.1,.4][case%3]
        joint=list(trajectories(p,gamma,'joint',coupling=c))
        marginal=list(trajectories(p,gamma,'marginal',coupling=c))
        hybrid=np.zeros((2,3))
        for a,b in zip(joint,marginal):
            assert np.array_equal(a['actions'],b['actions']) and abs(a['mass']-b['mass'])<1e-15
            for i in range(2):
                for t in range(2):
                    past=sum(gamma**(t-k)*a['advantages'][i,k] for k in range(t))
                    hybrid[i]+=a['mass']*gamma**(t+1)*past*b['advantages'][1-i,t]*a['scores'][i,t]
        _,own_joint,extra_joint=aa_field(theta,gamma,1.,'eq8','joint',coupling=c)
        _,own_marginal,extra_marginal=aa_field(theta,gamma,1.,'eq8','marginal',coupling=c)
        rows.append(dict(case=case,theta=theta.tolist(),gamma=gamma,coupling=c,
            actual_non_equilibrium_regret=best_responses_p(p,gamma,c)['max_gain'],
            own_gradient_difference=float(np.max(np.abs(own_joint-own_marginal))),
            joint_AA_correction_norm=float(np.linalg.norm(extra_joint)),
            opponent_only_marginal_correction_norm=float(np.linalg.norm(hybrid)),
            all_marginal_correction_norm=float(np.linalg.norm(extra_marginal))))
    result=dict(study='V205',analysis='POST_HOC_CAUSAL_OPERATOR_INTERVENTION',
        registered_primary_outcome_unchanged=True,debug_seed=2051930,profiles=12,
        maximum_own_gradient_discrepancy=max(r['own_gradient_difference'] for r in rows),
        maximum_hybrid_marginal_correction_norm=max(r['opponent_only_marginal_correction_norm'] for r in rows),
        minimum_joint_correction_norm=min(r['joint_AA_correction_norm'] for r in rows),
        operator_changes_not_an_unbiased_variance_reduction=True,
        general_proof_requires_independent_current_action_sampling_and_detached_advantages=True,
        external_scientific_confirmation=False,original_priority_unestablished=True,rows=rows,
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    out=B/'results/V205_POSTHOC_MARGINALIZATION.json';assert not out.exists()
    out.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2))


if __name__=='__main__':main()
