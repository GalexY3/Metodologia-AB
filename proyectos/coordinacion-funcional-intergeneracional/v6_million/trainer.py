"""Vectorized million-episode MARL runner. All rewards global; no central critic.

A batch contains independent whole societies. Exactly N agent-specific
policies are optimized together on team reward with a leave-one-WORLD-out
baseline within each k, never individual marginal rewards. A checkpoint
contains optimizer and config; resume never selects "best" weights.
"""
import argparse,json,os,sys,time,math,traceback,hashlib
from dataclasses import asdict
from pathlib import Path
import torch
from engine import Settings, Society, IndependentPolicy, COLORS

ROOT=Path(__file__).resolve().parent
RUNS=ROOT/"runs"

def atomic_json(path,data):
    path=Path(path);tmp=path.with_name(path.name+".tmp")
    tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    os.replace(tmp,path)
def save_state(path,state):
    tmp=Path(str(path)+".tmp")
    torch.save(state,tmp)
    os.replace(tmp,path)

def evaluate(policy,cfg,seed=85000,greedy=True,batch=12,steps=64,replay=False):
    """Development episodes, fixed world seeds; not a sealed test set."""
    was=policy.training
    policy.eval()
    rows=[];captures={}
    with torch.no_grad():
        for k in (2,3,4):
            # Restoring RNG is important: development must not change training
            # reproducibility from the next update's explicit seed.
            torch.manual_seed(seed+k*113)
            if torch.cuda.is_available():torch.cuda.manual_seed_all(seed+k*113)
            c=Settings(**{**asdict(cfg),"batch":batch,"horizon":steps})
            world=Society(c,torch.full((batch,),k,device=c.device,dtype=torch.long))
            start_D=world.D.clone()
            tail=[];churn=[];exact=[world.exact()]
            capture=[{"t":0,"colors":world.colors[0].cpu().tolist(),
                      "D":float(world.D[0]),"churn":0,"messages":[],
                      "hist":world.counts()[0].cpu().tolist()}]
            for t in range(steps):
                act=policy.decisions(world,greedy=greedy)
                _,rot=world.advance(act["choice"],act["slot"],act["request"],act["rec"])
                tail.append(world.D.detach().clone());churn.append(rot.detach().clone())
                exact.append(world.exact())
                if replay:
                    src=torch.arange(world.n,device=c.device)
                    m=act["active"][0]
                    links=[{"from":int(i),"to":int(j),"request":int(v)}
                      for i,j,v in zip(src[m].cpu().tolist(),
                           act["targets"][0][m].cpu().tolist(),
                           act["request"][0][m].cpu().tolist())]
                    capture.append({"t":t+1,"colors":world.colors[0].cpu().tolist(),
                        "D":float(world.D[0]),"churn":float(rot[0]),"messages":links,
                        "hist":world.counts()[0].cpu().tolist()})
            ds=torch.stack(tail);chs=torch.stack(churn)
            stable=((ds[-10:]<=.02)&(chs[-10:]<=.05)).all(0)
            row={"k":k,"initial_D":float(start_D.mean()),"final_D":float(ds[-1].mean()),
                 "mean_D":float(ds.mean()),"occupied":float((world.counts()>0).sum(-1).float().mean()),
                 "exact":int(world.exact().sum()),"ever_exact":int(torch.stack(exact).any(0).sum()),
                 "stable":int(stable.sum()),"worlds":batch,"churn":float(chs[-10:].mean()),
                 "curve":ds.mean(-1).cpu().tolist()}
            rows.append(row)
            if replay:captures[str(k)]=capture
    policy.train(was)
    return rows,captures

def current_cfg(args):
    device=args.device if args.device!="auto" else ("cuda" if torch.cuda.is_available() else "cpu")
    return Settings(side=args.side,batch=args.batch,horizon=args.horizon,
      hidden=args.hidden,seed=args.seed,gamma=args.gamma,lr=args.lr,
      entropy=args.entropy,clip=args.clip,proximity=args.proximity,
      terminal=args.terminal,ema_alpha=args.ema_alpha,device=device)

