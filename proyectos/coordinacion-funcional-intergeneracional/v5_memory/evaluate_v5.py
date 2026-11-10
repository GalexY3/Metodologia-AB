"""Reserved test for all 2x2 memory/width variants and no-training controls.

Only loads FINAL_MODEL.pt after each fixed pilot finishes. Locks SHA256 of
all models and scripts before running on new synthetic worlds.
"""
import sys,json,hashlib,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/"v4_10states"))
import torch
from torch.distributions import Categorical
from society10 import Society10,Config10,C,S
from agents_memory import MemoryAgents10
from evaluate_v4 import ref_iid
torch.set_num_threads(2)
OUT=ROOT/"holdout"
VARIANTS=((1,64),(1,128),(8,64),(8,128))
KS=(2,3,4)
B=100;T=100
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def model_path(mem,hidden):
 return ROOT/"runs"/f"W{mem}_H{hidden}_C2_seed521_u150"/"FINAL_MODEL.pt"

@torch.no_grad()
def evaluate(net,k,model_tag,kind,worldseed,reference):
 e=Society10(Config10(batch=B,seed=worldseed,reward_kind="level",churn_penalty=.03))
 e.reset(k=k)
 if net is not None:net.reset_memory(B)
 torch.manual_seed(worldseed+(1 if kind=="greedy" else 0))
 D=[e.D.clone()];C_h=[];occupied=[];messages=[];exact=[]
 for t in range(T):
  if kind=="no_history" and net is not None:net.reset_memory(B)
  observation=e.observe()
  stop=(kind=="stay" or (kind=="random_T24" and t>=24))
  if stop:
   send=torch.zeros((B,e.n),dtype=torch.long)
   inc,req,payload=e.deliveries(observation,send)
   choose=e.colors.clone()
  elif kind in ("random_always","random_T24"):
   # Same physical freedom to self-change and to send one legal request.
   legal=e.send_mask()
   probs=legal.float()/legal.float().sum(-1,keepdim=True)
   send=Categorical(probs=probs).sample()
   inc,req,payload=e.deliveries(observation,send)
   choose=torch.randint(0,C,(B,e.n))
  else:
   send,_,_=net.act_send(observation,deterministic=(kind=="greedy"))
   inc,req,payload=e.deliveries(observation,send)
   choose,_,_=net.act_choose(observation,inc,req,payload,send,
                              deterministic=(kind=="greedy"))
  result=e.step(send,choose,inc,req)
  D.append(result["D"].clone())
  C_h.append(result["churn"].clone())
  occupied.append(result["occupied"].clone())
  exact.append(result["exact"].clone())
  messages.append(result["messages"].clone())
 ds=torch.stack(D)
 ch=torch.stack(C_h)
 ex=torch.stack(exact)
 occ=torch.stack(occupied)
 stable=((ds[-10:]<=.02)&(ch[-10:]<=.05)).all(0)
 return {"variant":model_tag,"kind":kind,"k":k,"n":e.n,"n_worlds":B,
         "ticks":T,"seed_world":worldseed,
         "D_initial":float(ds[0].mean()),"D_final":float(ds[-1].mean()),
         "D_tail10":float(ds[-10:].mean()),
         "D_auc":float(ds[1:].mean()),
         "ratio_iid10":float(ds[-1].mean())/reference,
         "n_exact_final":int(ex[-1].sum()),
         "n_exact_any":int(ex.any(0).sum()),
         "n_stable10":int(stable.sum()),
         "occupied_final":float(occ[-1].float().mean()),
         "n_occupied_eq_k":int((occ[-1]==k).sum()),
         "churn_last10":float(ch[-10:].mean()),
         "send_rate":float(torch.stack(messages).mean()),
         "D_curve":ds.mean(1).tolist(),
         "occupied_curve":occ.float().mean(1).tolist(),
         "churn_curve":torch.cat((torch.zeros(1),ch.mean(1))).tolist(),
         "D_by_world":ds[-1].tolist()}
