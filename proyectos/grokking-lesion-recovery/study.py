"""Prospective exploratory MLP training and neuronal lesion pilot. 2026-11-09."""
from __future__ import annotations
import argparse,csv,hashlib,json,random,copy,time,platform
from pathlib import Path
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

HERE=Path(__file__).resolve().parent
torch.set_num_threads(4)

class Net(nn.Module):
    def __init__(self,p=31,dim=32,hid=300):
        super().__init__()
        self.p=p
        self.emb=nn.Embedding(p,dim)
        self.hidden=nn.Linear(2*dim,hid)
        self.out=nn.Linear(hid,p)
        self.register_buffer("mask",torch.ones(hid))
    def forward(self,x):
        z=self.emb(x).reshape(-1,self.emb.embedding_dim*2)
        z=F.relu(self.hidden(z))*self.mask
        return self.out(z)

def data(p,frac,split_seed):
    a,b=torch.meshgrid(torch.arange(p),torch.arange(p),indexing="ij")
    x=torch.stack([a.reshape(-1),b.reshape(-1)],dim=1)
    y=(x[:,0]+x[:,1])%p
    rng=torch.Generator().manual_seed(split_seed)
    idx=torch.randperm(p*p,generator=rng)
    n=int(p*p*frac)
    return x,y,idx[:n],idx[n:]

@torch.no_grad()
def measure(model,x,y,tr,te,step):
    model.eval()
    pred=model(x)
    res={"step":step}
    for key,ids in (("train",tr),("test",te)):
        res[key+"_acc"]=float((pred[ids].argmax(-1)==y[ids]).float().mean())
        res[key+"_loss"]=float(F.cross_entropy(pred[ids],y[ids]))
    res["weight_l2"]=float(torch.linalg.vector_norm(torch.cat([v.reshape(-1) for v in model.parameters()])))
    return res

def savecsv(path,records):
    with path.open("w",newline="",encoding="utf-8") as f:
        wr=csv.DictWriter(f,fieldnames=list(records[0]));wr.writeheader();wr.writerows(records)

