"""Independent optimistic quantized MDP check of the interpolation certificate.

Ceil all stock transitions onto a grid. Monotone production makes this an
optimistic physical process. Iterate from a global upper bound, with positive
roundoff guards. No interpolation and no use of the previous solver's values.
"""
from pathlib import Path
import json
import numpy as np
from research_resource_limits import apply_limits

B = Path(__file__).resolve().parent


def optimistic_control(gamma, points=16001):
    cap = max(4., .04/gamma)
    grid = np.linspace(0., cap, points)
    production = np.maximum(0., .25*(-np.expm1(-grid))-.05)
    no_stock = (1-gamma)*grid
    yes_stock = np.minimum(cap, no_stock+.04)
    # Explicit outward state guard exceeds ordinary double rounding error.
    no_idx = np.minimum(points-1, np.searchsorted(grid, no_stock+1e-12, side='left'))
    yes_idx = np.minimum(points-1, np.searchsorted(grid, yes_stock+1e-12, side='left'))
    upper = np.full(points, (.2+1e-12)/.05)
    for t in range(2000):
        updated = production+np.maximum(.95*upper[no_idx], -.04+.95*upper[yes_idx])+1e-12
        difference = float(np.max(np.abs(updated-upper)))
        upper = updated
        if difference < 1e-13:
            break
    first = min(points-1, int(np.searchsorted(grid, .04+1e-12, side='left')))
    first_action_upper = -.04+.95*float(upper[first])+1e-12
    return dict(gamma=gamma, points=points, cap=cap, iterations=t+1,
        guard_stock_and_reward=1e-12, optimistic_value_at_first_invested_state=float(upper[first]),
        first_investment_action_upper_bound=first_action_upper,
        strictly_negative_investment_bound=bool(first_action_upper < 0),
        first_action_upper_margin_below_zero=max(0., -first_action_upper))


def main():
    destination = B/'results/V201R_CAPITAL_BOUND_INDEPENDENT_AUDIT.json'
    assert not destination.exists()
    previous = json.loads((B/'results/V201R_SINGLE_AGENT_BELLMAN.json').read_text())
    rows = [optimistic_control(gamma) for gamma in [.25, .105, .05, .005]]
    for row in rows:
        prior = next(r for r in previous['rows'] if r['gamma'] == row['gamma'] and r['grid_points'] == 8001)
        row['agrees_with_interpolation_method_on_sign'] = bool(
            row['strictly_negative_investment_bound'] == prior['rest_at_zero_proved_optimal_by_strict_upper_bound'])
        assert row['agrees_with_interpolation_method_on_sign']
    result = dict(independent_algorithm=True, independent_external_team_or_data=False,
        monotone_ceiling_transition_upper_envelope=True,
        continuous_process='reward=max(0,0.25*(1-exp(-S))-0.05)-I; S_next=(1-gamma)*S+I; I in {0,0.04}',
        proof='At S=0, wait returns beta*V(0); invest returns -0.04+beta*V(0.04). If even an optimistic quantized upper bound on the latter is strictly negative, V(0)=0 and waiting is optimal.',
        floating_point_scope='Dominance argument is analytic; numerical bounds include explicit 1e-12 outward guards. This is not an arbitrary-precision interval-arithmetic package.',
        rows=rows, all_signs_agree=True,
        scope='Solitary autarky MDP without financing limits. Does not disprove coordinated investment, contingent public-good equilibria, or multiagent bootstrap.',
        CT2_historical=61, new_branch_score=None, N2=0, N3=0)
    destination.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    print('LIMITS', apply_limits(2), flush=True)
    main()
