"""V10B injury study on five pairs of eligible parity networks.
The same physical neuron masks are paired within each seed.
Fresh shared repair optimizer, uninjured continuation, and nested perturbations.
"""
from pathlib import Path
import argparse,copy,json,csv,statistics,math,time
import numpy as np
import torch
from torch.nn import functional as F
from parity_v10 import MLP,data,measure
ROOT=Path(__file__).resolve().parent
torch.set_num_threads(4)

def repair(m,x,y,ix,horizon=400,every=10,lr=.001):
    optimizer=torch.optim.AdamW(m.parameters(),lr=lr,weight_decay=0.)
    arr=[measure(m,x,y,ix,0)]
    for step in range(1,horizon+1):
        m.train();optimizer.zero_grad(set_to_none=True)
        loss=F.cross_entropy(m(x[ix["train"]]),y[ix["train"]])
        loss.backward();optimizer.step()
        if step%every==0 or step==horizon:arr.append(measure(m,x,y,ix,step))
    return arr

def first_stable(arr,threshold=.99,consecutive=2):
    for i in range(len(arr)-consecutive+1):
        if all(arr[j]["val_acc"]>=threshold for j in range(i,i+consecutive)):
            return arr[i]["step"]
    return None

def run(args):
    eligibility=json.loads((ROOT/"V10_ELIGIBILITY.json").read_text(encoding="utf-8"))
    good=eligibility["eligible_seeds"]
    if not good:raise RuntimeError("No eligible matched models")
    observations=[]
    out=ROOT/"parity_lesions"
    out.mkdir(exist_ok=True)
    for seed in good:
        x,y,ids=data(20261109,500,1000,2000)
        for lam in (1e-5,.001):
            name=f"lambda{lam:g}_seed{seed}_lr0.001_width300_nt500"
            ckfile=ROOT/"parity_runs"/name/"ck_008000.pt"
            ck=torch.load(ckfile,map_location="cpu",weights_only=False)
            model=MLP(300);model.load_state_dict(ck["model"])
            base=measure(model,x,y,ids,0)
            if base["train_acc"]!=1. or base["val_acc"]!=1. or base["test_acc"]!=1.:
                raise ValueError(f"Gate became invalid: {name}")
            folder=out/name;folder.mkdir(exist_ok=True)
            crows=repair(copy.deepcopy(model),x,y,ids,args.steps,args.every,args.lr)
            with (folder/"control.csv").open("w",newline="",encoding="utf-8") as f:
                writer=csv.DictWriter(f,fieldnames=list(crows[0]));writer.writeheader();writer.writerows(crows)
            for dose in args.doses:
                for ms in args.masks:
                    rng=np.random.default_rng(ms)
                    indices=sorted(rng.choice(300,dose,replace=False).tolist())
                    lesion=copy.deepcopy(model)
                    with torch.no_grad():lesion.mask[indices]=0.
                    drows=repair(lesion,x,y,ids,args.steps,args.every,args.lr)
                    initial=100*(base["val_acc"]-drows[0]["val_acc"])
                    deficit=[c["val_acc"]-d["val_acc"] for c,d in zip(crows,drows)]
                    auc=sum((deficit[i]+deficit[i+1])/2*(drows[i+1]["step"]-drows[i]["step"]) for i in range(len(drows)-1))
                    rec=first_stable(drows,.99,2)
                    obj={"seed":seed,"lambda":lam,"group":"grok" if lam==1e-5 else "continuous",
                         "dose":dose,"mask":ms,"indices":indices,
                         "base":base,"injured_initial":drows[0],"control_final":crows[-1],"injured_final":drows[-1],
                         "initial_damage_val_pp":initial,
                         "initial_damage_test_pp":100*(base["test_acc"]-drows[0]["test_acc"]),
                         "recovery_two_consecutive_val99_step":rec,
                         "mean_auc_val_control_deficit":auc,
                         "auc_per_unit_initial_damage":auc/(initial/100) if initial>0 else None,
                         "meaningful_damage":initial>=2}
                    observations.append(obj)
                    with (folder/f"dose{dose:03d}_mask{ms}.csv").open("w",newline="",encoding="utf-8") as f:
                        writer=csv.DictWriter(f,fieldnames=list(drows[0]));writer.writeheader();writer.writerows(drows)
                    print("INJURY",seed,f"{lam:g}","dose",dose,"mask",ms,"drop_pp",round(initial,2),
                        "recover",rec,"auc",round(auc,3), "final",round(drows[-1]["val_acc"],3),flush=True)
            (ROOT/"V10_LESION_RAW.json").write_text(json.dumps({"scope":"exploratory","protocol":"PREREG_V10B.md","config":vars(args),"observations":observations},ensure_ascii=False,indent=2),encoding="utf-8")
    print("COMPLETE",len(observations),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--doses",type=int,nargs="+",default=[30,90,150])
    p.add_argument("--masks",type=int,nargs="+",default=[101,102,103,104,105])
    p.add_argument("--steps",type=int,default=400)
    p.add_argument("--every",type=int,default=10)
    p.add_argument("--lr",type=float,default=.001)
    run(p.parse_args())
