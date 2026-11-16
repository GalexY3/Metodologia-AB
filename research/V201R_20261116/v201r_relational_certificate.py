"""Exact fixed-capital public-monitoring equilibrium controls.

This repairs, rather than implements, Hydrogen's proposed policy. Roles,
capital and partners are fixed. Everyone publicly observes the payment count
after a successful joint production. A public grim state switches EVERYONE
to AUTARKY after insufficient payments, and never resets on nonsuccess.
The strategy is programmed for a certificate; it is not a learned institution.
"""
from fractions import Fraction as F
from pathlib import Path
import itertools
import json
import math
from research_resource_limits import apply_limits

B = Path(__file__).resolve().parent
PI, A, BETA = F(13, 20), F(4, 5), F(19, 20)
TAU, PREP = F(1, 4), F(3, 10)
POLICIES = list(itertools.product([0, 1], repeat=2))


def probability_good(s):
    likelihood = A if s else 1-A
    return PI*likelihood/(PI*likelihood+(1-PI)*(1-likelihood))


def probs(policy):
    return (F(1, 5)*policy[0]+F(4, 5)*policy[1],
            F(4, 5)*policy[0]+F(1, 5)*policy[1])


def mode_coefficients(losses, profile, donors, i, s):
    pg = probability_good(s)
    pb = 1-pg
    for j in range(4):
        if j != i:
            qg, qb = probs(profile[j]); pg *= qg; pb *= qb
    net = TAU*len(donors) if i == 3 else -TAU*int(i in donors)
    return pg*F(4, 5)-pb*F(1, 4), pg*net-pb*losses[i]-PREP*int(i == 3)


def rent_coefficients(losses, profile, donors, i):
    pg, pb = PI, 1-PI
    for policy in profile:
        qg, qb = probs(policy); pg *= qg; pb *= qb
    qg, qb = probs(profile[i])
    net = TAU*len(donors) if i == 3 else -TAU*int(i in donors)
    return pg*F(4, 5)-pb*F(1, 4), pg*net-pb*losses[i]-PREP*int(i == 3)*(PI*qg+(1-PI)*qb)


def restrict(interval, coefficient, constant):
    """Intersect with coefficient*f+constant >= 0, using exact rationals."""
    lo, hi = interval
    if coefficient == 0:
        return (lo, hi) if constant >= 0 else (F(1), F(0))
    root = -constant/coefficient
    return (max(lo, root), hi) if coefficient > 0 else (lo, min(hi, root))


def certified_interval(losses, profile, donors):
    interval = (F(1, 5), F(1))  # optional autarkic work is individually rational
    for i in range(4):
        for s in [0, 1]:
            a, b = mode_coefficients(losses, profile, donors, i, s)
            sign = 1 if profile[i][s] else -1
            interval = restrict(interval, sign*a, sign*b)
    for i in donors:
        a, b = rent_coefficients(losses, profile, donors, i)
        interval = restrict(interval, BETA*a/(1-BETA), BETA*b/(1-BETA)-TAU)
    return interval


def explicit_rents(stock, losses, profile, donors):
    """Independent enumeration of the 2*16 hidden-state/signal outcomes."""
    y = .25*(-math.expm1(-stock))
    total = [0.]*4
    for good in [0, 1]:
        for signals in itertools.product([0, 1], repeat=4):
            probability = float(PI if good else 1-PI)
            choices = [profile[i][signals[i]] for i in range(4)]
            for s in signals:
                probability *= (.8 if s else .2) if good else (.2 if s else .8)
            for i in range(4):
                reward = y-.05
                if all(choices):
                    reward = (y+.8*(-math.expm1(-stock)) if good else -losses[i])-.05
                    if good:
                        reward += .25*len(donors) if i == 3 else -.25*int(i in donors)
                if i == 3 and choices[i]:
                    reward -= .30
                total[i] += probability*(reward-(y-.05))
    return total


