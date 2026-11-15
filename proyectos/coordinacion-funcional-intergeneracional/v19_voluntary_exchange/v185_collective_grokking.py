"""Exploratory independent-agent signaling / modular-generalization pilot.

Sender updates receive scalar correctness only. Receiver receives its own
supervised label. No gradient or parameter sharing between agents. Cooperative
payoffs and task roles are externally specified, not learned institutions.
"""
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

BASE = Path(__file__).resolve().parent
OUT = BASE/'results/V185_COLLECTIVE_GROKKING'
P, H, STEPS, EVAL = 31, 128, 30000, 100


class Receiver(nn.Module):
    def __init__(self):
        super().__init__()
        self.message = nn.Embedding(P, H)
        self.context = nn.Embedding(P, H)
        self.output = nn.Linear(H, P, bias=False)

    def forward(self, message, b):
        hidden = self.message(message) + self.context(b)
        return self.output(hidden.square())


def split():
    rng = np.random.default_rng(185000)
    unordered = [(a, b) for a in range(P) for b in range(a, P)]
    order = rng.permutation(len(unordered))
    selected = set(order[:int(.4*len(unordered))].tolist())
    mask = np.zeros((P, P), dtype=bool)
    for i, (a, b) in enumerate(unordered):
        if i in selected:
            mask[a, b] = mask[b, a] = True
    a, b = np.indices((P, P))
    y = (a+b) % P
    assert np.array_equal(mask, mask.T)
    assert set(a[mask].tolist()) == set(range(P))
    assert set(b[mask].tolist()) == set(range(P))
    assert set(y[mask].tolist()) == set(range(P))
    return mask, a.ravel(), b.ravel(), y.ravel()


