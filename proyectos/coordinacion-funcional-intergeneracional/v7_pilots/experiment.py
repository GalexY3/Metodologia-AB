"""V7: individual, color-equivariant actors; controlled memory and algorithm pilots.

Global reward only. Training and development seeds are disjoint; holdout is
not inspected here. Per-individual parameter blocks, no centralized critic.
"""
from __future__ import annotations
import argparse, json, math, os, sys, time
from dataclasses import asdict, replace
from pathlib import Path
import torch
from torch import nn
from torch.nn import functional as F
from torch.distributions import Categorical

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "v6_million"))
from engine import Settings, Society, IndependentPolicy, COLORS, NC

def atomic_json(path, obj):
    path = Path(path)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, path)

def features(e, req=None, snap=None):
    b, n = e.colors.shape
    if req is None: req = torch.zeros(b,n,COLORS,device=e.colors.device)
    if snap is None: snap = torch.zeros_like(req)
    own = F.one_hot(e.colors,COLORS).float()
    prev = F.one_hot(e.prev_colors,COLORS).float()
    sent = F.one_hot(e.prev_sent.clamp_min(0),COLORS).float() * (e.prev_sent>=0).unsqueeze(-1)
    every = lambda x: x[:,None,None].expand(b,n,COLORS)
    return torch.stack((
        own,prev,e.local,e.ema,e.local-e.ema,req,snap,
        sent,e.prev_recv,every(e.D),every(e.prev_delta),
        every(e.k.float()/COLORS),every(e.prev_churn),
        torch.full_like(e.local,e.turn/max(1,e.cfg.horizon))
    ),-1)

