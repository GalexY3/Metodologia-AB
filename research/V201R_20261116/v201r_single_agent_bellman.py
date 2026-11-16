"""A transparent planning control for physical bootstrap and unilateral exit.

Relaxation: one agent, investment as costly effort without a cash constraint,
optional work, no joint surplus, guaranteed access to a new empty site. This
does not solve the proposed multiagent learning/institutional equilibrium.
"""
from pathlib import Path
import json
import math
import numpy as np
from research_resource_limits import apply_limits

B = Path(__file__).resolve().parent
R = B/'results'
DISCOUNT, INVEST, WORK = .95, .04, .05


def solve(gamma, points):
    cap = max(4., INVEST/gamma)
    grid = np.linspace(0, cap, points)
    output = np.maximum(0., .25*(-np.expm1(-grid))-WORK)
    next_no = (1-gamma)*grid
    next_yes = np.minimum(cap, next_no+INVEST)
    value = np.zeros_like(grid)
    for iterations in range(10000):
        q_no = output+DISCOUNT*np.interp(next_no, grid, value)
        q_yes = output-INVEST+DISCOUNT*np.interp(next_yes, grid, value)
        updated = np.maximum(q_no, q_yes)
        residual = float(np.max(np.abs(updated-value)))
        value = updated
        if residual < 1e-12:
            break
    assert iterations < 9999
    # Evaluate the grid-derived policy on the continuous physical state using
    # exact rewards. Its discounted return is a feasible lower bound.
    stock, feasible_value = 0., 0.
    trajectory = []
    for t in range(2000):
        product = max(0., .25*(-math.expm1(-stock))-WORK)
        next_stock = [(1-gamma)*stock, min(cap, (1-gamma)*stock+INVEST)]
        candidate = [product+DISCOUNT*float(np.interp(next_stock[0], grid, value)),
                     product-INVEST+DISCOUNT*float(np.interp(next_stock[1], grid, value))]
        action = int(candidate[1] > candidate[0]+1e-12)
        reward = product-INVEST*action
        feasible_value += DISCOUNT**t*reward
        if t < 40 or t in [99, 199, 499, 1999]:
            trajectory.append(dict(step=t, stock=stock, investment=INVEST*action, reward=reward,
                                   working=bool(.25*(-math.expm1(-stock)) > WORK)))
        stock = next_stock[action]
    # A conservative Lipschitz interpolation bound; convergence differences
    # alone are not a proof of continuous-state optimality.
    lipschitz = .25/(1-DISCOUNT*(1-gamma))
    bound = DISCOUNT*lipschitz*(cap/(points-1))/(2*(1-DISCOUNT))
    bound += residual/(1-DISCOUNT)
    first_state_value = float(np.interp(INVEST, grid, value))
    first_action_upper = -INVEST+DISCOUNT*(first_state_value+bound)
    return dict(gamma=gamma, grid_points=points, cap=cap, iterations=iterations+1,
                Bellman_grid_residual=residual, approximate_value_at_zero=float(value[0]),
                feasible_continuous_policy_value=feasible_value,
                conservative_interpolation_error_bound=bound,
                value_upper_bound=float(value[0]+bound),
                value_at_first_invested_state_approximation=first_state_value,
                first_investment_action_value_upper_bound=first_action_upper,
                rest_at_zero_proved_optimal_by_strict_upper_bound=bool(first_action_upper < 0),
                feasible_return_tail_bound=.25*DISCOUNT**2000/(1-DISCOUNT),
                first_investment=trajectory[0]['investment'], sample_trajectory=trajectory)


def main():
    output = R/'V201R_SINGLE_AGENT_BELLMAN.json'
    assert not output.exists()
    rows = [solve(gamma, points) for gamma in [.25, .105, .05, .005] for points in [2001, 4001, 8001]]
    exit_rows = []
    for gamma in [.105, .05, .005]:
        solved = next(r for r in rows if r['gamma'] == gamma and r['grid_points'] == 8001)
        stock = max(0., math.log(.2375/(.05+.95*gamma)))
        delay = max(0, math.ceil(math.log(stock/.15)/(-math.log1p(-gamma)))) if stock > .15 else 0
        legacy = sum(DISCOUNT**t*max(0., .25*.25*(-math.expm1(-stock*(1-gamma)**t))-WORK)
                     for t in range(delay))
        stay_upper = legacy+DISCOUNT**delay*solved['value_upper_bound']
        leave_lower = solved['feasible_continuous_policy_value']-.12
        exit_rows.append(dict(gamma=gamma, old_reference_stock=stock, waiting_rounds_to_clear=delay,
            discounted_old_operating_return_while_waiting=legacy,
            passive_stay_value_upper_bound=stay_upper, immediate_leave_feasible_value_lower_bound=leave_lower,
            leaving_beats_passive_waiting_by_valid_bound=bool(leave_lower > stay_upper),
            guaranteed_new_site_assumed=True, other_mobility_strategies_not_solved=True))
    result = dict(planner_control_not_learned_agents=True, independent_private_autarky_only=True,
        discount=DISCOUNT, investment_quantum=INVEST, work_cost=WORK,
        constraints='Investment is costly effort without a cash borrowing limit; solitary access to clean land guaranteed; no joint production or transfers.',
        physical_parameters_taken_from_Hydrogen=True, no_hyperparameter_fit_to_cooperation=True,
        rows=rows, exit_controls=exit_rows,
        gamma025_no_reachable_stock_exceeds_work_threshold=bool(INVEST/.25 < -math.log(.8)),
        does_not_prove_multiagent_bootstrap_or_relational_equilibrium=True,
        CT2_historical=61, new_branch_score=None, N2=0, N3=0)
    output.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(dict(controls=[{k: r[k] for k in ['gamma', 'grid_points', 'approximate_value_at_zero',
        'feasible_continuous_policy_value', 'conservative_interpolation_error_bound', 'first_investment']} for r in rows],
        exit_controls=exit_rows), indent=2), flush=True)


if __name__ == '__main__':
    print('LIMITS', apply_limits(2), flush=True)
    main()
