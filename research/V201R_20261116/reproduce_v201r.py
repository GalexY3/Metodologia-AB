"""Reproduce the mathematical audit in a fresh directory without changing sources."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys

B = Path(__file__).resolve().parent
STEPS = ['v201r_theory_precheck.py', 'v201r_single_agent_bellman.py',
         'v201r_capital_coalition_audit.py', 'v201r_relational_certificate.py',
         'audit_v201r_capital_bounds.py', 'analyze_v201r_controls.py']
OUTPUTS = ['V201R_THEORY_PRECHECK.json', 'V201R_SINGLE_AGENT_BELLMAN.json',
           'V201R_CAPITAL_COALITION_AUDIT.json', 'V201R_RELATIONAL_CERTIFICATES.json',
           'V201R_CAPITAL_BOUND_INDEPENDENT_AUDIT.json', 'V201R_SCIENTIFIC_SYNTHESIS.json']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--destination', required=True)
    args = parser.parse_args()
    destination = Path(args.destination).resolve()
    assert not destination.exists(), 'Fresh destination required; nothing is removed or overwritten.'
    destination.mkdir(parents=True)
    (destination/'results').mkdir()
    inputs = Path('theory_inputs/HYDROGEN_V201R_20261116')
    (destination/inputs).mkdir(parents=True)
    for script in STEPS+['research_resource_limits.py']:
        shutil.copy2(B/script, destination/script)
    for name in ['HYDROGEN_V201R_RECONSTRUCTION.txt']:
        shutil.copy2(B/inputs/name, destination/inputs/name)
    receipts = []
    for script in STEPS:
        logfile = destination/'results'/f'{Path(script).stem}_REPRODUCE.log'
        with logfile.open('wb') as stream:
            completed = subprocess.run([sys.executable, '-X', 'utf8', script],
                cwd=destination, stdout=stream, stderr=subprocess.STDOUT, check=False)
        receipts.append(dict(script=script, exit_code=completed.returncode))
        print(json.dumps(receipts[-1]), flush=True)
        assert completed.returncode == 0, str(logfile)
    comparisons = []
    for name in OUTPUTS:
        old = B/'results'/name; new = destination/'results'/name
        same = json.loads(old.read_text(encoding='utf-8')) == json.loads(new.read_text(encoding='utf-8'))
        comparisons.append(dict(file=name, all_JSON_values_identical=same,
            original_sha256=hashlib.sha256(old.read_bytes()).hexdigest(),
            reproduced_sha256=hashlib.sha256(new.read_bytes()).hexdigest()))
        assert same, name
    receipt = dict(reproduction='PASS', fresh_directory=str(destination),
        script_runs=receipts, comparisons=comparisons,
        scientific_external_replication=False,
        limits='Same machine, same installed libraries, same author; a fresh staging reproduction, not independent evidence.')
    (B/'results/V201R_FRESH_REPRODUCTION.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
