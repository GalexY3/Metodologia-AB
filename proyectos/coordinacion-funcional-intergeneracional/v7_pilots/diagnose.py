"""Read-only exploration of V7 checkpoints; development, not sealed holdout."""
import argparse,json,torch
from pathlib import Path
from dataclasses import replace
from experiment import ROOT, Settings, Society, make_model, evaluate, capture, atomic_json, COLORS
torch.set_num_threads(4)

@torch.no_grad()
def random_reference(cfg,seed,batch=96,steps=32,freeze=False):
    torch.manual_seed(seed)
    c=replace(cfg,batch=batch,horizon=steps)
    ks=torch.tensor([2,3,4]*(batch//3),device=c.device)
    ks=ks[torch.randperm(batch,device=c.device)]
    s=Society(c,ks)
    start=s.D.clone()
    churn=torch.zeros(batch,device=c.device)
    if not freeze:
        for t in range(steps):
            new=torch.randint(COLORS,s.colors.shape,device=c.device)
            churn=(new!=s.colors).float().mean(-1)
            s.colors=new
            s.D=s.calcD()
    rows=[]
    for k in (2,3,4):
        m=s.k==k
        rows.append(dict(k=k,initial_D=float(start[m].mean()),
          final_D=float(s.D[m].mean()),
          occupied=float((s.counts()[m]>0).sum(-1).float().mean()),
          exact=int(s.exact()[m].sum()),stable=0,
          churn=float(churn[m].mean()),worlds=int(m.sum())))
    return rows

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--batch",type=int,default=96)
    parser.add_argument("--seed",type=int,default=700301)
    args=parser.parse_args()
    dirs=sorted((ROOT/"runs").glob("pilot_*"))
    if not dirs:raise RuntimeError("No pilot checkpoints")
    report={}
    for path in dirs:
        cfgraw=json.loads((path/"config.json").read_text(encoding="utf-8"))
        runargs=cfgraw["args"]
        cfg=Settings(**cfgraw["cfg"])
        torch.manual_seed(cfg.seed)
        if cfg.device=="cuda":torch.cuda.manual_seed_all(cfg.seed)
        initial=make_model(cfg,runargs["arm"])
        ck=torch.load(path/"latest.pt",map_location=cfg.device,weights_only=False)
        trained=make_model(cfg,runargs["arm"])
        trained.load_state_dict(ck["model"])
        disable=not runargs["messages"]
        result={}
        for name,policy in (("initial",initial),("trained",trained)):
            result[name]=dict(
              stochastic=evaluate(policy,cfg,seed=args.seed,batch=args.batch,
                                 steps=32,greedy=False,disable_messages=disable),
              greedy=evaluate(policy,cfg,seed=args.seed,batch=args.batch,
                                 steps=32,greedy=True,disable_messages=disable))
        result["updates"]=ck["update"]
        result["name"]=path.name
        report[path.name]=result
        atomic_json(path/"diagnostics.json",result)
        atomic_json(path/"replay.json",capture(trained,cfg,k=4,seed=args.seed+10,
                                                steps=32,disable_messages=disable))
        print(path.name,
          "STOCH(k4):",round(result["initial"]["stochastic"][2]["final_D"],4),
                          round(result["trained"]["stochastic"][2]["final_D"],4),
          "GREEDY(k4):",round(result["trained"]["greedy"][2]["final_D"],4),
          "churn(stoch):",round(result["trained"]["stochastic"][2]["churn"],4),
          flush=True)
    baseline_cfg=Settings(side=6,batch=args.batch,horizon=32,device="cpu")
    refs=dict(continuous=random_reference(baseline_cfg,args.seed,args.batch),
              random_stay=random_reference(baseline_cfg,args.seed,args.batch,freeze=True))
    atomic_json(ROOT/"exploratory_diagnostics.json",dict(arms=report,
        baselines=refs,seed=args.seed,batch=args.batch,designation="development_only"))
    print("BASELINE",[(x["k"],round(x["final_D"],4)) for x in refs["continuous"]])
if __name__=="__main__":main()
