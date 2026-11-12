"""V22 frozen held-out evaluation of endogenous labor division.

Test beyond development worlds and compare with strong stochastic switching
baselines, exogenous occupation-freezing, info-channel ablations and complete
agent relocations. No training, gradient steps or parameter updates.
"""
from __future__ import annotations
import argparse,json,time,copy
from pathlib import Path
import torch,numpy as np
from torch.distributions import Bernoulli
from targeted_gifts import C,PrivateGiftActor
from v22_occupations import PrivateOccupationActor,rollout
from audit_targeted import load
ROOT=Path(__file__).resolve().parent
SEEDS=(9901001,9901019,9901021,9901051,9901071,9901091)
SCENARIOS=((2,"ring"),(2,"rewired"),(4,"ring"))
INIT=("monolith","random")

class RandomRole:
    def __init__(self,p): self.p=p
    @torch.no_grad()
    def act(self,c,w,interval=8,greedy=False):
        dist=Bernoulli(probs=torch.full((c.batch,c.n),self.p,device=c.device))
        act=dist.sample()
        return act,dist.log_prob(act),dist.entropy()

class HiddenHistoryRole:
    def __init__(self,base):self.base=base
    @torch.no_grad()
    def act(self,c,w,interval=8,greedy=False):
        fake=dict(w,prev_gift=torch.zeros_like(w["prev_gift"]),
                  trust=torch.zeros_like(w["trust"]))
        return self.base.act(c,fake,interval,greedy)

def reshuffle_private(role,gift,seed,device,gift_spec):
    n=gift.n
    gen=torch.Generator(device="cpu");gen.manual_seed(seed)
    perm=torch.randperm(n,generator=gen)
    def reorder(actor):
        state=actor.state_dict()
        return {k:(x.index_select(0,perm.to(x.device)).clone()
                 if x.ndim>=1 and x.shape[0]==n else x.clone())
                for k,x in state.items()}
    shuffled_role=PrivateOccupationActor(n,role.W.shape[-1]).to(device)
    shuffled_role.load_state_dict(reorder(role))
    shuffled_gift=PrivateGiftActor(n,gift_spec["hidden"],
                            gift_spec["init_scale"]).to(device)
    shuffled_gift.load_state_dict(reorder(gift))
    return shuffled_role.eval(),shuffled_gift.eval()

@torch.no_grad()
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--name",required=True)
 p.add_argument("--worlds",type=int,default=24)
 p.add_argument("--horizon",type=int,default=48)
 p.add_argument("--device",choices=("cuda","cpu"),default="cuda")
 a=p.parse_args()
 torch.set_num_threads(2)
 folder=ROOT/"runs"/a.name
 spec=json.loads((folder/"v22_spec.json").read_text("utf8"))
 state=torch.load(folder/"role_latest.pt",weights_only=False,map_location="cpu")
 assert state["update"]==spec["updates"]
 gift,gift_spec,gu=load(spec["gift_source"],a.device)
 gift.eval().requires_grad_(False)
 actor=PrivateOccupationActor(gift.n,spec["hidden"]).to(a.device)
 actor.load_state_dict(state["model"]);actor.eval()
 for q in actor.parameters():q.requires_grad_(False)
 moving_role,moving_gift=reshuffle_private(actor,gift,888721,a.device,gift_spec)
 moving_gift.requires_grad_(False)
 t0=time.perf_counter()
 rows=[]
 condition_names=["learned","gift_signals_hidden",
      "role_and_gift_donation_history_hidden","fixed",
      "random_002","random_015","random_035","random_060",
      "relocated_people"]
 for degree,topology in SCENARIOS:
  for init in INIT:
   by_label={label:[] for label in condition_names}
   for seed in SEEDS:
    c=C(n=gift.n,k=2,degree=degree,topology=topology,
          batch=a.worlds,horizon=a.horizon,cost=gift_spec["cost"],
          gamma=gift_spec["gamma"],device=a.device)
    conditions=[
      ("learned",actor,gift,None,"normal"),
      ("gift_signals_hidden",actor,gift,None,"no_social"),
      ("role_and_gift_donation_history_hidden",HiddenHistoryRole(actor),
             gift,None,"no_social"),
      ("fixed",None,gift,"fixed","normal"),
      ("random_002",RandomRole(.02),gift,None,"normal"),
      ("random_015",RandomRole(.15),gift,None,"normal"),
      ("random_035",RandomRole(.35),gift,None,"normal"),
      ("random_060",RandomRole(.60),gift,None,"normal"),
      ("relocated_people",moving_role,moving_gift,None,"normal")]
    for label,policy,gift_policy,base,soc in conditions:
     torch.manual_seed(seed*7+degree*19+(init=="random")*71)
     data,*_=rollout(c,gift_policy,policy,seed,init=init,
       role_interval=spec["role_interval"],
       switch_cost=spec["switch_cost"],baseline=base,social=soc,
       save_gradient=False)
     by_label[label].append(data)
   for label,vals in by_label.items():
    row=dict(model=a.name,checkpoint=state["update"],degree=degree,
         topology=topology,init=init,condition=label,
         worlds=len(SEEDS)*a.worlds,
         food=float(np.mean([x["mean_food"] for x in vals])),
         final_food=float(np.mean([x["final_food"] for x in vals])),
         opposite_links=float(np.mean([x["opposite_links"] for x in vals])),
         balanced=float(np.mean([x["exactly_balanced"] for x in vals])),
         gift=float(np.mean([x["gift"] for x in vals])),
         switches=float(np.mean([x["mean_switches_per_agent"] for x in vals])),
         by_seed=[dict(seed=seed,**z) for seed,z in zip(SEEDS,vals)])
    rows.append(row)
    if degree==2 and topology=="ring" and init=="monolith":
     print("V22_HOLDOUT",a.name,label,"food",round(row["food"],4),
           "links",round(row["opposite_links"],4),
           "balance",round(row["balanced"],4),flush=True)
 payload=dict(model=a.name,training_seed=spec["seed"],gift_source=spec["gift_source"],
     checkpoint=state["update"],seeds=SEEDS,worlds_per_seed=a.worlds,
     horizon=a.horizon,rows=rows,
     caveat="Frozen role network and pretrained frozen gift network; does not show simultaneous learning from scratch. Identity relocation permutes all actor-specific parameters together; multiple alternative stochastic baselines.")
 dest=ROOT/"results"/("v22_holdout_"+a.name+".json")
 dest.write_text(json.dumps(payload,indent=1),encoding="utf8")
 print("V22_HOLDOUT_DONE",a.name,"rows",len(rows),
       "elapsed",round(time.perf_counter()-t0,1),flush=True)
if __name__=="__main__":main()
