"""V47 dynamic pairing across learning episodes, private exact opponent shaping.

Each update draws a new uniform perfect matching of 48 persons. Only paired
policies are rearranged; actor identities/optimizer states remain persistent.
No sharing of gradients, food, genes, rewards or teacher instructions.
"""
from __future__ import annotations
import argparse,json,os,time
from pathlib import Path
import numpy as np,torch
from torch import nn
from v46_exact_opponent_shaping import N,gradients,measurements,V,C,B,GAMMA,H
ROOT=Path(__file__).resolve().parent

def inverse_permutation_gradient(gradient,permutation):
 assert gradient.shape==(N,5)
 assert sorted(permutation.detach().cpu().tolist())==list(range(N))
 original=torch.empty_like(gradient)
 original[permutation]=gradient
 return original

def sample_pairing(seed,step):
 # Dedicated RNG, deterministic and independent of neural sampling.
 return np.random.default_rng(seed*300011+47+step*67).permutation(N)

@torch.no_grad()
def development(logits,q=.95):
 # Never use the 12 reserved heldout pairings in the development trajectory.
 seeds=(992001,992007,992009,992021)
 stats=[]
 for seed in seeds:
  indexes=np.random.default_rng(seed).permutation(N)
  metrics=measurements(logits[indexes],q=q)
  stats.append({key:metrics[key] for key in ("food","gifts","mutual","causal","positive_agents")})
 return {k:float(np.mean([row[k] for row in stats])) for k in stats[0]}

def main():
 parser=argparse.ArgumentParser()
 parser.add_argument("--name",required=True)
 parser.add_argument("--seed",required=True,type=int)
 parser.add_argument("--method",required=True,choices=("NL","LOLA"))
 parser.add_argument("--alpha",required=True,type=float)
 parser.add_argument("--updates",type=int,default=1000)
 parser.add_argument("--lr",type=float,default=.03)
 parser.add_argument("--q",type=float,default=.95)
 parser.add_argument("--save-every",type=int,default=200)
 parser.add_argument("--device",choices=("cpu","cuda"),default="cpu")
 args=parser.parse_args()
 assert args.method=="NL" and args.alpha==0 or args.method=="LOLA" and args.alpha in (5.,20.)
 assert args.q==.95
 assert args.updates>=1
 torch.set_num_threads(2)
 torch.manual_seed(args.seed)
 params=nn.Parameter(torch.randn(N,5,device=args.device)*.05)
 optimizer=torch.optim.Adam([params],lr=args.lr)
 folder=ROOT/"runs"/args.name
 folder.mkdir(parents=True,exist_ok=False)
 spec=dict(vars(args),n=N,partner_matching="reshuffle each update",
  pairing_seed_schedule="seed*300011+47+update*67",
  condition="partner turnover between experiences",
  payoff_base=B,payoff_received=V,own_cost=C,gamma=GAMMA,horizon=H,
  no_contracts=True,no_teacher=True,private_objective=True,
  opponent_gradient_available=True)
 (folder/"v47_spec.json").write_text(json.dumps(spec,indent=2),encoding="utf8")
 start=time.perf_counter()
 for u in range(1,args.updates+1):
  indices=sample_pairing(args.seed,u)
  perm=torch.tensor(indices,device=args.device,dtype=torch.long)
  current=params[perm]
  grad=gradients(current,q=args.q,method=args.method,alpha=args.alpha)
  original_grad=inverse_permutation_gradient(grad,perm)
  assert torch.isfinite(original_grad).all()
  optimizer.zero_grad(set_to_none=True)
  params.grad=-original_grad
  optimizer.step()
  if u==1 or u%args.save_every==0 or u==args.updates:
   with torch.no_grad():
    dev=development(params.detach(),q=args.q)
   report=dict(update=u,development=dev,
     gradient_norm=float(original_grad.norm().detach()),
     elapsed_seconds=time.perf_counter()-start)
   with (folder/"v47_history.jsonl").open("a",encoding="utf8") as h:
    h.write(json.dumps(report)+"\n")
   temp=folder/"checkpoint_tmp.pt"
   torch.save(dict(logits=params.detach().cpu().clone(),
    optimizer=optimizer.state_dict(),update=u),temp)
   os.replace(temp,folder/"v47_latest.pt")
   print("V47",args.name,"u",u,"FOOD",round(dev["food"],4),
    "MUTUAL",round(dev["mutual"],4),
    "CAUSAL",round(dev["causal"],4),
    "POS",round(dev["positive_agents"],2),
    "elapsed",round(report["elapsed_seconds"],1),flush=True)
 (folder/"v47_status.json").write_text(json.dumps(dict(state="completed",
   updates=args.updates,elapsed_seconds=time.perf_counter()-start)),encoding="utf8")
 print("V47_FINISHED",args.name,flush=True)

if __name__=="__main__":main()
