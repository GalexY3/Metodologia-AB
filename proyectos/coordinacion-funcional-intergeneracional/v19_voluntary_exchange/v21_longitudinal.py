"""V21 longitudinal stability of learned costly-gift conventions.

Continue a V20 independently trained multi-agent policy using its ORIGINAL
Adam state and both PRNG states. No teacher, parameter sharing, central
optimization or collective reward. Distinct files for new run.
"""
from __future__ import annotations
import argparse, json, os, time
from pathlib import Path
from dataclasses import replace
import torch, numpy as np
from targeted_gifts import C,PrivateGiftActor,simulate
from train_targeted import evaluate
ROOT=Path(__file__).resolve().parent

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--source",required=True)
 p.add_argument("--tag",required=True)
 p.add_argument("--additional",type=int,default=1000)
 p.add_argument("--eval-every",type=int,default=200)
 p.add_argument("--topology",choices=("ring","mixed"),default="ring")
 p.add_argument("--entropy-mult",type=float,default=1.)
 p.add_argument("--device",choices=("cuda","cpu"),default="cuda")
 a=p.parse_args()
 assert a.additional>=1 and a.entropy_mult>=0
 torch.set_num_threads(2)
 src=ROOT/"runs"/a.source
 original=json.loads((src/"v20_spec.json").read_text("utf8"))
 assert a.source.startswith("v20_")
 destination=ROOT/"runs"/a.tag
 destination.mkdir(parents=True,exist_ok=False)
 (destination/"v21_spec.json").write_text(json.dumps(dict(
   source=a.source,source_sha="31d553db871e18ac0266fdafdd1b7a23c223962e",
   additional=a.additional,eval_every=a.eval_every,
   topology=a.topology,entropy_mult=a.entropy_mult,
   original_spec=original),indent=2),encoding="utf8")
 (destination/"targeted_spec.json").write_text(
   (src/"targeted_spec.json").read_text("utf8"),encoding="utf8")
 actor=PrivateGiftActor(original["n"],original["hidden"],
                        original["init_scale"]).to(a.device)
 optimizer=torch.optim.Adam(actor.parameters(),lr=original["lr"])
 ck=torch.load(src/"targeted_latest.pt",map_location="cpu",weights_only=False)
 assert ck["update"]==original["updates"]
 actor.load_state_dict(ck["model"])
 optimizer.load_state_dict(ck["optimizer"])
 torch.set_rng_state(ck["rng_cpu"])
 if a.device=="cuda":torch.cuda.set_rng_state(ck["rng_gpu"])
 t0=time.perf_counter()
 # Preserve the original training-world pseudo-random seed sequence, shifted
 # to continue the same trajectory without reusing sampled worlds.
 start=ck["update"]
 for iteration in range(1,a.additional+1):
  u=start+iteration
  topology=("ring" if (u//2)%2 else "rewired") if a.topology=="mixed" else "ring"
  c=C(n=original["n"],k=2,degree=2,topology=topology,
     batch=original["batch"],horizon=original["horizon"],
     cost=original["cost"],gamma=original["gamma"],
     device=a.device,social=bool(original["social"]))
  m,log,ent,rews=simulate(c,actor,original["seed"]*19301+31*u)
  r=torch.stack(rews)
  R=[]
  G=torch.zeros_like(r[0])
  for x in reversed(r):
   G=x+c.gamma*G
   R.append(G)
  R=torch.stack(R[::-1])
  leave=(R.sum(1,keepdim=True)-R)/(c.batch-1)
  adv=((R-leave)/R.std(1,unbiased=False,keepdim=True).clamp_min(.25)).detach()
  loss=-(torch.stack(log)*adv).mean()-original["entropy"]*a.entropy_mult*torch.stack(ent).mean()
  optimizer.zero_grad(set_to_none=True)
  loss.backward()
  norms=torch.zeros(c.n,device=a.device)
  for parameter in actor.parameters():
   if parameter.grad is not None:
    norms+=parameter.grad.detach().reshape(c.n,-1).square().sum(1)
  with torch.no_grad():
   scale=(2/(norms.sqrt()+1e-10)).clamp(max=1)
   for parameter in actor.parameters():
    if parameter.grad is not None:
     parameter.grad.mul_(scale.reshape(c.n,*([1]*(parameter.ndim-1))))
  optimizer.step()
  if iteration==1 or iteration%a.eval_every==0 or iteration==a.additional:
   # Same scenarios & random seeds as V20 to monitor drift; a separate
   # held-out all-agent audit must confirm the selected checkpoints.
   dev,scenarios=evaluate(actor,a.device,original["cost"],seed=947001,batch=16,horizon=48)
   row=dict(update=u,additional=iteration,cost=original["cost"],
      loss=float(loss.detach()),train=m,eval=dev,
      elapsed_seconds=time.perf_counter()-t0)
   with (destination/"v21_history.jsonl").open("a",encoding="utf8") as f:
    f.write(json.dumps(row)+"\n")
   snap=dict(model=actor.state_dict(),optimizer=optimizer.state_dict(),
      update=u,rng_cpu=torch.get_rng_state(),
      rng_gpu=torch.cuda.get_rng_state() if a.device=="cuda" else None)
   torch.save(snap,destination/f"checkpoint_{u}.pt")
   torch.save(snap,destination/"targeted_latest.pt")
   tr=dev["trained_normal"];s=dev["trained_no_social"]
   ood=dev["ood_normal"]
   print("V21",a.tag,"u",u,"food",round(tr["food"],4),
         "gift",round(tr["gift"],4),
         "no_social",round(s["food"],4),
         "ood",round(ood["food"],4),
         "elapsed",round(time.perf_counter()-t0,1),flush=True)
 (destination/"targeted_status.json").write_text(json.dumps(dict(
   state="completed",updates=start+a.additional,
   elapsed_seconds=time.perf_counter()-t0)),encoding="utf8")
 print("V21_FINISHED",a.tag,flush=True)
if __name__=="__main__":main()
