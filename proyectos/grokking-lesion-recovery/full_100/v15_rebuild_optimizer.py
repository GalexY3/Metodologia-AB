"""V15 rebuild final AdamW moments by exactly rerunning the final 4000 steps.
Compare state tensors with archived V12 final weights; fail closed if mismatch.
"""
from pathlib import Path
import json,csv,time
import torch
from torch.nn import functional as F
from parity_v10 import MLP,data
torch.set_num_threads(4)
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"v15_optimizer_states";OUT.mkdir(exist_ok=True)
seeds=[11,12,13,14,18]
x,y,ids=data(20261110,500,1000,2000)
tr_x=x[ids["train"]];tr_y=y[ids["train"]]
val_x=x[ids["val"]];val_y=y[ids["val"]]
@torch.no_grad()
def inspect(m):
 m.eval()
 a=m(tr_x);b=m(val_x)
 return float((a.argmax(1)==tr_y).float().mean()),float((b.argmax(1)==val_y).float().mean())
def run():
 t0=time.perf_counter()
 for seed in seeds:
  for initial in (1e-5,.001):
   label=f"seed{seed}_prior{initial:g}"
   inp=ROOT/"v12_runs"/label/"ck_006000.pt"
   desired=ROOT/"v12_runs"/label/"ck_010000.pt"
   target=OUT/label
   target.mkdir(exist_ok=True)
   file=target/"ck_010000_with_optimizer.pt"
   proof=target/"weight_match.json"
   if file.exists() and proof.exists():continue
   if file.exists()!=proof.exists():raise RuntimeError("Partial rebuild "+label)
   start=torch.load(inp,map_location="cpu",weights_only=False)
   originalfinal=torch.load(desired,map_location="cpu",weights_only=False)
   net=MLP(300);net.load_state_dict(start["model"])
   assert inspect(net)==(1.,1.)
   optim=torch.optim.AdamW(net.parameters(),lr=.001,weight_decay=0.)
   for step in range(1,4001):
    net.train();optim.zero_grad(set_to_none=True)
    loss=F.cross_entropy(net(tr_x),tr_y)+.0001*sum(v.abs().sum() for v in net.parameters())
    loss.backward();optim.step()
   actual=net.state_dict();expected=originalfinal["model"]
   keys=set(actual)|set(expected)
   if keys!=set(actual) or keys!=set(expected):raise RuntimeError("Model keys don't match")
   perkey={key:float((actual[key].float()-expected[key].float()).abs().max()) for key in actual}
   maximum=max(perkey.values())
   info={"seed":seed,"initial_L1":initial,"step_start":6000,"step_final":10000,
     "continued_L1":.0001,"optimizer":"AdamW, fresh at step6000, state preserved through step10000",
     "max_model_weight_difference":maximum,"max_differences_by_key":perkey,
     "same_weights_tolerance":1e-6,"weights_verified":maximum<=1e-6,
     "final_train_val_accuracy":inspect(net),
     "optimizer_state_entries":len(optim.state),
     "source_checkpoint":str(desired),
     "protocol":"PREREG_V15_OPTIMIZER_REPAIR.md"}
   if not info["weights_verified"]:raise RuntimeError("Rebuild differs from original V12 "+json.dumps(info))
   torch.save({"model":net.state_dict(),"optimizer":optim.state_dict(),"config":info,"step":10000},file)
   proof.write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding="utf-8")
   print("V15_REBUILT",seed,initial,"maxdiff",maximum,"optim_params",len(optim.state),
     "elapsed",round(time.perf_counter()-t0,1),flush=True)
 print("V15_REBUILD_DONE",round(time.perf_counter()-t0,1),flush=True)
if __name__=="__main__":run()