def record_interval(losses, profile, donors, interval):
    lo, hi = interval
    return dict(losses=list(losses), policies=[list(p) for p in profile], donors=list(donors),
        payment_threshold=len(donors), lower_f_exact=str(lo), upper_f_exact=str(hi),
        lower_f=float(lo), upper_f=float(hi),
        stock_min=-math.log1p(-float(lo)),
        stock_max=-math.log1p(-float(hi)) if hi < 1 else None,
        upper_f_one_is_excluded=True)


def main():
    destination = B/'results/V201R_RELATIONAL_CERTIFICATES.json'
    assert not destination.exists()
    certificates, checks, max_error = [], 0, 0.
    for losses in itertools.product([1, 7], repeat=4):
        for n in [2, 3]:
            for donors in itertools.combinations(range(3), n):
                for profile in itertools.product(POLICIES, repeat=4):
                    if not all(any(p) for p in profile):
                        continue
                    interval = certified_interval(losses, profile, donors)
                    lo, hi = interval
                    if lo >= hi or lo >= 1:
                        continue
                    row = record_interval(losses, profile, donors, interval)
                    certificates.append(row)
                    f = float((lo+hi)/2); stock = -math.log1p(-f)
                    rents = explicit_rents(stock, losses, profile, donors)
                    for i, rent in enumerate(rents):
                        a, b = rent_coefficients(losses, profile, donors, i)
                        error = abs(rent-(float(a)*f+float(b)))
                        max_error = max(max_error, error); checks += 1
                        assert error < 1e-12
                        if i in donors:
                            assert float(BETA/(1-BETA))*rent >= float(TAU)-1e-12
    reference = []
    for gamma in [.105, .05, .005]:
        stock = math.log(.2375/(.05+.95*gamma)); f = -math.expm1(-stock)
        valid = [r for r in certificates if r['losses'] == [1, 1, 7, 7]
                 and r['lower_f'] <= f <= r['upper_f']]
        reference.append(dict(gamma=gamma, stock_reference_only_not_endogenous=stock,
            public_grim_fixed_stock_certificate_count=len(valid), certificates=valid))
    result = dict(audit_of_a_repair_not_the_original_policy=True,
        strategy='C initially. On successful GOOD joint production retain C iff T>=number_of_designated_donors. Otherwise retain C. Below threshold switch publicly and permanently to P. In P everybody selects AUTARKY and no transfers.',
        assumptions=['Public common-knowledge payment count after a successful production',
            'Fixed capital and role identities; no depreciation, investment, migration or role switching in this control',
            'IID private signals conditional on IID hidden states; stationary publicly known losses',
            'Two designated donors/threshold two, or three designated donors/threshold three',
            'Punishment AUTARKY is a weak stage equilibrium under unanimity; all players observe the public state',
            'No automatic transfer, fine or capital destruction, but the contingent strategy itself is imposed'],
        covered_deviations=['Every conditional mode decision in C', 'Every donor withholding decision after GOOD joint production',
            'Unilateral mode deviations in P; only the critical incurs an extra preparation cost',
            'Nonpayers making an unnecessary payment cannot improve continuation'],
        proof_scope='One-shot deviation certificate for this bounded discounted stationary fixed-capital public-history game. NOT the original private-monitoring model or the full capital/mobility game.',
        all_16_loss_allocations_checked=True, rational_inequalities=True,
        interval_certificates=certificates, certificate_count=len(certificates),
        independent_enumerated_rent_checks=checks, independent_max_error=max_error,
        original_reference_stocks=reference,
        learned_institution=False, original_three_donors_threshold_two_not_certified=True,
        does_not_establish_a_gamma_band=True, CT2_historical=61, new_branch_score=None, N2=0, N3=0)
    destination.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(dict(certificate_count=len(certificates), checks=checks, error=max_error,
        reference_counts=[(r['gamma'], r['public_grim_fixed_stock_certificate_count']) for r in reference]), indent=2), flush=True)


if __name__ == '__main__':
    print('LIMITS', apply_limits(2), flush=True)
    main()
