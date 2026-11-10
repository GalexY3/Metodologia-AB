"""Pilot: independently trained agent policies with local W1/W8 history.

Four C2 variants, a 2x2 design of memory W1 vs W8 and width 64 vs128.
Same team reward, seed, batch, horizon and optimizer. All agent theta_i
independent; same color scoring within each agent, no global population input.
"""
import sys,json,argparse,hashlib,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/"v4_10states"))
import torch
from society10 import Society10,Config10
from agents_memory import MemoryAgents10
torch.set_num_threads(2)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

@torch.no_grad()
def development(net,k,communication,seed=775111,batch=16,steps=64):
 e=Society10(Config10(batch=batch,seed=seed+100*k,
                        churn_penalty=.03,reward_kind="level"))
 e.reset(k=k);net.reset_memory(batch)
 torch.manual_seed(seed+k+300)
 ds=[e.D.clone()];changes=[]
 for _ in range(steps):
  obs=e.observe()
  sent,_,_=net.act_send(obs,disable_messages=not communication)
  incoming,req,pay=e.deliveries(obs,sent)
  color,_,_=net.act_choose(obs,incoming,req,pay,sent)
  metrics=e.step(sent,color,incoming,req)
  ds.append(metrics["D"].clone());changes.append(metrics["churn"].clone())
 D=torch.stack(ds);C=torch.stack(changes)
 stable=((D[-10:]<=.02)&(C[-10:]<=.05)).all(0)
 return {"k":k,"D_initial":float(D[0].mean()),"D_final":float(D[-1].mean()),
         "D_last10":float(D[-10:].mean()),"occupied":float((e.histogram()>0).sum(-1).float().mean()),
         "exact":int(e.exact().sum()),"stable":int(stable.sum()),
         "churn_last10":float(C[-10:].mean()),"worlds":batch}

