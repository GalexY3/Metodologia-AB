"""V2-B shared-team A2C vs added counterfactual individual credit.

No hand-coded balancing rule or color preference is used by the agents. Credit
is computed by CENTRAL TRAINER only from the global utility after actions.
Under both conditions the actors observe only local snapshots/messages and
previous team's scalar progress, never counts or marginal rewards.
"""
from pathlib import Path
import argparse,json,random,time
import numpy as np
import torch
import torch.nn.functional as F
from environment import VectorSociety,Configuration,MAX_K
from agents import LocalActor,CentralCritic
from train import evaluate

torch.set_num_threads(2)
ROOT=Path(__file__).resolve().parent

@torch.no_grad()
def marginal_credits(env,old,accept,after_tv):
    """Each accepted color change's immediate global difference reward.

    Compares actual global D at t+1 against world where one receptor
    retained its previous color while all other switches remain realized.
    This is NOT an action recommendation, only a trainer-side reward.
    """
    B,N=old.shape
    new=env.colors
    counts=F.one_hot(new,MAX_K).float().sum(1)
    oldhot=F.one_hot(old,MAX_K).float()
    newhot=F.one_hot(new,MAX_K).float()
    cf=(counts[:,None,:]+oldhot-newhot)/N
    valid=(torch.arange(MAX_K)[None,None,:]<env.k[:,None,None]).float()
    target=valid/env.k[:,None,None].float()
    dc=.5*((cf-target).abs()*valid).sum(-1)
    contribution=N*(dc-after_tv[:,None])
    # No contribution when no actual change; floating arithmetic may yield
    # numerical noise so explicitly zero these entries.
    contribution=torch.where(new!=old,contribution,torch.zeros_like(contribution))
    contribution=contribution.clamp(-2.,2.)
    slot=(accept-1).clamp(min=0)
    origin=env.neighbors[None].expand(B,-1,-1).gather(2,slot.unsqueeze(-1)).squeeze(-1)
    sender=torch.zeros_like(contribution)
    sender.scatter_add_(1,origin,contribution*(accept>0).float())
    return contribution,sender

