"""Train local send/accept policies with shared team-progress REINFORCE/A2C.

No color balancing heuristics, oracle actions, or group counts in actor.
Actor parameters are shared; the CENTRALIZED CRITIC sees global fractions
during training only. Never use heldout seeds for model selection.
"""
import argparse,json,time,random
from pathlib import Path
import numpy as np
import torch
from torch.nn import functional as F
from environment import VectorSociety,Configuration
from agents import LocalActor,CentralCritic

ROOT=Path(__file__).resolve().parent
torch.set_num_threads(2)

@torch.no_grad()
def evaluate(actor,seed=91000,batch=16,horizon=70,rows=6,cols=6,
             policy="learned",k=4,deterministic=True,randomize_majority=False):
    env=VectorSociety(Configuration(rows=rows,cols=cols,batch=batch,seed=seed,
                                        randomize_majority=randomize_majority))
    env.reset(k=k)
    tv=[env.tv()]
    churn=[]
    messages=[]
    incoming_max=0
    for t in range(horizon):
        obs=env.observe()
        legal=env.send_mask()
        if policy=="stay":
            outgoing=torch.zeros(batch,env.n,dtype=torch.long)
            incoming,requested,sender_snapshot=env.deliveries(obs,outgoing)
            accepting=torch.zeros_like(outgoing)
        else:
            outgoing,_,_,z=actor.sample_sender(obs,legal,
                   deterministic=deterministic and policy=="learned",
                   random_baseline=policy=="random")
            incoming,requested,sender_snapshot=env.deliveries(obs,outgoing)
            accepting,_,_=actor.sample_receiver(
                z,sender_snapshot,incoming,requested,
                deterministic=deterministic and policy=="learned",
                random_baseline=policy=="random")
        incoming_max=max(incoming_max,int(incoming.sum(-1).max()))
        metrics=env.step(outgoing,accepting,incoming,requested)
        tv.append(metrics["tv"])
        churn.append(metrics["churn"])
        messages.append(metrics["messages"])
    tt=torch.stack(tv)
    cc=torch.stack(churn)
    final10=(tt[-10:]<=.06)&(cc[-10:]<=.05)
    stable=final10.all(0)
    return {"k":k,"n":env.n,"policy":policy,"seed":seed,
            "batch":batch,"horizon":horizon,
            "initial_tv_mean":float(tt[0].mean()),
            "last_tv_mean":float(tt[-10:].mean()),
            "final_tv_mean":float(tt[-1].mean()),
            "min_tv_mean":float(tt.min(0).values.mean()),
            "final_tv":tt[-1].tolist(),
            "stable_fraction":float(stable.float().mean()),
            "at_least_once_tv_le_006":float((tt<=.06).any(0).float().mean()),
            "final_churn":float(cc[-10:].mean()),
            "messages_per_agent_tick":float(torch.stack(messages).mean()),
            "max_incoming_requests_observed":incoming_max}

