"""Explicit immutable evidence archive, preserving both experiment namespaces."""
from pathlib import Path
import hashlib
import json
import re
import zipfile
from research_resource_limits import apply_limits

B = Path(__file__).resolve().parent
OUT = B/'research/V195_V198_20261115'
MAX_RAW = 40000000


def main():
    OUT.mkdir(exist_ok=False)
    files, direct = set(), set()

    def add(relative, publish=True):
        p = (B/relative).resolve()
        assert p.is_relative_to(B.resolve()) and p.is_file(), relative
        files.add(p)
        if publish:
            direct.add(p)

    for path in ['v195_withdraw_counterfactual.py', 'make_v195_withdraw_registration.py',
        'verify_v195_withdraw_registration.py', 'audit_v195_withdraw_numpy.py', 'close_v195_withdraw.py',
        'audit_v197_tie_screen.py', 'v197_tie_policy_audit.py', 'v198_voting_expected_drift.py',
        'register_v198_expected_drift.py', 'audit_v198_voting_numpy.py', 'close_v197_v198.py',
        'stage_v195_v198_reproduction.py', 'archive_v195_v198.py', 'publish_v195_v198.py',
        'verify_v195_v198_evidence.py', 'audit_v192_numpy.py', 'REPRODUCE_V195_V198.md',
        'PREREG_V195_WITHDRAW_COUNTERFACTUAL.md', 'PREREG_V198_VOTING_EXPECTED_DRIFT.md',
        'docs/TFM_CAPITULO_RETIRADA_FEEDBACK_V195.md', 'docs/TFM_CAPITULO_DERIVA_Y_RUIDO_V197_V198.md',
        'docs/TFM_MANUSCRITO_TRABAJO_V195.md', 'docs/TFM_MANUSCRITO_TRABAJO_V198.md',
        'handoff_codex/ESTADO_20261115_V195_WITHDRAW.md', 'handoff_codex/ESTADO_20261115_V198.md',
        'literatura/V195_V198_REFERENCIAS_Y_LIMITES.json']:
        add(path)
    for receipt in ['results/V195_WITHDRAW_PREREG_RECEIPT.json', 'results/V198_EXPECTED_DRIFT_PREREG_RECEIPT.json']:
        info = json.loads((B/receipt).read_text(encoding='utf-8'))
        for path in info['source_sha256']:
            add(path, publish=(B/path).suffix not in ['.npz', '.pt'])
        for path in info['binary_parent_sha256']:
            add(path, publish=False)
    for folder in ['V195_WITHDRAW_COUNTERFACTUAL', 'V198_VOTING_EXPECTED_DRIFT',
                   'V194_PRIVATE_INFORMATION_LEARNING', 'V195_CORRELATED_EXPLORATION', 'V196_POST_PULSE_PLASTICITY']:
        for p in (B/'results'/folder).rglob('*'):
            if p.is_file():
                add(p.relative_to(B), publish=p.name == 'SUMMARY.json')
    for pattern in ['V195_WITHDRAW*', 'V195_ALIGNMENT*', 'V197_TIE*', 'V198*', 'V195_V198_DOCUMENT_QA.json', 'V195_V198_QA*']:
        for p in (B/'results').glob(pattern):
            if p.is_file():
                add(p.relative_to(B), publish=p.suffix not in ['.log'])
    for path in ['results/INFORME_V195_WITHDRAW_COUNTERFACTUAL_20261115.md',
        'results/INFORME_V197_V198_RUIDO_Y_DERIVA_20261115.md', 'results/ERRATA_V195_V196_TIE_POLICY_20261115.md',
        'results/FIG_V195_WITHDRAW_COUNTERFACTUAL.png', 'results/FIG_V198_MEAN_VS_SAMPLED_PRIVATE_Q.png',
        'v194_learned_information_institutions.py', 'v194a_exact_frozen_private_voting.py',
        'v195_joint_signal_policy_exploration.py', 'v195a_analytic_private_policy_audit.py',
        'v196_plastic_no_pulse_maintenance.py', 'audit_v194_v196_research_archive.py',
        'PREREG_V194_PRIVATE_ENDOGENOUS_INFORMATION_VOTE.md', 'PREREG_V194A_EXACT_FROZEN_STRATEGIC_AUDIT.md',
        'PREREG_V195_CORRELATED_PRIVATE_EXPLORATION.md', 'PREREG_V195A_EXACT_NO_PULSE_VALIDATION.md',
        'PREREG_V196_PLASTIC_MAINTENANCE_AFTER_EXPLORATION.md',
        'results/INFORME_V194_V196_CREDIT_SCALING_AND_MAINTENANCE.md',
        'results/V194_V196_ARCHIVE_AUDIT_20261115.json',
        'results/FIG_V195_COORDINATION_VS_INDEPENDENT_EXPLORATION.png',
        'results/FIG_V196_COORDINATION_MAINTENANCE_K12_UNANIMITY.png',
        'HANDOFF_CHATGPT_GOAL_V194_V196_20261115.md']:
        add(path)
    add('results/AB_PROGRESO_CT2_CT3.json', publish=False)
    for manuscript in ['docs/TFM_MANUSCRITO_TRABAJO_V195.md', 'docs/TFM_MANUSCRITO_TRABAJO_V198.md']:
        p = B/manuscript
        for link in re.findall(r'!\[[^\]]*\]\(([^)]+)\)', p.read_text(encoding='utf-8')):
            if '://' not in link:
                add((p.parent/link).resolve().relative_to(B.resolve()))
    readme = OUT/'README.md'
    readme.write_text('''# Evidencia V195 neuronal, V197 y V198

Extraer todos los EVIDENCE_XX.zip juntos en una carpeta vacía. Incluye código, recibos anteriores a los experimentos nuevos, datos/padres, pesos y momentos, políticas de votación, resultados negativos y la corrección de desempates. Cada shard tiene manifiesto interno; el global enumera todos los payloads.

V195_WITHDRAW retira FULL después de memorizar y pasa4/4. V197 corrige72políticas sin cambiar el fracaso principal V196. V198 conserva bienestar bajo deriva media, un diagnóstico ORÁCULO que no constituye un aprendiz privado realizable. No acredita originalidad2/3 ni aumenta61. Los identificadores reutilizados se distinguen por sus nombres y hashes.

Se preservan como procedencia los resultados originales V194–V196 de votación, sin sobrescribirlos. Su informe previo requiere la fe de erratas V197 para los extremos recalculados; la reproducción técnica antigua no convierte aquella aproximación de empate en una ley exacta del entrenador. No se incluyen PDF de terceros. El snapshot del progreso histórico no se publica como modificación de ese archivo de trabajo. Leer REPRODUCE_V195_V198.md.
''', encoding='utf-8')
    add(readme.relative_to(B))
    hashes = {p.relative_to(B).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}
    (OUT/'EVIDENCE_PAYLOAD_SHA256.json').write_text(json.dumps(hashes, indent=2, ensure_ascii=False), encoding='utf-8')
    groups, current, size = [], [], 0
    for p in sorted(files):
        length = p.stat().st_size
        assert length < MAX_RAW
        if current and size+length > MAX_RAW:
            groups.append(current); current, size = [], 0
        current.append(p); size += length
    if current:
        groups.append(current)
    shards = []
    for number, payloads in enumerate(groups, 1):
        path = OUT/f'EVIDENCE_{number:02d}.zip'
        sub = {p.relative_to(B).as_posix(): hashes[p.relative_to(B).as_posix()] for p in payloads}
        key = f'EVIDENCE_SHARD_{number:02d}_PAYLOAD_SHA256.json'
        with zipfile.ZipFile(path, 'x', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
            for p in payloads:
                z.write(p, p.relative_to(B).as_posix())
            z.writestr(key, json.dumps(sub, indent=2, ensure_ascii=False))
        with zipfile.ZipFile(path) as z:
            assert z.testzip() is None
            for item, expected in sub.items():
                assert hashlib.sha256(z.read(item)).hexdigest() == expected
        shards.append(dict(archive=path.name, bytes=path.stat().st_size,
            sha256=hashlib.sha256(path.read_bytes()).hexdigest(), payload_files=len(payloads),
            CRC_verified=True, all_payload_hashes_verified=True))
        direct.add(path)
    manifest = dict(shards=shards, total_payload_files=len(files), total_payload_bytes=sum(p.stat().st_size for p in files),
                    original_sources_and_negative_results_preserved=True, mutable_operation_logs_excluded=True,
                    independent_scientific_replication_claimed=False, canonical_score_not_edited=True)
    (OUT/'ARCHIVE_MANIFEST.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    direct |= {OUT/'ARCHIVE_MANIFEST.json', OUT/'EVIDENCE_PAYLOAD_SHA256.json'}
    paths = sorted(p.relative_to(B).as_posix() for p in direct)
    paths.append((OUT/'PUBLICATION_FILES.json').relative_to(B).as_posix())
    (OUT/'PUBLICATION_FILES.json').write_text(json.dumps(paths, indent=2), encoding='utf-8')
    print(json.dumps(dict(**manifest, direct_publication_files=len(paths))), flush=True)


if __name__ == '__main__':
    print('LIMITS', apply_limits(2), flush=True)
    main()