class GatedColorGRU(nn.Module):
    """A recurrent H-vector per agent and per exchangeable color."""
    def __init__(self, n, hidden=12, recurrent=True):
        super().__init__()
        self.n, self.hidden, self.recurrent = n, hidden, recurrent
        self.in_w = nn.Parameter(torch.empty(n,14,3*hidden))
        self.rec_w = nn.Parameter(torch.empty(n,hidden,3*hidden))
        self.bias = nn.Parameter(torch.zeros(n,3*hidden))
        self.out = nn.Parameter(torch.empty(n,hidden))
        self.gate_cur = nn.Parameter(torch.empty(n,hidden))
        self.gate_mean = nn.Parameter(torch.empty(n,hidden))
        self.gate_bias = nn.Parameter(torch.full((n,),-1.))
        self.target_w = nn.Parameter(torch.zeros(n,4))
        self.silent = nn.Parameter(torch.zeros(n))
        for i in range(n):
            nn.init.xavier_uniform_(self.in_w[i])
            nn.init.orthogonal_(self.rec_w[i])
        for p in (self.out, self.gate_cur, self.gate_mean):
            nn.init.normal_(p, std=.04)
        self.hstate = None
    def reset(self, b, device):
        self.hstate = torch.zeros(b,self.n,COLORS,self.hidden,device=device)
    def step(self, x, h):
        y = torch.einsum("bncf,nfh->bnch",x,self.in_w) + self.bias[None,:,None,:]
        z = torch.einsum("bnch,nhq->bncq",h,self.rec_w)
        xr,xu,xn = y.chunk(3,dim=-1)
        hr,hu,hn = z.chunk(3,dim=-1)
        r = (xr+hr).sigmoid()
        u = (xu+hu).sigmoid()
        candidate = (xn+r*hn).tanh()
        return u*h+(1-u)*candidate
    def color_logits(self,h):
        return torch.einsum("bnch,nh->bnc",h,self.out)
    def slot_logits(self,e):
        nb = e.colors[:,e.graph]
        same=(nb==e.colors[:,:,None]).float()
        local=e.local.gather(-1,nb)
        ema=e.ema.gather(-1,nb)
        repeat=(e.prev_target[:,:,None]==torch.arange(NC,device=nb.device)).float()
        x=torch.stack((same,local,ema,repeat),-1)
        scores=(x*self.target_w[None,:,None,:]).sum(-1)
        return torch.cat((scores,self.silent[None,:,None].expand(e.cfg.batch,self.n,1)),-1)
    def decisions(self,e,greedy=False,disable_messages=False):
        if self.hstate is None or self.hstate.shape[0]!=e.cfg.batch:
            self.reset(e.cfg.batch,e.colors.device)
        base=torch.zeros_like(self.hstate) if not self.recurrent else self.hstate
        before=self.step(features(e),base)
        d_target=Categorical(logits=self.slot_logits(e))
        if disable_messages:
            slot=torch.full_like(e.colors,NC)
            logt=torch.zeros_like(e.colors,dtype=torch.float32)
            entt=torch.zeros_like(logt)
        else:
            slot=d_target.logits.argmax(-1) if greedy else d_target.sample()
            logt=d_target.log_prob(slot)
            entt=d_target.entropy()
        d_request=Categorical(logits=self.color_logits(before))
        request=d_request.logits.argmax(-1) if greedy else d_request.sample()
        rec,snap,active,targets,count=e.send_messages(slot,request)
        nxt=self.step(features(e,rec,snap),base)
        self.hstate=nxt if self.recurrent else torch.zeros_like(nxt)
        color=Categorical(logits=self.color_logits(nxt))
        proposed=color.logits.argmax(-1) if greedy else color.sample()
        current_h=nxt.gather(2,e.colors[:,:,None,None].expand(-1,-1,1,self.hidden)).squeeze(2)
        change_score=(current_h*self.gate_cur[None]).sum(-1)
        change_score+=(nxt.mean(2)*self.gate_mean[None]).sum(-1)
        change_score+=self.gate_bias[None]
        gate=Categorical(logits=torch.stack((torch.zeros_like(change_score),change_score),-1))
        change=gate.logits.argmax(-1) if greedy else gate.sample()
        choice=torch.where(change.bool(),proposed,e.colors)
        logp=logt + active.float()*d_request.log_prob(request)
        logp=logp+gate.log_prob(change)+change.float()*color.log_prob(proposed)
        entropy=entt+active.float()*d_request.entropy()
        entropy=entropy+gate.entropy()+change.float()*color.entropy()
        return dict(choice=choice,slot=slot,request=request,rec=rec,
                    logp=logp,entropy=entropy,active=active,targets=targets)

