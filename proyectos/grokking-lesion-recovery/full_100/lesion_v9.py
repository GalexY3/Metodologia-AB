"""V9B destructive mask/recovery pilot for homogeneous modular-addition networks.
One optimizer and intact continuation per model. Masks nested within model.
"""
import argparse,copy,csv,json,time,hashlib,sys,statistics
from pathlib import Path
import numpy as np
import torch
from torch.nn import functional as F
from train_v9 import Net,build,measure
torch.set_num_threads(4)
ROOT=Path(__file__).resolve().parent
def recover(recs,base,threshold=.99,n=2):
    if base<=0:return None
    for i in range(0,len(recs)-n+1):
        if all(recs[k]["val_accuracy"]>=threshold*base for k in range(i,i+n)):
            return int(recs[i]["step"])
    return None
def train_continuation(model,x,y,train_ix,ix,maxsteps,measure_every,wd,lr):
    opt=torch.optim.AdamW(model.parameters(),lr=lr,weight_decay=wd)
    records=[measure(model,x,y,ix,0)]
    for step in range(1,maxsteps+1):
        model.train();opt.zero_grad(set_to_none=True)
        loss=F.cross_entropy(model(x[train_ix]),y[train_ix])
        loss.backward();opt.step()
        if step%measure_every==0 or step==maxsteps:
            records.append(measure(model,x,y,ix,step))
    return records
def main(a):
    torch.manual_seed(1707)
    root=ROOT/"lesion_runs"
    root.mkdir(exist_ok=True)
    summary=[]
    for seed in a.seeds:
        for wd in a.wds:
            name=f"wd{wd}_scale1.0_lr0.001_seed{seed}_split20261109"
            path=ROOT/"runs"/name/f"checkpoint_012000.pt"
            if not path.is_file():raise FileNotFoundError(path)
            ck=torch.load(path,map_location="cpu",weights_only=False)
            conf=ck["config"];x,y,ix=build(conf["p"],conf["fraction"],conf["split_seed"])
            m=Net(conf["p"],conf["dim"],conf["hidden"]);m.load_state_dict(ck["model"])
            before=measure(m,x,y,ix,0)
            if before["train_accuracy"]<.999 or before["val_accuracy"]<.999:
                print("INELIGIBLE",name,"train",before["train_accuracy"],"val",before["val_accuracy"],flush=True)
                continue
            control=train_continuation(copy.deepcopy(m),x,y,ix["train"],ix,a.steps,a.every,a.repair_wd,a.repair_lr)
            model_dir=root/name
            model_dir.mkdir(exist_ok=True)
            with (model_dir/"control.csv").open("w",newline="",encoding="utf-8") as f:
                wr=csv.DictWriter(f,fieldnames=list(control[0]));wr.writeheader();wr.writerows(control)
            for dose in a.doses:
                for mseed in a.masks:
                    rng=np.random.default_rng(mseed)
                    picks=sorted(rng.choice(conf["hidden"],dose,replace=False).tolist())
                    lesion=copy.deepcopy(m)
                    with torch.no_grad():lesion.mask[picks]=0.0
                    damaged=train_continuation(lesion,x,y,ix["train"],ix,a.steps,a.every,a.repair_wd,a.repair_lr)
                    damage_pp=100*(before["val_accuracy"]-damaged[0]["val_accuracy"])
                    deficit=[c["val_accuracy"]-d["val_accuracy"] for c,d in zip(control,damaged)]
                    area=sum((deficit[i-1]+deficit[i])/2*(damaged[i]["step"]-damaged[i-1]["step"]) for i in range(1,len(damaged)))
                    time_to=recover(damaged,before["val_accuracy"],a.threshold,2)
                    item={"seed":seed,"wd":wd,"dose":dose,"mask_seed":mseed,"neuron_indices":picks,
                       "before":before,"after_injury":damaged[0],"end_control":control[-1],"end_injured":damaged[-1],
                       "damage_val_pp":damage_pp,"recovery_step_two_consecutive":time_to,
                       "auc_val_control_minus_lesion":area,
                       "normalized_auc_by_initial_damage":area/(damage_pp/100) if damage_pp>0 else None,
                       "meaningful_initial_damage":damage_pp>=2,
                       "checkpoint":str(path),"training_steps_at_lesion":int(ck["step"])}
                    summary.append(item)
                    with (model_dir/f"dose{dose:03d}_mask{mseed}.csv").open("w",newline="",encoding="utf-8") as f:
                        wr=csv.DictWriter(f,fieldnames=list(damaged[0]));wr.writeheader();wr.writerows(damaged)
                    print("LESION",name,"dose",dose,"mask",mseed,"initial_loss_pp",round(damage_pp,2),"recover",time_to,"auc",round(area,2),"end",round(damaged[-1]["val_accuracy"],3),flush=True)
            (ROOT/"lesion_v9_summary.json").write_text(json.dumps({"status":"exploratory","config":vars(a),"observations":summary},indent=2,ensure_ascii=False),encoding="utf-8")
    print("FINISHED",len(summary),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--seeds",type=int,nargs="+",default=[0,1,2])
    p.add_argument("--wds",type=float,nargs="+",default=[1.,3.])
    p.add_argument("--doses",type=int,nargs="+",default=[30,60,90])
    p.add_argument("--masks",type=int,nargs="+",default=[101,102,103,104,105])
    p.add_argument("--steps",type=int,default=500)
    p.add_argument("--every",type=int,default=10)
    p.add_argument("--threshold",type=float,default=.99)
    p.add_argument("--repair-lr",type=float,default=.001)
    p.add_argument("--repair-wd",type=float,default=.1)
    main(p.parse_args())
