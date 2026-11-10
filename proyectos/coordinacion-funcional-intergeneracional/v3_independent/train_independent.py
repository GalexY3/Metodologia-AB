"""Train N fully independent, color-equivariant policies from ONE team reward.

Conditions:
  C1: no communication, but self-selected colors are always permitted.
  C2: optional one-to-many directed requests and self-selected colors.
  C3: evaluation ablation of C2 with messages switched off.

No shared actor parameters. No centralized value model, reward decomposition,
oracle actions, fixed minority rule or individual credit.
"""
import argparse,json,math,time,hashlib,sys
from pathlib import Path
import torch
from environment_v3 import IndependentSociety
from individual_agents import IndependentActors
from environment import Configuration
torch.set_num_threads(2)
ROOT=Path(__file__).resolve().parent

def random_floor(n,k):
    p=1.0/k
    return k/(2*n)*sum(abs(x-n*p)*math.comb(n,x)*p**x*(1-p)**(n-x)
                       for x in range(n+1))

@torch.no_grad()
def evaluate(net,k,mode,world_seed=650000,batch=20,steps=70,
             communication=True,deterministic=False):
    env=IndependentSociety(Configuration(rows=6,cols=6,batch=batch,seed=world_seed,
                                          randomize_majority=True))
    env.reset(k=k)
    torch.manual_seed(world_seed+11*len(mode))
    progress=[env.tv().clone()]
    churn=[]
    messages=[]
    matches=[]
    for t in range(steps):
        obs=env.observe()
        stopped=mode=="stay" or (mode=="random_T24" and t>=24)
        if stopped:
            send=torch.zeros((batch,env.n),dtype=torch.long)
            incoming,requested,payload=env.deliveries(obs,send)
            choice=env.colors.clone()
        else:
            use_random=mode.startswith("random")
            send,_,_=net.act_send(obs,env.k,uniform=use_random,
                   deterministic=deterministic,disable_messages=not communication)
            incoming,requested,payload=env.deliveries(obs,send)
            choice,_,_=net.act_choose(obs,env.k,incoming,requested,payload,
                   deterministic=deterministic,uniform=use_random)
        r=env.step(send,choice,incoming,requested)
        progress.append(r["tv"].clone())
        churn.append(r["churn"].clone())
        messages.append(r["messages"].clone())
        matches.append(r["choice_matches_request"].clone())
    ds=torch.stack(progress)
    cs=torch.stack(churn)
    stable=((ds[-10:]<=.06)&(cs[-10:]<=.05)).all(0)
    floor=random_floor(env.n,k)
    return {"k":k,"condition":mode,"communication":communication,
        "eval_world_seed":world_seed,"batch":batch,"steps":steps,
        "mean_initial_d":float(ds[0].mean()),
        "mean_final_d":float(ds[-1].mean()),
        "ratio_to_iid":float(ds[-1].mean())/floor,
        "mean_tail_churn":float(cs[-10:].mean()),
        "stable_count":int(stable.sum()),
        "exact_count":int((ds[-1]<=1e-6).sum()),
        "send_rate":float(torch.stack(messages).mean()),
        "request_match_rate":float(torch.stack(matches).mean()),
        "distance_curve_mean":ds.mean(1).tolist()}

