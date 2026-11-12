"""V23: from-scratch joint private donation and occupational choice.

Two independent, per-person neural actors are initialized randomly and
updated jointly from each person's own discounted food. No teacher, cloned
policy, central trainer's group reward or pretrained weights.
"""
from __future__ import annotations
import argparse,json,os,time
from pathlib import Path
import numpy as np,torch
from targeted_gifts import C,PrivateGiftActor,step
from v22_occupations import PrivateOccupationActor,start

ROOT=Path(__file__).resolve().parent
def cost_at(a,update):
    if a.schedule=="constant":return a.cost
    t=max(0,min(1,(update-1)/max(1,a.transition-1)))
    return a.low_cost+(a.cost-a.low_cost)*t

def roll(c,donor,occup,seed,init="mixed",social=True,
         interval=8,switch_cost=.015,baseline=None,greedy=False):
    w=start(c,seed,init=init)
    log_gift=[];ent_gift=[];log_role=[];ent_role=[];r_role_times=[]
    rews=[];gr=[];changes=[];linkseries=[]
    for t in range(c.horizon):
        if t%interval==0:
            if baseline=="fixed":
                changes_now=torch.zeros(c.batch,c.n,device=c.device)
                logp=en=None
            elif baseline is not None and baseline.startswith("random_"):
                pr=float(baseline.split("_",1)[1])
                changes_now=(torch.rand(c.batch,c.n,device=c.device)<pr).float()
                logp=en=None
            else:
                obs=w
                if not social:
                    obs=dict(w,prev_gift=torch.zeros_like(w["prev_gift"]),
                             trust=torch.zeros_like(w["trust"]))
                changes_now,logp,en=occup.act(c,obs,greedy=greedy)
            w["roles"]=(w["roles"]+changes_now.long())%c.k
            w["last_switch"]=changes_now
            changes.append(changes_now)
            if logp is not None:
                log_role.append(logp)
                ent_role.append(en)
                r_role_times.append(t)
        dest,gift,lp,e=donor.act(c,w,mode=("normal" if social else "no_social"),greedy=greedy)
        r=step(c,w,dest,gift)
        if t%interval==0:
            r=r-switch_cost*changes_now
            w["lastfood"]=r
        rews.append(r)
        gr.append(gift.mean().detach())
        log_gift.append(lp)
        ent_gift.append(e)
        linkseries.append((w["roles"][:,w["graph"]]!=w["roles"][:,:,None]).float().mean().detach())
    food=torch.stack(rews)
    rolezero=(w["roles"]==0).sum(1)
    opp=(w["roles"][:,w["graph"]]!=w["roles"][:,:,None]).float().mean((1,2))
    m=dict(mean_food=float(food.mean().detach()),
      last_food=float(food[-1].mean().detach()),
      gift=float(torch.stack(gr).mean()),
      complementary_links=float(opp.mean().detach()),
      mean_complement_trajectory=float(torch.stack(linkseries).mean()),
      balanced=float((rolezero==c.n//c.k).float().mean()),
      role_entropy_var=float(((rolezero.float()-c.n/c.k).square()).mean()),
      switches_per_agent=float(torch.stack(changes).sum(0).mean()),
      worlds=c.batch)
    return m,food,log_gift,ent_gift,log_role,ent_role,r_role_times

@torch.no_grad()
def evaluate(donor,actor,a,seed=991818,worlds=20,horizon=48):
    rows=[]
    for topo,degree in (("ring",2),("rewired",2),("ring",4)):
        for init in ("monolith","random"):
            c=C(n=a.n,k=2,degree=degree,topology=topo,batch=worlds,
                horizon=horizon,cost=a.cost,gamma=a.gamma,device=a.device,
                social=bool(a.social))
            for social in (True,False):
                torch.manual_seed(seed+degree*73+(init=="random")*151)
                m,*_=roll(c,donor,actor,seed+degree*73+(init=="random")*151,
                          init=init,social=social,interval=a.role_interval,
                          switch_cost=a.switch_cost)
                rows.append(dict(topology=topo,degree=degree,init=init,
                                 social=social,**m))
    return rows

def gradients_per_agent(mod,n,lim=2.):
    norms=torch.zeros(n,device=next(mod.parameters()).device)
    for par in mod.parameters():
        if par.grad is not None:
            norms+=par.grad.detach().reshape(n,-1).square().sum(1)
    with torch.no_grad():
        scale=(lim/(norms.sqrt()+1e-10)).clamp(max=1)
        for par in mod.parameters():
            if par.grad is not None:
                par.grad.mul_(scale.reshape(n,*([1]*(par.ndim-1))))

def parser():
    p=argparse.ArgumentParser()
    p.add_argument("--name",required=True)
    p.add_argument("--seed",type=int,required=True)
    p.add_argument("--schedule",choices=("constant","smooth"),default="smooth")
    p.add_argument("--updates",type=int,default=1400)
    p.add_argument("--transition",type=int,default=800)
    p.add_argument("--n",type=int,default=24)
    p.add_argument("--hidden",type=int,default=20)
    p.add_argument("--init-scale",type=float,default=8.)
    p.add_argument("--cost",type=float,default=.12)
    p.add_argument("--low-cost",type=float,default=.01)
    p.add_argument("--batch",type=int,default=20)
    p.add_argument("--horizon",type=int,default=48)
    p.add_argument("--role-interval",type=int,default=8)
    p.add_argument("--switch-cost",type=float,default=.015)
    p.add_argument("--gamma",type=float,default=.995)
    p.add_argument("--lr-gift",type=float,default=.002)
    p.add_argument("--lr-role",type=float,default=.003)
    p.add_argument("--ent-gift",type=float,default=.015)
    p.add_argument("--ent-role",type=float,default=.01)
    p.add_argument("--social",type=int,choices=(0,1),default=1)
    p.add_argument("--eval-every",type=int,default=280)
    p.add_argument("--device",choices=("cpu","cuda"),default="cuda")
    return p

def main():
    a=parser().parse_args()
    assert a.n==24 and 0<a.low_cost<=a.cost<=.2 and a.batch>=2
    assert a.role_interval>0 and a.horizon%a.role_interval==0
    torch.set_num_threads(2)
    torch.manual_seed(a.seed);np.random.seed(a.seed)
    folder=ROOT/"runs"/a.name
    folder.mkdir(parents=True,exist_ok=False)
    (folder/"v23_spec.json").write_text(json.dumps(vars(a),indent=2),encoding="utf8")
    donor=PrivateGiftActor(a.n,a.hidden,a.init_scale).to(a.device)
    role=PrivateOccupationActor(a.n,a.hidden).to(a.device)
    og=torch.optim.Adam(donor.parameters(),lr=a.lr_gift)
    orole=torch.optim.Adam(role.parameters(),lr=a.lr_role)
    t0=time.perf_counter()
    for u in range(1,a.updates+1):
        cost=cost_at(a,u)
        c=C(n=a.n,k=2,degree=2,topology="ring",batch=a.batch,
          horizon=a.horizon,cost=cost,gamma=a.gamma,device=a.device,
          social=bool(a.social))
        metrics,rr,lg,eg,lr,er,rt=roll(c,donor,role,a.seed*19301+31*u,
          init="mixed",social=bool(a.social),interval=a.role_interval,
          switch_cost=a.switch_cost)
        values=[]
        g=torch.zeros_like(rr[0])
        for r in reversed(rr):
            g=r+a.gamma*g
            values.append(g)
        R=torch.stack(values[::-1])
        leave=(R.sum(1,keepdim=True)-R)/(a.batch-1)
        adv=((R-leave)/R.std(1,unbiased=False,keepdim=True).clamp_min(.25)).detach()
        gift_loss=-(torch.stack(lg)*adv).mean()-a.ent_gift*torch.stack(eg).mean()
        role_adv=adv[rt]
        role_loss=-(torch.stack(lr)*role_adv).mean()-a.ent_role*torch.stack(er).mean()
        og.zero_grad(set_to_none=True)
        orole.zero_grad(set_to_none=True)
        (gift_loss+role_loss).backward()
        gradients_per_agent(donor,a.n)
        gradients_per_agent(role,a.n)
        og.step();orole.step()
        if u==1 or u%a.eval_every==0 or u==a.updates:
            saved_cpu=torch.get_rng_state()
            saved_gpu=torch.cuda.get_rng_state() if a.device=="cuda" else None
            rows=evaluate(donor,role,a)
            torch.set_rng_state(saved_cpu)
            if saved_gpu is not None:torch.cuda.set_rng_state(saved_gpu)
            line=dict(update=u,cost=cost,training=metrics,
               gift_loss=float(gift_loss.detach()),role_loss=float(role_loss.detach()),
               development=rows,elapsed_seconds=time.perf_counter()-t0)
            with (folder/"v23_history.jsonl").open("a",encoding="utf8") as fh:
                fh.write(json.dumps(line)+"\n")
            chk=dict(gift=donor.state_dict(),role=role.state_dict(),
                     gift_optimizer=og.state_dict(),role_optimizer=orole.state_dict(),
                     update=u,rng_cpu=torch.get_rng_state(),
                     rng_gpu=torch.cuda.get_rng_state() if a.device=="cuda" else None)
            tmp=folder/"joint_tmp.pt"
            torch.save(chk,tmp);os.replace(tmp,folder/"joint_latest.pt")
            target=next(x for x in rows if x["topology"]=="ring" and
                        x["degree"]==2 and x["init"]=="monolith" and x["social"])
            no=next(x for x in rows if x["topology"]=="ring" and
                      x["degree"]==2 and x["init"]=="monolith" and not x["social"])
            print("V23",a.name,"u",u,"cost",round(cost,3),
                  "FOOD",round(target["mean_food"],4),
                  "DONATE",round(target["gift"],4),
                  "OPPOSITE",round(target["complementary_links"],3),
                  "BALANCED",round(target["balanced"],3),
                  "NO_SOCIAL",round(no["mean_food"],4),
                  "elapsed",round(time.perf_counter()-t0,1),flush=True)
    (folder/"v23_status.json").write_text(json.dumps(dict(
        state="completed",updates=a.updates,
        elapsed_seconds=time.perf_counter()-t0)),encoding="utf8")
    print("V23_FINISHED",a.name,flush=True)

if __name__=="__main__":main()