def main():
 ck={(m,h):model_path(m,h) for m,h in VARIANTS}
 for p in ck.values():
  if not p.exists():raise RuntimeError("Missing completed model "+str(p))
 lock={
  "protocol":"PREREG_V5.md","seed_train":521,
  "k":list(KS),"n_societies_per_variant_kind_k":B,"ticks":T,
  "worldseed":"7200000+100*k",
  "code_sha":{name:digest(ROOT/name) for name in
                ("agents_memory.py","train_v5.py","evaluate_v5.py")},
  "environment_sha":digest(ROOT.parent/"v4_10states"/"society10.py"),
  "weights":{f"W{m}_H{h}":digest(p) for (m,h),p in ck.items()},
  "evaluation":"stochastic and deterministic, frozen; untrained controls from same seed",
  "no_test_tuning":True}
 OUT.mkdir(exist_ok=True)
 lockfile=OUT/"LOCK.json"
 if lockfile.exists():
  if json.loads(lockfile.read_text(encoding="utf-8"))!=lock:raise RuntimeError("Lock mismatch")
 else:lockfile.write_text(json.dumps(lock,indent=2,ensure_ascii=False),encoding="utf-8")
 actors={}
 untrained={}
 for (m,h),path in ck.items():
  raw=torch.load(path,weights_only=False,map_location="cpu")
  if raw["update"]!=150 or raw["config"]["mem"]!=m or raw["config"]["hidden"]!=h:
   raise RuntimeError("Model/checkpoint mismatch")
  actor=MemoryAgents10(n=36,hidden=h,memory=m)
  actor.load_state_dict(raw["model"]);actor.eval()
  actors[(m,h)]=actor
  torch.manual_seed(521)
  plain=MemoryAgents10(n=36,hidden=h,memory=m)
  plain.eval()
  untrained[(m,h)]=plain
 table=[];start=time.perf_counter()
 for k in KS:
  worldseed=7200000+100*k
  reference=ref_iid(k)
  for m,h in VARIANTS:
   tag=f"W{m}_H{h}"
   for stage,model in (("trained",actors[(m,h)]),
                       ("untrained",untrained[(m,h)])):
    kinds=("sample","greedy","no_history") if m==8 and stage=="trained" else ("sample","greedy")
    for kind in kinds:
     dest=OUT/f"k{k}_{tag}_{stage}_{kind}.json"
     if dest.exists():
      row=json.loads(dest.read_text(encoding="utf-8"))
     else:
      row=evaluate(model,k,f"{tag}_{stage}",kind,worldseed,reference)
      dest.write_text(json.dumps(row,indent=2,ensure_ascii=False),encoding="utf-8")
     table.append({a:b for a,b in row.items() if a not in
                ("D_curve","occupied_curve","churn_curve","D_by_world")})
     print("V5_HOLDOUT",k,tag,stage,kind,"D",round(row["D_final"],4),
           "occupied",round(row["occupied_final"],2),"stable",row["n_stable10"],
           "exact",row["n_exact_final"],"churn",round(row["churn_last10"],3),
           "elapsed",round(time.perf_counter()-start,1),flush=True)
  for kind in ("random_always","random_T24","stay"):
   dest=OUT/f"k{k}_{kind}.json"
   if dest.exists():
    row=json.loads(dest.read_text(encoding="utf-8"))
   else:
    row=evaluate(None,k,"baseline",kind,worldseed,reference)
    dest.write_text(json.dumps(row,indent=2,ensure_ascii=False),encoding="utf-8")
   table.append({a:b for a,b in row.items() if a not in
                ("D_curve","occupied_curve","churn_curve","D_by_world")})
   print("V5_BASELINE",k,kind,"D",round(row["D_final"],4),flush=True)
 (OUT/"SUMMARY.json").write_text(json.dumps({
   "lock":lock,"n_independent_training_seeds":1,
   "cautions":["100 test worlds share one trained population per architecture",
    "The MLP has two hidden layers, NOT explicit causal planning",
    "Observational memory is a fixed eight-tick buffer, NOT an LSTM/GRU",
    "Greedy vs sampling compares deployment policies, not reward optimization"],
   "rows":table},indent=2,ensure_ascii=False),encoding="utf-8")
 print("V5_HOLDOUT_DONE",len(table),round(time.perf_counter()-start,1),flush=True)
if __name__=="__main__":main()
