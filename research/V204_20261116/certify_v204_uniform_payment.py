"""Post hoc algebraic certificate of a known LOLA field, not a new learner.

An independently calculated closed form is compared with autodiff output.
Only n=4, signal accuracy .8 is numerically checked against the frozen game.
General-n / accuracy expressions are algebraic predictions pending another
implementation and novelty review, not new learning experiments.
"""
from pathlib import Path
import hashlib
import json
import math
import numpy as np
import torch
from v204_opponent_gradient import lola_components
from research_resource_limits import apply_limits

B=Path(__file__).resolve().parent
STOCK=.8903152454708944
F=1-math.exp(-STOCK);Y=.25*F


def occupancy_square(n,q,beta=.95,prior=.65):
    good=prior*q**n;bad=(1-prior)*q**n;alone=1-q**n;delta=1-beta
    before=delta/(delta+beta*good);after=beta*good/(delta+beta*good)
    start=(delta+beta*alone*before)**2+(beta*bad*before)**2
    count_square=math.comb(2*(n-1),n-1)/4**(n-1)
    recorded=count_square*beta**2*((alone**2+bad**2)*after**2+good**2)
    return start+recorded


def formula(native_q,loss,epsilon=0.,n=4,accuracy=.8,prior=.65,beta=.95,tau=.25):
    q=epsilon/2+(1-epsilon)*native_q
    mode_derivative=(1-epsilon)*native_q*(1-native_q)
    pay_derivative=(1-epsilon)/4
    information=prior**2*(accuracy**2+(1-accuracy)**2)*(.8*F-tau/2)
    information-=2*prior*(1-prior)*accuracy*(1-accuracy)*(Y+loss)
    square=occupancy_square(n,q,beta,prior)
    direct=-tau*pay_derivative*prior*q**n
    cross=tau*pay_derivative*information*square*mode_derivative**2*q**(2*n-2)
    return direct,cross,square,information


def main():
    torch.set_num_threads(2);torch.set_num_interop_threads(1)
    earlier=json.loads((B/'results/V204_POSTHOC_GRADIENT_DECOMPOSITION.json').read_text(encoding='utf-8'))
    checks=[]
    for row in earlier['rows']:
        for i,loss in enumerate([1.,1.,7.]):
            direct,cross,square,info=formula(row['q'],loss)
            observed=row['unscaled_LOLA_payment_correction'][i]
            checks.append(dict(source='Earlier posthoc autodiff probe',native_q=row['q'],epsilon=0.,agent=i,
                analytic_direct=direct,analytic_cross=cross,observed_cross=observed,
                relative_cross_error=abs(cross-observed)/max(abs(cross),1e-300)))
    extra=[]
    for native_q,epsilon,losses in [
        (.1,.02,[1.,1.,7.,7.]),(.5,.02,[1.,1.,7.,7.]),(.9,.02,[1.,1.,7.,7.]),
        (.1,.2,[1.,1.,7.,7.]),(.5,.2,[1.,1.,7.,7.]),(.9,.2,[1.,1.,7.,7.]),
        (.5,0.,[1.,2.5,9.7,0.]),(.5,0.,[1.,2.5,9.7,100.]),
        (.5,.2,[1.,2.5,9.7,0.]),(.5,.2,[1.,2.5,9.7,100.])]:
        theta=np.zeros((4,15,2,2));theta[:,:,:,0]=math.log(native_q/(1-native_q))
        x=torch.tensor(theta,dtype=torch.float64,requires_grad=True)
        _,own,cross=lola_components(x,losses=losses,epsilon=epsilon)
        dd=own.detach().numpy()[:3,:,:,1].sum((1,2));cc=cross.detach().numpy()[:3,:,:,1].sum((1,2))
        for i in range(3):
            d,c,_,_=formula(native_q,losses[i],epsilon)
            assert abs(d-dd[i])<1e-11
            error=abs(c-cc[i])/max(abs(c),1e-300)
            assert error<1e-9,(native_q,epsilon,losses,i,c,cc[i],error)
            extra.append(dict(native_q=native_q,epsilon=epsilon,losses=losses,agent=i,
                analytic_direct=d,observed_direct=float(dd[i]),analytic_cross=c,
                observed_cross=float(cc[i]),relative_cross_error=float(error)))
    maximum=max(r['relative_cross_error'] for r in checks+extra)
    assert maximum<1e-9
    thresholds=[]
    for loss in [1.,7.]:
        benefit=.65*(.8*F-.125);risk=.35*(Y+loss)
        z=benefit/(2*(benefit+risk))
        accuracy=(1+math.sqrt(1-4*z))/2
        thresholds.append(dict(donor_loss=loss,critical_signal_accuracy_zero_of_cross=accuracy))
    result=dict(study='V204',analysis='POST_HOC_CLOSED_FORM_CERTIFICATE',status='PASS',
        n4_cross_component_checks=len(checks)+len(extra),maximum_relative_cross_error=maximum,
        independently_calculated_formula_not_a_fit=True,
        general_n_or_other_signal_accuracy_numerically_validated=False,
        formulas_scope='Uniform native mode probability, payment probability .5, history count/outcome tabular logits, exact original LOLA Eq4.4',
        initial_epsilon20_ratio=formula(.5,1.,.2)[1]*20/abs(formula(.5,1.,.2)[0]),
        signal_accuracy_thresholds_algebraic_predictions=thresholds,
        original_priority_unestablished=True,external_scientific_confirmation=False,
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        earlier_checks=checks,new_cost_and_mixture_checks=extra,
        CT2_historical=61,new_branch_score=None,N2=0,N3=0)
    out=B/'results/V204_CLOSED_FORM_CERTIFICATE.json';assert not out.exists()
    out.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ['earlier_checks','new_cost_and_mixture_checks']},indent=2))


if __name__=='__main__':
    print('LIMITS',apply_limits(2),flush=True)
    main()
