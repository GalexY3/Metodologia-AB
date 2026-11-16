"""Freeze prospectively; no scientific flow evaluations are performed here."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import platform
import shutil
import numpy
import scipy
import numba

B = Path(__file__).resolve().parent
FILES = [
    'v203_exact_gradient.py', 'audit_v203_exact_gradient.py',
    'audit_v203_mixture.py', 'run_v203_exact_flows.py',
    'V203_HISTORY_INVARIANCE_LEMMA.md', 'PREREG_V203_EXACT_GRADIENT_FLOWS.md',
    'v202_relational_learning.py', 'v202_exact_evaluation.py',
    'research_resource_limits.py', 'prepare_v203_registration.py',
    'results/V203_PRE_INTEGRATION_AUDIT.json',
    'results/V203_MIXTURE_GRADIENT_AUDIT.json',
]


def main():
    assert not (B/'results/V203_EXACT_GRADIENT_FLOWS').exists()
    folder = B/'research/V203_20261116'
    folder.mkdir(exist_ok=False)
    hashes = {}
    for name in FILES:
        data = (B/name).read_bytes()
        hashes[name] = hashlib.sha256(data).hexdigest()
        dest = folder/'registered_sources'/name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(B/name, dest)
    manifest = dict(study='V203', stage='PROSPECTIVE_BEFORE_ODE_INTEGRATIONS',
        timestamp_utc=datetime.now(timezone.utc).isoformat(), source_sha256=hashes,
        software=dict(python=platform.python_version(), numpy=numpy.__version__,
                      scipy=scipy.__version__, numba=numba.__version__),
        scientific_integrations_executed=False, oracle_not_private_learner=True,
        independent_worlds=0, deterministic_sensitivity_cases=20,
        additional_precision_runs=4, CT2_historical=61, new_branch_score=None,
        N2=0, N3=0)
    (folder/'REGISTRATION_MANIFEST.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    publication = []
    for p in sorted(folder.rglob('*')):
        if p.is_file():
            publication.append(dict(local=str(p), path=p.relative_to(B).as_posix(),
                bytes=p.stat().st_size, sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    (folder/'REGISTRATION_FILES.json').write_text(json.dumps(publication, indent=2), encoding='utf-8')
    print(json.dumps(dict(files=len(publication), source_sha256=hashes,
                          software=manifest['software']), indent=2))


if __name__ == '__main__':
    main()
