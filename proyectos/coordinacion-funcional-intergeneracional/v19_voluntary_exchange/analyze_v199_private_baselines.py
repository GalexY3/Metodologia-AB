"""Frozen primary and secondary decision rules for the private-learner study."""
from pathlib import Path
import json
import numpy as np
from research_resource_limits import apply_limits

B = Path(__file__).resolve().parent
R = B/'results'
ROOT = R/'V199_PRIVATE_BASELINES'


def main():
    output = R/'V199_PRIVATE_BASELINES_ANALYSIS.json'
    assert not output.exists()
    assert (ROOT/'SUMMARY.json').exists()
    contrasts, gates = [], []
    for cohort in ['MAINTENANCE', 'FORMATION']:
        for k in [4, 8, 12]:
            for rule in ['UNANIMITY', 'MAJORITY']:
                summary = json.loads((ROOT/f'{cohort}_k{k}_{rule}/SUMMARY.json').read_text(encoding='utf-8'))
                by_method = {r['method']: r for r in summary['runs']}
                before = {name: next(row for row in r['history'] if row['step'] == 8000) for name, r in by_method.items()}
                rng = np.random.default_rng(np.random.SeedSequence([199, 999, int(cohort == 'FORMATION'), k, int(rule == 'MAJORITY')]))
                indices = rng.integers(0, 32, size=(20000, 32))
                baseline = np.array(before['IQL_EXACT']['greedy_world_welfare'])
                for name, row in before.items():
                    delta = np.array(row['greedy_world_welfare'])-baseline
                    resampled = delta[indices].mean(1)
                    ci = np.quantile(resampled, [.025, .975]).tolist()
                    simultaneous = np.quantile(resampled, [.05/12, 1-.05/12]).tolist()
                    contrast = dict(cohort=cohort, k=k, rule=rule, method=name,
                        mean_advantage_against_IQL_EXACT=float(delta.mean()), descriptive_CI95=ci,
                        six_contrast_family_CI991667=simultaneous,
                        mean_welfare=row['greedy_mean_welfare'], low_payoff=row['greedy_low_payoff'], high_payoff=row['greedy_high_payoff'])
                    contrasts.append(contrast)
                    if name == 'HYSTERETIC':
                        useful = (by_method[name]['maintenance_passed'] if cohort == 'MAINTENANCE'
                                  else row['greedy_mean_welfare'] >= .05 and row['greedy_low_payoff'] >= 0 and row['greedy_high_payoff'] >= 0)
                        passed = useful and delta.mean() >= .02 and simultaneous[0] > 0
                        gates.append(dict(cohort=cohort, k=k, rule=rule, passed=bool(passed),
                                          utility_or_retention_gate=bool(useful), mean_advantage=float(delta.mean()), simultaneous_lower=simultaneous[0]))
    primary_counts = {c: sum(g['passed'] for g in gates if g['cohort'] == c) for c in ['MAINTENANCE', 'FORMATION']}
    result = dict(primary_counts=primary_counts, H1_hysteretic_maintenance_passed=primary_counts['MAINTENANCE'] >= 4,
        H2_hysteretic_formation_passed=primary_counts['FORMATION'] >= 4, gates=gates, contrasts=contrasts,
        bootstrap_resamples=20000, worlds_as_inference_unit=32,
        simultaneous_intervals_family_scope='Six HYSTERETIC versus IQL_EXACT cases within each cohort; separate H1/H2 families.',
        other_method_intervals_are_secondary_descriptive=True,
        known_algorithm_success_does_not_accredit_originality=True, CT2_historical=61, new_branch_score=None, N2=0, N3=0)
    output.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k not in ['gates', 'contrasts']}), flush=True)


if __name__ == '__main__':
    print('LIMITS', apply_limits(2), flush=True)
    main()
