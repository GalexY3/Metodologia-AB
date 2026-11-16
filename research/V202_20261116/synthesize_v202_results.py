"""Post-run scientific synthesis, keeps the registered analysis unchanged."""
from pathlib import Path
import json
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from v202_relational_learning import ARMS

B=Path(__file__).resolve().parent


def main():
    folder=B/'results/V202_RELATIONAL_ACQUISITION'
    out=B/'results/V202_SCIENTIFIC_SYNTHESIS.json';assert not out.exists()
    analysis=json.loads((folder/'ANALYSIS.json').read_text(encoding='utf-8'))
    initial=json.loads((B/'results/V202_POSTHOC_INITIAL_AND_GRADIENT.json').read_text(encoding='utf-8'))
    grouped={a:[] for a in ARMS};category={a:dict(ordinary_L1=[],ordinary_L7=[],critical_L7=[]) for a in ARMS}
    for arm in ARMS:
        for world in range(32):
            record=json.loads((folder/f'{arm}_world{world:02}.json').read_text(encoding='utf-8'))
            for g in record['groups']:
                grouped[arm].append(g)
                for i,loss in enumerate(g['losses']):
                    key='critical_L7' if i==3 else ('ordinary_L1' if loss==1 else 'ordinary_L7')
                    category[arm][key].append(g['evaluation']['gain_over_autarky'][i])
    result={}
    for arm in ARMS:
        groups=grouped[arm]
        result[arm]=dict(functional_groups=sum(g['evaluation']['functional'] for g in groups),groups=256,
            terminal=analysis['arms'][arm],initial=initial['initial_policy_summary'][arm],
            mean_private_gain_by_category={k:float(np.mean(v)) for k,v in category[arm].items()},
            functional_and_no_feasible_deviation_above_point01=sum(g['evaluation']['functional'] and
                g['deviations']['max_normalized_gain']<=.01 for g in groups),
            deviation_audit_scope=groups[0]['deviations']['scope'])
    warm=result['PG_PUBLIC_WARM']
    continuous_change=warm['terminal']['mean_GOOD_rate']-warm['initial']['initial_GOOD_rate']
    fig,ax=plt.subplots(1,2,figsize=(12.8,4.6),constrained_layout=True)
    positions=np.arange(6)
    before=[100*result[a]['initial']['initial_GOOD_rate'] for a in ARMS]
    after=[100*result[a]['terminal']['mean_GOOD_rate'] for a in ARMS]
    ax[0].bar(positions-.17,before,.32,label='Política inicial',color='#b5bdc8')
    ax[0].bar(positions+.17,after,.32,label='Después de aprender',color='#2a719f')
    ax[0].set_xticks(positions,['Q\npúblico','PG\npúblico','Q\nprivado','PG\nprivado','Q\nprior dado','PG\nprior dado'])
    ax[0].set_ylabel('Tasa GOOD conjunta descontada (%)')
    ax[0].set_title('Desde cero y desde un acuerdo suministrado')
    ax[0].legend(frameon=False,fontsize=8)
    cats=['ordinary_L1','ordinary_L7','critical_L7'];before_cat=[]
    initial_record=next(r for r in initial['records'] if r['arm']=='PG_PUBLIC_WARM')
    with np.load(folder/'PG_PUBLIC_WARM_world00_0.npz') as z:loss=z['losses'][0]
    for key in cats:
        indices=[i for i,l in enumerate(loss) if ('critical_L7' if i==3 else ('ordinary_L1' if l==1 else 'ordinary_L7'))==key]
        before_cat.append(float(np.mean([initial_record['initial']['gain_over_autarky'][i] for i in indices])))
    p=np.arange(3)
    ax[1].bar(p-.17,before_cat,.32,color='#b5bdc8',label='Prior PG')
    ax[1].bar(p+.17,[warm['mean_private_gain_by_category'][k] for k in cats],.32,color='#2a719f',label='PG final')
    ax[1].axhline(.02,color='#b85c38',linestyle='--',label='Umbral privado preregistrado')
    ax[1].set_xticks(p,['Ordinario L=1','Ordinario L=7','Crítico L=7'])
    ax[1].set_ylabel('Ganancia privada frente a AUTO')
    ax[1].set_title('El salto binario WARM cruza un umbral pequeño')
    ax[1].legend(frameon=False,fontsize=8)
    for a in ax:
        a.spines[['top','right']].set_visible(False);a.grid(axis='y',alpha=.15);a.set_axisbelow(True)
    fig.savefig(B/'results/FIG_V202_PRIOR_AND_CONTINUOUS_GAINS.png',dpi=180);plt.close(fig)
    synthesis=dict(study='V202',registered_primary=analysis['primary'],
        preregistration_commit='358df109d6e0fefdded66b9c68751665393ac3c5',
        scientific_training_roots=32,arms=6,groups_per_root=8,group_rounds=92160000,
        outcomes=result,PG_WARM_GOOD_rate_absolute_increase=continuous_change,
        binary_WARM_transition_does_not_demonstrate_rule_invention=True,
        learned_public_functional_profiles_with_exploitability_at_most_point01=0,
        private_information_regret_is_only_a_feasible_lower_bound=True,
        warnings=['PG_COLD still has a simple profitable AUTO deviation; no impossibility claim about stronger private learners.',
            'PUBLIC WARM priors differ by algorithm (Q deterministic, PG 95%); algorithm contrasts do not isolate a single optimizer mechanism.',
            'All-zero bootstrap intervals do not imply a population probability exactly zero; see V202_ZERO_SUCCESS_BOUND.json.',
            'Post hoc initial-state and gradient interpretation does not confirm a new hypothesis.'],
        decision='FAIL H1; preserve negative. Do not repeat rate sweeps to rescue it. A stronger learner or a new causal mechanism requires its own preregistration.',
        full_institutional_organization_emergence=False,external_scientific_confirmation=False,
        CT2_historical=61,new_branch_score=None,new_N1_awards=[],N2=0,N3=0)
    out.write_text(json.dumps(synthesis,indent=2),encoding='utf-8')
    print(json.dumps(dict(primary=analysis['primary'],PG_WARM_GOOD_rate_increase=continuous_change,
        public_functional_near_equilibria=0),indent=2))


if __name__=='__main__':main()
