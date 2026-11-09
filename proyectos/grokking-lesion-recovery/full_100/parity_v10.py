"""V10 binary parity amid distracting features. L1 strength search; exploratory.
External inspiration: Google PAIR 2023 1s/0s grokking explorable, not exact reproduction.
"""
from __future__ import annotations
import argparse,json,csv,time,hashlib,platform
from pathlib import Path
import torch
from torch import nn
from torch.nn import functional as F
torch.set_num_threads(4)
ROOT=Path(__file__).resolve().parent

class MLP(nn.Module):
    def __init__(self, width=300):
        super().__init__()
        self.a=nn.Linear(30,width)
        self.b=nn.Linear(width,2)
        self.register_buffer("mask",torch.ones(width))
    def forward(self,x):
        z=torch.relu(self.a(x))
        return self.b(z*self.mask)

def data(seed=20261109,ntrain=1200,nval=1000,ntest=2000):
    g=torch.Generator().manual_seed(seed)
    n=ntrain+nval+ntest
    # independent Bernoulli draws; forbid overlap between partitions
    seen=set();xs=[]
    while len(xs)<n:
        r=torch.randint(0,2,(min(4096,n),30),generator=g,dtype=torch.uint8)
        for v in r:
            key=bytes(v.tolist())
            if key not in seen:
                seen.add(key);xs.append(v)
            if len(xs)>=n:break
    x=torch.stack(xs).float()
    y=((x[:,:3].sum(1).long())%2)
    return x,y,{"train":torch.arange(0,ntrain),"val":torch.arange(ntrain,ntrain+nval),"test":torch.arange(ntrain+nval,n)}

@torch.no_grad()
def measure(net,x,y,ids,step):
    net.eval()
    pred=net(x)
    o={"step":step}
    for k,ix in ids.items():
        z=pred[ix]
        o[k+"_acc"]=float((z.argmax(1)==y[ix]).float().mean())
        o[k+"_loss"]=float(F.cross_entropy(z,y[ix]))
    o["l1_parameters"]=float(sum(v.detach().abs().sum() for v in net.parameters()))
    o["parameter_l2"]=float(torch.sqrt(sum(v.detach().square().sum() for v in net.parameters())))
    return o

def run(a):
    x,y,idx=data(a.split_seed,a.ntrain,a.nval,a.ntest)
    torch.manual_seed(a.seed)
    m=MLP(a.width)
    opt=torch.optim.AdamW(m.parameters(),lr=a.lr,weight_decay=0.)
    name=f"lambda{a.l1:g}_seed{a.seed}_lr{a.lr}_width{a.width}_nt{a.ntrain}"
    out=ROOT/"parity_runs"/name
    if out.exists():raise FileExistsError(out)
    out.mkdir(parents=True)
    cfg=vars(a).copy();cfg.update({"torch":torch.__version__,"python":platform.python_version(),
        "x_sha256":hashlib.sha256(x.numpy().tobytes()).hexdigest(),
        "train_y_sha256":hashlib.sha256(y[idx["train"]].numpy().tobytes()).hexdigest(),
        "sample_counts":{k:len(ix) for k,ix in idx.items()}})
    (out/"config.json").write_text(json.dumps(cfg,indent=2),encoding="utf-8")
    def checkpoint(step):
        torch.save({"model":m.state_dict(),"optimizer":opt.state_dict(),"config":cfg,"step":step},out/f"ck_{step:06d}.pt")
    rows=[measure(m,x,y,idx,0)];checkpoint(0)
    stable=0;start=time.perf_counter()
    for step in range(1,a.steps+1):
        m.train();opt.zero_grad(set_to_none=True)
        pred=m(x[idx["train"]])
        ce=F.cross_entropy(pred,y[idx["train"]])
        penalty=sum(v.abs().sum() for v in m.parameters())
        loss=ce+a.l1*penalty
        loss.backward();opt.step()
        if step%a.record_every==0 or step==a.steps:
            r=measure(m,x,y,idx,step);rows.append(r)
            stable=stable+1 if r["train_acc"]>=.999 and r["val_acc"]==1 else 0
            if step%a.checkpoint_every==0 or step==a.steps or stable in (5,10):
                checkpoint(step)
            if step%500==0 or step==a.steps:
                print("AT",name,step,"train",round(r["train_acc"],4),"val",round(r["val_acc"],4),"valloss",round(r["val_loss"],4),flush=True)
    with (out/"metrics.csv").open("w",newline="",encoding="utf-8") as f:
        wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
    report={"name":name,"elapsed_s":round(time.perf_counter()-start,2),"final":rows[-1]}
    (out/"result.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print("RESULT",json.dumps(report,ensure_ascii=False),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--split-seed",type=int,default=20261109)
    p.add_argument("--ntrain",type=int,default=1200)
    p.add_argument("--nval",type=int,default=1000)
    p.add_argument("--ntest",type=int,default=2000)
    p.add_argument("--seed",type=int,default=0)
    p.add_argument("--width",type=int,default=300)
    p.add_argument("--l1",type=float,default=.00001)
    p.add_argument("--lr",type=float,default=.001)
    p.add_argument("--steps",type=int,default=6000)
    p.add_argument("--record-every",type=int,default=100)
    p.add_argument("--checkpoint-every",type=int,default=1000)
    run(p.parse_args())