def technical():
    torch.manual_seed(185001)
    receiver = Receiver()
    actor = nn.Parameter(torch.zeros(P, P))
    a = torch.arange(P)
    b = (a*7) % P
    labels = (a+b) % P
    dist = actor[a].softmax(dim=1)
    messages = torch.multinomial(dist.detach(), 1).squeeze(1)
    prediction = receiver(messages, b)
    reward = (a % 3 == 0).float()  # nonzero scalar-feedback technical fixture
    nn.functional.cross_entropy(prediction, labels).backward()
    receiver_only = actor.grad is None
    receiver.zero_grad(set_to_none=True)
    loss = -(reward*actor[a].log_softmax(1).gather(1, messages[:, None]).squeeze(1)).mean()
    loss.backward()
    actor_only = all(parameter.grad is None for parameter in receiver.parameters())
    nonzero_sender_update = bool(actor.grad is not None and actor.grad.abs().sum() > 0)
    shared = any(actor.data_ptr() == p.data_ptr() for p in receiver.parameters())
    mask, _, _, _ = split()
    report = dict(receiver_gradient_does_not_reach_actor=receiver_only,
                  actor_gradient_does_not_reach_receiver=actor_only,
                  nonzero_sender_gradient_fixture=nonzero_sender_update,
                  shared_parameters=shared, train_pairs=int(mask.sum()), test_pairs=int((~mask).sum()),
                  split_has_no_reversed_pair_leakage=bool(np.array_equal(mask, mask.T)),
                  technical_fixture_only=True, scientific_training_executed=False)
    assert receiver_only and actor_only and nonzero_sender_update and not shared
    (BASE/'results/V185_TECHNICAL_AUDIT.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report), flush=True)


@torch.no_grad()
def evaluate(receiver, actor, dictionary, data, mask, device):
    a, b, y = data
    protocol = dictionary if dictionary is not None else actor.argmax(1)
    logits = receiver(protocol[a], b)
    right = logits.argmax(1) == y
    train = torch.as_tensor(mask.ravel(), device=device)
    probs = actor.softmax(1) if dictionary is None else torch.eye(P, device=device)[dictionary]
    bound = probs.max(dim=0).values.sum()/P
    return dict(train=float(right[train].float().mean()), test=float(right[~train].float().mean()),
                train_nll=float(nn.functional.cross_entropy(logits[train], y[train])),
                test_nll=float(nn.functional.cross_entropy(logits[~train], y[~train])),
                protocol_symbols=int(protocol.unique().numel()),
                bayes_bound_stochastic=float(bound), bayes_bound_greedy=float(protocol.unique().numel()/P),
                sender_entropy=float(-(probs*probs.clamp_min(1e-12).log()).sum(1).mean()))


def train(seed, condition, device, checkpoint=None, freeze=None):
    name = f'{condition}_s{seed}' if freeze is None else f'{freeze}_s{seed}'
    target = OUT/name
    target.mkdir(exist_ok=False)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    receiver = Receiver().to(device)
    actor = nn.Parameter(torch.zeros((P, P), device=device))
    actor_optim = torch.optim.Adam([actor], lr=.03)
    receiver_optim = torch.optim.AdamW(receiver.parameters(), lr=.001, weight_decay=1., betas=(.9, .98))
    generator = torch.Generator(device=device).manual_seed(seed+10000)
    dictionary = None
    if condition == 'FIXED_PROTOCOL':
        dictionary = torch.tensor(np.random.default_rng(seed+20000).permutation(P), device=device)
    baseline = torch.zeros(P, device=device)
    mask, aa, bb, yy = split()
    full = tuple(torch.tensor(v, device=device, dtype=torch.long) for v in (aa, bb, yy))
    train_mask = torch.tensor(mask.ravel(), device=device)
    a, b, y = (v[train_mask] for v in full)
    observation_counts = torch.bincount(a, minlength=P).float()
    group_matrix = nn.functional.one_hot(a, P).float().T/observation_counts[:, None]
    start, history, t_mem, t_gen, streak_mem, streak_gen = 0, [], None, None, 0, 0
    if checkpoint is not None:
        receiver.load_state_dict(checkpoint['receiver'])
        actor.data.copy_(checkpoint['actor'].to(device))
        baseline = checkpoint['baseline'].to(device).clone()
        receiver_optim.load_state_dict(copy.deepcopy(checkpoint['receiver_optimizer']))
        actor_optim.load_state_dict(copy.deepcopy(checkpoint['actor_optimizer']))
        generator.set_state(checkpoint['generator_state'])
        start = checkpoint['step']
        history = copy.deepcopy(checkpoint['history'])
        t_mem = start
    began = time.monotonic()
    memorized_path = None
    for step in range(start+1, STEPS+1):
        actor_logits = actor[a]
        log_probs = actor_logits.log_softmax(1)
        probs = log_probs.exp()
        messages = dictionary[a] if dictionary is not None else torch.multinomial(probs.detach(), 1, generator=generator).squeeze(1)
        logits = receiver(messages, b)
        reward = (logits.detach().argmax(1) == y).float()
        # Receiver sees its own label and symbolic message, never sender logits.
        if freeze != 'FROZEN_RECEIVER':
            receiver_optim.zero_grad(set_to_none=True)
            nn.functional.cross_entropy(logits, y).backward()
            receiver_optim.step()
        if condition == 'INDEPENDENT_COMM' and freeze != 'FROZEN_SENDER':
            advantage = (reward-baseline[a]).detach()
            sender_entropy = -(probs*log_probs).sum(1).mean()
            actor_loss = -(advantage*log_probs.gather(1, messages[:, None]).squeeze(1)).mean()-.01*sender_entropy
            actor_optim.zero_grad(set_to_none=True)
            actor_loss.backward()
            actor_optim.step()
        baseline = .95*baseline+.05*(group_matrix@reward).detach()
        if step % EVAL == 0:
            row = dict(step=step, **evaluate(receiver, actor, dictionary, full, mask, device))
            history.append(row)
            streak_mem = streak_mem+1 if row['train'] >= .99 else 0
            streak_gen = streak_gen+1 if row['test'] >= .95 else 0
            if t_gen is None and streak_gen >= 5:
                t_gen = step
            if t_mem is None and streak_mem >= 5:
                t_mem = step
                if condition == 'INDEPENDENT_COMM' and freeze is None:
                    snapshot = dict(receiver=copy.deepcopy(receiver.state_dict()), actor=actor.detach().clone(),
                                    baseline=baseline.clone(), receiver_optimizer=copy.deepcopy(receiver_optim.state_dict()),
                                    actor_optimizer=copy.deepcopy(actor_optim.state_dict()), generator_state=generator.get_state(),
                                    step=step, history=copy.deepcopy(history), seed=seed)
                    memorized_path = target/'first_memorized.pt'
                    torch.save(snapshot, memorized_path)
            if step % 1000 == 0:
                print('V185', name, step, 'train', round(row['train'], 4), 'test', round(row['test'], 4),
                      'symbols', row['protocol_symbols'], 'sec', round(time.monotonic()-began, 1), flush=True)
            if step % 5000 == 0:
                torch.save(dict(receiver=receiver.state_dict(), actor=actor.detach(), baseline=baseline,
                                receiver_optimizer=receiver_optim.state_dict(), actor_optimizer=actor_optim.state_dict(),
                                generator_state=generator.get_state(), step=step, history=history, seed=seed),
                           target/f'checkpoint_{step}.pt')
                (target/'progress.json').write_text(json.dumps(dict(step=step, history=history), indent=2), encoding='utf-8')
    final = history[-1]
    delayed = t_mem is not None and t_gen is not None and t_gen >= 5*t_mem and t_gen-t_mem >= 2000 and final['test'] >= .95
    result = dict(seed=seed, condition=condition, freeze=freeze, updates_total=STEPS,
                  updates_this_continuation=STEPS-start, t_mem=t_mem, t_gen=t_gen,
                  delayed_generalization_gate=bool(delayed), final=final, history=history,
                  common_payoff_imposed=True, institution_formation_demonstrated=False)
    (target/'metrics.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    torch.save(dict(receiver=receiver.state_dict(), actor=actor.detach(), dictionary=dictionary,
                    generator_state=generator.get_state(), config=result), target/'final.pt')
    del receiver, actor, actor_optim, receiver_optim
    torch.cuda.empty_cache()
    return result, memorized_path


