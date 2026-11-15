"""Generated V183 intervention, see v183_build_kernel.py and preregistration.
Original-order branch must pass V182 cross-language fixtures before experiments.
"""
import numpy as np
from numba import njit
from v182_yaman_kernel import _perm, _rand, _choose, _sanction

@njit(cache=True)
def lifetime_timing(matrix, env, T, alpha, seed, game,
             p3, p4, p10, uniforms, replay=False, attack_first=False):
    """game=0 settlement, 1 pasture. Roles returned as zero-based indices."""
    np.random.seed(seed)
    ntype = matrix.shape[0]
    q = np.full((10, 10, ntype), 10.)
    field = np.full((10, 10), 0. if game == 0 else 100.)
    phi, field_trend, attack_trend = np.zeros(T), np.zeros(T), np.zeros(T)
    role_trend = np.zeros((ntype, T), dtype=np.int64)
    total, used = np.zeros((ntype, ntype)), np.zeros((ntype, ntype))
    counters = np.zeros(4, dtype=np.int64)
    nrew, npun = 0, 0
    insurance_actual, insurance_expected = np.zeros(T), np.zeros(T)
    max_conservation, max_identity = 0., 0.
    role = np.zeros((10, 10), dtype=np.int64)
    for t in range(T):
        role = _choose(q, p3, p4, p10, uniforms, counters, replay)
        pay = np.zeros((10, 10))
        if game == 0:
            for i in range(10):
                for j in range(10):
                    if role[i, j] == 1:
                        pay[i, j] = 3.
                    elif role[i, j] == 2:
                        hunters = 0
                        for di in range(-1, 2):
                            for dj in range(-1, 2):
                                if role[(i+di) % 10, (j+dj) % 10] == 2:
                                    hunters += 1
                        if hunters >= 5:
                            pay[i, j] = 6.
                    pay[i, j] = max(0., pay[i, j] - field[i, j])
        else:
            for i in range(10):
                for j in range(10):
                    growth = env[0] * .5
                    if role[i, j] == 2:
                        growth += env[1] * .5
                    # Preserve the expression evaluation order in MATLAB.
                    dres = growth * field[i, j] * (1. - field[i, j] / 100.)
                    field[i, j] += dres
            ir = _perm(10, p3, p4, p10, uniforms, counters, replay)
            jr = _perm(10, p3, p4, p10, uniforms, counters, replay)
            for i in ir:
                for j in jr:
                    use = 10. if role[i, j] == 0 else (5. if role[i, j] == 1 else 0.)
                    if use == 0:
                        continue
                    ris = _perm(3, p3, p4, p10, uniforms, counters, replay)
                    rjs = _perm(3, p3, p4, p10, uniforms, counters, replay)
                    for oi in ris:
                        ii = (i + oi - 1) % 10
                        for oj in rjs:
                            if use == 0:
                                break
                            jj = (j + oj - 1) % 10
                            if field[ii, jj] > 0:
                                if use <= field[ii, jj]:
                                    field[ii, jj] -= use
                                    pay[i, j] += use
                                    use = 0.
                                else:
                                    use -= field[ii, jj]
                                    pay[i, j] += field[ii, jj]
                                    field[ii, jj] = 0.
                        if use == 0:
                            break
        # Intervention: move only material destruction before transfers.
        # Replay's separate uniform/permutation streams preserve exogenous draws.
        base_pay = pay.copy()
        protection_mask = np.zeros((10, 10), dtype=np.bool_)
        survive = np.ones((10, 10), dtype=np.bool_)
        attacks_before = 0
        if game == 0:
            for i in range(10):
                for j in range(10):
                    for di in range(-1, 2):
                        for dj in range(-1, 2):
                            if role[(i+di) % 10, (j+dj) % 10] == 3:
                                protection_mask[i, j] = True
            if attack_first:
                assert replay, 'Matched intervention requires separate RNG tapes'
                for i in range(10):
                    for j in range(10):
                        coin = _rand(p3, p4, p10, uniforms, counters, replay)
                        if coin < env[1] and not protection_mask[i, j]:
                            survive[i, j] = False
                            if pay[i, j] > 0:
                                attacks_before += 1
                            pay[i, j] = 0.
        pre_transfer_total = np.sum(pay)
        nr, np_ = _sanction(pay, role, matrix, total, used, game == 0,
                           p3, p4, p10, uniforms, counters, replay)
        max_conservation = max(max_conservation, abs(np.sum(pay)-pre_transfer_total))
        delta_before_hazard = pay - base_pay
        nrew += nr
        npun += np_
        if game == 0:
            waste_max = env[0] * 6.
            for i in range(10):
                for j in range(10):
                    field[i, j] = min(waste_max, field[i, j] + waste_max / 10.)
            attacks = 0
            for i in range(10):
                for j in range(10):
                    if role[i, j] == 0:
                        for di in range(-1, 2):
                            for dj in range(-1, 2):
                                field[(i+di) % 10, (j+dj) % 10] = 0.
                    if not attack_first:
                        if _rand(p3, p4, p10, uniforms, counters, replay) < env[1]:
                            if not protection_mask[i, j]:
                                survive[i, j] = False
                                if pay[i, j] > 0:
                                    pay[i, j] = 0.
                                    attacks += 1
            attack_trend[t] = attacks_before if attack_first else attacks
            insurance_actual[t] = (np.sum(pay)-np.sum(base_pay*survive))/100.
            if not attack_first:
                insurance_expected[t] = env[1]*np.sum(protection_mask*delta_before_hazard)/100.
                identity_right = np.sum(survive*delta_before_hazard)/100.
            else:
                identity_right = 0.
            max_identity = max(max_identity, abs(insurance_actual[t]-identity_right))
        for i in range(10):
            for j in range(10):
                a = role[i, j]
                q[i, j, a] = q[i, j, a] + alpha * (pay[i, j] - q[i, j, a])
                role_trend[a, t] += 1
        phi[t] = np.mean(pay)
        field_trend[t] = np.mean(field)
    ratio = np.zeros((ntype, ntype))
    for a in range(ntype):
        for b in range(ntype):
            if total[a, b] > 0:
                ratio[a, b] = used[a, b] / total[a, b]
    return phi, field_trend, attack_trend, role_trend, role, ratio, nrew, npun, counters, insurance_actual, insurance_expected, max_conservation, max_identity