def train(args):
    start=time.perf_counter()
    torch.manual_seed(args.seed)
    net=IndependentActors(n=args.rows*args.cols,hidden=args.hidden)
    if args.rows!=6 or args.cols!=6:raise RuntimeError("Only baseline 6x6 pilot implemented")
    optimizer=torch.optim.Adam(net.parameters(),lr=args.lr)
    output=ROOT/"runs"/f"v3b_seed{args.seed}_{args.mode}_updates{args.updates}"
    if output.exists():raise RuntimeError("Refuse to overwrite prior experiment "+str(output))
    output.mkdir(parents=True)
    settings=vars(args).copy()
    settings["initial_policy_sha256"]=hashlib.sha256(
       b"".join(v.detach().cpu().numpy().tobytes() for v in net.parameters())).hexdigest()
    (output/"CONFIG.json").write_text(json.dumps(settings,ensure_ascii=False,indent=2),
                                       encoding="utf-8")
    logs=[]
    communication=(args.mode=="C2")
    for stepidx in range(1,args.updates+1):
        env=IndependentSociety(Configuration(rows=args.rows,cols=args.cols,
               batch=args.batch,seed=args.seed*100000+stepidx,
               randomize_majority=True))
        ks=torch.tensor([2+i%3 for i in range(args.batch)],dtype=torch.long)
        env.reset(k=ks)
        chosen_lp=[];entropy=[];rewards=[];distance=[];churn=[]
        for tick in range(args.steps):
            obs=env.observe()
            sends,send_lp,send_entropy=net.act_send(obs,env.k,
                                                   disable_messages=not communication)
            incoming,requested,snapshot=env.deliveries(obs,sends)
            colors,color_lp,color_entropy=net.act_choose(obs,env.k,incoming,requested,snapshot)
            metrics=env.step(sends,colors,incoming,requested)
            chosen_lp.append(send_lp+color_lp)
            entropy.append(send_entropy+color_entropy)
            rewards.append(metrics["reward"].detach())
            distance.append(metrics["tv"].detach())
            churn.append(metrics["churn"].detach())
        # Team returns. No individual reward decomposition. Leave-one-out
        # over independent worlds means baseline for world b excludes b itself.
        returns=[];G=torch.zeros(args.batch)
        for r in reversed(rewards):
            G=r+args.gamma*G
            returns.append(G)
        returns=torch.stack(returns[::-1]) # T,B
        if args.batch<2:raise RuntimeError("Independent leave-one-out baseline requires batch>1")
        # Compare only with OTHER worlds of the same task k.
        # Thus every agent receives the same advantage in world b;
        # the baseline does not include that world's actions/reward.
        baseline=torch.empty_like(returns)
        for task_k in (2,3,4):
            mask=(ks==task_k)
            count=int(mask.sum())
            if count<2:raise RuntimeError("At least two worlds per k for LOO")
            group=returns[:,mask]
            baseline[:,mask]=(group.sum(1,keepdim=True)-group)/(count-1)
        advantage=(returns-baseline).detach() / args.adv_scale
        # Sum log-probabilities over agents, not mean across N; each theta_i
        # receives ONLY ∇logπ_i times the SAME team advantage for that world.
        logprob=torch.stack(chosen_lp)    # T,B,N
        ent=torch.stack(entropy)           # T,B,N
        objective=-(logprob.sum(-1)*advantage).mean()-args.entropy_beta*ent.sum(-1).mean()
        optimizer.zero_grad(set_to_none=True)
        objective.backward()
        # Per-agent clipping, NEVER a single global norm combining agent i
        # and agent j (that would couple otherwise independent updates).
        n=net.n
        norm2=torch.zeros(n)
        for p in net.parameters():
            if p.grad is not None:
                norm2+=p.grad.detach().reshape(n,-1).pow(2).sum(1)
        norms=norm2.sqrt()
        scales=(args.grad_clip/(norms+1e-12)).clamp(max=1.0)
        for p in net.parameters():
            if p.grad is not None:
                p.grad.mul_(scales.view(n,*([1]*(p.grad.ndim-1))))
        norm=float(norms.max())
        optimizer.step()
        row={"update":stepidx,"train_worlds_seen":args.batch*stepidx,
             "train_final_tv":float(distance[-1].mean()),
             "train_mean_reward":float(torch.stack(rewards).sum(0).mean()),
             "train_tail_churn":float(torch.stack(churn)[-4:].mean()),
             "loss":float(objective.detach()),"grad_norm_preclip":norm,
             "elapsed_s":round(time.perf_counter()-start,2)}
        if stepidx in (1,args.updates) or stepidx%args.eval_every==0:
            with torch.no_grad():
                checks=[]
                for k in (2,3,4):
                    checks.append(evaluate(net,k,"learned",world_seed=660000+100*k,
                                           communication=communication))
                    if communication:
                        checks.append(evaluate(net,k,"learned",world_seed=660000+100*k,
                                           communication=False))
                    if stepidx==args.updates:
                        checks.append(evaluate(net,k,"random_T24",world_seed=660000+100*k,
                                           communication=communication))
            row["development"]=checks
            print("DEV",args.mode,stepidx,
              [(z["k"],"msg" if z["communication"] else "no_msg",
                z["condition"],round(z["mean_final_d"],3),z["stable_count"],
                "ratio",round(z["ratio_to_iid"],2)) for z in checks],
              "elapsed",round(time.perf_counter()-start,1),flush=True)
        elif stepidx%10==0:
            print("TRAIN",args.mode,stepidx,"D",round(row["train_final_tv"],3),
                "churn",round(row["train_tail_churn"],3),
                "grad",round(row["grad_norm_preclip"],2),
                "elapsed",round(time.perf_counter()-start,1),flush=True)
        logs.append(row)
    (output/"TRAINING_LOG.json").write_text(json.dumps(logs,ensure_ascii=False,indent=2),encoding="utf-8")
    torch.save({"model":net.state_dict(),"config":settings,"update":args.updates},
               output/"FINAL_MODEL.pt")
    print("FINISHED",args.mode,output,"worlds",args.batch*args.updates,
          "elapsed",round(time.perf_counter()-start,2),flush=True)

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--seed",type=int,default=311)
    parser.add_argument("--mode",choices=["C1","C2"],required=True)
    parser.add_argument("--updates",type=int,default=60)
    parser.add_argument("--batch",type=int,default=12)
    parser.add_argument("--steps",type=int,default=24)
    parser.add_argument("--rows",type=int,default=6)
    parser.add_argument("--cols",type=int,default=6)
    parser.add_argument("--hidden",type=int,default=24)
    parser.add_argument("--lr",type=float,default=.002)
    parser.add_argument("--gamma",type=float,default=.99)
    parser.add_argument("--entropy-beta",type=float,default=.003)
    parser.add_argument("--adv-scale",type=float,default=10)
    parser.add_argument("--grad-clip",type=float,default=10)
    parser.add_argument("--eval-every",type=int,default=20)
    train(parser.parse_args())
