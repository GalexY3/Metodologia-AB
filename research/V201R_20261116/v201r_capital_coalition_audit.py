"""Deterministic feasibility controls, not learned investment or an institution.

All contributors commit to invest for T periods, then stop. The commitment
is an oracle control. A one-period omission tests its unilateral incentives.
No joint production, roles, transfers, cash constraints or stochastic data.
"""
from pathlib import Path
import hashlib
import json
import math
import numpy as np
from research_resource_limits import apply_limits

B = Path(__file__).resolve().parent
BETA, COST, WORK = .95, .04, .05
HORIZON = 2000


def path(gamma, contributors, rounds, omitted_at=None):
    stock, value, omitted_value = 0., 0., 0.
    omitted_stock = 0.
    for t in range(HORIZON):
        invest = COST if t < rounds else 0.
        omit = omitted_at is not None and t == omitted_at
        reward = max(0., .25*(-math.expm1(-stock))-WORK)-invest
        other_reward = max(0., .25*(-math.expm1(-omitted_stock))-WORK)-invest+COST*omit
        value += BETA**t*reward
        omitted_value += BETA**t*other_reward
        stock = (1-gamma)*stock+contributors*invest
        omitted_stock = (1-gamma)*omitted_stock+contributors*invest-COST*omit
    return value, omitted_value


def vectorized_values(gamma, contributors, rounds):
    """Independent closed-form physical trajectories, one row per duration."""
    t = np.arange(HORIZON, dtype=float)[None, :]
    duration = np.asarray(rounds, dtype=float)[:, None]
    stock = COST*contributors/gamma*(1-(1-gamma)**np.minimum(t, duration))
    stock *= (1-gamma)**np.maximum(0., t-duration)
    rewards = np.maximum(0., .25*(-np.expm1(-stock))-WORK)-COST*(t < duration)
    return rewards @ (BETA**t[0])


def main():
    destination = B/'results/V201R_CAPITAL_COALITION_AUDIT.json'
    assert not destination.exists()
    rows, max_error = [], 0.
    for gamma in [.25, .105, .05, .005]:
        for contributors in [1, 2, 3, 4]:
            durations = np.arange(0, 201)
            values = vectorized_values(gamma, contributors, durations)
            best = int(np.argmax(values))
            direct, missed = path(gamma, contributors, best, 0 if best else None)
            error = abs(direct-float(values[best])); max_error = max(max_error, error)
            assert error < 1e-12
            omissions = [dict(round=t, deviation_gain=path(gamma, contributors, best, t)[1]-direct)
                         for t in range(min(best, 50))]
            maximum = max(omissions, key=lambda x: x['deviation_gain']) if omissions else None
            rows.append(dict(gamma=gamma, contributors=contributors,
                searched_investment_durations=[0, 200], selected_duration_within_this_family=best,
                feasible_private_discounted_return=direct,
                positive_feasible_return=bool(direct > 1e-10),
                first_investment_omission_gain=missed-direct if best else None,
                max_single_omission_among_first_50=maximum,
                unobserved_omission_continuation_assumes_others_keep_investing=True,
                this_is_not_an_equilibrium_or_a_globally_optimal_policy=True))
    result = dict(protocol='Post-input mathematical diagnostic; no confirmatory learning run',
        physical_model='S_next=(1-gamma)*S+0.04*n_investors; own reward=max(0,0.25*(1-exp(-S))-0.05)-own_investment',
        discount=BETA, horizon=HORIZON, omitted_positive_tail_bound=.25*BETA**HORIZON/(1-BETA),
        cap_assumption='No cap binds on the displayed feasible paths; Hydrogen did not specify S_max.',
        commitment_control_not_learned=True, investment_is_costly_effort_without_cash_constraint=True,
        scalar_closed_form_parity_max_error=max_error, rows=rows,
        limits='Positive return is a feasibility witness only. One profitable omission refutes this open-loop commitment, not every possible contingent equilibrium.',
        input_sha256=hashlib.sha256((B/'theory_inputs/HYDROGEN_V201R_20261116/HYDROGEN_V201R_RECONSTRUCTION.txt').read_bytes()).hexdigest(),
        CT2_historical=61, new_branch_score=None, N2=0, N3=0)
    destination.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(dict(rows=rows, max_error=max_error), indent=2), flush=True)


if __name__ == '__main__':
    print('LIMITS', apply_limits(2), flush=True)
    main()
