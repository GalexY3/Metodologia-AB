"""Exploratory milestone diagnostics on DEVELOPMENT worlds, never reserved test.

Compare learned deterministic and stochastic policies to UNTRAINED policy.
No action or weight changes. Do not select checkpoints based on this.
"""
import argparse,json,torch
from pathlib import Path
from society10 import Society10,Config10
from actors10 import IndependentActors10
torch.set_num_threads(2)
ROOT=Path(__file__).resolve().parent

@torch.no_grad()
def evaluate(net,k,mode,det,worldseed=77800,batch=32,steps=100):
 e=Society10(Config10(batch=batch,seed=worldseed+100*k))
 e.reset(k=k)
 torch.manual_seed(worldseed+41*k+int(det)*200)
 Ds=[e.D.clone()];ch=[];messages=[]
 for _ in range(steps):
  obs=e.observe()
  send,_,_=net.act_send(obs,disable_messages=(mode=="C1"),deterministic=det)
  inc,req,pay=e.deliveries(obs,send)
  c,_,_=net.act_choose(obs,inc,req,pay,deterministic=det)
  z=e.step(send,c,inc,req)
  Ds.append(z["D"].clone());ch.append(z["churn"].clone());messages.append(z["messages"].clone())
 d=torch.stack(Ds);r=torch.stack(ch)
 return {"mode":mode,"k":k,"deterministic":det,"D_initial":float(d[0].mean()),
   "D_final":float(d[-1].mean()),"churn_last10":float(r[-10:].mean()),
   "occupied_end":float((e.histogram()>0).sum(-1).float().mean()),
   "exact":int(e.exact().sum()),"stable10":int(((d[-10:]<.02)&(r[-10:]<.05)).all(0).sum()),
   "messages":float(torch.stack(messages).mean())}

def main(args):
 torch.manual_seed(421)
 original=IndependentActors10(n=36,hidden=64)
 path=ROOT/"runs"/f"tenstates_N36_H64_seed421_{args.mode}_u10000"/f"MILESTONE_{args.update:05d}.pt"
 if not path.exists():raise RuntimeError("No completed milestone "+str(path))
 ck=torch.load(path,weights_only=False,map_location="cpu")
 assert ck["update"]==args.update
 actor=IndependentActors10(n=36,hidden=64)
 actor.load_state_dict(ck["model"]);actor.eval()
 diff=sum(float((x-y).abs().sum()) for x,y in zip(original.parameters(),actor.parameters()))
 baseline=sum(float(x.abs().sum()) for x in original.parameters())
 report={"mode":args.mode,"update":args.update,"weight_change_l1_frac":diff/(baseline+1e-9),"cases":[]}
 for condition,model in [("trained",actor),("untrained",original)]:
  for k in (2,3,4):
   for deterministic in (False,True):
    z=evaluate(model,k,args.mode,deterministic)
    z["weights"]=condition
    report["cases"].append(z)
    print("DIAG",args.mode,args.update,condition,k,"greedy" if deterministic else "sample",
       "D",round(z["D_final"],4),"occupied",round(z["occupied_end"],2),
       "exact",z["exact"],"stable",z["stable10"],
       "churn",round(z["churn_last10"],3),flush=True)
 print("WEIGHT_DRIFT",round(report["weight_change_l1_frac"],6),flush=True)
 out=ROOT/"development_diagnostics";out.mkdir(exist_ok=True)
 file=out/f"{args.mode}_u{args.update}.json"
 if file.exists():raise RuntimeError("Refuse overwrites")
 file.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")

if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--mode",choices=["C1","C2"],required=True)
 p.add_argument("--update",type=int,default=1000)
 main(p.parse_args())
