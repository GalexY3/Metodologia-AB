"""Frozen primary estimand; worlds, not groups or timepoints, are resampled."""
from pathlib import Path
import json
import numpy as np
from v202_relational_learning import ARMS

B=Path(__file__).resolve().parent


def analyze(folder):
    rows=[json.loads((folder/f'{arm}_world{world:02}.json').read_text(encoding='utf-8'))
          for world in range(32) for arm in ARMS]
    by_arm={a:[] for a in ARMS}
    for row in rows:
        by_arm[row['arm']].append(row)
    metrics={}
    for arm,items in by_arm.items():
        functional=np.array([np.mean([g['evaluation']['functional'] for g in r['groups']]) for r in items])
        metrics[arm]=dict(world_functional_fractions=functional.tolist(),mean_functional_fraction=float(functional.mean()),
            mean_GOOD_rate=float(np.mean([g['evaluation']['discounted_GOOD_joint_rate'] for r in items for g in r['groups']])),
            mean_payment_disable_effect=float(np.mean([g['evaluation']['payment_disable_effect'] for r in items for g in r['groups']])),
            mean_min_private_gain=float(np.mean([min(g['evaluation']['gain_over_autarky']) for r in items for g in r['groups']])),
            mean_deviation_gain=float(np.mean([g['deviations']['max_normalized_gain'] for r in items for g in r['groups']])),
            deviation_scope=items[0]['groups'][0]['deviations']['scope'])
    public=np.array(metrics['PG_PUBLIC_COLD']['world_functional_fractions'])
    private=np.array(metrics['PG_PRIVATE_COLD']['world_functional_fractions'])
    rng=np.random.Generator(np.random.Philox(2026111603))
    indices=rng.integers(0,32,(20000,32))
    public_ci=np.quantile(public[indices].mean(1),[.0125,.9875])
    difference=public-private
    diff_ci=np.quantile(difference[indices].mean(1),[.0125,.9875])
    primary=dict(hypothesis='H1_PG_PUBLIC_ACQUISITION',world_roots=32,groups_per_root=8,
        public_functional_fraction=float(public.mean()),public_CI97p5=public_ci.tolist(),
        public_minus_private=float(difference.mean()),difference_CI97p5=diff_ci.tolist(),
        public_lower_at_least_half=bool(public_ci[0]>=.50),difference_lower_at_least_point20=bool(diff_ci[0]>=.20),
        result='PASS' if public_ci[0]>=.50 and diff_ci[0]>=.20 else 'FAIL',
        methods='Paired world bootstrap 20000, two Bonferroni 97.5% intervals; no group pseudoreplication.')
    result=dict(study='V202',primary=primary,arms=metrics,
        WARM_supplied_prior_not_emergence=True,roles_capital_membership_fixed=True,
        external_confirmation=False,novelty_not_accredited=True,CT2_historical=61,new_branch_score=None,N2=0,N3=0)
    destination=folder/'ANALYSIS.json';assert not destination.exists()
    destination.write_text(json.dumps(result,indent=2),encoding='utf-8')
    return result
