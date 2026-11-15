"""POST HOC: optimistic fixed points versus mean utility and imposed risk.

No new training. Frozen peer laws do not reconstruct coadaptation or establish
an equilibrium. Expectile algebra is established prior art, not a new theorem.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
from research_resource_limits import apply_limits

B = Path(__file__).resolve().parent
R = B/'results'
ROOT = R/'V199_PRIVATE_BASELINES'
OUT = R/'V199B_EXPECTILE_AUDIT'


def root(pg, pb, loss, alpha=.1, beta=.01):
    numerator = alpha*pg-beta*loss*pb
    denominator = (alpha*pg+beta*(1-pg) if numerator >= 0 else alpha*(1-pb)+beta*pb)
    return numerator/denominator


def main():
    assert (ROOT/'SUMMARY.json').exists() and not OUT.exists()
    OUT.mkdir()
    rng = np.random.default_rng(1997553)
    max_residual = 0.
    for _ in range(1000):
        pg, pb, _ = rng.dirichlet([1, 1, 1]); loss = float(rng.choice([1, 7]))
        value = root(pg, pb, loss)
        rewards = np.array([1., -loss, 0.]); probabilities = np.array([pg, pb, 1-pg-pb])
        errors = rewards-value
        drift = float(np.dot(probabilities, np.where(errors >= 0, .1, .01)*errors))
        max_residual = max(max_residual, abs(drift)); assert abs(drift) < 1e-12
        assert abs(root(pg, pb, loss, .1, .1)-(pg-loss*pb)) < 1e-12
    records = []
    for cohort in ['MAINTENANCE', 'FORMATION']:
        for k in [4, 8, 12]:
            for rule in ['UNANIMITY', 'MAJORITY']:
                folder = ROOT/f'{cohort}_k{k}_{rule}'
                context = np.load(folder/'CONTEXT.npz'); losses = context['losses']
                source = folder/'checkpoint_8000.npz'; data = np.load(source)
                j = int(np.flatnonzero(context['method_ids'] == 3)[0]); q = data['Q'][j]
                choice = (q[..., 1] > q[..., 0]).astype(float)+.5*(q[..., 1] == q[..., 0])
                h = k-1 if rule == 'UNANIMITY' else k//2
                raw = json.loads((folder/'HYSTERETIC.json').read_text(encoding='utf-8'))['history'][8]
                for epsilon in [0., .08]:
                    behavior = epsilon/2+(1-epsilon)*choice
                    target = np.zeros(q.shape); expectile = np.zeros(q.shape)
                    for w in range(32):
                        for g in range(20):
                            p_good = .8*behavior[w, g, :, 1]+.2*behavior[w, g, :, 0]
                            p_bad = .2*behavior[w, g, :, 1]+.8*behavior[w, g, :, 0]
                            for i in range(k-1):
                                approval_probabilities = []
                                for probs in [p_good, p_bad]:
                                    polynomial = np.array([1.])
                                    for other, p in enumerate(probs):
                                        if other != i:
                                            polynomial = np.convolve(polynomial, [1-p, p])
                                    approval_probabilities.append([float(polynomial[h-a:].sum()) for a in [0, 1]])
                                for s in range(2):
                                    likelihood = .8 if s else .2
                                    ps = .6*likelihood+.4*(1-likelihood)
                                    for a in range(2):
                                        pg = .6*likelihood*approval_probabilities[0][a]/ps
                                        pb = .4*(1-likelihood)*approval_probabilities[1][a]/ps
                                        target[w, g, i, s, a] = pg-losses[w, g, i]*pb
                                        expectile[w, g, i, s, a] = root(pg, pb, losses[w, g, i])
                    signal_mass = np.array([.44, .56])
                    current_state_value = (1-choice)*target[..., 0]+choice*target[..., 1]
                    current = (current_state_value*signal_mass).sum(-1)
                    actual_mixed = (((1-behavior)*target[..., 0]+behavior*target[..., 1])*signal_mass).sum(-1)
                    best = (target.max(-1)*signal_mass).sum(-1)
                    regret = best-current
                    assert regret.min() >= -1e-12
                    reference = raw['greedy_mean_welfare'] if epsilon == 0 else raw['native_mean_welfare']
                    error = abs(float(actual_mixed.mean())-reference); assert error < 1e-12
                    if rule == 'UNANIMITY':
                        assert np.max(np.abs(target[..., 0])) == 0 and best.min() >= -1e-12
                    mean_choice = (target[..., 1] > target[..., 0]).astype(float)+.5*(target[..., 1] == target[..., 0])
                    optimistic_choice = (expectile[..., 1] > expectile[..., 0]).astype(float)+.5*(expectile[..., 1] == expectile[..., 0])
                    rows = []
                    for loss in [1, 7]:
                        mask = losses == loss
                        weighted_disagreement = (np.abs(mean_choice-optimistic_choice)*signal_mass).sum(-1)
                        agreement_mean = (np.abs(choice-mean_choice)*signal_mass).sum(-1)
                        agreement_optimistic = (np.abs(choice-optimistic_choice)*signal_mass).sum(-1)
                        rows.append(dict(loss=loss, current_greedy_against_peer_law=float(current[mask].mean()),
                            best_unilateral_expected_payoff=float(best[mask].mean()),
                            fraction_people_with_negative_best_response_value=float((best[mask] < -1e-12).mean()),
                            mean_unilateral_regret=float(regret[mask].mean()),
                            signal_weighted_mean_expectile_choice_disagreement=float(weighted_disagreement[mask].mean()),
                            signal_weighted_actual_choice_disagreement_with_mean=float(agreement_mean[mask].mean()),
                            signal_weighted_actual_choice_disagreement_with_expectile=float(agreement_optimistic[mask].mean())))
                    name = f'{cohort}_k{k}_{rule}_PEER_EPS{int(epsilon*100):02d}'
                    np.savez_compressed(OUT/f'{name}.npz', mean_targets=target, expectile_targets=expectile,
                        best_response_private_payoff=best, current_private_payoff=current, losses=losses)
                    records.append(dict(cohort=cohort, k=k, rule=rule, peer_epsilon=epsilon, private_types=rows,
                        forward_payoff_parity_error=error, checkpoint_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                        analysis_is_posthoc=True))
    result = dict(analysis_is_posthoc=True, new_training_executed=False,
        stationary_scalar_fixed_point_algebra_is_known=True, root_residual_fixtures=1000, maximum_root_residual=max_residual,
        alpha=.1, beta=.01, expectile_tau=10/11,
        mean_dynamics_fixed_point_not_constant_gain_stationary_sample_mean=True,
        frozen_peers_are_a_diagnostic_not_original_learning_dynamics=True,
        majority_can_bind_a_voter_who_rejects_and_has_no_exit=True,
        records=records, CT2_historical=61, new_branch_score=None, N2=0, N3=0)
    (OUT/'SUMMARY.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k != 'records'}), flush=True)
    for row in records:
        if row['peer_epsilon'] == 0:
            print('V199B', row['cohort'], row['k'], row['rule'], 'HIGH_RISK', json.dumps(row['private_types'][1]), flush=True)


if __name__ == '__main__':
    print('LIMITS', apply_limits(2), flush=True)
    main()