def train(args):
    start=time.perf_counter()
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    random.seed(args.seed)
    actor=LocalActor(args.hidden)
    critic=CentralCritic(args.hidden)
    aopt=torch.optim.Adam(actor.parameters(),lr=args.actor_lr)
    copt=torch.optim.Adam(critic.parameters(),lr=args.critic_lr)
    name=f"credit{args.credit_weight:g}_seed{args.seed}_u{args.updates}"
    out=ROOT/"runs"/name
    if out.exists():raise RuntimeError("Result directory already exists: "+str(out))
    out.mkdir(parents=True)
    config=vars(args)
    (out/"CONFIG.json").write_text(json.dumps(config,indent=2),encoding="utf-8")
    logs=[]
    for iteration in range(1,args.updates+1):
        env=VectorSociety(Configuration(rows=args.rows,cols=args.cols,
             batch=args.batch,seed=args.seed*100000+iteration,
             randomize_majority=True))
        rewards=[];ls=[];la=[];entropies=[];vals=[];dists=[];churns=[];creditsr=[];creditss=[]
        for t in range(args.steps):
            obs=env.observe()
            send,lp_s,ent_s,z=actor.sample_sender(obs,env.send_mask())
            incoming,req,snapshot=env.deliveries(obs,send)
            accept,lp_a,ent_a=actor.sample_receiver(z,snapshot,incoming,req)
            v=critic(env)
            old=env.colors.clone()
            outcome=env.step(send,accept,incoming,req)
            with torch.no_grad():
                rec_credit,send_credit=marginal_credits(env,old,accept,outcome["tv"])
            rewards.append(outcome["reward"].detach())
            ls.append(lp_s);la.append(lp_a)
            entropies.append((ent_s+ent_a).mean(-1))
            vals.append(v)
            dists.append(outcome["tv"].detach())
            churns.append(outcome["churn"].detach())
            creditsr.append(rec_credit);creditss.append(send_credit)
        gret=torch.zeros(args.batch)
        rt=[]
        for r in reversed(rewards):
            gret=r+args.gamma*gret
            rt.append(gret)
        returns=torch.stack(rt[::-1])
        values=torch.stack(vals)
        advantage=returns-values.detach()
        advantage=(advantage-advantage.mean())/(advantage.std()+1e-6)
        send_log=torch.stack(ls)
        accept_log=torch.stack(la)
        team_loss=-((send_log+accept_log).mean(-1)*advantage).mean()
        c_recv=torch.stack(creditsr)
        c_send=torch.stack(creditss)
        def standardized(x):
            return (x-x.mean())/(x.std()+1e-6)
        credit_loss=-(
            accept_log*standardized(c_recv)
            +send_log*standardized(c_send)
            ).mean()
        entropy_loss=-args.entropy_beta*torch.stack(entropies).mean()
        loss=team_loss+args.credit_weight*credit_loss+entropy_loss
        vloss=F.smooth_l1_loss(values,returns)
        aopt.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(actor.parameters(),5.)
        aopt.step()
        copt.zero_grad(set_to_none=True)
        vloss.backward()
        torch.nn.utils.clip_grad_norm_(critic.parameters(),5.)
        copt.step()
        rec={"iteration":iteration,"society_episodes_seen":iteration*args.batch,
         "team_loss":float(team_loss.detach()),
         "credit_loss":float(credit_loss.detach()),
         "value_loss":float(vloss.detach()),
         "train_final_tv":float(dists[-1].mean()),
         "train_early_tv":float(dists[0].mean()),
         "train_final_churn":float(torch.stack(churns)[-5:].mean()),
         "train_mean_return":float(torch.stack(rewards).sum(0).mean()),
         "elapsed_s":round(time.perf_counter()-start,2)}
        if iteration%args.eval_every==0 or iteration in (1,args.updates):
            dev=[]
            for k in (2,3,4):
                for mode,det in (("learned",True),("learned",False),("random",False),("stay",True)):
                    result=evaluate(actor,seed=81000+100*k,batch=18,horizon=70,
                        rows=args.rows,cols=args.cols,k=k,policy=mode,
                        deterministic=det,randomize_majority=True)
                    result["deterministic"]=det
                    dev.append(result)
            rec["development"]=dev
            torch.save({"actor":actor.state_dict(),"critic":critic.state_dict(),
                 "config":config,"iteration":iteration},out/f"checkpoint_{iteration:04d}.pt")
            print("DEV",args.credit_weight,args.seed,iteration,"episodes",iteration*args.batch,
                "outcomes",[(q["k"],q["policy"],"D" if q["deterministic"] else "S",
                    round(q["final_tv_mean"],3),round(q["final_churn"],3),
                    round(q["stable_fraction"],2)) for q in dev],
                "elapsed",round(time.perf_counter()-start,1),flush=True)
        elif iteration%10==0:
            print("TRAIN",args.credit_weight,args.seed,iteration,
                  "trainTV",round(rec["train_final_tv"],3),
                  "teamloss",round(rec["team_loss"],4),
                  "creditloss",round(rec["credit_loss"],4),
                  "elapsed",round(time.perf_counter()-start,1),flush=True)
        logs.append(rec)
    (out/"TRAINING_LOG.json").write_text(json.dumps(logs,ensure_ascii=False,indent=2),encoding="utf-8")
    print("CREDIT_TRAIN_FINISHED",name,"episodes",args.updates*args.batch,
          "duration",round(time.perf_counter()-start,1),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--credit-weight",type=float,default=2.)
    p.add_argument("--seed",type=int,default=221)
    p.add_argument("--updates",type=int,default=180)
    p.add_argument("--batch",type=int,default=12)
    p.add_argument("--steps",type=int,default=24)
    p.add_argument("--rows",type=int,default=6)
    p.add_argument("--cols",type=int,default=6)
    p.add_argument("--hidden",type=int,default=64)
    p.add_argument("--actor-lr",type=float,default=.003)
    p.add_argument("--critic-lr",type=float,default=.005)
    p.add_argument("--entropy-beta",type=float,default=.003)
    p.add_argument("--gamma",type=float,default=.99)
    p.add_argument("--eval-every",type=int,default=30)
    train(p.parse_args())
