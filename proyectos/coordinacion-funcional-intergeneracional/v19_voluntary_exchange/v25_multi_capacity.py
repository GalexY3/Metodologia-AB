"""V25: endogenously learned professions and multiple costly gifts per round.

Each privately learned donor can independently decline or offer up to k-1
goods to chosen social neighbors. Recipient receives goods physically; the
donor pays per emitted unit. No teacher, institution or reward sharing.
"""
from __future__ import annotations
import argparse,json,os,time
from pathlib import Path
import numpy as np,torch
from targeted_gifts import C,PrivateGiftActor
from v24_k4_joint import PrivateOccupationK,start4,adjacent_potential
from v23_joint_cold import gradients_per_agent
ROOT=Path(__file__).resolve().parent

def step_multi(c,w,dests,gifts):
 assert dests.shape==gifts.shape==(c.batch,c.n,c.k-1)
 graph=w["graph"];n=c.n
 anydelivery=((dests[:,graph,:]==torch.arange(n,device=c.device)[None,:,None,None])
      &(gifts[:,graph,:]>.5)).float()
 incoming=(anydelivery.sum(3)>0).float()
 rolesender=w["roles"][:,graph]
 onehot=torch.nn.functional.one_hot(rolesender,c.k).float()
 received=(onehot*anydelivery.sum(3)[...,None]).sum(2)>0
 own=torch.nn.functional.one_hot(w["roles"],c.k).bool()
 distinct=(received&(~own)).float().sum(2)
 cover=distinct/(c.k-1)
 full=(distinct>=c.k-1).float()
 sent=gifts.sum(2)
 food=.20+.55*cover+.25*full-c.cost*sent
 w["incoming"]=incoming
 w["trust"]=torch.maximum(incoming,c.memory_decay*w["trust"])
 w["prev_gift"]=(sent>0).float()
 w["prev_recipient"]=dests[:,:,0]
 w["lastfood"]=food
 w["cover"]=cover
 w["full"]=full
 w["t"]+=1
 # Counts of distinct needed types, not duplicate delivered units.
 return food,distinct

def oracle(c,seed=401):
 assert c.k==4 and c.degree==6 and c.topology=="ring"
 w=start4(c,seed,"balanced")
 target=torch.arange(c.n,device=c.device)[None,:,None]
 offsets=torch.arange(1,c.k,device=c.device)[None,None,:]
 dests=((target+offsets)%c.n).expand(c.batch,-1,-1)
 gifts=torch.ones(c.batch,c.n,c.k-1,device=c.device)
 food,distinct=step_multi(c,w,dests,gifts)
 return dict(food=float(food.mean()),full=float(w["full"].mean()),
             cover=float(w["cover"].mean()),
             count=float(gifts.sum(2).mean()))