def rollout(model,cfg,seed,greedy=False,disable_messages=False,with_grad=True):
    torch.manual_seed(seed)
    if cfg.device=="cuda": torch.cuda.manual_seed_all(seed)
    ks=torch.tensor([2,3,4]*(cfg.batch//3),device=cfg.device)
    ks=ks[torch.randperm(cfg.batch,device=cfg.device)]
    world=Society(cfg,ks)
    if hasattr(model,"reset"): model.reset(cfg.batch,cfg.device)
    init=world.D.detach().clone()
    lps=[]; ents=[]; rewards=[]; churn=[]; hist=[]
    for t in range(cfg.horizon):
        act=model.decisions(world,greedy=greedy,disable_messages=disable_messages)
        delta,turnover=world.advance(act["choice"],act["slot"],act["request"],act["rec"])
        if with_grad:
            lps.append(act["logp"])
            ents.append(act["entropy"])
        rewards.append((world.n*delta+cfg.proximity*(1-world.D)+
                        (cfg.terminal*(1-world.D) if t==cfg.horizon-1 else 0)).detach())
        churn.append(turnover.detach())
        hist.append(world.D.detach().clone())
    return dict(world=world,ks=ks,initial=init,logps=lps,entropies=ents,
                rewards=torch.stack(rewards),churn=torch.stack(churn),
                trajectory=torch.stack(hist))

@torch.no_grad()
def evaluate(model,cfg,seed=700101,batch=12,steps=32,greedy=True,disable_messages=False):
    was=model.training
    model.eval()
    c=replace(cfg,batch=batch,horizon=steps)
    r=rollout(model,c,seed,greedy,disable_messages,with_grad=False)
    rows=[]
    for k in (2,3,4):
        mask=r["ks"]==k
        d=r["trajectory"][:,mask]
        ch=r["churn"][:,mask]
        w=r["world"]
        stable=((d[-10:]<=.02)&(ch[-10:]<=.05)).all(0)
        rows.append(dict(k=k,initial_D=float(r["initial"][mask].mean()),
            final_D=float(d[-1].mean()),mean_D=float(d.mean()),
            occupied=float((w.counts()[mask]>0).sum(-1).float().mean()),
            exact=int(w.exact()[mask].sum()),stable=int(stable.sum()),
            churn=float(ch[-10:].mean()),worlds=int(mask.sum()),
            curve=d.mean(-1).cpu().tolist()))
    model.train(was)
    return rows

@torch.no_grad()
def capture(model,cfg,k=4,seed=700202,steps=32,disable_messages=False):
    """A visible development example, never the sealed test."""
    c=replace(cfg,batch=1,horizon=steps)
    torch.manual_seed(seed+k*101)
    if c.device=="cuda": torch.cuda.manual_seed_all(seed+k*101)
    w=Society(c,torch.tensor([k],device=c.device))
    if hasattr(model,"reset"):model.reset(1,c.device)
    was=model.training
    model.eval()
    def frame(t,ch,messages):
        return dict(t=t,colors=w.colors[0].tolist(),D=float(w.D[0]),
                    occupied=int((w.counts()[0]>0).sum()),
                    churn=float(ch),messages=messages)
    frames=[frame(0,0,[])]
    for t in range(steps):
        a=model.decisions(w,greedy=True,disable_messages=disable_messages)
        active=a["active"][0]
        src=torch.arange(w.n,device=c.device)[active]
        target=a["targets"][0,active]
        req=a["request"][0,active]
        messages=[dict(src=int(x),dst=int(y),color=int(z)) for x,y,z in
                  zip(src.tolist(),target.tolist(),req.tolist())]
        _,ch=w.advance(a["choice"],a["slot"],a["request"],a["rec"])
        frames.append(frame(t+1,ch[0],messages))
    model.train(was)
    return dict(kind="development_replay",k=k,side=c.side,frames=frames)

def legacy_model(cfg):
    return IndependentPolicy(cfg.side**2,cfg.hidden).to(cfg.device)

def make_model(cfg, arm):
    if arm=="legacy": return legacy_model(cfg)
    return GatedColorGRU(cfg.side**2,cfg.hidden,recurrent=arm!="gated").to(cfg.device)

def train_reinforce(model,opt,cfg,seed,disable_messages=False):
    r=rollout(model,cfg,seed,disable_messages=disable_messages)
    running=torch.zeros(cfg.batch,device=cfg.device)
    ret=[]
    for reward in r["rewards"].flip(0):
        running=reward+cfg.gamma*running
        ret.append(running)
    ret=torch.stack(ret[::-1])
    advantage=torch.empty_like(ret)
    for k in (2,3,4):
        mask=r["ks"]==k
        sample=ret[:,mask]
        baseline=(sample.sum(-1,keepdim=True)-sample)/(sample.shape[1]-1)
        scale=sample.std(-1,keepdim=True,unbiased=False).clamp_min(.25)
        advantage[:,mask]=(sample-baseline)/scale
    lp=torch.stack(r["logps"])
    ent=torch.stack(r["entropies"])
    loss=-(lp.sum(-1)*advantage.detach()).mean()-cfg.entropy*ent.sum(-1).mean()
    opt.zero_grad(set_to_none=True)
    loss.backward()
    # Clip each independent individual's gradients, never normalize across individuals.
    sq=torch.zeros(model.n,device=cfg.device)
    for p in model.parameters():
        if p.grad is not None:
            assert p.shape[0]==model.n
            sq+=p.grad.detach().reshape(model.n,-1).square().sum(-1)
    norm=sq.sqrt()
    factor=(cfg.clip/(norm+1e-12)).clamp_max(1)
    for p in model.parameters():
        if p.grad is not None:
            p.grad*=factor.reshape(model.n,*([1]*(p.grad.ndim-1)))
    opt.step()
    return dict(loss=float(loss.detach()),grad_max=float(norm.max()),
        D_train=float(r["world"].D.mean()),churn=float(r["churn"][-5:].mean()),
        entropy=float(ent.detach().mean()))

@torch.no_grad()
def team_fitness(model,cfg,seed,disable_messages):
    r=rollout(model,cfg,seed,disable_messages=disable_messages,with_grad=False)
    d=r["world"].D
    # Same discounted collective return optimized by REINFORCE; no individual attribution.
    discounts=cfg.gamma**torch.arange(cfg.horizon,device=cfg.device)
    return float((r["rewards"]*discounts[:,None]).sum(0).mean())

@torch.no_grad()
def train_es(model,cfg,seed,sigma=.035,directions=6,es_lr=.008,disable_messages=False):
    assert directions>=2
    params=list(model.parameters())
    originals=[p.detach().clone() for p in params]
    estimate=[torch.zeros_like(p) for p in params]
    vals=[]
    # Common random numbers for antithetic +/- fitness evaluations.
    for q in range(directions):
        torch.manual_seed(seed+q*997)
        noise=[torch.randn_like(p) for p in params]
        pair=[]
        for sign in (1,-1):
            for p,base,eps in zip(params,originals,noise):
                p.copy_(base + sign*sigma*eps)
            fitness=team_fitness(model,cfg,seed+900000+q,disable_messages)
            pair.append(fitness)
        vals.append(pair)
        diff=pair[0]-pair[1]
        for g,eps in zip(estimate,noise):
            g.add_(eps,alpha=diff/(2*sigma*directions))
    for p,base,g in zip(params,originals,estimate):
        p.copy_(base+es_lr*g.clamp(-10,10))
    return dict(es_positive=sum(v[0] for v in vals)/directions,
                es_negative=sum(v[1] for v in vals)/directions,
                grad_proxy=float(torch.stack([g.square().mean() for g in estimate]).mean().sqrt()))

def run(args):
    if args.batch%3 or args.batch<9: raise ValueError("batch must be 9+ and divisible by 3")
    if args.eval_batch%3 or args.eval_batch<3: raise ValueError("development batch must be divisible by 3")
    if args.updates<=0: raise ValueError("updates must be positive")
    if args.side%6: raise ValueError("side must be divisible by 6 to support k=2/3/4 exact")
    if args.arm=="es" and args.hidden>32: raise ValueError("ES is a pilot; hidden<=32")
    torch.set_num_threads(min(4,os.cpu_count() or 2))
    if torch.cuda.is_available(): torch.set_float32_matmul_precision("high")
    device=args.device if args.device!="auto" else ("cuda" if torch.cuda.is_available() else "cpu")
    cfg=Settings(side=args.side,batch=args.batch,horizon=args.horizon,hidden=args.hidden,
        seed=args.seed,device=device,lr=args.lr)
    runpath=ROOT/"runs"/args.name
    runpath.mkdir(parents=True,exist_ok=True)
    setting=dict(args=vars(args),cfg=asdict(cfg),version="v7_pilot_1")
    conf=runpath/"config.json"
    if conf.exists() and json.loads(conf.read_text(encoding="utf-8"))!=setting:
        raise RuntimeError("Existing run has different config")
    atomic_json(conf,setting)
    torch.manual_seed(args.seed)
    if cfg.device=="cuda": torch.cuda.manual_seed_all(args.seed)
    model=make_model(cfg,args.arm)
    opt=torch.optim.AdamW(model.parameters(),lr=cfg.lr,weight_decay=.0003) if args.arm!="es" else None
    ck=runpath/"latest.pt"
    done=0
    if ck.exists():
        state=torch.load(ck,map_location=cfg.device,weights_only=False)
        model.load_state_dict(state["model"])
        if opt: opt.load_state_dict(state["optimizer"])
        done=state["update"]
    def save(upd):
        temp=Path(str(ck)+".tmp")
        torch.save(dict(update=upd,model=model.state_dict(),
            optimizer=opt.state_dict() if opt else None,config=setting),temp)
        os.replace(temp,ck)
    control=runpath/"control.json"
    if not control.exists():atomic_json(control,dict(pause=False,stop=False))
    history=runpath/"history.jsonl"
    t0=time.time()
    def update_status(state,upd,extra=None):
        atomic_json(runpath/"status.json",dict(state=state,update=upd,
             episodes=upd*cfg.batch,wall_seconds=time.time()-t0,
             arm=args.arm,device=cfg.device,report=extra))
    update_status("training",done)
    try:
        for u in range(done+1,args.updates+1):
            while True:
                ctl=json.loads(control.read_text(encoding="utf-8"))
                if ctl.get("stop"):
                    save(u-1);update_status("stopped",u-1);return
                if not ctl.get("pause"):break
                update_status("paused",u-1);time.sleep(1)
            seed=args.seed+104729*u
            if args.arm=="es":
                row=train_es(model,cfg,seed,args.sigma,args.directions,args.es_lr,
                    disable_messages=not args.messages)
            else:
                row=train_reinforce(model,opt,cfg,seed,disable_messages=not args.messages)
            if u==1 or u%args.eval_every==0 or u==args.updates:
                # Fixed development seeds, never treated as final heldout.
                row["development"]=evaluate(model,cfg,seed=700101,batch=args.eval_batch,steps=args.eval_steps,
                    disable_messages=not args.messages)
                atomic_json(runpath/"replay.json",capture(model,cfg,k=4,steps=args.eval_steps,
                    disable_messages=not args.messages))
                row.update(update=u,episodes=u*cfg.batch,arm=args.arm,
                           eval_mode="greedy",messages=args.messages)
                with history.open("a",encoding="utf-8") as f:
                    f.write(json.dumps(row,ensure_ascii=False)+"\n")
                update_status("training",u,row)
                print("V7",args.name,"UPDATE",u,"DEV",
                    [(x["k"],round(x["final_D"],4),x["occupied"]) for x in row["development"]],flush=True)
            if u%args.checkpoint_every==0 or u==args.updates:save(u)
        update_status("completed",args.updates)
    except BaseException as exc:
        save(max(done,u-1))
        update_status("failed",max(done,u-1),str(exc))
        raise

def parse():
    p=argparse.ArgumentParser()
    p.add_argument("--name",required=True)
    p.add_argument("--arm",choices=["legacy","gated","gru","es"],default="gru")
    p.add_argument("--messages",action="store_true")
    p.add_argument("--side",type=int,default=6)
    p.add_argument("--batch",type=int,default=12)
    p.add_argument("--hidden",type=int,default=12)
    p.add_argument("--horizon",type=int,default=12)
    p.add_argument("--updates",type=int,default=40)
    p.add_argument("--seed",type=int,default=6123)
    p.add_argument("--device",choices=["auto","cuda","cpu"],default="auto")
    p.add_argument("--lr",type=float,default=.0007)
    p.add_argument("--eval-every",type=int,default=10)
    p.add_argument("--eval-batch",type=int,default=96)
    p.add_argument("--eval-steps",type=int,default=32)
    p.add_argument("--checkpoint-every",type=int,default=10)
    p.add_argument("--directions",type=int,default=4)
    p.add_argument("--sigma",type=float,default=.035)
    p.add_argument("--es-lr",type=float,default=.008)
    return p.parse_args()

if __name__=="__main__":
    run(parse())