def run_train(args):
    torch.manual_seed(args.seed)
    random.seed(args.seed)
    x,y,tr,te=data(args.p,args.fraction,args.split_seed)
    model=Net(args.p,args.dim,args.hidden)
    if args.init_scale!=1.0:
        with torch.no_grad():
            for name,v in model.named_parameters():
                v.mul_(args.init_scale)
    opt=torch.optim.AdamW(model.parameters(),lr=args.lr,weight_decay=args.wd)
    out=HERE/"runs"/f"mlp_p{args.p}_h{args.hidden}_frac{args.fraction}_wd{args.wd}_scale{args.init_scale}_s{args.seed}"
    out.mkdir(parents=True,exist_ok=True)
    cfg={k:v for k,v in vars(args).items() if k not in ("mode","checkpoint")}
    cfg.update({"torch":torch.__version__,"python":platform.python_version(),"cuda":torch.cuda.is_available(),"device":"cpu","train_indices_sha256":hashlib.sha256(tr.numpy().tobytes()).hexdigest()})
    (out/"config.json").write_text(json.dumps(cfg,indent=2),encoding="utf-8")
    rows=[measure(model,x,y,tr,te,0)]
    start=time.perf_counter()
    def snapshot(step):
        torch.save({"model":model.state_dict(),"optimizer":opt.state_dict(),"config":cfg,"step":step},out/f"checkpoint_{step:06d}.pt")
    snapshot(0)
    for step in range(1,args.steps+1):
        model.train()
        opt.zero_grad(set_to_none=True)
        loss=F.cross_entropy(model(x[tr]),y[tr])
        loss.backward()
        opt.step()
        if step % args.record_every==0 or step==args.steps:
            row=measure(model,x,y,tr,te,step)
            rows.append(row)
            if step % args.checkpoint_every==0 or step==args.steps or 0.53<=row["test_acc"]<=0.67:
                snapshot(step)
            if step % max(args.record_every,500)==0:
                print(f"TRAIN wd={args.wd} scale={args.init_scale} seed={args.seed} step={step} train={row['train_acc']:.3f} test={row['test_acc']:.3f}",flush=True)
    savecsv(out/"metrics.csv",rows)
    result={"out":str(out),"duration_s":round(time.perf_counter()-start,2),"final":rows[-1]}
    (out/"summary.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    print("RESULT",json.dumps(result),flush=True)

def run_lesion(args):
    blob=torch.load(args.checkpoint,map_location="cpu",weights_only=False)
    c=blob["config"]
    x,y,tr,te=data(c["p"],c["fraction"],c["split_seed"])
    model=Net(c["p"],c["dim"],c["hidden"])
    model.load_state_dict(blob["model"])
    base=measure(model,x,y,tr,te,0)
    rng=np.random.default_rng(args.mask_seed)
    picks=sorted(rng.choice(c["hidden"],size=round(c["hidden"]*args.frac_lesion),replace=False).tolist())
    if len(picks)!=30 or c["hidden"]!=300: raise ValueError("Pilot specifically assumes 30/300")
    output=[]
    for arm in ("control","ablate","reset"):
        m=copy.deepcopy(model)
        opt=torch.optim.AdamW(m.parameters(),lr=c["lr"],weight_decay=c["wd"])
        opt.load_state_dict(copy.deepcopy(blob["optimizer"]))
        if arm=="ablate":
            with torch.no_grad():m.mask[picks]=0
        if arm=="reset":
            with torch.no_grad():
                old_hid=m.hidden.weight.detach().clone()
                old_bias=m.hidden.bias.detach().clone()
                old_out=m.out.weight.detach().clone()
                # Reinitialize only 30 incoming and outgoing neuronal connections
                g=torch.Generator().manual_seed(args.mask_seed+999)
                m.hidden.weight[picks]=torch.randn((30,old_hid.shape[1]),generator=g)*float(old_hid.std())
                m.hidden.bias[picks]=torch.randn(30,generator=g)*float(old_bias.std())
                m.out.weight[:,picks]=torch.randn((old_out.shape[0],30),generator=g)*float(old_out.std())
                # Remove stale Adam moments for reset connections
                for param,axis in ((m.hidden.weight,0),(m.hidden.bias,0),(m.out.weight,1)):
                    state=opt.state.get(param,{})
                    for key in ("exp_avg","exp_avg_sq","max_exp_avg_sq"):
                        if key in state:
                            if axis==0: state[key][picks]=0
                            else: state[key][:,picks]=0
        init=measure(m,x,y,tr,te,0)
        records=[{"arm":arm,**init}]
        for step in range(1,args.repair_steps+1):
            m.train();opt.zero_grad(set_to_none=True)
            loss=F.cross_entropy(m(x[tr]),y[tr]);loss.backward();opt.step()
            if step%args.measure_every==0 or step==args.repair_steps:
                records.append({"arm":arm,**measure(m,x,y,tr,te,step)})
        output.extend(records)
    by_arm={k:[r for r in output if r["arm"]==k] for k in ("control","ablate","reset")}
    threshold=.95*base["test_acc"]
    summary={"checkpoint":str(Path(args.checkpoint).resolve()),"checkpoint_step":blob["step"],"base":base,
      "mask_seed":args.mask_seed,"indices":picks,"repair_steps":args.repair_steps,
      "threshold":threshold,"arms":{}}
    for arm,rows in by_arm.items():
        onset=next((r["step"] for r in rows if r["test_acc"]>=threshold),None)
        summary["arms"][arm]={"initial":rows[0],"final":rows[-1],"recovery_step":onset,
         "initial_damage_test_pp":100*(base["test_acc"]-rows[0]["test_acc"])}
    out=HERE/"lesions"/(Path(args.checkpoint).parent.name+"_"+Path(args.checkpoint).stem+f"_m{args.mask_seed}")
    out.mkdir(parents=True,exist_ok=True)
    savecsv(out/"trajectories.csv",output)
    (out/"results.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print("LESION",json.dumps(summary),flush=True)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("mode",choices=["train","lesion"])
    p.add_argument("--p",type=int,default=31)
    p.add_argument("--fraction",type=float,default=.55)
    p.add_argument("--split-seed",type=int,default=20261109)
    p.add_argument("--dim",type=int,default=32)
    p.add_argument("--hidden",type=int,default=300)
    p.add_argument("--seed",type=int,default=0)
    p.add_argument("--wd",type=float,default=.1)
    p.add_argument("--lr",type=float,default=.001)
    p.add_argument("--init-scale",type=float,default=1.)
    p.add_argument("--steps",type=int,default=3500)
    p.add_argument("--record-every",type=int,default=100)
    p.add_argument("--checkpoint-every",type=int,default=500)
    p.add_argument("--checkpoint",type=str)
    p.add_argument("--mask-seed",type=int,default=11)
    p.add_argument("--frac-lesion",type=float,default=.1)
    p.add_argument("--repair-steps",type=int,default=150)
    p.add_argument("--measure-every",type=int,default=10)
    a=p.parse_args()
    if a.mode=="train":run_train(a)
    else:
        if not a.checkpoint:p.error("lesion requires --checkpoint")
        run_lesion(a)
if __name__=="__main__":main()