def roll(c,donor,role,seed,init="mixed",interval=8,move_cost=.015,
         social=True,baseline=None):
 w=start4(c,seed,init)
 rews=[];lg=[];eg=[];lr=[];er=[];rt=[]
 giftcounts=[];coverages=[];completes=[];switches=[]
 unique=[];issued=[]
 for t in range(c.horizon):
  if t%interval==0:
   if baseline=="fixed":
    newrole=w["roles"];rolelog=roleent=None
   elif baseline is not None and baseline.startswith("random_"):
    probability=float(baseline.split("_",1)[1])
    choose=(torch.rand(c.batch,c.n,device=c.device)<probability)
    candidate=torch.randint(c.k,(c.batch,c.n),device=c.device)
    newrole=torch.where(choose,candidate,w["roles"])
    rolelog=roleent=None
   else:newrole,rolelog,roleent=role.act(c,w,history=social)
   changed=(newrole!=w["roles"]).float()
   w["roles"]=newrole
   w["last_switch"]=changed
   switches.append(changed)
   if rolelog is not None:
    lr.append(rolelog);er.append(roleent);rt.append(t)
  actions=[donor.act(c,w,mode=("normal" if social else "no_social"))
           for j in range(c.k-1)]
  dests=torch.stack([z[0] for z in actions],2)
  gifts=torch.stack([z[1] for z in actions],2)
  lp=torch.stack([z[2] for z in actions]).sum(0)
  ent=torch.stack([z[3] for z in actions]).sum(0)
  reward,distinct=step_multi(c,w,dests,gifts)
  if t%interval==0:
   reward=reward-move_cost*changed
   w["lastfood"]=reward
  rews.append(reward)
  lg.append(lp);eg.append(ent)
  giftcounts.append(gifts.sum(2).mean().detach())
  coverages.append(w["cover"].mean().detach())
  completes.append(w["full"].mean().detach())
  unique.append(distinct.sum().detach())
  issued.append(gifts.sum().detach())
 counts=torch.nn.functional.one_hot(w["roles"],c.k).float().sum(1)
 gifts_total=torch.stack(issued).sum().item()
 metrics=dict(food=float(torch.stack(rews).mean()),
    final_food=float(rews[-1].mean()),
    gifts_per_person=float(torch.stack(giftcounts).mean()),
    gifts_slot_rate=float(torch.stack(giftcounts).mean())/(c.k-1),
    distinct_coverage=float(torch.stack(coverages).mean()),
    complete=float(torch.stack(completes).mean()),
    useful_delivery_ratio=(float(torch.stack(unique).sum())/gifts_total
                          if gifts_total>0 else 0),
    potential_coverage=adjacent_potential(c,w),
    balanced=float((counts==c.n/c.k).all(1).float().mean()),
    professions=float((counts>0).float().sum(1).mean()),
    switches=float(torch.stack(switches).sum(0).mean()))
 return metrics,torch.stack(rews),lg,eg,lr,er,rt

@torch.no_grad()
def evaluate(donor,role,a,seed=194141,worlds=12):
 rows=[]
 for topology in ("ring","rewired"):
  for init in ("monolith","random","balanced"):
   for cond in ("normal","no_history","fixed"):
    c=C(n=a.n,k=a.k,degree=6,topology=topology,batch=worlds,
        horizon=a.horizon,cost=a.cost,gamma=a.gamma,device=a.device)
    worldseed=(seed+(topology=="rewired")*991+
           {"monolith":11,"random":19,"balanced":23}[init])
    torch.manual_seed(worldseed*37)
    m,*_=roll(c,donor,role,worldseed,init=init,interval=a.role_interval,
       move_cost=a.move_cost,social=cond!="no_history",
       baseline="fixed" if cond=="fixed" else None)
    rows.append(dict(topology=topology,init=init,
                     condition=cond,**m))
 return rows

def args():
 p=argparse.ArgumentParser()
 p.add_argument("--name",required=True)
 p.add_argument("--seed",type=int,required=True)
 p.add_argument("--n",type=int,default=48)
 p.add_argument("--k",type=int,default=4)
 p.add_argument("--updates",type=int,default=1000)
 p.add_argument("--batch",type=int,default=12)
 p.add_argument("--horizon",type=int,default=48)
 p.add_argument("--role-interval",type=int,default=8)
 p.add_argument("--move-cost",type=float,default=.015)
 p.add_argument("--cost",type=float,choices=(.12,.04),required=True)
 p.add_argument("--low-cost",type=float,default=.002)
 p.add_argument("--flat",type=int,default=500)
 p.add_argument("--rise",type=int,default=300)
 p.add_argument("--hidden",type=int,default=20)
 p.add_argument("--init-scale",type=float,default=8.)
 p.add_argument("--gamma",type=float,default=.995)
 p.add_argument("--lr-gift",type=float,default=.002)
 p.add_argument("--lr-role",type=float,default=.003)
 p.add_argument("--ent-gift",type=float,default=.015)
 p.add_argument("--ent-role",type=float,default=.01)
 p.add_argument("--eval-every",type=int,default=250)
 p.add_argument("--device",choices=("cuda","cpu"),default="cuda")
 return p

def cost_at(a,u):
 if u<=a.flat:return a.low_cost
 return a.low_cost+(a.cost-a.low_cost)*min(1.,(u-a.flat)/a.rise)

