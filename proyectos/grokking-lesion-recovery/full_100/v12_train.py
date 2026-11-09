"""Prospective V12 replication: independent seeds and split, no test-label access
for selection, training or interim analysis. See PREREG_V12.md.
"""
from pathlib import Path
import csv,json,hashlib,time,torch
from torch.nn import functional as F
from parity_v10 import MLP,data

torch.set_num_threads(4)
ROOT=Path(__file__).resolve().parent
DIR=ROOT/"v12_runs"
DIR.mkdir(exist_ok=True)
SPLIT=20261110
x,y,ids=data(SPLIT,500,1000,2000)
train_x=x[ids["train"]];train_y=y[ids["train"]]
val_x=x[ids["val"]];val_y=y[ids["val"]]
# Do not inspect test data or labels until AFTER pair selection and lesion analysis.
@torch.no_grad()
def measure(model,step):
 model.eval()
 a=model(train_x)
 b=model(val_x)
 return {"step":step,
         "train_acc":float((a.argmax(1)==train_y).float().mean()),
         "val_acc":float((b.argmax(1)==val_y).float().mean()),
         "train_ce":float(F.cross_entropy(a,train_y)),
         "val_ce":float(F.cross_entropy(b,val_y)),
         "weight_norm":float(torch.sqrt(sum(v.detach().square().sum() for v in model.parameters())))}

def historygate(rows,lam):
 firstfit=next((int(r["step"]) for r in rows if r["train_acc"]>=.99),None)
 firstgen=next((int(r["step"]) for r in rows if r["val_acc"]>=.95),None)
 lag=firstgen-firstfit if (firstfit is not None and firstgen is not None) else None
 longlow=bool(firstfit is not None and any(r["step"]>=firstfit+1000 and r["val_acc"]<=.65 for r in rows))
 stable=(len(rows)>=5 and all(r["train_acc"]==1. and r["val_acc"]==1. for r in rows[-5:]))
 hist_ok=bool(lag is not None and ((lag>=1000 and longlow) if lam==1e-5 else (lag<1000 and not longlow)))
 return {"first_train99":firstfit,"first_val95":firstgen,"lag":lag,
         "low_val_1000postfit":longlow,"stable_last5":stable,
         "history_ok":hist_ok,"eligible":hist_ok and stable}

def csvsave(path,rows):
 with path.open("w",newline="",encoding="utf-8") as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]))
  w.writeheader();w.writerows(rows)

def first_phase(seed,lam):
 name=f"seed{seed}_prior{lam:g}"
 d=DIR/name
 if d.exists():raise FileExistsError(d)
 d.mkdir(parents=True)
 torch.manual_seed(seed)
 model=MLP(300)
 opt=torch.optim.AdamW(model.parameters(),lr=.001,weight_decay=0.)
 hist=[measure(model,0)]
 start=time.perf_counter()
 for step in range(1,6001):
  model.train();opt.zero_grad(set_to_none=True)
  pred=model(train_x)
  loss=F.cross_entropy(pred,train_y)+lam*sum(v.abs().sum() for v in model.parameters())
  loss.backward();opt.step()
  if step%100==0:hist.append(measure(model,step))
 gate=historygate(hist,lam)
 csvsave(d/"phase1.csv",hist)
 cfg={"seed":seed,"prior_lambda":lam,"split_seed":SPLIT,
      "ntrain":500,"nval":1000,"ntest_reserved":2000,
      "train_and_val_only":True,"gate":gate,
      "input_data_sha256":hashlib.sha256(x.numpy().tobytes()).hexdigest(),
      "train_labels_sha256":hashlib.sha256(train_y.numpy().tobytes()).hexdigest(),
      "protocol":"PREREG_V12.md"}
 (d/"config.json").write_text(json.dumps(cfg,indent=2),encoding="utf-8")
 torch.save({"model":model.state_dict(),"optimizer":opt.state_dict(),"config":cfg,"step":6000},d/"ck_006000.pt")
 print("V12_A",seed,lam,"train",round(hist[-1]["train_acc"],3),"val",round(hist[-1]["val_acc"],3),
       "lag",gate["lag"],"eligible",gate["eligible"],"elapsed",round(time.perf_counter()-start,1),flush=True)
 return d,model,gate

def common_phase(d,model,seed,lam):
 opt=torch.optim.AdamW(model.parameters(),lr=.001,weight_decay=0.)
 hist=[measure(model,6000)]
 for i in range(1,4001):
  model.train();opt.zero_grad(set_to_none=True)
  pred=model(train_x)
  loss=F.cross_entropy(pred,train_y)+.0001*sum(v.abs().sum() for v in model.parameters())
  loss.backward();opt.step()
  if i%250==0:
   hist.append(measure(model,6000+i))
   if i%2000==0:
    torch.save({"model":model.state_dict(),"seed":seed,"prior_lambda":lam,
                "common_lambda":.0001,"step":6000+i,"protocol":"PREREG_V12.md"},d/f"ck_{6000+i:06d}.pt")
 csvsave(d/"phase2.csv",hist)
 stable=len(hist)>=5 and all(r["train_acc"]==1. and r["val_acc"]==1. for r in hist[-5:])
 print("V12_B",seed,lam,"val",round(hist[-1]["val_acc"],4),"stable",stable,flush=True)
 return stable

def main():
 gates=[];finished=[]
 for seed in range(10,20):
  two={}
  for lam in (1e-5,.001):
   d,model,gate=first_phase(seed,lam)
   two[lam]=(d,model,gate)
  eligible=all(two[lam][2]["eligible"] for lam in two)
  gates.append({"seed":seed,"paired_eligible_phase1":eligible,
                 "A":two[1e-5][2],"B":two[.001][2]})
  (DIR/"V12_GATE_LOG.json").write_text(json.dumps(gates,indent=2),encoding="utf-8")
  if eligible:
   for lam in (1e-5,.001):
    d,model,_=two[lam]
    stable=common_phase(d,model,seed,lam)
    finished.append({"seed":seed,"lambda":lam,"stable_common":stable})
    (DIR/"V12_COMMON_LOG.json").write_text(json.dumps(finished,indent=2),encoding="utf-8")
 eligible_seeds=[g["seed"] for g in gates if g["paired_eligible_phase1"] and
      len([z for z in finished if z["seed"]==g["seed"] and z["stable_common"]])==2]
 result={"phase1_gates":gates,"common_phase":finished,
         "eligible_for_lesions":eligible_seeds,
         "test_not_consulted":True,"protocol":"PREREG_V12.md"}
 (ROOT/"V12_GATES.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
 print("V12_TRAINING_COMPLETE",len(gates),"eligible_for_lesion",eligible_seeds,flush=True)

if __name__=="__main__": main()
