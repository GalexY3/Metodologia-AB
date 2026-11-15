"""Produce an inspectable timing intervention without editing frozen V182 code."""
from pathlib import Path
import hashlib
import json

BASE = Path(__file__).resolve().parent


def main():
    original = (BASE / 'v182_yaman_kernel.py').read_text(encoding='utf-8')
    start = original.index('@njit(cache=True)\ndef lifetime(')
    end = original.index('\n\ndef empty_tape()', start)
    function = original[start:end]
    function = function.replace('def lifetime(', 'def lifetime_timing(', 1)
    function = function.replace('uniforms, replay=False):', 'uniforms, replay=False, attack_first=False):', 1)
    function = function.replace('    nrew, npun = 0, 0\n', '''    nrew, npun = 0, 0
    insurance_actual, insurance_expected = np.zeros(T), np.zeros(T)
    max_conservation, max_identity = 0., 0.
''', 1)
    marker = '        nr, np_ = _sanction(pay, role, matrix, total, used, game == 0,\n'
    assert function.count(marker) == 1
    function = function.replace(marker, '''        # Intervention: move only material destruction before transfers.
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
''' + marker, 1)
    marker = '        nrew += nr\n'
    function = function.replace(marker, '''        max_conservation = max(max_conservation, abs(np.sum(pay)-pre_transfer_total))
        delta_before_hazard = pay - base_pay
''' + marker, 1)
    old = '''                    if _rand(p3, p4, p10, uniforms, counters, replay) < env[1]:
                        protected = False
                        for di in range(-1, 2):
                            for dj in range(-1, 2):
                                if role[(i+di) % 10, (j+dj) % 10] == 3:
                                    protected = True
                        if not protected and pay[i, j] > 0:
                            pay[i, j] = 0.
                            attacks += 1
            attack_trend[t] = attacks
'''
    assert function.count(old) == 1
    new = '''                    if not attack_first:
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
'''
    function = function.replace(old, new, 1)
    old = '    return phi, field_trend, attack_trend, role_trend, role, ratio, nrew, npun, counters'
    assert function.count(old) == 1
    function = function.replace(old, old + ', insurance_actual, insurance_expected, max_conservation, max_identity', 1)
    header = '''"""Generated V183 intervention, see v183_build_kernel.py and preregistration.
Original-order branch must pass V182 cross-language fixtures before experiments.
"""
import numpy as np
from numba import njit
from v182_yaman_kernel import _perm, _rand, _choose, _sanction

'''
    output = BASE / 'v183_yaman_timing_kernel.py'
    assert not output.exists(), output
    output.write_text(header+function+'\n', encoding='utf-8')
    record = dict(original_sha256=hashlib.sha256((BASE/'v182_yaman_kernel.py').read_bytes()).hexdigest(),
                  intervention_sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
                  generated_by='v183_build_kernel.py', original_kernel_modified=False)
    (BASE/'results/V183_KERNEL_DERIVATION.json').write_text(json.dumps(record, indent=2), encoding='utf-8')
    print(json.dumps(record), flush=True)


if __name__ == '__main__':
    main()