def main(args):
 if args.mode!="C2":raise ValueError("V5 prereg pilot only C2.")
 if args.batch%3 or args.batch<6:raise ValueError("Need >=2 worlds per k")
 if args.mem not in (1,8) or args.hidden not in (64,128):raise ValueError("Invalid architecture")
 torch.manual_seed(args.seed)
 model=MemoryAgents10(n=36,hidden=args.hidden,memory=args.mem)
 optimizer=torch.optim.Adam(model.parameters(),lr=args.lr)
 folder=ROOT/"runs"/f"W{args.mem}_H{args.hidden}_{args.mode}_seed{args.seed}_u{args.updates}"
 if folder.exists():raise RuntimeError("Refuse to overwrite existing pilot")
 folder.mkdir(parents=True)
 config=vars(args).copy()
 config.update({"n_independent_policies":36,"parameter_count_total":sum(x.numel() for x in model.parameters()),
                "parameters_per_agent":sum(x.numel() for x in model.parameters())//36,
                "score_width":args.hidden,"depth_hidden_layers":2,"memory_window":args.mem,
                "policy_sha":sha(ROOT/"agents_memory.py"),
                "environment_sha":sha(ROOT.parent/"v4_10states"/"society10.py")})
 (folder/"CONFIG.json").write_text(json.dumps(config,indent=2,ensure_ascii=False),encoding="utf-8")
 print("V5_START",folder.name,"PARAMS",config["parameter_count_total"],
       "per_agent",config["parameters_per_agent"],flush=True)
 all_logs=[];t0=time.perf_counter()
 for step in range(1,args.updates+1):
  torch.manual_seed(args.seed*100000+step)
  e=Society10(Config10(batch=args.batch,seed=args.seed*100000+step,
                       churn_penalty=.03,reward_kind="level"))
  ks=torch.tensor([2+i%3 for i in range(args.batch)],dtype=torch.long)
  e.reset(k=ks)
  model.reset_memory(args.batch)
  lp=[];ent=[];reward=[];D=[];churn=[]
  for tick in range(args.steps):
   obs=e.observe()
   send,send_lp,send_ent=model.act_send(obs)
   incoming,request,payload=e.deliveries(obs,send)
   colors,color_lp,color_ent=model.act_choose(obs,incoming,request,payload,send)
   z=e.step(send,colors,incoming,request)
   lp.append(send_lp+color_lp)
   ent.append(send_ent+color_ent)
   reward.append(z["reward"].detach())
   D.append(z["D"].detach());churn.append(z["churn"].detach())
  rewards=torch.stack(reward)
  G=torch.zeros(args.batch)
  sequence=[]
  for r in reversed(rewards):
   G=r+args.gamma*G;sequence.append(G)
  ret=torch.stack(sequence[::-1])
  baseline=torch.empty_like(ret)
  for k in (2,3,4):
   mask=(ks==k);s=ret[:,mask]
   baseline[:,mask]=(s.sum(1,keepdim=True)-s)/(int(mask.sum())-1)
  advantage=(ret-baseline).detach()/args.adv_scale
  logits_lp=torch.stack(lp)
  entropy=torch.stack(ent)
  loss=-(logits_lp.sum(-1)*advantage).mean()-args.entropy_beta*entropy.sum(-1).mean()
  optimizer.zero_grad(set_to_none=True)
  loss.backward()
  n=model.n
  norm_sq=torch.zeros(n)
  for p in model.parameters():
   if p.grad is not None:
    norm_sq+=p.grad.detach().reshape(n,-1).pow(2).sum(1)
  norms=norm_sq.sqrt()
  clip=(args.grad_clip/(norms+1e-12)).clamp(max=1)
  for p in model.parameters():
   if p.grad is not None:
    p.grad.mul_(clip.view(n,*([1]*(p.grad.ndim-1))))
  optimizer.step()
  log={"update":step,
       "D_train_final":float(D[-1].mean()),
       "D_train_mean":float(torch.stack(D).mean()),
       "churn_tail":float(torch.stack(churn)[-5:].mean()),
       "team_return_mean":float(rewards.sum(0).mean()),
       "max_norm_preclip":float(norms.max()),
       "objective":float(loss.detach())}
  if step==1 or step%args.eval_every==0 or step==args.updates:
   log["development"]=[development(model,k,True) for k in (2,3,4)]
   print("V5_DEV",folder.name,step,[(q["k"],round(q["D_final"],4),
      round(q["occupied"],1),q["exact"],q["stable"],
      round(q["churn_last10"],3)) for q in log["development"]],
      "elapsed",round(time.perf_counter()-t0,1),flush=True)
  elif step%args.log_every==0:
   print("V5_TRAIN",folder.name,step,"D",round(log["D_train_final"],4),
      "churn",round(log["churn_tail"],3),
      "grad",round(log["max_norm_preclip"],5),
      "elapsed",round(time.perf_counter()-t0,1),flush=True)
  all_logs.append(log)
  if step%50==0 or step==args.updates:
   (folder/"TRAINING_LOG.json").write_text(json.dumps(all_logs,indent=1,
           ensure_ascii=False),encoding="utf-8")
   torch.save({"model":model.state_dict(),"config":config,
               "update":step},folder/f"CHECKPOINT_{step:04d}.pt")
 (folder/"CONFIG.json").write_text(json.dumps(config,indent=2,ensure_ascii=False),encoding="utf-8")
 torch.save({"model":model.state_dict(),"config":config,"update":args.updates},
            folder/"FINAL_MODEL.pt")
 print("V5_DONE",folder.name,args.updates,"worlds",args.updates*args.batch,
       "elapsed",round(time.perf_counter()-t0,1),flush=True)

if __name__=="__main__":
 ap=argparse.ArgumentParser()
 ap.add_argument("--mode",default="C2")
 ap.add_argument("--mem",type=int,required=True)
 ap.add_argument("--hidden",type=int,required=True)
 ap.add_argument("--seed",type=int,default=521)
 ap.add_argument("--updates",type=int,default=150)
 ap.add_argument("--batch",type=int,default=12)
 ap.add_argument("--steps",type=int,default=32)
 ap.add_argument("--lr",type=float,default=.001)
 ap.add_argument("--gamma",type=float,default=.98)
 ap.add_argument("--entropy-beta",type=float,default=.0005)
 ap.add_argument("--adv-scale",type=float,default=10)
 ap.add_argument("--grad-clip",type=float,default=10)
 ap.add_argument("--eval-every",type=int,default=50)
 ap.add_argument("--log-every",type=int,default=25)
 main(ap.parse_args())
