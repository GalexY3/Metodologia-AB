"""Audit Hydrogen's revised theory before any new MARL training.

The input is user-supplied theory, not verified evidence. Balanced roles and
fixed capital are diagnostic controls, not claims of emergent institutions.
"""
from pathlib import Path
from fractions import Fraction as F
import hashlib
import itertools
import json
import math
import numpy as np
from research_resource_limits import apply_limits

B = Path(__file__).resolve().parent
R = B/'results'
PI, A = F(13, 20), F(4, 5)
BETA, COST, WORK, DELTA, TAU = .95, .04, .05, .30, .25


def posterior(signal):
    lg = A if signal else 1-A
    lb = 1-lg
    ps = PI*lg+(1-PI)*lb
    return PI*lg/ps


def mode_gain(stock, losses, policies, payers, i, signal):
    """JOINT minus AUTARKY, conditional on private signal, kept transfers."""
    p = float(posterior(signal))
    prod_good = prod_bad = 1.
    for j, policy in enumerate(policies):
        if j != i:
            prod_good *= .2*policy[0]+.8*policy[1]
            prod_bad *= .8*policy[0]+.2*policy[1]
    f = -math.expm1(-stock)
    bonus = .8*f+(.25*sum(payers) if i == 3 else -.25*payers[i])
    return p*prod_good*bonus-(1-p)*prod_bad*(.25*f+losses[i])-(DELTA if i == 3 else 0.)


def scalar_gain(stock, losses, policies, payers, i, signal):
    """Independent explicit state/other-signal outcome enumeration."""
    p = float(posterior(signal)); y = .25*(-math.expm1(-stock))
    values = []
    others = [j for j in range(4) if j != i]
    for action in [0, 1]:
        expected = 0.
        for good, state_prob in [(True, p), (False, 1-p)]:
            for signals in itertools.product([0, 1], repeat=3):
                probability = state_prob
                choices = [0]*4; choices[i] = action
                for j, s in zip(others, signals):
                    probability *= (.8 if s else .2) if good else (.2 if s else .8)
                    choices[j] = policies[j][s]
                complete = all(choices)
                reward = y-WORK
                if complete:
                    reward = (y+.8*(-math.expm1(-stock)) if good else -losses[i])-WORK
                    if good:
                        reward += TAU*sum(payers) if i == 3 else -TAU*payers[i]
                if i == 3 and action:
                    reward -= DELTA
                expected += probability*reward
        values.append(expected)
    return values[1]-values[0]


def aut_stock(gamma):
    return max(0., math.log(.2375/(.05+.95*gamma)))


def investment_pv(gamma, stock=0., finite=True, work_optional=False):
    present = 0.
    for h in range(1, 2001):
        increment = COST*(1-gamma)**(h-1)
        if finite:
            if work_optional:
                before = max(0., .25*(-math.expm1(-stock))-WORK)
                after = max(0., .25*(-math.expm1(-(stock+increment)))-WORK)
                gain = after-before
            else:
                gain = .25*math.exp(-stock)*(-math.expm1(-increment))
        else:
            gain = .25*math.exp(-stock)*increment
        present += BETA**h*gain
    return present


def bisect_root(fn, left, right):
    assert fn(left)*fn(right) <= 0
    for _ in range(100):
        middle = (left+right)/2
        if fn(middle)*fn(left) > 0:
            left = middle
        else:
            right = middle
    return (left+right)/2


