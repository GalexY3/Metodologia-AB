"""Matched-budget causal follow-up; dictionary repair is an external oracle."""
import os
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG', ':4096:8')
from pathlib import Path
import argparse
import copy
import hashlib
import json
import time
import numpy as np
import torch
from torch import nn
from research_resource_limits import apply_limits
from v185_collective_grokking import Receiver, split, evaluate, P

BASE = Path(__file__).resolve().parent
PARENT = BASE/'results/V185_COLLECTIVE_GROKKING'
OUT = BASE/'results/V186_INFORMATION_BOTTLENECK'


def repair(dictionary):
    result = np.array(dictionary, dtype=np.int64).copy()
    seen, collisions = set(), []
    for a, symbol in enumerate(result):
        if int(symbol) in seen:
            collisions.append(a)
        else:
            seen.add(int(symbol))
    unused = sorted(set(range(P))-seen)
    assert len(unused) == len(collisions)
    for a, symbol in zip(collisions, unused):
        result[a] = symbol
    assert len(set(result.tolist())) == P
    return result


def oracle_bound(dictionary, mask):
    # For fixed b, distinct a imply distinct correct labels. One output per
    # (message,b) can solve at most one of its admissible a values.
    right = sum(len(set(dictionary[np.flatnonzero(mask[:, b])].tolist())) for b in range(P))
    return float(right/mask.sum())


def audit():
    OUT.mkdir(exist_ok=True)
    mask, aa, bb, yy = split()
    rows = []
    for seed in [185115, 185116]:
        c = torch.load(PARENT/f'INDEPENDENT_COMM_s{seed}/checkpoint_30000.pt', map_location='cpu', weights_only=False)
        receiver = Receiver()
        receiver.load_state_dict(c['receiver'])
        dictionary = c['actor'].argmax(1).numpy()
        fixed = repair(dictionary)
        with torch.no_grad():
            mm, bvalues = np.indices((P, P))
            answers = receiver(torch.tensor(mm.ravel()), torch.tensor(bvalues.ravel())).argmax(1).numpy().reshape(P, P)
        q = np.zeros((P, P))
        for a in range(P):
            available = np.flatnonzero(mask[a])
            for m in range(P):
                q[a, m] = np.mean(answers[m, available] == (a+available) % P)
        current = q[np.arange(P), dictionary]
        row = dict(seed=seed, original_dictionary=dictionary.tolist(), repaired_dictionary=fixed.tolist(),
                   values_reassigned=int(np.sum(dictionary != fixed)),
                   original_bounds=dict(train=oracle_bound(dictionary, mask), test=oracle_bound(dictionary, ~mask),
                                        full=oracle_bound(dictionary, np.ones_like(mask))),
                   repaired_bounds=dict(train=oracle_bound(fixed, mask), test=oracle_bound(fixed, ~mask), full=1.),
                   maximum_unilateral_accuracy_gain=float(np.max(q.max(axis=1)-current)),
                   mean_unilateral_accuracy_gain=float(np.mean(q.max(axis=1)-current)),
                   full_Q_counterfactual=q.tolist(), decoder_is_not_used_for_training=True,
                   posthoc_analysis_of_already_known_endpoints=True)
        rows.append(row)
    (OUT/'PREAUDIT.json').write_text(json.dumps(rows, indent=2), encoding='utf-8')
    print(json.dumps([{k:v for k,v in row.items() if k not in ('full_Q_counterfactual',)} for row in rows], indent=2), flush=True)


