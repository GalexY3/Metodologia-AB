"""Assemble transparent theory evidence and a scientific figure; no new runs."""
from pathlib import Path
from fractions import Fraction as F
import hashlib
import json
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import v201r_relational_certificate as certificate

B = Path(__file__).resolve().parent
R = B/'results'


def load(name):
    return json.loads((R/name).read_text(encoding='utf-8'))


def main():
    output = R/'V201R_SCIENTIFIC_SYNTHESIS.json'
    assert not output.exists()
    pre = load('V201R_THEORY_PRECHECK.json')
    bellman = load('V201R_SINGLE_AGENT_BELLMAN.json')
    independent = load('V201R_CAPITAL_BOUND_INDEPENDENT_AUDIT.json')
    coalition = load('V201R_CAPITAL_COALITION_AUDIT.json')
    relational = load('V201R_RELATIONAL_CERTIFICATES.json')
    stock = math.log(.2375/(.05+.95*.05)); f = -math.expm1(-stock)
    losses = [1, 1, 7, 7]; donors = [0, 1]
    profile = [(1, 1), (1, 1), (0, 1), (0, 1)]
    rents, mode = [], []
    for i in range(4):
        a, b = certificate.rent_coefficients(losses, profile, donors, i)
        rent = float(a)*f+float(b)
        rents.append(dict(role=i, loss=losses[i], incremental_rent_per_round=rent,
            discounted_future_rent=19*rent,
            voluntary_payment_IC_margin=19*rent-.25 if i in donors else None))
        for s in [0, 1]:
            a, b = certificate.mode_coefficients(losses, profile, donors, i, s)
            mode.append(dict(role=i, signal=s, prescribed_mode=profile[i][s],
                joint_minus_autarky=float(a)*f+float(b)))
    critical_positive = next(r['joint_minus_autarky'] for r in mode if r['role'] == 3 and r['signal'] == 1)
    assert critical_positive > 0
    direct_scope_test = dict(reference_stock=stock, repaired_policies=[list(p) for p in profile],
        donors=donors, rents=rents, conditional_mode_gains=mode,
        private_critical_only_punishment_forgiveness_gain_on_positive_signal=critical_positive,
        interpretation='If only the critical switches to AUTARKY after nonpayment while ordinary agents retain these policies and still promise future payments, resuming JOINT on a positive signal is profitable. This rejects that punishment strategy, not every private-monitoring equilibrium.',
        public_grim_control_is_a_different_information_structure=True)
    gammas = [.25, .105, .05, .005]
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.7), constrained_layout=True)
    x = np.arange(4)
    for k, color in [(1, '#5c6370'), (2, '#3182bd'), (4, '#2a9d8f')]:
        values = [next(r['feasible_private_discounted_return'] for r in coalition['rows']
                       if r['gamma'] == g and r['contributors'] == k) for g in gammas]
        axes[0].bar(x+(k == 2)*.25+(k == 4)*.5-.25, values, width=.23,
                    label=f'{k} inversor(es)', color=color)
    axes[0].set_xticks(x, [str(g) for g in gammas])
    axes[0].set_xlabel('Depreciación por ronda, γ')
    axes[0].set_ylabel('Retorno descontado por inversor')
    axes[0].set_title('Invertir juntos puede crear excedente')
    axes[0].legend(frameon=False)
    axes[0].axhline(0, color='black', linewidth=.7)
    axes[0].text(.02, .98, 'Compromiso impuesto durante T rondas (T ∈ 0…200).\nSin producción JOINT; es viabilidad, no emergencia.',
                 transform=axes[0].transAxes, va='top', fontsize=8)
    omission = [next(r['first_investment_omission_gain'] for r in coalition['rows']
                    if r['gamma'] == g and r['contributors'] == 4) for g in gammas]
    axes[1].bar(x, omission, color='#b85c38', width=.6)
    axes[1].set_xticks(x, [str(g) for g in gammas])
    axes[1].set_xlabel('Depreciación por ronda, γ')
    axes[1].set_ylabel('Ganancia por omitir la primera aportación')
    axes[1].set_title('Ese compromiso permite desviarse')
    axes[1].axhline(0, color='black', linewidth=.7)
    axes[1].text(.02, .98, 'Cuatro inversores; los otros mantienen su plan.\nUna ganancia positiva refuta este plan abierto.',
                 transform=axes[1].transAxes, va='top', fontsize=8)
    for ax in axes:
        ax.spines[['top', 'right']].set_visible(False)
        ax.grid(axis='y', alpha=.15); ax.set_axisbelow(True)
    axes[0].set_ylim(-.03, 2.65); axes[1].set_ylim(-.0007, .031)
    fig.savefig(R/'FIG_V201R_BOOTSTRAP_AND_DEVIATION.png', dpi=180)
    plt.close(fig)
    scripts = ['v201r_theory_precheck.py', 'v201r_single_agent_bellman.py',
        'v201r_capital_coalition_audit.py', 'v201r_relational_certificate.py',
        'audit_v201r_capital_bounds.py', 'analyze_v201r_controls.py', 'research_resource_limits.py']
    result = dict(status='POST_HOC_THEORY_AUDIT_AND_CONSTRUCTIVE_CONTROLS',
        source_sha256={s: hashlib.sha256((B/s).read_bytes()).hexdigest() for s in scripts},
        theory_input_sha256=pre['input_sha256'],
        conditional_payoff_max_error=pre['payoff_enumeration_max_error'],
        capital_control_independent_sign_agreement=independent['all_signs_agree'],
        rational_relational_interval_count=relational['certificate_count'],
        relational_independent_checks=relational['independent_enumerated_rent_checks'],
        monitoring_scope_counterexample=direct_scope_test,
        V201R_original_policy_not_validated=True,
        capital_bootstrap_is_a_separate_coordination_problem=True,
        numerical_controls_are_not_learned_institutions=True,
        statistical_holdout_used=False, external_confirmation=False,
        AB2_not_accredited=True, new_N1_awards=[], CT2_historical=61,
        new_branch_score=None, N2=0, N3=0)
    output.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(direct_scope_test, indent=2))


if __name__ == '__main__':
    main()