def main():
    output = R/'V201R_THEORY_PRECHECK.json'
    assert not output.exists()
    signal = []
    for s in [0, 1]:
        p = posterior(s)
        signal.append(dict(signal=s, posterior_G=str(p), posterior_G_float=float(p),
            other_three_follow_G_joint=float(p*A**3), other_three_follow_B_joint=float((1-p)*(1-A)**3)))
    all_follow = [(0, 1)]*4
    losses = [1., 1., 7., 7.]
    payers = [1, 1, 1, 0]
    s05 = aut_stock(.05)
    gains = []
    parity_max = 0.
    for stock in [0., .40215, .49913, s05, 1.5]:
        for i in range(4):
            for s in [0, 1]:
                formula = mode_gain(stock, losses, all_follow, payers, i, s)
                scalar = scalar_gain(stock, losses, all_follow, payers, i, s)
                error = abs(formula-scalar); parity_max = max(parity_max, error)
                assert error < 1e-12
                gains.append(dict(stock=stock, role=i, loss=losses[i], signal=s, joint_minus_autarky=formula,
                                  all_peers_follow_signals=True, three_promised_payers=True))
    counter_low = mode_gain(s05, losses, all_follow, payers, 0, 0)
    counter_high = mode_gain(1.5, losses, all_follow, payers, 2, 0)
    assert counter_low > 0 and counter_high > 0
    # Ex-post incentives: no donor is pivotal when three pay but two suffice.
    transfer = [dict(promised_payers=n, critical_required_payments=h,
        payments_after_one_defection=n-1, continuation_still_authorized=n-1 >= h,
        immediate_defection_gain=TAU,
        payer_is_pivotal_for_written_continuation=bool(n-1 < h),
        one_period_deviation_not_deterred_by_written_threshold=bool(n-1 >= h),
        full_sequential_incentive_compatibility_assessed=False) for n, h in [(3, 2), (2, 2), (3, 3)]]
    assert transfer[0]['continuation_still_authorized']
    pg_joint = float(PI*A**4)
    original_ord_rent = float(F(59, 100))*mode_gain(s05, losses, all_follow, payers, 0, 1)
    memory = dict(probability_good_completed_opportunity=pg_joint,
        calendar_count_expected_lifetime_if_reset_on_every_nonsuccess=1/(1-pg_joint),
        calendar_memory_future_rent_upper_reference=BETA*original_ord_rent/(1-BETA*pg_joint),
        claimed_permanent_memory_future_rent_reference=BETA*original_ord_rent/(1-BETA),
        payment_now=TAU,
        calendar_memory_also_fails_reference_payment_bound=BETA*original_ord_rent/(1-BETA*pg_joint) < TAU,
        initially_zero_calendar_memory_is_absorbing_under_the_written_threshold=True,
        last_successful_opportunity_memory_is_a_different_policy=True)
    gamma_marginal = (.2375-.05)/.95
    gamma_finite = bisect_root(lambda g: investment_pv(g)-COST, .001, .4)
    investment = dict(claimed_marginal_gamma_boot=gamma_marginal,
        finite_increment_gamma_boot_if_working_exogenously=gamma_finite,
        current_stock_for_positive_operating_output=-math.log(1-WORK/.25),
        maximum_autarky_output_from_one_investment=.25*(-math.expm1(-COST)),
        one_investment_cost=COST,
        single_investment_PV_optional_work_at_zero=investment_pv(.05, work_optional=True),
        single_investment_net_optional_work_at_zero=investment_pv(.05, work_optional=True)-COST,
        single_investment_PV_forced_work_reference=investment_pv(.05),
        positive_first_investment_marginal_with_optional_rest_refuted=True,
        does_not_rule_out_profitable_multiperiod_investment=True,
        aut_stock_formula_is_not_a_solved_four_player_stock_equilibrium=True)
    # Find conditional participation candidates under kept payments. This is
    # not a sequential equilibrium: no investment/mobility or monitoring game.
    candidates = []
    policies = list(itertools.product([0, 1], repeat=2))
    for gamma in [.105, .05, .005]:
        stock = aut_stock(gamma)
        viable = []
        for donor_ids in itertools.combinations(range(3), 2):
            coalition = [int(i in donor_ids) for i in range(3)]+[0]
            for profile in itertools.product(policies, repeat=4):
                if not all(any(policy) for policy in profile):
                    continue
                condition = True
                for i in range(4):
                    for s in [0, 1]:
                        gain = mode_gain(stock, losses, profile, coalition, i, s)
                        if (profile[i][s] == 1 and gain < -1e-12) or (profile[i][s] == 0 and gain > 1e-12):
                            condition = False
                if condition:
                    viable.append(dict(donors=list(donor_ids), role_policies=[list(x) for x in profile]))
        candidates.append(dict(gamma=gamma, reference_stock=stock, conditional_mode_equilibria=len(viable),
            profiles=viable, transfers_assumed_kept=True, not_a_full_relational_equilibrium=True))
    # Two incompatible renewal laws for shocks during versus outside downtime.
    renewal = [dict(sigma_times_rebuild=x, stated_fraction=1/(1+x),
        fraction_if_independent_Poisson_shocks_reset_rebuilding=math.exp(-x)) for x in [.1, .5, 1., 2.]]
    missing = ['S_max not numerically fixed', 'sigma not numerically fixed in the six-arm design',
        'T_build and C_coord not solved', 'V_build and V_out not computed',
        'Poisson shocks versus one scheduled shock are different processes',
        'No vacant destination in16full sites for64agents unless site creation/reassignment is defined',
        'Investment financing, stock-use rights and learning substage transitions not fully specified',
        'Credible punishment and private/public monitoring not proved',
        'S_zero removes all joint productive surplus, not just durability',
        'Autarkic reference stock cannot be held fixed when joint production changes investment incentives']
    result = dict(input='theory_inputs/HYDROGEN_V201R_20261116/HYDROGEN_V201R_RECONSTRUCTION.txt',
        input_sha256=hashlib.sha256((B/'theory_inputs/HYDROGEN_V201R_20261116/HYDROGEN_V201R_RECONSTRUCTION.txt').read_bytes()).hexdigest(),
        scientific_training_executed=False, analytic_theory_audit=True, no_AB_originality_awarded=True,
        conditional_probabilities=signal, payoff_enumeration_max_error=parity_max, conditional_gains=gains,
        negative_signal_low_loss_counterexample=counter_low,
        negative_signal_high_loss_at1p5_counterexample=counter_high,
        transfer_pivotality=transfer, monitoring_memory=memory, investment=investment,
        conditional_mode_candidates=candidates, renewal_process_counterexamples=renewal,
        unresolved_definitions=missing, all_follow_signal_policy_is_not_Bayes_Nash_in_claimed_region=True,
        all_three_payment_profile_is_not_self_enforcing_under_threshold2=True,
        exact_gamma_band_not_established=True, long_MARL_campaign_not_justified_yet=True,
        CT2_historical=61, new_branch_score=None, N2=0, N3=0)
    output.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k not in ['conditional_gains', 'conditional_mode_candidates']}, indent=2), flush=True)
    print('CONDITIONAL_CANDIDATE_COUNTS', [(r['gamma'], r['conditional_mode_equilibria']) for r in candidates], flush=True)


if __name__ == '__main__':
    print('LIMITS', apply_limits(2), flush=True)
    main()
