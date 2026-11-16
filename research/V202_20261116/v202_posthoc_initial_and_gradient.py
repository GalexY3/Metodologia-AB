"""Post hoc interpretation, no rescue of the failed preregistered H1.

Compare initial policies and derive the private one-stage gradients at the
state-independent cold policy. These observations do not confirm a new H.
"""
from pathlib import Path
import json
import numpy as np
from v202_relational_learning import ARMS,probabilities,F,Y
from v202_exact_evaluation import evaluate,deviation_audit

B=Path(__file__).resolve().parent


def main():
    folder=B/'results/V202_RELATIONAL_ACQUISITION'
    output=B/'results/V202_POSTHOC_INITIAL_AND_GRADIENT.json'
    assert not output.exists()
    summaries={};records=[]
    for arm in ARMS:
        items=[]
        for world in range(32):
            with np.load(folder/f'{arm}_world{world:02}_0.npz') as z:
                initial=probabilities(z['q'],z['theta'],arm.startswith('PG'))
                losses=z['losses'].copy()
            with np.load(folder/f'{arm}_world{world:02}_60000.npz') as z:
                terminal=probabilities(z['q'],z['theta'],arm.startswith('PG'))
            for g in range(8):
                evaluation=evaluate(initial[g],losses[g],'_PUBLIC_' in arm)
                record=dict(arm=arm,world=world,group=g,initial=evaluation,
                    mean_absolute_probability_change=float(np.mean(np.abs(terminal[g]-initial[g]))),
                    maximum_absolute_probability_change=float(np.max(np.abs(terminal[g]-initial[g]))))
                items.append(record);records.append(record)
        summaries[arm]=dict(initial_functional_fraction=float(np.mean([r['initial']['functional'] for r in items])),
            initial_GOOD_rate=float(np.mean([r['initial']['discounted_GOOD_joint_rate'] for r in items])),
            initial_mean_min_private_gain=float(np.mean([min(r['initial']['gain_over_autarky']) for r in items])),
            mean_absolute_probability_change=float(np.mean([r['mean_absolute_probability_change'] for r in items])),
            maximum_absolute_probability_change=float(max(r['maximum_absolute_probability_change'] for r in items)))
    signs=[]
    for i,loss in enumerate([1,1,7,7]):
        net=.375 if i==3 else -.125
        for s,posterior in [(0,13/41),(1,52/59)]:
            gain=posterior*.125*(.8*F+net)-(1-posterior)*.125*(Y+loss)-.3*(i==3)
            signs.append(dict(role=i,loss=loss,signal=s,JOINT_minus_AUTO_with_uniform_peers=gain))
    critical_upper=(52/59)*.125*(.8+.375)-(7/59)*.125*(.25+7)-.3
    assert critical_upper<0
    result=dict(status='POST_HOC_INTERPRETATION_NOT_CONFIRMATION',
        registered_primary_still='FAIL',initial_policy_summary=summaries,
        uniform_cold_conditional_mode_advantages=signs,
        conditional_payment_advantage_at_uniform_history_independent_policy=-.25,
        reason_payment_gradient='At initialization all continuation values are history independent, so changing the payment only costs 0.25. Public and private memory do not initially induce a different continuation response.',
        critical_positive_signal_advantage_upper_bound_over_all_fixed_nonnegative_stocks=critical_upper,
        upper_bound_scope='Uniform 0.5 modes and 0.5 payments of peers, L_critical=7, fixed stock. Not a result about endogenous investment, every initialization or every learning algorithm.',
        warning='WARM PG starts with almost the full behavioral blueprint. Its binary functional transition crosses a small private-gain threshold; report continuous changes and profitable deviations.',
        records=records,scientific_external_confirmation=False,N2=0,N3=0)
    output.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))


if __name__=='__main__':main()
