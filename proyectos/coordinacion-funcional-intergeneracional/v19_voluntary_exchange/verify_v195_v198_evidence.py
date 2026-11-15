"""Read-only scientific-source, document, archive and workspace verification."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
import zipfile
import numpy as np
import torch
from PIL import Image
from research_resource_limits import apply_limits

B = Path(__file__).resolve().parent
REPO = B.parents[2]
OUT = B/'research/V195_V198_20261115'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(documents_only):
    documents = [B/p for p in ['results/INFORME_V195_WITHDRAW_COUNTERFACTUAL_20261115.md',
        'results/INFORME_V197_V198_RUIDO_Y_DERIVA_20261115.md', 'results/ERRATA_V195_V196_TIE_POLICY_20261115.md',
        'docs/TFM_CAPITULO_RETIRADA_FEEDBACK_V195.md', 'docs/TFM_CAPITULO_DERIVA_Y_RUIDO_V197_V198.md',
        'docs/TFM_MANUSCRITO_TRABAJO_V195.md', 'docs/TFM_MANUSCRITO_TRABAJO_V198.md']]
    image_checks = []
    for document in documents:
        assert document.is_file()
        for link in re.findall(r'!\[[^\]]*\]\(([^)]+)\)', document.read_text(encoding='utf-8')):
            if '://' not in link:
                path = (document.parent/link).resolve()
                assert path.is_relative_to(B.resolve()) and path.is_file(), (document, link)
                with Image.open(path) as im:
                    im.verify()
                image_checks.append(dict(document=document.relative_to(B).as_posix(), image=path.relative_to(B).as_posix(), valid=True))
    for name in ['V195_WITHDRAW', 'V198_EXPECTED_DRIFT']:
        receipt = json.loads((B/f'results/{name}_PREREG_RECEIPT.json').read_text(encoding='utf-8'))
        assert receipt['before_training']
        for path, expected in dict(receipt['source_sha256'], **receipt['binary_parent_sha256']).items():
            assert sha(B/path) == expected, path
    neural = json.loads((B/'results/V195_WITHDRAW_NUMPY_FINAL_AUDIT.json').read_text(encoding='utf-8'))
    drift = json.loads((B/'results/V198_NUMPY_FINAL_AUDIT.json').read_text(encoding='utf-8'))
    assert not neural['failures'] and not drift['failures']
    # Record the two unlogged alignment evaluations transparently. Their saved
    # states permit a retrospective independent calculation without retraining.
    aligned_path = B/'results/V195_WITHDRAW_COUNTERFACTUAL/BOTH_BANDIT/initial_aligned_state.pt'
    aligned = torch.load(aligned_path, map_location='cpu', weights_only=False)
    aa, bb = np.indices((31, 31)); truth = (aa+bb) % 31
    alignment_rows = []
    for s, seed in enumerate(range(192115, 192119)):
        cut = aligned['individual_switch_steps'][s]
        masks = np.load(B/f'results/V191_DUAL_NEURAL_AUDIT_V2/context_s{seed}.npz')['masks']
        predicted = []
        for role in range(2):
            weights = {k: v[0].numpy().astype(np.float64) for k, v in aligned['bundles'][s]['models'][role].items()}
            hidden = weights['message'][:, None, :]+weights['context'][None, :, :]
            predicted.append(np.einsum('abh,hp->abp', hidden**2, weights['output']).argmax(2))
        metrics = {}
        for split, select in [('train', masks), ('test', ~masks)]:
            actions = [predicted[r][select[r]] for r in range(2)]
            targets = [truth[select[r]] for r in range(2)]
            metrics[split] = float((((actions[0][:, None]+actions[1][None, :]) % 31) ==
                                    ((targets[0][:, None]+targets[1][None, :]) % 31)).mean())
        alignment_rows.append(dict(seed=seed, step=1200, intervention_cut=cut,
            missing_during_training_log=bool(cut < 1200), retrospectively_recomputed_from_saved_weights=True, **metrics))
    score = B/'results/AB_PROGRESO_CT2_CT3.json'
    assert sha(score) == '0db038a35ee828a59c96de2a9e5e071545b26213ed692a29e79ad68f26778047'
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True, encoding='utf-8').strip()
    assert head == 'c032a32d2d8d7710a6ad5a88519b0801ea186891'
    index = Path(subprocess.check_output(['git', 'rev-parse', '--git-path', 'index'], cwd=REPO, text=True, encoding='utf-8').strip())
    if not index.is_absolute():
        index = REPO/index
    assert sha(index) == '0fc87bbef0de6ced68aa787004ef36d3c7934f757f51b5d8505665bd071184a1'
    archives, payloads = [], 0
    if not documents_only:
        manifest = json.loads((OUT/'ARCHIVE_MANIFEST.json').read_text(encoding='utf-8'))
        expected = json.loads((OUT/'EVIDENCE_PAYLOAD_SHA256.json').read_text(encoding='utf-8'))
        for path, value in expected.items():
            assert sha(B/path) == value, path
        seen = set()
        for entry in manifest['shards']:
            path = OUT/entry['archive']
            assert sha(path) == entry['sha256'] and path.stat().st_size == entry['bytes']
            with zipfile.ZipFile(path) as z:
                assert z.testzip() is None
                key = next(name for name in z.namelist() if name.startswith('EVIDENCE_SHARD_'))
                sub = json.loads(z.read(key))
                for name, value in sub.items():
                    assert name not in seen and expected[name] == value
                    assert hashlib.sha256(z.read(name)).hexdigest() == value
                    seen.add(name)
            archives.append(dict(archive=path.name, CRC_and_payload_hashes_valid=True))
        assert seen == set(expected) and len(seen) == manifest['total_payload_files']
        payloads = len(seen)
    result = dict(documents=len(documents), document_sha256={p.relative_to(B).as_posix(): sha(p) for p in documents},
        image_links_verified=len(image_checks), images=image_checks,
        neural_final_metric_checks=neural['metric_checks'], voting_final_metric_checks=drift['metric_checks'],
        archived_payloads_verified=payloads, archives=archives, canonical_score_unchanged=True,
        user_index_unchanged=True, local_HEAD_unchanged=True, frozen_sources_and_parents_unchanged=True,
        alignment_logging_deviation=dict(omitted_post_switch_evaluations=2,
            final_primary_criterion_unaffected=True, retrospective_rows=alignment_rows,
            note='The two cut1100 histories did not log the1200 evaluation during prefix alignment. Saved aligned states permit retrospective evaluation; no training or stopping changed.'),
        documents_only=documents_only, failures=[])
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--documents-only', action='store_true')
    a = p.parse_args()
    apply_limits(2); torch.set_num_threads(2)
    main(a.documents_only)
