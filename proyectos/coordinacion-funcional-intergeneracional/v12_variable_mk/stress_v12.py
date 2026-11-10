"""Cross-M/k stress tests of frozen trained agents, no new learning."""
from pathlib import Path
import json, torch
from dataclasses import replace
from v12 import ROOT,Config,IndividualAgent,evaluate,write_json
torch.set_num_threads(3)
runs=["v12_ext_n60_c0_s3111","v12_ext_n120_c0pub_s3111"]
rows=[]
for name in runs:
    folder=ROOT/"runs"/name
    cfg=Config(**{**json.loads((folder/"config.json").read_text(encoding="utf8"))["config"],"device":"cpu"})
    actor=IndividualAgent(cfg.n)
    ck=torch.load(folder/"latest.pt",map_location="cpu",weights_only=False)
    actor.load_state_dict(ck["model"])
    actor.eval()
    for M,k in [(30,2),(30,3),(30,5),(50,6),(50,10),(80,8),(80,12),(80,15)]:
        if cfg.n%k:continue
        ec=replace(cfg,m=M,k=k,init="random")
        for mode in ("learned","random","imitate"):
            result=[]
            for seed in (991001,991019):
                kw={"baseline":mode} if mode!="learned" else {}
                e=evaluate(actor if mode=="learned" else None,ec,seed=seed,
                           batch=64,horizon=70,greedy=False,**kw)["final"]
                result.append(e)
            meanfood=sum(x["food"] for x in result)/len(result)
            row=dict(model=name,n=cfg.n,m=M,k=k,mode=mode,
                food=meanfood,dist=sum(x["d"] for x in result)/len(result),
                exact=sum(x["exact"] for x in result),worlds=128)
            print("STRESS",name,M,k,mode,round(meanfood,4),row["exact"],flush=True)
            rows.append(row)
write_json(ROOT/"STRESS_80_PROFESIONES.json",{
    "kind":"EXPLORATORY_FROZEN_TRANSFER",
    "seeds":[991001,991019],"batch":64,"horizon":70,
    "no_training_on_held_k":True,"results":rows})
print("STRESS_COMPLETE")