def run():
    receipt = json.loads((BASE/'results/V185_PREREG_RECEIPT.json').read_text(encoding='utf-8'))
    assert receipt['before_scientific_training'] and receipt['remote_commit']
    for path, sha in receipt['source_sha256'].items():
        assert hashlib.sha256((BASE/path).read_bytes()).hexdigest() == sha, path
    technical_report = json.loads((BASE/'results/V185_TECHNICAL_AUDIT.json').read_text(encoding='utf-8'))
    assert technical_report['receiver_gradient_does_not_reach_actor'] and technical_report['actor_gradient_does_not_reach_receiver']
    assert torch.cuda.is_available()
    device = torch.device('cuda')
    torch.set_num_threads(2)
    torch.backends.cuda.matmul.allow_tf32 = False
    OUT.mkdir(exist_ok=False)
    mask, a, b, y = split()
    np.savez_compressed(OUT/'data_split.npz', a=a, b=b, y=y, train_mask=mask)
    manifest = dict(preregistration=receipt, torch=torch.__version__, numpy=np.__version__, cuda=torch.version.cuda,
                    device=torch.cuda.get_device_name(), explicit_separate_agent_parameters=True,
                    exact_cross_hardware_bitwise_reproduction_claimed=False)
    (OUT/'MANIFEST.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    results = []
    for seed in [185115, 185116]:
        for condition in ['FIXED_PROTOCOL', 'INDEPENDENT_COMM']:
            result, checkpoint_path = train(seed, condition, device)
            results.append(result)
            if checkpoint_path is not None:
                checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)
                for freeze in ['FROZEN_SENDER', 'FROZEN_RECEIVER']:
                    r, _ = train(seed, condition, device, checkpoint=checkpoint, freeze=freeze)
                    results.append(r)
    # Final cross-play and marginal-preserving message intervention.
    transfer = []
    for receiver_seed in [185115, 185116]:
        rstate = torch.load(OUT/f'INDEPENDENT_COMM_s{receiver_seed}/final.pt', map_location=device, weights_only=False)
        receiver = Receiver().to(device)
        receiver.load_state_dict(rstate['receiver'])
        aa, bb, yy = (torch.tensor(v, dtype=torch.long, device=device) for v in (a, b, y))
        for sender_seed in [185115, 185116]:
            sstate = torch.load(OUT/f'INDEPENDENT_COMM_s{sender_seed}/final.pt', map_location=device, weights_only=False)
            messages = sstate['actor'].argmax(1)[aa]
            with torch.no_grad():
                accuracy = float((receiver(messages, bb).argmax(1) == yy).float().mean())
                rng = np.random.default_rng(185900+sender_seed+receiver_seed)
                shuffled = []
                for _ in range(16):
                    # Permute a separately inside each fixed b; same message marginals.
                    order = np.arange(P*P).reshape(P, P)
                    for column in range(P):
                        order[:, column] = rng.permutation(order[:, column])
                    perm = torch.tensor(order.ravel(), device=device)
                    shuffled.append(float((receiver(messages[perm], bb).argmax(1) == yy).float().mean()))
            transfer.append(dict(sender_seed=sender_seed, receiver_seed=receiver_seed,
                                 all_pair_accuracy=accuracy, shuffled_message_accuracy=float(np.mean(shuffled))))
    summary = dict(runs=[{k:v for k,v in r.items() if k!='history'} for r in results], crossplay=transfer,
                   exploratory_only=True, novel_collective_grokking_established=False,
                   CT2_historical=61, new_branch_score=None, N2=0, N3=0)
    (OUT/'SUMMARY.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print('V185_COMPLETE', json.dumps(summary), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['technical', 'run'])
    args = parser.parse_args()
    print('LIMITS', apply_limits(2), flush=True)
    {'technical':technical, 'run':run}[args.command]()
