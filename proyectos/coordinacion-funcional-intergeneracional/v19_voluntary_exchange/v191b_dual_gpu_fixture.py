"""One-update synthetic GPU fixtures; no scientific training trajectory."""
from pathlib import Path
import json
import numpy as np
import torch
from research_resource_limits import apply_limits
from v188_private_conventions import BatchedReceiver
from v191_dual_neural_credit import P,SEEDS,sample_action,sampling_probability,full_loss,bandit_loss,environment_feedback

B=Path(__file__).resolve().parent


def main():
    torch.set_num_threads(2);torch.cuda.set_per_process_memory_fraction(.35)
    torch.backends.cuda.matmul.allow_tf32=False
    rng=np.random.default_rng(191991);checks=[]
    for family in ['FULL','BANDIT']:
        networks=[BatchedReceiver([191000+2*s+role for s in range(4)],device='cuda') for role in range(2)]
        opts=[torch.optim.AdamW(m.parameters(),lr=.001,weight_decay=1.,betas=(.9,.98)) for m in networks]
        n=17
        x=[torch.tensor(rng.integers(P,size=(4,n)),device='cuda') for _ in range(4)]
        # Random unrelated latent payoffs, not modular-sum training examples.
        fa=torch.tensor(rng.integers(P,size=(4,n)),device='cuda');fb=torch.tensor(rng.integers(P,size=(4,n)),device='cuda')
        values=[networks[role](x[2*role],x[2*role+1]) for role in range(2)]
        greedy=[v.detach().argmax(2) for v in values]
        coins=torch.tensor(rng.random((2,4,n)),device='cuda')
        actions=[sample_action(greedy[r],coins[r]) for r in range(2)]
        permutation=torch.tensor(np.stack([rng.permutation(n) for _ in range(4)]),device='cuda')
        pa,pb,ra,rb=environment_feedback(fa,fb,actions[0],actions[1],permutation)
        losses=[full_loss(values[0],pa),full_loss(values[1],pb)] if family=='FULL' else [
            bandit_loss(values[r],actions[r],[ra,rb][r],sampling_probability(actions[r],greedy[r])) for r in range(2)]
        untouched={k:v.detach().clone() for k,v in networks[1].state_dict().items()}
        opts[0].zero_grad(set_to_none=True);losses[0].backward();opts[0].step()
        assert all(p.grad is None for p in networks[1].parameters())
        assert all(torch.equal(v,untouched[k]) for k,v in networks[1].state_dict().items())
        opts[0].zero_grad(set_to_none=True)
        opts[1].zero_grad(set_to_none=True);losses[1].backward();opts[1].step()
        assert all(p.grad is None for p in networks[0].parameters())
        assert all(torch.isfinite(p).all() for m in networks for p in m.parameters())
        assert all(torch.isfinite(loss.detach()) for loss in losses)
        checks.append(dict(family=family,synthetic_updates=1,role_parameters_disjoint=True,
                           first_update_leaves_other_network_bit_identical=True,both_losses_finite=True))
        del networks,opts,values,losses;torch.cuda.empty_cache()
    result=dict(checks=checks,failures=[],scientific_training_executed=False,synthetic_fixture_only=True)
    p=B/'results/V191B_GPU_TECHNICAL_AUDIT.json';assert not p.exists()
    p.write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result),flush=True)


if __name__=='__main__':print('LIMITS',apply_limits(2),flush=True);main()
