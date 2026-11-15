"""Faithful epsilon=0 lifetime physics from Yaman et al. (2023), CC0 archive.

Ported from game_settlement.m and game_pasture.m, not from the prose alone.
Original grid size, optimistic Q=10, randomized tie breaking, Cartesian actor
orders, sequential budget-limited transfers, update timing and 101-step score.
This module does NOT port the faulty archived pasture outer GA. It evaluates
fixed original norms. RNG laws match; seed sequences do not match MATLAB.
Replay mode consumes explicit permutations/uniforms for cross-language checks.
"""
import numpy as np
from numba import njit


@njit(cache=True)
def _perm(n, p3, p4, p10, uniforms, counters, replay):
    if not replay:
        return np.random.permutation(n)
    if n == 3:
        ix = counters[0]
        counters[0] += 1
        return p3[ix].copy()
    if n == 4:
        ix = counters[1]
        counters[1] += 1
        return p4[ix].copy()
    ix = counters[2]
    counters[2] += 1
    return p10[ix].copy()


@njit(cache=True)
def _rand(p3, p4, p10, uniforms, counters, replay):
    if not replay:
        return np.random.random()
    ix = counters[3]
    counters[3] += 1
    return uniforms[ix]


@njit(cache=True)
def _choose(q, p3, p4, p10, uniforms, counters, replay):
    roles = np.empty((10, 10), dtype=np.int64)
    ntype = q.shape[2]
    for i in range(10):
        for j in range(10):
            order = _perm(ntype, p3, p4, p10, uniforms, counters, replay)
            choice = order[0]
            for k in range(1, ntype):
                if q[i, j, order[k]] > q[i, j, choice]:
                    choice = order[k]
            # The original consumes a rand even with epsilon=0.
            _rand(p3, p4, p10, uniforms, counters, replay)
            roles[i, j] = choice
    return roles


@njit(cache=True)
def _sanction(pay, role, matrix, total, used, clip,
              p3, p4, p10, uniforms, counters, replay):
    ir = _perm(10, p3, p4, p10, uniforms, counters, replay)
    jr = _perm(10, p3, p4, p10, uniforms, counters, replay)
    nrew, npun = 0, 0
    for i in ir:
        for j in jr:
            a = role[i, j]
            ris = _perm(3, p3, p4, p10, uniforms, counters, replay)
            for oi in ris:
                di = oi - 1
                ii = (i + di) % 10
                rjs = _perm(3, p3, p4, p10, uniforms, counters, replay)
                for oj in rjs:
                    dj = oj - 1
                    if di == 0 and dj == 0:
                        continue
                    jj = (j + dj) % 10
                    b = role[ii, jj]
                    out = matrix[a, b]
                    if clip:
                        out = min(5., max(-5., out))
                    if out == 0:
                        continue
                    total[a, b] += 1
                    if out > 0 and pay[i, j] >= out:
                        used[a, b] += 1
                        pay[i, j] -= out
                        pay[ii, jj] += out
                        nrew += 1
                    elif out < 0 and pay[ii, jj] >= abs(out):
                        used[a, b] += 1
                        pay[i, j] += abs(out)
                        pay[ii, jj] -= abs(out)
                        npun += 1
    return nrew, npun


@njit(cache=True)
def lifetime(matrix, env, T, alpha, seed, game,
             p3, p4, p10, uniforms, replay=False):
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
        nr, np_ = _sanction(pay, role, matrix, total, used, game == 0,
                           p3, p4, p10, uniforms, counters, replay)
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
                    if _rand(p3, p4, p10, uniforms, counters, replay) < env[1]:
                        protected = False
                        for di in range(-1, 2):
                            for dj in range(-1, 2):
                                if role[(i+di) % 10, (j+dj) % 10] == 3:
                                    protected = True
                        if not protected and pay[i, j] > 0:
                            pay[i, j] = 0.
                            attacks += 1
            attack_trend[t] = attacks
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
    return phi, field_trend, attack_trend, role_trend, role, ratio, nrew, npun, counters


def empty_tape():
    return (np.zeros((1, 3), dtype=np.int64), np.zeros((1, 4), dtype=np.int64),
            np.zeros((1, 10), dtype=np.int64), np.zeros(1))


def make_tape(T, seed):
    rng = np.random.default_rng(seed)
    return (np.argsort(rng.random((T*710, 3)), axis=1).astype(np.int64),
            np.argsort(rng.random((T*110, 4)), axis=1).astype(np.int64),
            np.argsort(rng.random((T*5, 10)), axis=1).astype(np.int64), rng.random(T*210))