def run(args):
    if args.batch<9 or args.batch%3:raise ValueError("--batch must be multiple of 3, at least 9")
    if args.episodes<=0:raise ValueError("Need positive episode target")
    if args.side%2 or args.side<4:raise ValueError("side even and >=4")
    if args.side*args.side%12:raise ValueError("population must divide by 2,3,4")
    torch.set_num_threads(min(4,os.cpu_count() or 2))
    if torch.cuda.is_available():torch.set_float32_matmul_precision("high")
    cfg=current_cfg(args)
    run_dir=RUNS/args.run
    run_dir.mkdir(parents=True,exist_ok=True)
    config_path=run_dir/"config.json"
    config=asdict(cfg)
    config["architecture"]="independent-color-target-MLP-local-EMA"
    config["team_reward"]="N*(D_before-D_after)+proximity*(1-D_after), terminal common bonus"
    config["graph"]="toroidal square with diagonal perfect matching, degree 5"
    config["available_colors"]=COLORS
    if config_path.exists():
        saved=json.loads(config_path.read_text(encoding="utf-8"))
        if saved!=config:raise RuntimeError("Configuration mismatch. New experiment needs new --run.")
    else:
        atomic_json(config_path,config)
    torch.manual_seed(cfg.seed)
    if torch.cuda.is_available():torch.cuda.manual_seed_all(cfg.seed)
    model=IndependentPolicy(cfg.side**2,cfg.hidden).to(cfg.device)
    optimizer=torch.optim.AdamW(model.parameters(),lr=cfg.lr,weight_decay=.0003)
    done=0
    cp=run_dir/"latest.pt"
    if cp.exists():
        check=torch.load(cp,map_location=cfg.device,weights_only=False)
        if check["config"]!=config:raise RuntimeError("Checkpoint/config mismatch")
        done=check["updates"];model.load_state_dict(check["model"])
        optimizer.load_state_dict(check["optimizer"])
        print("RESUME",done,"updates",done*cfg.batch,"episodes",flush=True)
    (run_dir/"runner.pid").write_text(str(os.getpid()),encoding="utf-8")
    control_file=run_dir/"control.json"
    if not control_file.exists():atomic_json(control_file,{"pause":False,"stop":False})
    history_path=run_dir/"history.jsonl"
    t0=time.perf_counter()
    total=math.ceil(args.episodes/cfg.batch)
    last_dev=None
    if done>=total:
        print("Already reached target; no extra updates",flush=True)
        return
    def checkpoint(update):
        save_state(cp,{"model":model.state_dict(),"optimizer":optimizer.state_dict(),
                  "updates":update,"config":config})
    def status(state,update,other=None):
        payload={"state":state,"run":args.run,"device":cfg.device,"side":cfg.side,
                 "agents":cfg.side**2,"available_colors":COLORS,
                 "completed_episodes":update*cfg.batch,
                 "target_episodes":args.episodes,"updates":update,
                 "batch":cfg.batch,"horizon":cfg.horizon,
                 "elapsed_seconds":time.perf_counter()-t0,
                 "updates_per_second":(update-done)/max(.01,time.perf_counter()-t0),
                 "last_dev":last_dev,"checkpoint_exists":cp.exists()}
        if other:payload.update(other)
        atomic_json(run_dir/"status.json",payload)
    status("training",done)
    try:
        for update in range(done+1,total+1):
            control=json.loads(control_file.read_text(encoding="utf-8"))
            while control.get("pause"):
                status("paused",update-1)
                time.sleep(1)
                control=json.loads(control_file.read_text(encoding="utf-8"))
            if control.get("stop"):
                checkpoint(update-1);status("stopped",update-1)
                print("GRACEFUL_STOP",update-1,flush=True)
                break
            seed=cfg.seed+update*104729
            torch.manual_seed(seed)
            if cfg.device=="cuda":torch.cuda.manual_seed_all(seed)
            tasks=torch.tensor(([2,3,4]*(cfg.batch//3)),device=cfg.device)
            tasks=tasks[torch.randperm(cfg.batch,device=cfg.device)]
            world=Society(cfg,tasks)
            logps=[];entropies=[];rewards=[];churns=[]
            for t in range(cfg.horizon):
                actions=model.decisions(world)
                logps.append(actions["logp"])
                entropies.append(actions["entropy"])
                delta,turnover=world.advance(actions["choice"],actions["slot"],
                                              actions["request"],actions["rec"])
                # One common scalar reward for every agent in a world.
                reward=world.n*delta+cfg.proximity*(1-world.D)
                if t==cfg.horizon-1:reward=reward+cfg.terminal*(1-world.D)
                rewards.append(reward.detach())
                churns.append(turnover.detach())
            reward=torch.stack(rewards) # T,B
            returns=[];running=torch.zeros(cfg.batch,device=cfg.device)
            for t in range(cfg.horizon-1,-1,-1):
                running=reward[t]+cfg.gamma*running
                returns.append(running)
            returns=torch.stack(returns[::-1])
            advantage=torch.empty_like(returns)
            for k in (2,3,4):
                mask=world.k==k
                r=returns[:,mask]
                baseline=(r.sum(dim=1,keepdim=True)-r)/(r.shape[1]-1)
                scale=r.std(dim=1,unbiased=False,keepdim=True).clamp_min(.25)
                advantage[:,mask]=(r-baseline)/scale
            lp=torch.stack(logps)
            entropy=torch.stack(entropies)
            progress=min(1.,update/max(1,total))
            beta=cfg.entropy*(1-.8*progress)
            loss=-(lp.sum(-1)*advantage.detach()).mean()-beta*entropy.sum(-1).mean()
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            clip_sq=torch.zeros(model.n,device=cfg.device)
            for p in model.parameters():
                if p.grad is not None:
                    clip_sq+=p.grad.detach().reshape(model.n,-1).pow(2).sum(-1)
            norms=clip_sq.sqrt()
            factor=(cfg.clip/(norms+1e-10)).clamp(max=1)
            for p in model.parameters():
                if p.grad is not None:p.grad.mul_(factor.view(model.n,*([1]*(p.grad.ndim-1))))
            optimizer.step()
            if update==1 or update%args.log_every==0 or update==total:
                row={"update":update,"episodes":update*cfg.batch,
                    "D_train":float(world.D.mean()),"initial_D":float(world.initial.mean()),
                    "churn_train":float(torch.stack(churns)[-5:].mean()),
                    "loss":float(loss.detach()),"max_agent_grad":float(norms.max()),
                    "entropy":float(entropy.detach().mean())}
                if update%args.eval_every==0 or update==1 or update==total:
                    rows,replay=evaluate(model,cfg,seed=82000,batch=args.eval_batch,
                                         steps=args.eval_steps,replay=True)
                    last_dev=rows
                    atomic_json(run_dir/"replay.json",{
                       "kind":"development_not_test","updates":update,
                       "episodes":update*cfg.batch,"graph":world.graph.cpu().tolist(),
                       "n":world.n,"color_count":COLORS,"traces":replay})
                    row["development"]=rows
                with history_path.open("a",encoding="utf-8") as f:
                    f.write(json.dumps(row,ensure_ascii=False)+"\n")
                status("training",update,{"last_train":row})
                print("TRAIN",update,"EP",update*cfg.batch,"D",round(row["D_train"],4),
                    "CHURN",round(row["churn_train"],3),"DEV",
                    [(x["k"],round(x["final_D"],4),x["exact"]) for x in last_dev or []],
                    "SEC",round(time.perf_counter()-t0,1),flush=True)
            if update%args.checkpoint_every==0 or update==total:checkpoint(update)
        else:
            status("completed",total)
            print("TARGET_COMPLETED",total*cfg.batch,"episodes",flush=True)
    except BaseException as exc:
        checkpoint(max(done,update-1))
        status("failed",max(done,update-1),{"error":str(exc),"traceback":traceback.format_exc()[-5000:]})
        raise

def parse():
    p=argparse.ArgumentParser()
    p.add_argument("--run",default="principal")
    p.add_argument("--episodes",type=int,default=1_000_000)
    p.add_argument("--side",type=int,default=12)
    p.add_argument("--batch",type=int,default=48)
    p.add_argument("--horizon",type=int,default=16)
    p.add_argument("--hidden",type=int,default=64)
    p.add_argument("--seed",type=int,default=6123)
    p.add_argument("--device",choices=["auto","cpu","cuda"],default="auto")
    p.add_argument("--gamma",type=float,default=.99)
    p.add_argument("--lr",type=float,default=.0007)
    p.add_argument("--entropy",type=float,default=.0015)
    p.add_argument("--clip",type=float,default=5.)
    p.add_argument("--proximity",type=float,default=.25)
    p.add_argument("--terminal",type=float,default=2.)
    p.add_argument("--ema-alpha",type=float,default=.15)
    p.add_argument("--log-every",type=int,default=20)
    p.add_argument("--eval-every",type=int,default=200)
    p.add_argument("--eval-batch",type=int,default=12)
    p.add_argument("--eval-steps",type=int,default=64)
    p.add_argument("--checkpoint-every",type=int,default=100)
    return p.parse_args()

if __name__=="__main__":
    run(parse())
