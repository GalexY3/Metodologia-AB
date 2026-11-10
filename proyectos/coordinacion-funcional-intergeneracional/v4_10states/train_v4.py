"""V4: long-budget independent REINFORCE, ten possible labels and k∈{2,3,4}.

Independent per-agent θ_i, collective-only reward and leave-one-OUT worlds
baseline matched by k. Resumable checkpoints include Adam state.
"""
import argparse,hashlib,json,time,math
from pathlib import Path
import torch
from society10 import Society10,Config10
from actors10 import IndependentActors10
torch.set_num_threads(2)
ROOT=Path(__file__).resolve().parent
CHECKPOINTS=(500,1000,2000,5000,10000)

def checksum(path):return hashlib.sha256(path.read_bytes()).hexdigest()

@torch.no_grad()
def test_dev(actor,k,comm,seed=77800,B=16,T=64):
 env=Society10(Config10(rows=6,cols=6,batch=B,seed=seed+100*k))
 env.reset(k=k)
 torch.manual_seed(seed+k+101)
 initial=float(env.D.mean())
 hist=[];rot=[];messages=[]
 for _ in range(T):
  o=env.observe()
  send,_,_=actor.act_send(o,disable_messages=not comm)
  inc,req,pay=env.deliveries(o,send)
  action,_,_=actor.act_choose(o,inc,req,pay)
  out=env.step(send,action,inc,req)
  hist.append(out["D"].clone());rot.append(out["churn"].clone());messages.append(out["messages"].clone())
 ds=torch.stack(hist);rs=torch.stack(rot)
 stable=((ds[-10:]<=.02)&(rs[-10:]<=.05)).all(0)
 return {"k":k,"initial_D":initial,"final_D":float(ds[-1].mean()),
 "last10_D":float(ds[-10:].mean()),"exact_at_T":int(env.exact().sum()),
 "stable10_count":int(stable.sum()),"mean_last10_churn":float(rs[-10:].mean()),
 "n_societies":B,"mean_send":float(torch.stack(messages).mean()),
 "occupied_final_mean":float((env.histogram()>0).sum(-1).float().mean())}

