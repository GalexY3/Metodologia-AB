"""Post hoc diagnostic after observing the first cold endpoint, not H1 evidence.

No integration or eta selection. Probe the known field at nine uniform
mode probabilities, with private payment probability fixed at one half.
The summed payment-logit component is a directional derivative for shifting
all own payment logits together, not an actual aggregate policy update.
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


def main():
    torch.set_num_threads(2);torch.set_num_interop_threads(1)
    qs=[.001,.002,.005,.01,.02,.05,.1,.2,.5]
    rows=[]
    for q in qs:
        theta=np.zeros((4,15,2,2));theta[:,:,:,0]=math.log(q/(1-q))
        x=torch.tensor(theta,dtype=torch.float64,requires_grad=True)
        _,own,cross=lola_components(x,epsilon=0.)
        own=own.detach().numpy();cross=cross.detach().numpy()
        direct=own[:3,:,:,1].sum((1,2));correction=cross[:3,:,:,1].sum((1,2))
        analytic=-.65*.25*.25*q**4
        assert np.max(np.abs(direct-analytic))<1e-11
        rows.append(dict(q=q,direct_payment_logit_direction=direct.tolist(),
            analytic_history_blind_direct_cost=analytic,
            unscaled_LOLA_payment_correction=correction.tolist(),
            eta20_correction_over_absolute_direct=(20*correction/np.abs(direct)).tolist(),
            total_eta20_payment_logit_direction=(direct+20*correction).tolist()))
    a=rows[:5]
    slope_direct=float(np.polyfit(np.log([r['q'] for r in a]),np.log([-r['direct_payment_logit_direction'][0] for r in a]),1)[0])
    correction=np.array([r['unscaled_LOLA_payment_correction'][0] for r in a])
    slope_cross=float(np.polyfit(np.log([r['q'] for r in a]),np.log(np.abs(correction)),1)[0])
    out=dict(study='V204',analysis='POST_HOC_NOT_PREREGISTERED_CONFIRMATION',
        triggered_after='First COLD LOLA endpoint reported no functionality; other cases already running',
        learning_trajectories_or_registered_eta_changed=False,
        probe_epsilon=0.,training_epsilon_schedule_still_registered=True,
        directional_derivative_not_mean_policy_update=True,
        low_q_loglog_fit_range=[.001,.02],empirical_direct_exponent=slope_direct,
        empirical_abs_cross_exponent=slope_cross,
        fitted_power_is_not_a_proof_or_general_n_player_law=True,
        original_priority_unestablished=True,rows=rows,
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    target=B/'results/V204_POSTHOC_GRADIENT_DECOMPOSITION.json';assert not target.exists()
    target.write_text(json.dumps(out,indent=2),encoding='utf-8')
    print(json.dumps(out,indent=2))


if __name__=='__main__':
    print('LIMITS',apply_limits(2),flush=True)
    main()
