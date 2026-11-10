"""Sealed V4 evaluation after 10,000-update training (no checkpoint selection).

Ten AVAILABLE states, target exactly k arbitrarily chosen labels at 1/k.
Both stochastic and greedy deployment are evaluated; no retraining.
"""
import json,hashlib,torch,time
from pathlib import Path
from society10 import Society10,Config10,C
from actors10 import IndependentActors10
torch.set_num_threads(2)
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"holdout"
KS=(2,3,4)
MODES=("C1","C2","C3","C1_greedy","C2_greedy","C3_greedy",
       "random_always","random_T24","stay")
N=36
B=100
T=120

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def checkpoint(mode):return ROOT/"runs"/f"tenstates_N36_H64_seed421_{mode}_u10000"/"FINAL_MODEL.pt"

def ref_iid(k,seed=20261110,n=36,rep=100000):
 gen=torch.Generator().manual_seed(seed+n*100+k)
 total=0.0
 for _ in range(rep//2000):
  colors=torch.randint(0,C,(2000,n),generator=gen)
  f=torch.nn.functional.one_hot(colors,C).float().mean(1)
  scores=f.topk(k).values.clamp(max=1/k).sum(1)
  total+=float((1-scores).sum())
 return total/rep

@torch.no_grad()
def run(net,k,mode,worldseed,reference):
 torch.manual_seed(worldseed+sum(ord(c) for c in mode)*53)
 env=Society10(Config10(rows=6,cols=6,batch=B,seed=worldseed))
 env.reset(k=k)
 D=[env.D.clone()]
 churn=[]
 occupied=[]
 exact=[]
 message=[]
 values=[]
 deterministic=mode.endswith("_greedy")
 use_random=mode.startswith("random")
 active_comm=mode.startswith("C2") or mode.startswith("random")
 for tick in range(T):
  o=env.observe()
  if mode=="stay" or (mode=="random_T24" and tick>=24):
   send=torch.zeros((B,N),dtype=torch.long)
   inc,req,pay=env.deliveries(o,send)
   choose=env.colors.clone()
  else:
   send,_,_=net.act_send(o,disable_messages=not active_comm,
             uniform=use_random,deterministic=deterministic)
   inc,req,pay=env.deliveries(o,send)
   choose,_,_=net.act_choose(o,inc,req,pay,
             uniform=use_random,deterministic=deterministic)
  r=env.step(send,choose,inc,req)
  D.append(r["D"].clone())
  churn.append(r["churn"].clone())
  occupied.append(r["occupied"].clone())
  exact.append(r["exact"].clone())
  message.append(r["messages"].clone())
  values.append(r["reward"].clone())
 ds=torch.stack(D)
 ch=torch.stack(churn)
 oc=torch.stack(occupied)
 ex=torch.stack(exact)
 strict=((ds[-10:]<=.02)&(ch[-10:]<=.05)).all(0)
 practical=((ds[-10:]<=.06)&(ch[-10:]<=.05)).all(0)
 exact_stable=ex[-10:].all(0)&(ch[-10:]<=.05).all(0)
 return {"mode":mode,"k":k,"worldseed":worldseed,"n":N,"worlds":B,
   "ticks":T,"reference_iid10_D":reference,
   "D_initial":float(ds[0].mean()),
   "D_final":float(ds[-1].mean()),
   "D_tail10":float(ds[-10:].mean()),
   "ratio_to_iid10":float(ds[-1].mean())/reference,
   "D_mean_T1_120":float(ds[1:].mean()),
   "churn_tail10":float(ch[-10:].mean()),
   "exact_count_final":int(ex[-1].sum()),
   "exact_count_anytime":int(ex.any(0).sum()),
   "exact_stable_count":int(exact_stable.sum()),
   "stable_strict_count":int(strict.sum()),
   "stable_practical_count":int(practical.sum()),
   "occupied_final_mean":float(oc[-1].float().mean()),
   "occupied_equal_k_final_count":int((oc[-1]==k).sum()),
   "send_rate":float(torch.stack(message).mean()),
   "D_curve":ds.mean(-1).tolist(),
   "churn_curve":ch.mean(-1).tolist(),
   "occupied_curve":oc.float().mean(-1).tolist(),
   "final_D_worlds":ds[-1].tolist(),
   "final_occupied_worlds":oc[-1].tolist(),
   "exact_final_worlds":ex[-1].tolist()}

def main():
 OUT.mkdir(exist_ok=True)
 paths={m:checkpoint(m) for m in ("C1","C2")}
 if any(not p.exists() for p in paths.values()):
  raise RuntimeError("Both completed 10000-update models required; do not substitute partial.")
 lock={
  "protocol":"PREREG_V4.md",
  "test_script":sha(ROOT/"evaluate_v4.py"),
  "policy_script":sha(ROOT/"actors10.py"),
  "society_script":sha(ROOT/"society10.py"),
  "weights_sha":{m:sha(p) for m,p in paths.items()},
  "n":N,"k":[2,3,4],"worlds_per_k_mode":B,"steps":T,
  "worldseed":"4900000+100*k",
  "no_learning":True,"conditions":list(MODES),
  "iid_reference_seed":20261110}
 loc=OUT/"LOCK.json"
 if loc.exists():
  if json.loads(loc.read_text(encoding="utf-8"))!=lock:raise RuntimeError("Holdout lock mismatch")
 else:loc.write_text(json.dumps(lock,ensure_ascii=False,indent=2),encoding="utf-8")
 nets={}
 for key,p in paths.items():
  z=torch.load(p,map_location="cpu",weights_only=False)
  if z["update"]!=10000:raise RuntimeError("Partial checkpoint forbidden")
  a=IndependentActors10(n=N,hidden=64)
  a.load_state_dict(z["model"]);a.eval()
  nets[key]=a
 rows=[]
 t0=time.perf_counter()
 for k in KS:
  ref=ref_iid(k)
  for mode in MODES:
   path=OUT/f"k{k}_{mode}.json"
   if path.exists():
    result=json.loads(path.read_text(encoding="utf-8"))
   else:
    actor=nets["C1"] if mode.startswith("C1") else nets["C2"]
    result=run(actor,k,mode,4900000+100*k,ref)
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
   rows.append({key:value for key,value in result.items() if key not in
              ("D_curve","churn_curve","occupied_curve","final_D_worlds",
                "final_occupied_worlds","exact_final_worlds")})
   print("V4_HELDOUT",k,mode,"D",round(result["D_final"],4),
        "IIDratio",round(result["ratio_to_iid10"],3),
        "occupied",round(result["occupied_final_mean"],2),
        "exact",result["exact_count_final"],
        "stable",result["stable_practical_count"],"/",B,
        "churn",round(result["churn_tail10"],3),
        "elapsed",round(time.perf_counter()-t0,1),flush=True)
 p=OUT/"SUMMARY.json"
 if p.exists():raise RuntimeError("Do not overwrite summary")
 p.write_text(json.dumps({"lock":lock,"cases":rows,
  "n_training_seeds":1,
  "note":"One training seed, worlds nested; stochastic/greedy and controls, NOT 100 independent learned societies."},
   ensure_ascii=False,indent=2),encoding="utf-8")
 print("V4_HELDOUT_DONE",len(rows),"cases",flush=True)

if __name__=="__main__":main()