def main():
 a=args().parse_args()
 assert a.k==4 and a.n%4==0 and a.updates>=a.flat+a.rise
 assert a.horizon%a.role_interval==0 and a.batch>=2
 torch.set_num_threads(2);torch.manual_seed(a.seed);np.random.seed(a.seed)
 folder=ROOT/"runs"/a.name;folder.mkdir(parents=True,exist_ok=False)
 (folder/"v25_spec.json").write_text(json.dumps(vars(a),indent=2),encoding="utf8")
 actor=PrivateGiftActor(a.n,a.hidden,a.init_scale).to(a.device)
 role=PrivateOccupationK(a.n,a.k,a.hidden).to(a.device)
 og=torch.optim.Adam(actor.parameters(),lr=a.lr_gift)
 orole=torch.optim.Adam(role.parameters(),lr=a.lr_role)
 t0=time.perf_counter()
 for update in range(1,a.updates+1):
  unitprice=cost_at(a,update)
  c=C(n=a.n,k=a.k,degree=6,topology="ring",
      batch=a.batch,horizon=a.horizon,cost=unitprice,
      gamma=a.gamma,device=a.device)
  m,rewards,gl,ge,rl,re,rt=roll(c,actor,role,
       a.seed*19301+31*update,init="mixed",
       interval=a.role_interval,move_cost=a.move_cost)
  G=torch.zeros_like(rewards[0]);history=[]
  for x in reversed(rewards):
   G=x+a.gamma*G;history.append(G)
  returns=torch.stack(history[::-1])
  base=(returns.sum(1,keepdim=True)-returns)/(a.batch-1)
  adv=((returns-base)/returns.std(1,unbiased=False,
           keepdim=True).clamp_min(.25)).detach()
  loss_gift=-(torch.stack(gl)*adv).mean()-a.ent_gift*torch.stack(ge).mean()
  loss_role=-(torch.stack(rl)*adv[rt]).mean()-a.ent_role*torch.stack(re).mean()
  og.zero_grad(set_to_none=True);orole.zero_grad(set_to_none=True)
  (loss_gift+loss_role).backward()
  gradients_per_agent(actor,a.n);gradients_per_agent(role,a.n)
  og.step();orole.step()
  if update==1 or update%a.eval_every==0 or update==a.updates:
   cpu=torch.get_rng_state()
   gpu=torch.cuda.get_rng_state() if a.device=="cuda" else None
   with torch.no_grad():development=evaluate(actor,role,a)
   torch.set_rng_state(cpu)
   if gpu is not None:torch.cuda.set_rng_state(gpu)
   row=dict(update=update,unitprice=unitprice,train=m,
      development=development,
      loss_gift=float(loss_gift.detach()),loss_role=float(loss_role.detach()),
      elapsed=time.perf_counter()-t0)
   with (folder/"v25_history.jsonl").open("a",encoding="utf8") as f:
    f.write(json.dumps(row)+"\n")
   tmp=folder/"joint_tmp.pt"
   torch.save(dict(gift=actor.state_dict(),role=role.state_dict(),
       opt_gift=og.state_dict(),opt_role=orole.state_dict(),
       update=update,rng_cpu=torch.get_rng_state(),
       rng_gpu=torch.cuda.get_rng_state() if a.device=="cuda" else None),tmp)
   os.replace(tmp,folder/"joint_latest.pt")
   z=next(t for t in development if t["topology"]=="ring" and
       t["init"]=="monolith" and t["condition"]=="normal")
   print("V25",a.name,"u",update,"PRICE",round(unitprice,4),
     "FOOD",round(z["food"],4),"GIFTS",round(z["gifts_per_person"],4),
     "COVER",round(z["distinct_coverage"],4),
     "FULL",round(z["complete"],4),
     "USEFUL",round(z["useful_delivery_ratio"],4),
     "POTENTIAL",round(z["potential_coverage"],4),
     "elapsed",round(time.perf_counter()-t0,1),flush=True)
 (folder/"v25_status.json").write_text(json.dumps(
  dict(state="completed",updates=a.updates,
     elapsed_seconds=time.perf_counter()-t0)),encoding="utf8")
 print("V25_FINISHED",a.name,flush=True)
if __name__=="__main__":main()