def train(args):
    start=time.perf_counter()
    random.seed(args.seed);np.random.seed(args.seed);torch.manual_seed(args.seed)
    actor=LocalActor(hidden=args.hidden)
    critic=CentralCritic(hidden=args.hidden)
    actoropt=torch.optim.Adam(actor.parameters(),lr=args.actor_lr)
    criticopt=torch.optim.Adam(critic.parameters(),lr=args.critic_lr)
    out=ROOT/"runs"/f"a2c_seed{args.seed}_u{args.updates}"
    if out.exists():raise RuntimeError("Experiment destination exists; do not overwrite: "+str(out))
    out.mkdir(parents=True)
    cfg=vars(args)
    (out/"CONFIG.json").write_text(json.dumps(cfg,indent=2,ensure_ascii=False),encoding="utf-8")
    logs=[]
    for iteration in range(1,args.updates+1):
        env=VectorSociety(Configuration(rows=args.rows,cols=args.cols,
             batch=args.batch,seed=args.seed*100000+iteration))
        rewards=[];logprobs=[];entropies=[];values=[];distances=[];churns=[]
        for step in range(args.steps):
            obs=env.observe()
            legal=env.send_mask()
            send,logsend,entsend,z=actor.sample_sender(obs,legal)
            received,requests,snapshot=env.deliveries(obs,send)
            accept,logaccept,entaccept=actor.sample_receiver(z,snapshot,received,requests)
            v=critic(env)
            metrics=env.step(send,accept,received,requests)
            logprobs.append((logsend+logaccept).mean(-1))
            entropies.append((entsend+entaccept).mean(-1))
            values.append(v)
            rewards.append(metrics["reward"].detach())
            distances.append(metrics["tv"].detach())
            churns.append(metrics["churn"].detach())
        discounted=[]
        accumulator=torch.zeros(args.batch)
        for reward in reversed(rewards):
            accumulator=reward+args.gamma*accumulator
            discounted.append(accumulator)
        returns=torch.stack(discounted[::-1])
        vals=torch.stack(values)
        advantage=returns-vals.detach()
        normadv=(advantage-advantage.mean())/(advantage.std()+1e-6)
        policy_loss=-(torch.stack(logprobs)*normadv).mean()-args.entropy_beta*torch.stack(entropies).mean()
        value_loss=F.smooth_l1_loss(vals,returns)
        actoropt.zero_grad(set_to_none=True)
        policy_loss.backward()
        torch.nn.utils.clip_grad_norm_(actor.parameters(),5.)
        actoropt.step()
        criticopt.zero_grad(set_to_none=True)
        value_loss.backward()
        torch.nn.utils.clip_grad_norm_(critic.parameters(),5.)
        criticopt.step()
        meanfinal=float(distances[-1].mean())
        rec={"iteration":iteration,"episodes_seen":iteration*args.batch,
          "experience_ticks":iteration*args.batch*args.steps,
          "policy_loss":float(policy_loss.detach()),
          "value_loss":float(value_loss.detach()),
          "train_final_tv":meanfinal,
          "train_best_tv":float(torch.stack(distances).min(0).values.mean()),
          "train_last_churn":float(torch.stack(churns)[-5:].mean()),
          "train_reward_sum":float(torch.stack(rewards).sum(0).mean()),
          "duration_s":round(time.perf_counter()-start,2)}
        if iteration%args.eval_every==0 or iteration in (1,args.updates):
            dev=[]
            for k in (2,3,4):
                for mode in ("learned","random","stay"):
                    dev.append(evaluate(actor,seed=80000+100*k,batch=12,horizon=50,
                            rows=args.rows,cols=args.cols,policy=mode,k=k))
            rec["development"]=dev
            torch.save({"actor":actor.state_dict(),"critic":critic.state_dict(),
                "iteration":iteration,"config":cfg},out/f"checkpoint_{iteration:04d}.pt")
            summary=[(d["k"],d["policy"],round(d["final_tv_mean"],3),
                      round(d["stable_fraction"],3)) for d in dev]
            print("TRAIN_DEV",iteration, "cohorts",iteration*args.batch,
                "finaltrainD",round(meanfinal,3),
                "results",summary,
                "elapsed",round(time.perf_counter()-start,1),flush=True)
        elif iteration%5==0:
            print("TRAIN",iteration,"finalD",round(meanfinal,3),
              "reward",round(rec["train_reward_sum"],2),
              "elapsed",round(time.perf_counter()-start,1),flush=True)
        logs.append(rec)
    with (out/"TRAINING_LOG.json").open("w",encoding="utf-8") as file:
        json.dump(logs,file,indent=2,ensure_ascii=False)
    print("TRAINING_COMPLETED",out,"elapsed",round(time.perf_counter()-start,2),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--seed",type=int,default=211)
    p.add_argument("--updates",type=int,default=120)
    p.add_argument("--batch",type=int,default=12)
    p.add_argument("--steps",type=int,default=24)
    p.add_argument("--rows",type=int,default=6)
    p.add_argument("--cols",type=int,default=6)
    p.add_argument("--hidden",type=int,default=64)
    p.add_argument("--actor-lr",type=float,default=.003)
    p.add_argument("--critic-lr",type=float,default=.005)
    p.add_argument("--entropy-beta",type=float,default=.003)
    p.add_argument("--gamma",type=float,default=.99)
    p.add_argument("--eval-every",type=int,default=20)
    train(p.parse_args())