def continue_model(seed, mode, checkpoint, destination, end):
    device = torch.device('cuda')
    receiver = Receiver().to(device)
    receiver.load_state_dict(checkpoint['receiver'])
    actor = nn.Parameter(checkpoint['actor'].to(device).clone())
    baseline = checkpoint['baseline'].to(device).clone()
    actor_optim = torch.optim.Adam([actor], lr=.03)
    receiver_optim = torch.optim.AdamW(receiver.parameters(), lr=.001, weight_decay=1., betas=(.9, .98))
    actor_optim.load_state_dict(copy.deepcopy(checkpoint['actor_optimizer']))
    receiver_optim.load_state_dict(copy.deepcopy(checkpoint['receiver_optimizer']))
    generator = torch.Generator(device=device)
    # torch.load(map_location='cuda') also moves this CPU ByteTensor. The
    # Generator API requires its serialized state on CPU even for a CUDA RNG.
    generator.set_state(checkpoint['generator_state'].cpu())
    dictionary = None
    if mode != 'CONTINUE_JOINT':
        values = actor.detach().argmax(1).cpu().numpy()
        if mode == 'BIJECTIVE_REPAIR':
            values = repair(values)
        dictionary = torch.tensor(values, device=device)
    mask, aa, bb, yy = split()
    full = tuple(torch.tensor(v, device=device, dtype=torch.long) for v in (aa, bb, yy))
    train_mask = torch.tensor(mask.ravel(), device=device)
    a, b, y = (v[train_mask] for v in full)
    counts = torch.bincount(a, minlength=P).float()
    group_matrix = nn.functional.one_hot(a, P).float().T/counts[:, None]
    history, started = [], time.monotonic()
    for step in range(checkpoint['step']+1, end+1):
        actor_logits = actor[a]
        log_probs = actor_logits.log_softmax(1)
        probs = log_probs.exp()
        messages = dictionary[a] if dictionary is not None else torch.multinomial(probs.detach(), 1, generator=generator).squeeze(1)
        logits = receiver(messages, b)
        reward = (logits.detach().argmax(1) == y).float()
        receiver_optim.zero_grad(set_to_none=True)
        nn.functional.cross_entropy(logits, y).backward()
        receiver_optim.step()
        if mode == 'CONTINUE_JOINT':
            advantage = (reward-baseline[a]).detach()
            sender_entropy = -(probs*log_probs).sum(1).mean()
            actor_loss = -(advantage*log_probs.gather(1, messages[:, None]).squeeze(1)).mean()-.01*sender_entropy
            actor_optim.zero_grad(set_to_none=True)
            actor_loss.backward()
            actor_optim.step()
        baseline = .95*baseline+.05*(group_matrix@reward).detach()
        if step % 100 == 0:
            history.append(dict(step=step, **evaluate(receiver, actor, dictionary, full, mask, device)))
        if step % 5000 == 0:
            print('V186', seed, mode, step, 'test', round(history[-1]['test'], 4),
                  'sec', round(time.monotonic()-started, 1), flush=True)
            if destination is not None:
                (destination/'progress.json').write_text(json.dumps(history, indent=2), encoding='utf-8')
    state = dict(receiver=copy.deepcopy(receiver.state_dict()), actor=actor.detach().clone(), baseline=baseline.clone(),
                 dictionary=dictionary, generator_state=generator.get_state(), step=end,
                 actor_optimizer=copy.deepcopy(actor_optim.state_dict()),
                 receiver_optimizer=copy.deepcopy(receiver_optim.state_dict()))
    if destination is not None:
        torch.save(state, destination/'final.pt')
        result = dict(seed=seed, mode=mode, initial_step=checkpoint['step'], final_step=end,
                      history=history, final=history[-1], private_institution_learned=False,
                      oracle_repair=mode == 'BIJECTIVE_REPAIR')
        (destination/'metrics.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    return state, history


def replay():
    rows = []
    for seed in [185115, 185116]:
        start = torch.load(PARENT/f'INDEPENDENT_COMM_s{seed}/checkpoint_25000.pt', map_location='cuda', weights_only=False)
        expected = torch.load(PARENT/f'INDEPENDENT_COMM_s{seed}/checkpoint_30000.pt', map_location='cuda', weights_only=False)
        got, history = continue_model(seed, 'CONTINUE_JOINT', start, None, 30000)
        errors = {key:float(torch.max(torch.abs(got['receiver'][key]-expected['receiver'][key]))) for key in expected['receiver']}
        errors['actor'] = float(torch.max(torch.abs(got['actor']-expected['actor'])))
        errors['baseline'] = float(torch.max(torch.abs(got['baseline']-expected['baseline'])))
        exact_rng = torch.equal(got['generator_state'].cpu(), expected['generator_state'].cpu())
        # Record actual errors; do not silently relabel an approximate replay exact.
        passed = max(errors.values()) <= 1e-5 and exact_rng
        rows.append(dict(seed=seed, update_replay_from=25000, to=30000, errors=errors, exact_rng=exact_rng,
                         passed=passed, known_old_trajectory_only=True))
    (OUT/'UPDATE_REPLAY_AUDIT.json').write_text(json.dumps(rows, indent=2), encoding='utf-8')
    print('UPDATE_REPLAY', json.dumps(rows), flush=True)
    assert all(r['passed'] for r in rows), rows


def run():
    receipt = json.loads((BASE/'results/V186_PREREG_RECEIPT.json').read_text(encoding='utf-8'))
    assert receipt['before_new_continuations'] and receipt['remote_commit']
    for path, sha in receipt['source_sha256'].items():
        assert hashlib.sha256((BASE/path).read_bytes()).hexdigest() == sha, path
    assert all(r['passed'] for r in json.loads((OUT/'UPDATE_REPLAY_AUDIT.json').read_text(encoding='utf-8')))
    (OUT/'SOURCE_MANIFEST.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    results = []
    for seed in [185115, 185116]:
        checkpoint_path = PARENT/f'INDEPENDENT_COMM_s{seed}/checkpoint_30000.pt'
        for mode in ['CONTINUE_JOINT', 'FROZEN_ORIGINAL', 'BIJECTIVE_REPAIR']:
            destination = OUT/f'{mode}_s{seed}'
            destination.mkdir(exist_ok=False)
            # Reload for every arm, even though optimizers are also deep-copied.
            checkpoint = torch.load(checkpoint_path, map_location='cuda', weights_only=False)
            _, history = continue_model(seed, mode, checkpoint, destination, 60000)
            results.append(dict(seed=seed, mode=mode, final=history[-1]))
            torch.cuda.empty_cache()
    gates = []
    for seed in [185115, 185116]:
        scores = {r['mode']:r['final']['test'] for r in results if r['seed'] == seed}
        passed = scores['BIJECTIVE_REPAIR'] >= .95 and all(scores['BIJECTIVE_REPAIR']-scores[r] >= .10
                    for r in ['CONTINUE_JOINT', 'FROZEN_ORIGINAL'])
        gates.append(dict(seed=seed, scores=scores, gate_passed=passed))
    summary = dict(results=results, gates=gates, primary_passed=all(g['gate_passed'] for g in gates),
                   reused_original_histories=2, new_continuations=6, extra_updates_each=30000,
                   CT2_historical=61, new_branch_score=None, N2=0, N3=0,
                   novel_collective_grokking_established=False, oracle_repair_not_autonomous=True)
    (OUT/'SUMMARY.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print('V186_COMPLETE', json.dumps(summary), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['audit', 'replay', 'run'])
    args = parser.parse_args()
    print('LIMITS', apply_limits(2), flush=True)
    torch.set_num_threads(2)
    torch.backends.cuda.matmul.allow_tf32 = False
    {'audit':audit, 'replay':replay, 'run':run}[args.command]()
