"""Exploratory V10 optimized micro-learner (no oracle).

Changes RELATIVE to micro_agent.py are explicit treatments:
1. Include own state in frequency estimate (Argon-style).
2. Less restrictive per-individual return-variance normalization (floor .2 vs .5).
3. Optional mixing alpha=0.1 of realized mean food into personal learning reward.
No communication learning or access to counterfactual rewards. Compare against original
micro_agent.py; these changes must not be misattributed to network capacity.
"""
import sys,os,json,torch
from pathlib import Path
import village,micro_agent
def main():
    argv=sys.argv[1:]
    ix=argv.index("--alpha") if "--alpha" in argv else -1
    alpha=float(argv[ix+1]) if ix>=0 else 0.
    if ix>=0:del argv[ix:ix+2]
    if not 0<=alpha<=1:raise ValueError("alpha out of bounds")
    deg=int(argv[argv.index("--degree")+1]) if "--degree" in argv else 5
    name=argv[argv.index("--name")+1]
    root=Path(village.ROOT)/"runs"/name;root.mkdir(parents=True,exist_ok=True)
    scheme={"self_in_local_histogram":True,"advantage_std_min":.2,
       "optimizer":"Adam inherited from k_comparison village",
       "alpha":alpha,"normalization":"individual leave-one-world-out",
       "communication":"disabled","actor_global_access":"public observation only"}
    f=root/"OPTIMIZATION.json"
    if f.exists() and json.loads(f.read_text(encoding="utf8"))!=scheme:raise ValueError("scheme mismatch")
    f.write_text(json.dumps(scheme,indent=2),encoding="utf8")
    class MicroSelf(micro_agent.MicroAgent):
        def choose(self,obs,colors,communication,greedy=False):
            obs=obs.clone()
            obs[...,10:20]=(obs[...,10:20]*deg+obs[...,:10])/(deg+1)
            return super().choose(obs,colors,communication,greedy)
    micro_agent.MicroAgent=MicroSelf
    base_rollout=village.rollout
    def rollout(*args,**kwargs):
        r=base_rollout(*args,**kwargs)
        if alpha>0 and kwargs.get("with_grad",True) and r["logprobs"]:
            f=r["rewards"]
            r["rewards"]=(1-alpha)*f+alpha*f.mean(2,keepdim=True)
        return r
    village.rollout=rollout
    def update(model,opt,cfg,seed):
        r=village.rollout(model,cfg,seed)
        running=torch.zeros(cfg.batch,cfg.n,device=cfg.device)
        returns=[]
        for reward in reversed(r["rewards"]):
            running=reward+cfg.gamma*running;returns.append(running)
        returns=torch.stack(returns[::-1])
        baseline=(returns.sum(dim=1,keepdim=True)-returns)/(cfg.batch-1)
        scale=returns.std(dim=1,keepdim=True,unbiased=False).clamp_min(.2)
        advantage=((returns-baseline)/scale).detach()
        lp=torch.stack(r["logprobs"])
        ent=torch.stack(r["entropies"])
        loss=-(lp*advantage).mean()-cfg.entropy*ent.mean()
        opt.zero_grad(set_to_none=True);loss.backward()
        with torch.no_grad():
            norm=torch.zeros(cfg.n,device=cfg.device)
            for p in model.parameters():
                if p.grad is not None:norm+=p.grad.reshape(cfg.n,-1).square().sum(1)
            norm=norm.sqrt()
            for p in model.parameters():
                if p.grad is not None:
                    p.grad.mul_((1/(norm+1e-8)).clamp(max=1).reshape(cfg.n,*([1]*(p.ndim-1))))
        opt.step()
        return dict(loss=float(loss.detach()),train_food=r["final"]["food_mean"],
         train_Dk=r["final"]["Dk"],grad=float(norm.mean()),entropy=float(ent.mean().detach()))
    village.update=update
    sys.argv=[sys.argv[0]]+argv
    micro_agent.main()
if __name__=="__main__":main()