def main(args):
 if args.mode not in ("C1","C2"):raise ValueError("No such mode")
 if args.rows!=6 or args.cols!=6:
  raise ValueError("This first pre-registered V4 training is N36")
 if args.batch%3 or args.batch<6:raise ValueError("Batch must contain >=2 worlds per k")
 torch.manual_seed(args.seed)
 model=IndependentActors10(n=args.rows*args.cols,hidden=args.hidden)
 opt=torch.optim.Adam(model.parameters(),lr=args.lr)
 root=ROOT/"runs"/f"tenstates_N{model.n}_H{args.hidden}_seed{args.seed}_{args.mode}_u{args.updates}"
 settings=vars(args).copy()
 settings["policy_init_sha256"]=hashlib.sha256(
   b"".join(x.detach().cpu().numpy().tobytes() for x in model.parameters())).hexdigest()
 settings["policy_script_sha256"]=checksum(ROOT/"actors10.py")
 settings["society_script_sha256"]=checksum(ROOT/"society10.py")
 if args.resume:
  if not root.exists():raise RuntimeError("Cannot resume nonexistent experiment")
  prev=json.loads((root/"CONFIG.json").read_text(encoding="utf-8"))
  if prev!=settings:raise RuntimeError("Config changed: refuse unsafe resume")
  ck=torch.load(root/"LATEST.pt",weights_only=False,map_location="cpu")
  model.load_state_dict(ck["model"]);opt.load_state_dict(ck["optimizer"])
  start_step=ck["update"]
  records=json.loads((root/"TRAINING_LOG.json").read_text(encoding="utf-8"))
  if len(records)!=start_step:raise RuntimeError("Records vs checkpoint mismatch")
 else:
  if root.exists():raise RuntimeError("Refusing overwrite: "+str(root))
  root.mkdir(parents=True)
  (root/"CONFIG.json").write_text(json.dumps(settings,indent=2),encoding="utf-8")
  start_step=0
  records=[]
 print("TRAIN_START",args.mode,"N",model.n,"H",args.hidden,"updates",
       args.updates,"from",start_step,"k=2,3,4 ten possible labels",flush=True)
 t0=time.perf_counter()
 comm=(args.mode=="C2")
 for step in range(start_step+1,args.updates+1):
  torch.manual_seed(args.seed*100000+step) # deterministic for resume
  env=Society10(Config10(rows=args.rows,cols=args.cols,batch=args.batch,
               seed=args.seed*100000+step,
               churn_penalty=args.churn_penalty,reward_kind=args.reward_kind))
  ks=torch.tensor([2+i%3 for i in range(args.batch)],dtype=torch.long)
  env.reset(k=ks)
  chosen=[];ent=[];rewards=[];ds=[];ch=[]
  for tick in range(args.steps):
   obs=env.observe()
   sends,slp,sent=model.act_send(obs,disable_messages=not comm)
   incoming,req,snap=env.deliveries(obs,sends)
   colors,clp,cent=model.act_choose(obs,incoming,req,snap)
   out=env.step(sends,colors,incoming,req)
   chosen.append(slp+clp);ent.append(sent+cent)
   rewards.append(out["reward"].detach())
   ds.append(out["D"].detach());ch.append(out["churn"].detach())
  rewards=torch.stack(rewards) # T,B
  G=torch.zeros(args.batch)
  returns=[]
  for rr in reversed(rewards):
   G=rr+args.gamma*G;returns.append(G)
  returns=torch.stack(returns[::-1])
  baseline=torch.empty_like(returns)
  for k in (2,3,4):
   mask=ks==k;g=returns[:,mask];n=int(mask.sum())
   baseline[:,mask]=(g.sum(1,keepdim=True)-g)/(n-1)
  advantage=(returns-baseline).detach()/args.adv_scale
  lp=torch.stack(chosen)
  entropy=torch.stack(ent)
  # Exactly ONE team advantage per world and time, same for ALL its agents.
  loss=-(lp.sum(-1)*advantage).mean()-args.entropy_beta*entropy.sum(-1).mean()
  opt.zero_grad(set_to_none=True)
  loss.backward()
  n=model.n
  norm2=torch.zeros(n)
  for p in model.parameters():
   if p.grad is not None:norm2+=p.grad.detach().reshape(n,-1).pow(2).sum(1)
  norms=norm2.sqrt()
  scales=(args.clip/(norms+1e-12)).clamp(max=1)
  for p in model.parameters():
   if p.grad is not None:
    p.grad.mul_(scales.view(n,*([1]*(p.grad.ndim-1))))
  opt.step()
  row={"update":step,"D_last":float(ds[-1].mean()),
    "D_mean":float(torch.stack(ds).mean()),
    "churn_last":float(torch.stack(ch)[-5:].mean()),
    "team_reward_sum":float(rewards.sum(0).mean()),
    "max_agent_grad_norm_preclip":float(norms.max()),
    "loss":float(loss.detach())}
  if step in (1,500,1000,2000,5000,10000) or step%args.eval_every==0:
   with torch.no_grad():
    row["dev"]=[test_dev(model,k,comm) for k in (2,3,4)]
   print("DEVELOPMENT",args.mode,step,
      [(x["k"],round(x["final_D"],4),x["exact_at_T"],x["stable10_count"],
        round(x["mean_last10_churn"],3)) for x in row["dev"]],
      "elapsed_s",round(time.perf_counter()-t0,1),flush=True)
  elif step%args.log_every==0:
   print("TRAIN",args.mode,step,"D",round(row["D_last"],4),
     "churn",round(row["churn_last"],3),"maxgrad",round(row["max_agent_grad_norm_preclip"],2),
     "elapsed_s",round(time.perf_counter()-t0,1),flush=True)
  records.append(row)
  if step%args.checkpoint_every==0 or step in CHECKPOINTS or step==args.updates:
   tmp=root/"LATEST.tmp.pt"
   torch.save({"model":model.state_dict(),"optimizer":opt.state_dict(),
               "update":step,"config":settings},tmp)
   tmp.replace(root/"LATEST.pt")
   (root/"TRAINING_LOG.json").write_text(json.dumps(records,indent=1),encoding="utf-8")
   if step in CHECKPOINTS or step==args.updates:
    torch.save({"model":model.state_dict(),"optimizer":opt.state_dict(),
               "update":step,"config":settings},root/f"MILESTONE_{step:05d}.pt")
 if args.updates:
  torch.save({"model":model.state_dict(),"update":args.updates,"config":settings},
            root/"FINAL_MODEL.pt")
 print("TRAIN_COMPLETED",args.mode,args.updates,"episodes",args.updates*args.batch,
       "society_rounds",args.updates*args.batch*args.steps,
       "elapsed_s",round(time.perf_counter()-t0,2),flush=True)

if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--mode",choices=("C1","C2"),required=True)
 p.add_argument("--seed",type=int,default=421)
 p.add_argument("--updates",type=int,default=10000)
 p.add_argument("--rows",type=int,default=6)
 p.add_argument("--cols",type=int,default=6)
 p.add_argument("--hidden",type=int,default=64)
 p.add_argument("--batch",type=int,default=12)
 p.add_argument("--steps",type=int,default=32)
 p.add_argument("--lr",type=float,default=.001)
 p.add_argument("--gamma",type=float,default=.98)
 p.add_argument("--entropy-beta",type=float,default=.0005)
 p.add_argument("--adv-scale",type=float,default=10)
 p.add_argument("--clip",type=float,default=10)
 p.add_argument("--churn-penalty",type=float,default=.03)
 p.add_argument("--reward-kind",choices=("level","delta"),default="level")
 p.add_argument("--log-every",type=int,default=100)
 p.add_argument("--eval-every",type=int,default=1000)
 p.add_argument("--checkpoint-every",type=int,default=250)
 p.add_argument("--resume",action="store_true")
 main(p.parse_args())
